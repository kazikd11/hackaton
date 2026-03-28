"""
Build case-level summaries from step_occurrences.

A "case" is all activity for one user within one process family on a single day.
This is a practical proxy for "one execution of a process" given the desktop-monitoring data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .config import CACHE_DIR, ensure_dirs


def build_cases(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "cases.parquet"
    steps_path = CACHE_DIR / "step_occurrences.parquet"
    if not force and out.exists():
        return out

    if not steps_path.exists():
        raise FileNotFoundError(
            f"{steps_path} not found – run ingest_events first"
        )

    df = pd.read_parquet(steps_path)
    df["step_start"] = pd.to_datetime(df["step_start"], errors="coerce")
    df["step_end"] = pd.to_datetime(df["step_end"], errors="coerce")
    df["date"] = df["step_start"].dt.date

    cases = (
        df.groupby(["user_uuid", "process_family", "date"])
        .agg(
            step_count=("process_step", "count"),
            unique_steps=("process_step", "nunique"),
            unique_apps=("application", "nunique"),
            total_duration_ms=("duration_ms", "sum"),
            total_copies=("copies", "sum"),
            total_pastes=("pastes", "sum"),
            total_cuts=("cuts", "sum"),
            total_text_entries=("text_entries", "sum"),
            total_clicks=("clicks", "sum"),
            first_step=("step_start", "min"),
            last_step=("step_end", "max"),
        )
        .reset_index()
    )
    cases["case_id"] = [f"case-{i:06d}" for i in range(len(cases))]
    cases["wall_time_ms"] = (
        (cases["last_step"] - cases["first_step"]).dt.total_seconds() * 1000
    ).fillna(0).astype(int)

    cases.to_parquet(out, index=False)
    print(f"[build_cases] {len(cases):,} cases -> {out.name}")
    return out


if __name__ == "__main__":
    build_cases(force="--force" in sys.argv)
