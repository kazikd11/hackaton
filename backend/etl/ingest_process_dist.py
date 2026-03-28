"""
Ingest Process Distribution Export CSV -> process_families.parquet

Schema: Aggregate (date), and one [HH:MM:SS] column per process family.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

from .config import CACHE_DIR, DATASET_DIR, KNOWN_FAMILIES, UNASSIGNED_LABEL, ensure_dirs


def _hhmmss_to_seconds(val: str) -> int:
    """Convert 'HH:MM:SS' or 'H:MM:SS' to total seconds."""
    if not val or not isinstance(val, str):
        return 0
    parts = val.strip().split(":")
    if len(parts) != 3:
        return 0
    try:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        return 0


def ingest_process_dist(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "process_families.parquet"
    if not force and out.exists():
        return out

    csv_path = None
    for f in sorted(DATASET_DIR.iterdir()):
        if f.name.startswith("Process Distribution Export"):
            csv_path = f
            break

    if csv_path is None:
        raise FileNotFoundError("Process Distribution Export CSV not found")

    df = pd.read_csv(csv_path)

    # Parse columns: "Collector [HH:MM:SS]" -> family name + seconds
    rows: list[dict] = []
    for _, raw_row in df.iterrows():
        row_dict: dict = {"date": raw_row.iloc[0]}  # Aggregate column
        for col in df.columns[1:]:
            # Extract family name from "FamilyName [HH:MM:SS]"
            match = re.match(r"^(.+?)\s*\[HH:MM:SS\]$", col)
            if match:
                family_name = match.group(1).strip()
                row_dict[family_name + "_seconds"] = _hhmmss_to_seconds(
                    str(raw_row[col])
                )
        rows.append(row_dict)

    result = pd.DataFrame(rows)
    result.to_parquet(out, index=False)
    print(f"[ingest_process_dist] {len(result)} rows -> {out.name}")
    return out


if __name__ == "__main__":
    ingest_process_dist(force="--force" in sys.argv)
