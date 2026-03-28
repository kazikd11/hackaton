# Data Decisions – Agent 1

## Data Sources

| Source | File Pattern | Records | Purpose |
|--------|-------------|---------|---------|
| Activity Sequence Export | 20 CSV files, ~1.5 GB total | 2,261,737 events / 558,859 de-duped step occurrences | Primary event log – source of truth |
| Activity Heatmap Export | 2 CSV files | 210 edges | Copy-paste flow between apps/steps |
| Process Distribution Export | 1 CSV | 26 daily rows | Time spent per process family per day |
| Tool use aggregated Export | 1 CSV | 182 rows | Total/active/passive time per app |
| Tool use over time Export | 1 CSV | 1,556 rows | Daily time per app |
| Headcount Coverage Export | 1 CSV | 20 rows | Measured vs expected user counts |
| PRM Export | 1 CSV | 15,000 rows | Process Resource Matrix – app/view durations |
| BPMN model | 1 file | 54 nodes, 256 flows | Process graph for Collector |
| PDD Export | 1 DOCX | 1 section, 100 tables | Process Definition Document |

## Process Families

Five families discovered from `Process Name` field:

| Family | Cases | Users | Duration (h) | Avg Steps/Case |
|--------|-------|-------|-------------|----------------|
| Collector | 577 | 50 | 167.8 | 249 |
| Unassigned/Other | 325 | 43 | 348.5 | 783 |
| Communication | 221 | 38 | 135.2 | 515 |
| Youtrack Production Process | 140 | 28 | 40.8 | 227 |
| Coding Activities | 52 | 11 | 15.2 | 276 |

**Mapping rule**: Empty or unrecognised `Process Name` → `Unassigned/Other`.

## Case Definition

A "case" = one user × one process family × one calendar day. This is a pragmatic proxy because the desktop-monitoring data lacks explicit case IDs. Wall time = `last_step_end − first_step_start` for the same case.

## Metric Definitions

### Raw Metrics (per family)

| Metric | Source | Meaning |
|--------|--------|---------|
| `manual_effort_raw` | Avg (copies + pastes + text_entries + clicks) per case | Volume of manual interactions |
| `time_cost_raw` | Avg wall time per case in hours | Elapsed time cost |
| `handoff_raw` | Avg unique applications per case | Context switching breadth |
| `repetition_raw` | Total steps / unique steps ratio | How repetitive the step sequence is |
| `variance_raw` | StdDev(duration) / Mean(duration) across cases | Execution inconsistency |
| `coverage_penalty_raw` | 1 − (measured_users / expected_users) | Data completeness penalty |
| `copy_paste_signals` | Sum of copy + paste + cut across all steps | Volume of clipboard operations |
| `context_switches` | Count of app-to-app transitions within family | Frequency of switching |

### Normalisation

All raw metrics (except coverage_penalty) are min-max normalised to [0, 1] across families.

### Composite Score

```
score = 0.30 × manual_effort
      + 0.25 × time_cost
      + 0.20 × handoff
      + 0.15 × repetition
      + 0.10 × variance
      − 0.10 × coverage_penalty
```

Higher score = stronger automation opportunity.

## Cache Artifacts

All cached in `.cache/analytics/`:

| File | Format | Description |
|------|--------|-------------|
| `events_core.parquet` | Parquet | Normalised event log (2.2M rows, lean columns) |
| `step_occurrences.parquet` | Parquet | De-duped step occurrences (559K rows) |
| `cases.parquet` | Parquet | Case-level rollups (1,315 cases) |
| `app_transitions.parquet` | Parquet | App-to-app transition edges (11,890) |
| `heatmap_edges.parquet` | Parquet | Copy-paste heatmap edges (210) |
| `process_families.parquet` | Parquet | Daily time by family (26 rows) |
| `tool_usage_aggregated.parquet` | Parquet | App time totals (182 rows) |
| `tool_usage_daily.parquet` | Parquet | Daily app usage (1,556 rows) |
| `headcount.parquet` | Parquet | Headcount coverage (20 rows) |
| `prm.parquet` | Parquet | Process Resource Matrix (15K rows) |
| `bpmn_nodes.json` | JSON | BPMN graph nodes and flows |
| `pdd_variants.json` | JSON | PDD sections and tables |
| `automation_input_metrics.json` | JSON | Scored metrics per family (5 records) |

## Fixture Files

In `shared/fixtures/`:

| File | Contract | Description |
|------|----------|-------------|
| `overview.json` | ProcessOverview | Full overview with family summaries, top tools, headcount |
| `process_detail.json` | ProcessDetail (VariantSummary + StepInsight) | Collector family deep-dive |
| `opportunities.json` | AutomationOpportunity[] | Ranked list with score components + evidence |
| `workflow_sample.json` | WorkflowDefinition | Sample input/output for workflow generation |

## Design Decisions

1. **CSV safety**: `csv.field_size_limit(2^30)` to handle OCR/Content fields. We skip OCR/Content entirely for V1 analytics.
2. **Streaming**: All CSVs are read with `csv.DictReader` (row-by-row), not `pd.read_csv()` for the large Activity Sequence files. This keeps memory bounded.
3. **Parquet**: All intermediate caches use Parquet for fast columnar reads.
4. **Idempotent**: Pipeline skips steps when cache already exists (`force=True` overrides).
5. **Timestamps**: All timestamp parsing uses `pd.to_datetime(..., errors="coerce")` for robustness.
6. **BPMN**: Only the Collector process has BPMN data. Other families lack BPMN models.
