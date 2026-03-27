# Agent 1: Data And Mining

## Your Scope
- You own this directory.
- You may also create metric-prep files in `backend/analytics` using the prefixes `prep_`, `derive_`, or `extract_`.
- You own `shared/fixtures`.

## Objective
- Build the canonical ingest and cache pipeline from the challenge exports.

## Inputs
- `Activity Sequence Export` CSV files
- `Activity Heatmap Export` CSV files
- `Headcount Coverage Export` CSV
- `PRM Export` CSV
- `Process Distribution Export` CSV
- `Tool use aggregated Export` CSV
- `Tool use over time Export` CSV
- `model (67).bpmn`
- `PDD Export - 2026-03-20 09_09_56.docx`

## Rules
- Treat event logs as source of truth.
- Treat BPMN and PDD as enrichment only.
- Stream or chunk large CSVs.
- Do not require full OCR or large content blobs for V1 analytics.
- Keep short excerpts only when useful for evidence cards.
- Bucket empty or unknown `Process Name` into `Unassigned/Other`.

## Expected Outputs
- Canonical cache tables or files for:
  - `events_core`
  - `step_occurrences`
  - `cases`
  - `process_families`
  - `app_transitions`
  - `tool_usage_daily`
  - `heatmap_edges`
  - `pdd_variants`
  - `bpmn_nodes`
- Gold fixtures in `shared/fixtures`
- Clear metric notes in `docs/data-decisions.md`

## Handoff Bar
- Downstream agents should be able to build against your fixtures without guessing field meanings.
- If a shape is uncertain, freeze one shape and document it instead of leaving it implicit.

