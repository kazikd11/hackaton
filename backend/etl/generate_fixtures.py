"""
Generate gold fixtures from cached analytics data.

Produces 3 fixture files in shared/fixtures/:
  1. overview.json          – full process overview payload
  2. process_detail.json    – detail for one representative process family
  3. opportunities.json     – ranked automation opportunities
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

from .config import CACHE_DIR, FIXTURE_DIR, KNOWN_FAMILIES, UNASSIGNED_LABEL, ensure_dirs


def _load_json(path: Path) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ts(dt) -> str | None:
    """Format a datetime for JSON."""
    if pd.isna(dt):
        return None
    if isinstance(dt, pd.Timestamp):
        return dt.isoformat()
    return str(dt)


def generate_fixtures(force: bool = False) -> list[Path]:
    ensure_dirs()
    out_files: list[Path] = []

    # ── Load cached data ────────────────────────────────────────────
    cases = pd.read_parquet(CACHE_DIR / "cases.parquet")
    steps = pd.read_parquet(CACHE_DIR / "step_occurrences.parquet")
    transitions = pd.read_parquet(CACHE_DIR / "app_transitions.parquet")
    metrics = _load_json(CACHE_DIR / "automation_input_metrics.json")
    heatmap = pd.read_parquet(CACHE_DIR / "heatmap_edges.parquet")
    bpmn = _load_json(CACHE_DIR / "bpmn_nodes.json")
    headcount = pd.read_parquet(CACHE_DIR / "headcount.parquet")

    # Try loading tool usage
    try:
        tool_agg = pd.read_parquet(CACHE_DIR / "tool_usage_aggregated.parquet")
    except Exception:
        tool_agg = pd.DataFrame()

    try:
        tool_daily = pd.read_parquet(CACHE_DIR / "tool_usage_daily.parquet")
    except Exception:
        tool_daily = pd.DataFrame()

    # ═══════════════════════════════════════════════════════════════
    #  1. overview.json – ProcessOverview
    # ═══════════════════════════════════════════════════════════════
    families_summary = []
    for fam in sorted(cases["process_family"].unique()):
        c = cases[cases["process_family"] == fam]
        families_summary.append({
            "id": fam.lower().replace(" ", "_").replace("/", "_"),
            "name": fam,
            "case_count": int(len(c)),
            "unique_users": int(c["user_uuid"].nunique()),
            "total_duration_hours": round(float(c["total_duration_ms"].sum() / 3_600_000), 2),
            "avg_steps_per_case": round(float(c["step_count"].mean()), 1),
            "avg_apps_per_case": round(float(c["unique_apps"].mean()), 1),
        })

    # Date range from cases
    cases["first_step"] = pd.to_datetime(cases["first_step"], errors="coerce")
    cases["last_step"] = pd.to_datetime(cases["last_step"], errors="coerce")
    date_range = {
        "start": _ts(cases["first_step"].min()),
        "end": _ts(cases["last_step"].max()),
    }

    # Top tools
    top_tools = []
    if not tool_agg.empty and "Application" in tool_agg.columns:
        for _, row in tool_agg.head(10).iterrows():
            entry = {"application": row["Application"]}
            if "total_sec" in tool_agg.columns:
                entry["total_hours"] = round(row["total_sec"] / 3600, 2)
            if "active_sec" in tool_agg.columns:
                entry["active_hours"] = round(row["active_sec"] / 3600, 2)
            top_tools.append(entry)

    overview = {
        "date_range": date_range,
        "total_cases": int(len(cases)),
        "total_users": int(cases["user_uuid"].nunique()),
        "total_events": int(steps["duration_ms"].count()),
        "process_families": families_summary,
        "top_tools": top_tools,
        "headcount_summary": {
            "avg_measured": round(float(headcount["measured_users"].astype(int).mean()), 1) if len(headcount) > 0 else 0,
            "avg_expected": round(float(headcount["expected_users"].astype(int).mean()), 1) if len(headcount) > 0 else 0,
        },
    }

    overview_path = FIXTURE_DIR / "overview.json"
    with open(overview_path, "w", encoding="utf-8") as f:
        json.dump(overview, f, indent=2, ensure_ascii=False)
    out_files.append(overview_path)
    print(f"[fixtures] overview.json ({len(families_summary)} families)")

    # ═══════════════════════════════════════════════════════════════
    #  2. process_detail.json – one process family in detail
    # ═══════════════════════════════════════════════════════════════
    # Pick the family with the most cases (most interesting)
    best_fam = max(families_summary, key=lambda x: x["case_count"])
    fam_name = best_fam["name"]
    fam_id = best_fam["id"]

    fam_cases = cases[cases["process_family"] == fam_name]
    fam_steps = steps[steps["process_family"] == fam_name]

    # Variant summaries: top step sequences
    variant_groups = (
        fam_steps.groupby("process_step")
        .agg(
            occurrence_count=("duration_ms", "count"),
            total_duration_ms=("duration_ms", "sum"),
            avg_duration_ms=("duration_ms", "mean"),
            unique_users=("user_uuid", "nunique"),
            primary_app=("application", lambda x: x.mode().iloc[0] if len(x) > 0 else ""),
            copy_paste_count=("copies", "sum"),
        )
        .reset_index()
        .sort_values("occurrence_count", ascending=False)
    )

    variants: list[dict] = []
    for _, row in variant_groups.head(20).iterrows():
        variants.append({
            "step_name": row["process_step"],
            "occurrence_count": int(row["occurrence_count"]),
            "total_duration_hours": round(float(row["total_duration_ms"] / 3_600_000), 3),
            "avg_duration_ms": round(float(row["avg_duration_ms"]), 0),
            "unique_users": int(row["unique_users"]),
            "primary_application": row["primary_app"],
            "copy_paste_count": int(row["copy_paste_count"]),
        })

    # Step insights
    step_insights: list[dict] = []
    for _, row in variant_groups.head(15).iterrows():
        insight = {
            "step_name": row["process_step"],
            "application": row["primary_app"],
            "avg_duration_ms": round(float(row["avg_duration_ms"]), 0),
            "occurrence_count": int(row["occurrence_count"]),
            "signals": [],
        }
        if row["copy_paste_count"] > 10:
            insight["signals"].append({
                "type": "copy_paste",
                "description": f'{int(row["copy_paste_count"])} copy/paste operations detected',
                "severity": "high" if row["copy_paste_count"] > 100 else "medium",
            })
        if row["avg_duration_ms"] > 60000:
            insight["signals"].append({
                "type": "long_duration",
                "description": f'Average duration {row["avg_duration_ms"]/1000:.0f}s – potential bottleneck',
                "severity": "high" if row["avg_duration_ms"] > 300000 else "medium",
            })
        step_insights.append(insight)

    # Transitions within this family
    fam_transitions = transitions[transitions["to_family"] == fam_name].head(15) if "to_family" in transitions.columns else pd.DataFrame()
    transition_list = []
    if not fam_transitions.empty:
        for _, row in fam_transitions.iterrows():
            transition_list.append({
                "from_app": row.get("from_app", ""),
                "to_app": row.get("to_app", ""),
                "count": int(row.get("count", 0)),
            })

    # Graph nodes (from BPMN if process matches)
    graph_nodes = [n for n in bpmn.get("nodes", []) if fam_name.lower() in n.get("process", "").lower()]
    graph_flows = [f for f in bpmn.get("flows", []) if fam_name.lower() in f.get("process", "").lower()]

    process_detail = {
        "id": fam_id,
        "name": fam_name,
        "summary": best_fam,
        "variants": variants,
        "step_insights": step_insights,
        "app_transitions": transition_list,
        "graph": {
            "nodes": graph_nodes[:50],
            "edges": graph_flows[:100],
        },
        "copy_paste_heatmap": heatmap.head(20).to_dict(orient="records") if not heatmap.empty else [],
    }

    detail_path = FIXTURE_DIR / "process_detail.json"
    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(process_detail, f, indent=2, ensure_ascii=False, default=str)
    out_files.append(detail_path)
    print(f"[fixtures] process_detail.json (family={fam_name})")

    # ═══════════════════════════════════════════════════════════════
    #  3. opportunities.json – AutomationOpportunity list
    # ═══════════════════════════════════════════════════════════════
    opportunities = []
    for m in metrics:
        fam = m["process_family"]
        fam_c = cases[cases["process_family"] == fam]
        fam_s = steps[steps["process_family"] == fam]

        # Find top steps with highest copy-paste as evidence
        evidence = []
        if not fam_s.empty:
            top_cp = (
                fam_s.groupby("process_step")
                .agg(cp=("copies", "sum"), ps=("pastes", "sum"))
                .assign(total_cp=lambda d: d["cp"] + d["ps"])
                .sort_values("total_cp", ascending=False)
                .head(3)
            )
            for step_name, row in top_cp.iterrows():
                if row["total_cp"] > 0:
                    evidence.append({
                        "type": "copy_paste",
                        "step": step_name,
                        "count": int(row["total_cp"]),
                    })

        # Add context-switching evidence
        if m.get("context_switches", 0) > 100:
            evidence.append({
                "type": "context_switching",
                "count": m["context_switches"],
                "description": f'{m["context_switches"]} app-to-app transitions',
            })

        opportunities.append({
            "id": f'opp-{fam.lower().replace(" ", "_").replace("/", "_")}',
            "process_family": fam,
            "rank": m["rank"],
            "score": m["score"],
            "score_components": {
                "manual_effort": round(m.get("manual_effort", 0), 4),
                "time_cost": round(m.get("time_cost", 0), 4),
                "handoff": round(m.get("handoff", 0), 4),
                "repetition": round(m.get("repetition", 0), 4),
                "variance": round(m.get("variance", 0), 4),
                "coverage_penalty": round(m.get("coverage_penalty", 0), 4),
            },
            "raw_values": {
                "manual_effort_raw": m.get("manual_effort_raw", 0),
                "time_cost_raw": m.get("time_cost_raw", 0),
                "handoff_raw": m.get("handoff_raw", 0),
                "repetition_raw": m.get("repetition_raw", 0),
                "variance_raw": m.get("variance_raw", 0),
            },
            "case_count": m["case_count"],
            "step_occurrence_count": m["step_occurrence_count"],
            "copy_paste_signals": m.get("copy_paste_signals", 0),
            "context_switches": m.get("context_switches", 0),
            "evidence": evidence,
        })

    opportunities.sort(key=lambda x: x["rank"])

    opp_path = FIXTURE_DIR / "opportunities.json"
    with open(opp_path, "w", encoding="utf-8") as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)
    out_files.append(opp_path)
    print(f"[fixtures] opportunities.json ({len(opportunities)} opportunities)")

    # ═══════════════════════════════════════════════════════════════
    #  4. workflow_sample.json – sample workflow gen input/output
    # ═══════════════════════════════════════════════════════════════
    if variants:
        workflow_sample = {
            "input": {
                "process_family": fam_name,
                "selected_steps": [v["step_name"] for v in variants[:8]],
            },
            "output": {
                "workflow_id": "wf-sample-001",
                "name": f"{fam_name} Automation Workflow",
                "steps": [
                    {
                        "order": i + 1,
                        "name": v["step_name"],
                        "application": v["primary_application"],
                        "action_type": "automated" if v["copy_paste_count"] > 50 else "manual",
                        "estimated_duration_ms": int(v["avg_duration_ms"]),
                    }
                    for i, v in enumerate(variants[:8])
                ],
                "estimated_savings_percent": 35,
                "notes": "Generated from process mining data. Review automated steps for feasibility.",
            },
        }
        wf_path = FIXTURE_DIR / "workflow_sample.json"
        with open(wf_path, "w", encoding="utf-8") as f:
            json.dump(workflow_sample, f, indent=2, ensure_ascii=False)
        out_files.append(wf_path)
        print(f"[fixtures] workflow_sample.json")

    print(f"\n[fixtures] {len(out_files)} fixture files generated in {FIXTURE_DIR}")
    return out_files


if __name__ == "__main__":
    generate_fixtures(force="--force" in sys.argv)
