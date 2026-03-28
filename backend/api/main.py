"""
Process-to-Automation Copilot — FastAPI Backend

Entry point for the API server.
Run with: uvicorn backend.api.main:app --reload --port 8000
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.config import get_settings
from backend.api.routes import api_router

# ── Logging ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)s │ %(levelname)s │ %(message)s",
)
logger = logging.getLogger(__name__)

# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Process-to-Automation Copilot API",
    description=(
        "Backend API for process mining analysis, automation opportunity "
        "scoring, workflow generation, and AI-powered explanations."
    ),
    version="0.1.0",
)

# ── CORS (allow frontend dev server) ───────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────────────────

app.include_router(api_router)


# ── Health & startup ───────────────────────────────────────────────────────


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "ok",
        "mode": settings.app_mode,
        "openai_configured": settings.has_openai,
        "fixtures_dir": settings.fixtures_dir,
        "cache_dir": settings.cache_dir,
    }


@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    logger.info("=" * 60)
    logger.info("Process-to-Automation Copilot API starting")
    logger.info(f"  Mode:              {settings.app_mode}")
    logger.info(f"  Dataset dir:       {settings.dataset_dir}")
    logger.info(f"  Cache dir:         {settings.cache_dir}")
    logger.info(f"  Fixtures dir:      {settings.fixtures_dir}")
    logger.info(f"  OpenAI configured: {settings.has_openai}")
    if settings.has_openai:
        logger.info(f"  OpenAI model:      {settings.openai_model}")
    logger.info("=" * 60)
