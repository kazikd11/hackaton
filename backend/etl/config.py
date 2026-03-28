"""
Centralised configuration for ETL / analytics.
All paths are resolved lazily so env-vars can be overridden before import.
"""
from __future__ import annotations
import os
from pathlib import Path

# ── repo root ───────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]

# ── dataset directory ───────────────────────────────────────────────
DATASET_DIR = Path(
    os.environ.get(
        "DATASET_DIR",
        str(REPO_ROOT / "Process-to-Automation Copilot Challenge" / "Dataset"),
    )
)

# ── cache directory ─────────────────────────────────────────────────
CACHE_DIR = Path(os.environ.get("CACHE_DIR", str(REPO_ROOT / ".cache" / "analytics")))

# ── fixture directory ───────────────────────────────────────────────
FIXTURE_DIR = REPO_ROOT / "shared" / "fixtures"

# ── app mode ────────────────────────────────────────────────────────
APP_MODE: str = os.environ.get("APP_MODE", "fixture")

# ── CSV safety ──────────────────────────────────────────────────────
CSV_FIELD_LIMIT: int = 2**30  # 1 GiB – handles huge OCR / Content fields

# ── process family mapping ──────────────────────────────────────────
KNOWN_FAMILIES = [
    "Collector",
    "Communication",
    "Youtrack Production Process",
    "Coding Activities",
]
UNASSIGNED_LABEL = "Unassigned/Other"


def ensure_dirs() -> None:
    """Create cache and fixture dirs if missing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
