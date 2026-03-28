"""
Ingest Activity Sequence Export CSVs -> events_core.parquet + step_occurrences.parquet

Streams rows with csv.reader to avoid loading huge OCR / Content fields.
Outputs only the columns needed for downstream analytics.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Iterator

import pandas as pd

from .config import CACHE_DIR, CSV_FIELD_LIMIT, DATASET_DIR, KNOWN_FAMILIES, UNASSIGNED_LABEL, ensure_dirs

# ── column indices we care about ────────────────────────────────────
_CORE_COLS = [
    "User name",          # 0  – user UUID hash
    "Process step",       # 2
    "Application name",   # 3
    "Activity Status",    # 5
    "Process step start", # 6
    "Process step end",   # 7
    "Activity duration (ms)",  # 8
    "Activity type",      # 9
    "Activity start timestamp",  # 11
    "Process Name",       # 15
    "Process ID",         # 16
    "User UUID",          # 18
    "Copy No.",           # 29
    "Paste No.",          # 30
    "Cut No.",            # 31
    "Text entries No.",   # 26
    "Clicks No.",         # 27
]

# Lightweight subset for step_occurrences
_STEP_COLS = [
    "User UUID",
    "Process step",
    "Application name",
    "Process Name",
    "Process step start",
    "Process step end",
    "Activity duration (ms)",
    "Copy No.",
    "Paste No.",
    "Cut No.",
    "Text entries No.",
    "Clicks No.",
]


def _family(raw: str) -> str:
    """Map raw process name to canonical family label."""
    if not raw or raw.strip() == "":
        return UNASSIGNED_LABEL
    for k in KNOWN_FAMILIES:
        if k.lower() in raw.lower():
            return k
    return UNASSIGNED_LABEL


def _iter_activity_csvs() -> Iterator[Path]:
    """Yield Activity Sequence CSV paths in deterministic order."""
    for f in sorted(DATASET_DIR.iterdir()):
        if f.name.startswith("Activity Sequence Export") and f.suffix == ".csv":
            yield f


def _safe_int(val: str, default: int = 0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def ingest_events(force: bool = False) -> tuple[Path, Path]:
    """
    Read all Activity Sequence CSVs, emit:
      - events_core.parquet   (one row per activity)
      - step_occurrences.parquet (one row per process-step occurrence, de-duped)
    Returns paths to both files.
    """
    ensure_dirs()
    events_path = CACHE_DIR / "events_core.parquet"
    steps_path = CACHE_DIR / "step_occurrences.parquet"
    if not force and events_path.exists() and steps_path.exists():
        return events_path, steps_path

    csv.field_size_limit(CSV_FIELD_LIMIT)

    event_rows: list[dict] = []
    step_keys_seen: set[tuple] = set()
    step_rows: list[dict] = []

    for csv_path in _iter_activity_csvs():
        with open(csv_path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                user_uuid = row.get("User UUID", "")
                process_step = row.get("Process step", "")
                app = row.get("Application name", "")
                proc_name_raw = row.get("Process Name", "")
                family = _family(proc_name_raw)
                start = row.get("Process step start", "")
                end = row.get("Process step end", "")
                duration_ms = _safe_int(row.get("Activity duration (ms)", "0"))
                activity_type = row.get("Activity type", "")
                timestamp = row.get("Activity start timestamp", "")
                copies = _safe_int(row.get("Copy No.", "0"))
                pastes = _safe_int(row.get("Paste No.", "0"))
                cuts = _safe_int(row.get("Cut No.", "0"))
                text_entries = _safe_int(row.get("Text entries No.", "0"))
                clicks = _safe_int(row.get("Clicks No.", "0"))

                event_rows.append({
                    "user_uuid": user_uuid,
                    "process_step": process_step,
                    "application": app,
                    "activity_status": row.get("Activity Status", ""),
                    "step_start": start,
                    "step_end": end,
                    "duration_ms": duration_ms,
                    "activity_type": activity_type,
                    "timestamp": timestamp,
                    "process_name": proc_name_raw,
                    "process_family": family,
                    "process_id": row.get("Process ID", ""),
                    "copies": copies,
                    "pastes": pastes,
                    "cuts": cuts,
                    "text_entries": text_entries,
                    "clicks": clicks,
                })

                # De-dup step occurrences on (user, step, start, app)
                step_key = (user_uuid, process_step, start, app)
                if step_key not in step_keys_seen:
                    step_keys_seen.add(step_key)
                    step_rows.append({
                        "user_uuid": user_uuid,
                        "process_step": process_step,
                        "application": app,
                        "process_family": family,
                        "step_start": start,
                        "step_end": end,
                        "duration_ms": duration_ms,
                        "copies": copies,
                        "pastes": pastes,
                        "cuts": cuts,
                        "text_entries": text_entries,
                        "clicks": clicks,
                    })

    # ── Build DataFrames ────────────────────────────────────────────
    df_events = pd.DataFrame(event_rows)
    if not df_events.empty:
        for ts_col in ("step_start", "step_end", "timestamp"):
            df_events[ts_col] = pd.to_datetime(df_events[ts_col], errors="coerce")

    df_steps = pd.DataFrame(step_rows)
    if not df_steps.empty:
        for ts_col in ("step_start", "step_end"):
            df_steps[ts_col] = pd.to_datetime(df_steps[ts_col], errors="coerce")

    df_events.to_parquet(events_path, index=False)
    df_steps.to_parquet(steps_path, index=False)

    print(f"[ingest_events] {len(df_events):,} events -> {events_path.name}")
    print(f"[ingest_events] {len(df_steps):,} step occurrences -> {steps_path.name}")
    return events_path, steps_path


if __name__ == "__main__":
    ingest_events(force="--force" in sys.argv)
