"""
prep_metrics.py – Agent 1 analytics prep

Derives per-process-family metric components used by the scoring formula:
  score = 0.30*manual_effort + 0.25*time_cost + 0.20*handoff
        + 0.15*repetition + 0.10*variance - 0.10*coverage_penalty

Produces automation_input_metrics.json in CACHE_DIR.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np

from backend.etl.config import CACHE_DIR, KNOWN_FAMILIES, UNASSIGNED_LABEL, ensure_dirs


def _safe_norm(series: pd.Series) -> pd.Series:
    """Min-max normalise to [0, 1] without NaN."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def prepare_metrics(force: bool = False) -> Path:
    """
    Read cached parquet files and compute metric components
    per process family.  Output JSON with one entry per family.
    """
    ensure_dirs()
    out = CACHE_DIR / "automation_input_metrics.json"
    if not force and out.exists():
        return out

    # ── Load data ───────────────────────────────────────────────────
    cases = pd.read_parquet(CACHE_DIR / "cases.parquet")
    steps = pd.read_parquet(CACHE_DIR / "step_occurrences.parquet")
    transitions = pd.read_parquet(CACHE_DIR / "app_transitions.parquet")
    headcount = pd.read_parquet(CACHE_DIR / "headcount.parquet")

    families = list(cases["process_family"].unique())

    records: list[dict] = []

    for fam in families:
        c = cases[cases["process_family"] == fam]
        s = steps[steps["process_family"] == fam]

        # ── manual_effort: avg copy+paste+text_entries+clicks per case ──
        manual_signals = (
            c["total_copies"] + c["total_pastes"] + c["total_text_entries"] + c["total_clicks"]
        )
        manual_effort_raw = manual_signals.mean() if len(c) > 0 else 0

        # ── time_cost: avg wall_time_ms per case (in hours) ─────────
        time_cost_raw = (c["wall_time_ms"].mean() / 3_600_000) if len(c) > 0 else 0

        # ── handoff: unique apps per case (avg) ─────────────────────
        handoff_raw = c["unique_apps"].mean() if len(c) > 0 else 0

        # ── repetition: ratio of total steps to unique steps ────────
        repetition_raw = (
            (c["step_count"].sum() / max(c["unique_steps"].sum(), 1))
            if len(c) > 0
            else 1
        )

        # ── variance: std of duration across cases  ─────────────────
        variance_raw = (
            c["total_duration_ms"].std() / max(c["total_duration_ms"].mean(), 1)
            if len(c) > 1
            else 0
        )

        # ── coverage_penalty: what fraction of team is NOT measured ─
        if len(headcount) > 0:
            measured = headcount["measured_users"].astype(int).sum()
            expected = headcount["expected_users"].astype(int).sum()
            coverage_penalty_raw = 1 - (measured / max(expected, 1))
        else:
            coverage_penalty_raw = 0.5

        # ── copy-paste evidence ─────────────────────────────────────
        copy_paste_total = int(s["copies"].sum() + s["pastes"].sum() + s["cuts"].sum())

        # ── context switching ────────────────────────────────────────
        # transitions within this family
        t_fam = transitions[transitions["to_family"] == fam] if "to_family" in transitions.columns else pd.DataFrame()
        context_switches = int(t_fam["count"].sum()) if len(t_fam) > 0 else 0

        records.append({
            "process_family": fam,
            "case_count": int(len(c)),
            "step_occurrence_count": int(len(s)),
            "manual_effort_raw": round(float(manual_effort_raw), 4),
            "time_cost_raw": round(float(time_cost_raw), 4),
            "handoff_raw": round(float(handoff_raw), 4),
            "repetition_raw": round(float(repetition_raw), 4),
            "variance_raw": round(float(variance_raw), 4),
            "coverage_penalty_raw": round(float(coverage_penalty_raw), 4),
            "copy_paste_signals": copy_paste_total,
            "context_switches": context_switches,
        })

    # ── Normalise across families ───────────────────────────────────
    df = pd.DataFrame(records)
    for col in ["manual_effort_raw", "time_cost_raw", "handoff_raw",
                 "repetition_raw", "variance_raw"]:
        norm_col = col.replace("_raw", "")
        df[norm_col] = _safe_norm(df[col])

    # Coverage penalty is already 0..1
    df["coverage_penalty"] = df["coverage_penalty_raw"].clip(0, 1)

    # ── Compute composite score ─────────────────────────────────────
    df["score"] = (
        0.30 * df["manual_effort"]
        + 0.25 * df["time_cost"]
        + 0.20 * df["handoff"]
        + 0.15 * df["repetition"]
        + 0.10 * df["variance"]
        - 0.10 * df["coverage_penalty"]
    ).round(4)

    df["rank"] = df["score"].rank(ascending=False, method="dense").astype(int)

    result = df.sort_values("rank").to_dict(orient="records")

    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"[prep_metrics] {len(result)} families scored -> {out.name}")
    return out


if __name__ == "__main__":
    prepare_metrics(force="--force" in sys.argv)
