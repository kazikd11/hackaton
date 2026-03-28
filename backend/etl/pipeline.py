"""
Master pipeline – runs all ETL steps in order.

Usage:
    python -m backend.etl.pipeline [--force]
"""
from __future__ import annotations

import sys
import time

from .config import ensure_dirs


def run_pipeline(force: bool = False) -> None:
    ensure_dirs()
    t0 = time.time()

    print("=" * 60)
    print("  Process-to-Automation Copilot – ETL Pipeline")
    print("=" * 60)

    # Step 1: Ingest raw events (biggest step)
    print("\n[1/10] Ingesting Activity Sequence CSVs...")
    from .ingest_events import ingest_events
    ingest_events(force=force)

    # Step 2: Build case summaries
    print("\n[2/10] Building case summaries...")
    from .build_cases import build_cases
    build_cases(force=force)

    # Step 3: Build app transitions
    print("\n[3/10] Building app transitions...")
    from .build_transitions import build_transitions
    build_transitions(force=force)

    # Step 4: Ingest heatmaps
    print("\n[4/10] Ingesting heatmaps...")
    from .ingest_heatmap import ingest_heatmap
    ingest_heatmap(force=force)

    # Step 5: Ingest process distribution
    print("\n[5/10] Ingesting process distribution...")
    from .ingest_process_dist import ingest_process_dist
    ingest_process_dist(force=force)

    # Step 6: Ingest tool usage
    print("\n[6/10] Ingesting tool usage...")
    from .ingest_tools import ingest_tools
    ingest_tools(force=force)

    # Step 7: Ingest headcount
    print("\n[7/10] Ingesting headcount coverage...")
    from .ingest_headcount import ingest_headcount
    ingest_headcount(force=force)

    # Step 8: Ingest BPMN & PDD
    print("\n[8/10] Ingesting BPMN & PDD...")
    from .ingest_bpmn import ingest_bpmn
    from .ingest_pdd import ingest_pdd
    from .ingest_prm import ingest_prm
    ingest_bpmn(force=force)
    ingest_pdd(force=force)
    ingest_prm(force=force)

    # Step 9: Prepare metrics
    print("\n[9/10] Preparing automation metrics...")
    from backend.analytics.prep_metrics import prepare_metrics
    prepare_metrics(force=force)

    # Step 10: Generate fixtures
    print("\n[10/10] Generating gold fixtures...")
    from .generate_fixtures import generate_fixtures
    generate_fixtures(force=force)

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  Pipeline complete in {elapsed:.1f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run_pipeline(force="--force" in sys.argv)
