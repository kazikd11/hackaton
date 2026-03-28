"""
Data loader abstraction.

Provides a unified interface for loading data regardless of mode:
- fixture mode: reads JSON files from shared/fixtures/
- live mode: reads Agent 1's cached analytics from .cache/analytics/

Routes call this instead of reading files directly.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from backend.api.config import get_settings

logger = logging.getLogger(__name__)

# ── In-memory cache (lightweight, per-process) ────────────────────────────

_cache: dict[str, Any] = {}


def _read_json(path: Path) -> Any:
    """Read and parse a JSON file, with caching."""
    key = str(path)
    if key in _cache:
        return _cache[key]

    if not path.exists():
        logger.warning(f"Data file not found: {path}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _cache[key] = data
    return data


def invalidate_cache() -> None:
    """Clear the in-memory cache (useful for live mode reloads)."""
    _cache.clear()


# ── Fixture paths ─────────────────────────────────────────────────────────


def _fixtures_dir() -> Path:
    return Path(get_settings().fixtures_dir)


def _cache_dir() -> Path:
    return Path(get_settings().cache_dir)


# ── Public loaders ────────────────────────────────────────────────────────


def load_overview() -> Optional[dict]:
    """Load the process overview data."""
    settings = get_settings()

    if settings.is_fixture_mode:
        return _read_json(_fixtures_dir() / "overview.json")

    # Live mode: try cache, then fall back to fixtures
    live = _read_json(_cache_dir() / "overview.json")
    if live:
        return live
    logger.info("Live overview not found, falling back to fixtures")
    return _read_json(_fixtures_dir() / "overview.json")


def load_processes() -> Optional[list[dict]]:
    """Load the process family list."""
    settings = get_settings()

    if settings.is_fixture_mode:
        return _read_json(_fixtures_dir() / "processes.json")

    live = _read_json(_cache_dir() / "processes.json")
    if live:
        return live
    logger.info("Live processes not found, falling back to fixtures")
    return _read_json(_fixtures_dir() / "processes.json")


def load_process_by_id(process_id: str) -> Optional[dict]:
    """Load a single process family by ID."""
    processes = load_processes()
    if not processes:
        return None
    for p in processes:
        if p.get("id") == process_id:
            return p
    return None


def load_variants(process_id: str) -> Optional[dict]:
    """Load variant summary for a process."""
    settings = get_settings()

    if settings.is_fixture_mode:
        # Try process-specific fixture first
        data = _read_json(
            _fixtures_dir() / f"process_{process_id.replace('-', '_')}_variants.json"
        )
        if data:
            return data
        # Fall back to variants dir pattern
        data = _read_json(_fixtures_dir() / f"variants_{process_id}.json")
        return data

    live = _read_json(_cache_dir() / f"variants_{process_id}.json")
    if live:
        return live
    # Fall back to fixture
    return _read_json(
        _fixtures_dir() / f"process_{process_id.replace('-', '_')}_variants.json"
    )


def load_graph(process_id: str) -> Optional[dict]:
    """Load process graph for a process."""
    settings = get_settings()

    if settings.is_fixture_mode:
        data = _read_json(
            _fixtures_dir() / f"process_{process_id.replace('-', '_')}_graph.json"
        )
        if data:
            return data
        return _read_json(_fixtures_dir() / f"graph_{process_id}.json")

    live = _read_json(_cache_dir() / f"graph_{process_id}.json")
    if live:
        return live
    return _read_json(
        _fixtures_dir() / f"process_{process_id.replace('-', '_')}_graph.json"
    )


def load_steps(process_id: str) -> Optional[list[dict]]:
    """Load step insights for a process."""
    settings = get_settings()

    if settings.is_fixture_mode:
        data = _read_json(
            _fixtures_dir() / f"process_{process_id.replace('-', '_')}_steps.json"
        )
        if data:
            return data
        return _read_json(_fixtures_dir() / f"steps_{process_id}.json")

    live = _read_json(_cache_dir() / f"steps_{process_id}.json")
    if live:
        return live
    return _read_json(
        _fixtures_dir() / f"process_{process_id.replace('-', '_')}_steps.json"
    )


def load_opportunities() -> Optional[list[dict]]:
    """Load automation opportunities."""
    settings = get_settings()

    if settings.is_fixture_mode:
        return _read_json(_fixtures_dir() / "opportunities.json")

    live = _read_json(_cache_dir() / "opportunities.json")
    if live:
        return live
    logger.info("Live opportunities not found, falling back to fixtures")
    return _read_json(_fixtures_dir() / "opportunities.json")


def load_workflow_sample() -> Optional[dict]:
    """Load the workflow generation sample (fixture only)."""
    return _read_json(_fixtures_dir() / "workflow_sample.json")


def load_copilot_sample() -> Optional[dict]:
    """Load the copilot explanation sample (fixture only)."""
    return _read_json(_fixtures_dir() / "copilot_sample.json")
