"""
Ingest Activity Heatmap Export CSVs -> heatmap_edges.parquet

Two heatmap CSVs:
  - App-level: Application(Copy&Cut), Application(Paste), Count
  - Step-level: Application(Copy&Cut), Process Step(Copy&Cut), Application(Paste), Process Step(Paste), Count
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .config import CACHE_DIR, DATASET_DIR, ensure_dirs


def ingest_heatmap(force: bool = False) -> Path:
    ensure_dirs()
    out = CACHE_DIR / "heatmap_edges.parquet"
    if not force and out.exists():
        return out

    frames: list[pd.DataFrame] = []
    for f in sorted(DATASET_DIR.iterdir()):
        if not f.name.startswith("Activity Heatmap Export"):
            continue
        df = pd.read_csv(f)
        # Normalise column names
        cols = {}
        for c in df.columns:
            if "Copy" in c and "Application" in c:
                cols[c] = "from_app"
            elif "Paste" in c and "Application" in c:
                cols[c] = "to_app"
            elif "Copy" in c and "Step" in c:
                cols[c] = "from_step"
            elif "Paste" in c and "Step" in c:
                cols[c] = "to_step"
            elif c == "Count":
                cols[c] = "count"
        df = df.rename(columns=cols)
        # Fill missing step columns
        if "from_step" not in df.columns:
            df["from_step"] = ""
        if "to_step" not in df.columns:
            df["to_step"] = ""
        df = df[["from_app", "from_step", "to_app", "to_step", "count"]]
        frames.append(df)

    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    result.to_parquet(out, index=False)
    print(f"[ingest_heatmap] {len(result):,} heatmap edges -> {out.name}")
    return out


if __name__ == "__main__":
    ingest_heatmap(force="--force" in sys.argv)
