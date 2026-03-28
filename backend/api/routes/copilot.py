"""POST /copilot/explain — AI-powered process explanation."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from backend.api.data_loader import (
    load_overview,
    load_process_by_id,
    load_opportunities,
    load_steps,
)
from backend.api.config import get_settings
from backend.analytics.explain_copilot import generate_explanation

router = APIRouter()


class ExplainRequest(BaseModel):
    context: str = Field(
        ..., description="Process ID or 'overview' for general questions"
    )
    question: str = Field(..., description="The user's question")
    include_evidence: bool = Field(True)


@router.post("/copilot/explain")
async def post_copilot_explain(request: ExplainRequest):
    """Generate a natural-language explanation for a process or opportunity.

    Uses OpenAI if configured, otherwise returns a deterministic
    template-based explanation grounded in the same evidence.
    """
    settings = get_settings()
    context_id = request.context.lower().strip()

    # Gather context data
    if context_id == "overview":
        process_data = load_overview()
    else:
        process_data = load_process_by_id(context_id)

    # Load related data
    opportunities = load_opportunities()
    if opportunities and context_id != "overview":
        opportunities = [
            o for o in opportunities if o.get("process_id") == context_id
        ]

    steps = None
    if context_id != "overview":
        steps = load_steps(context_id)

    result = await generate_explanation(
        question=request.question,
        context_id=context_id,
        process_data=process_data,
        opportunities=opportunities,
        steps=steps,
        prefer_llm=settings.has_openai,
    )

    return result
