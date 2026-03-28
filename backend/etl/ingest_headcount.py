"""
Ingest Headcount Coverage Export CSV -> headcount.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .config import CACHE_DIR, DATASET_DIR, ensure_dirs


def ingest_headcount(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "headcount.parquet"
    if not force and out.exists():
        return out

    csv_path = None
    for f in sorted(DATASET_DIR.iterdir()):
        if f.name.startswith("Headcount Coverage Export"):
            csv_path = f
            break

    if csv_path is None:
        raise FileNotFoundError("Headcount Coverage Export CSV not found")

    df = pd.read_csv(csv_path)
    # Columns: Aggregate, Measured users, Not measured users, Expected users
    df = df.rename(columns={
        "Aggregate": "date",
        "Measured users": "measured_users",
        "Not measured users": "not_measured_users",
        "Expected users": "expected_users",
    })
    # Drop the trailing filter lines
    df = df[df["date"].str.match(r"^\d{2}\.\d{2}$", na=False)].copy()
    df.to_parquet(out, index=False)
    print(f"[ingest_headcount] {len(df)} rows -> {out.name}")
    return out


if __name__ == "__main__":
    ingest_headcount(force="--force" in sys.argv)
