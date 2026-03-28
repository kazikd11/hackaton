"""
Centralized configuration for the backend API.

Reads from environment variables with sensible defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings loaded from environment."""

    # Paths
    dataset_dir: str = os.environ.get(
        "DATASET_DIR",
        str(
            Path(__file__).resolve().parents[2]
            / "Process-to-Automation Copilot Challenge"
            / "Dataset"
        ),
    )
    cache_dir: str = os.environ.get(
        "CACHE_DIR",
        str(Path(__file__).resolve().parents[2] / ".cache" / "analytics"),
    )
    fixtures_dir: str = os.environ.get(
        "FIXTURES_DIR",
        str(Path(__file__).resolve().parents[2] / "shared" / "fixtures"),
    )

    # Mode: "fixture" or "live"
    app_mode: str = os.environ.get("APP_MODE", "fixture")

    # OpenAI (optional)
    openai_api_key: str | None = os.environ.get("OPENAI_API_KEY")
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def is_fixture_mode(self) -> bool:
        return self.app_mode.lower() == "fixture"

    @property
    def is_live_mode(self) -> bool:
        return self.app_mode.lower() == "live"

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
