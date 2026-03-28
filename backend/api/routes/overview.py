"""GET /overview — Process mining overview."""

from fastapi import APIRouter, HTTPException

from backend.api.data_loader import load_overview

router = APIRouter()


@router.get("/overview")
async def get_overview():
    """Return a high-level overview of all process mining data.

    Includes total stats, process families, and top applications.
    """
    data = load_overview()
    if data is None:
        raise HTTPException(status_code=503, detail="Overview data not available")
    return data
