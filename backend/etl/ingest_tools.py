"""
Ingest Tool use CSVs:
  - Tool use aggregated Export -> tool_usage_aggregated.parquet
  - Tool use over time Export  -> tool_usage_daily.parquet
"""
from __future__ import annotations

import re
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


def ingest_tools(force: bool = False) -> tuple[Path, Path]:
    ensure_dirs()
    agg_out = CACHE_DIR / "tool_usage_aggregated.parquet"
    daily_out = CACHE_DIR / "tool_usage_daily.parquet"
    if not force and agg_out.exists() and daily_out.exists():
        return agg_out, daily_out

    # ── aggregated ──────────────────────────────────────────────────
    agg_path = None
    daily_path = None
    for f in sorted(DATASET_DIR.iterdir()):
        if f.name.startswith("Tool use aggregated"):
            agg_path = f
        if f.name.startswith("Tool use over time"):
            daily_path = f

    if agg_path:
        df_agg = pd.read_csv(agg_path)
        # Columns: Application, Total [HH:MM:SS], Active [HH:MM:SS], Passive [HH:MM:SS]
        for col in df_agg.columns:
            if "[HH:MM:SS]" in col:
                base = col.replace(" [HH:MM:SS]", "").strip().lower().replace(" ", "_")
                df_agg[base + "_sec"] = df_agg[col].apply(
                    lambda v: _hhmmss_to_seconds(str(v))
                )
        df_agg.to_parquet(agg_out, index=False)
        print(f"[ingest_tools] {len(df_agg)} aggregated rows -> {agg_out.name}")

    # ── daily (tool use over time) ──────────────────────────────────
    if daily_path:
        df_daily = pd.read_csv(daily_path)
        # First column is "Aggregate" (date), remaining are app columns
        rows = []
        date_col = df_daily.columns[0]
        for _, raw in df_daily.iterrows():
            d = raw[date_col]
            for app_col in df_daily.columns[1:]:
                val = str(raw[app_col])
                secs = _hhmmss_to_seconds(val)
                if secs > 0:
                    rows.append({
                        "date": d,
                        "application": app_col,
                        "total_seconds": secs,
                    })
        result = pd.DataFrame(rows)
        result.to_parquet(daily_out, index=False)
        print(f"[ingest_tools] {len(result)} daily tool rows -> {daily_out.name}")

    return agg_out, daily_out


if __name__ == "__main__":
    ingest_tools(force="--force" in sys.argv)
