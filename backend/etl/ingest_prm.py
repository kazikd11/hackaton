"""
Ingest PRM Export CSV -> prm.parquet

PRM = Process Resource Matrix.
Schema: Path, Member, Member UUID, Application, View, Duration [HH:MM:SS], …
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .config import CACHE_DIR, DATASET_DIR, ensure_dirs


def _hhmmss_to_seconds(val: str) -> int:
    if not val or not isinstance(val, str):
        return 0
    parts = val.strip().split(":")
    if len(parts) != 3:
        return 0
    try:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        return 0


def ingest_prm(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "prm.parquet"
    if not force and out.exists():
        return out

    csv_path = None
    for f in sorted(DATASET_DIR.iterdir()):
        if f.name.startswith("PRM Export"):
            csv_path = f
            break

    if csv_path is None:
        raise FileNotFoundError("PRM Export CSV not found")

    df = pd.read_csv(csv_path)
    # Convert duration columns from HH:MM:SS to seconds
    for col in df.columns:
        if "[HH:MM:SS]" in col:
            base = col.replace(" [HH:MM:SS]", "").strip().lower().replace(" ", "_")
            df[base + "_sec"] = df[col].apply(lambda v: _hhmmss_to_seconds(str(v)))

    df.to_parquet(out, index=False)
    print(f"[ingest_prm] {len(df)} rows -> {out.name}")
    return out


if __name__ == "__main__":
    ingest_prm(force="--force" in sys.argv)
