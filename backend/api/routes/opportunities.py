"""GET /opportunities — Scored automation opportunities."""

from fastapi import APIRouter, HTTPException

from backend.api.data_loader import load_opportunities

router = APIRouter()


@router.get("/opportunities")
async def get_opportunities():
    """Return all scored automation opportunities, ranked by score.

    Each opportunity includes the composite score, component breakdown,
    recommendation type, and supporting evidence.
    """
    data = load_opportunities()
    if data is None:
        raise HTTPException(
            status_code=503, detail="Opportunity data not available"
        )
    # Ensure sorted by score descending
    if isinstance(data, list):
        data.sort(key=lambda o: o.get("score", 0), reverse=True)
    return data
