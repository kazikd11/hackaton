"""
Build app transition counts (context-switching evidence).

Transitions capture when a user switches between applications within a process step sequence.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .config import CACHE_DIR, ensure_dirs


def build_transitions(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "app_transitions.parquet"
    events_path = CACHE_DIR / "events_core.parquet"
    if not force and out.exists():
        return out

    if not events_path.exists():
        raise FileNotFoundError(f"{events_path} not found – run ingest_events first")

    # Only load the lightweight columns we need
    df = pd.read_parquet(
        events_path,
        columns=["user_uuid", "application", "timestamp", "process_family"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values(["user_uuid", "timestamp"])

    # Detect transitions: where successive rows for same user have different apps
    df["prev_app"] = df.groupby("user_uuid")["application"].shift(1)
    df["prev_family"] = df.groupby("user_uuid")["process_family"].shift(1)
    transitions = df[df["application"] != df["prev_app"]].copy()
    transitions = transitions.rename(columns={
        "prev_app": "from_app",
        "application": "to_app",
        "prev_family": "from_family",
        "process_family": "to_family",
    })

    # Aggregate transition counts
    agg = (
        transitions.groupby(["from_app", "to_app", "to_family"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    agg.to_parquet(out, index=False)
    print(f"[build_transitions] {len(agg):,} transition edges -> {out.name}")
    return out


if __name__ == "__main__":
    build_transitions(force="--force" in sys.argv)
