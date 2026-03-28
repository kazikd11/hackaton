"""POST /workflow/generate — Workflow definition generator."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.api.data_loader import (
    load_process_by_id,
    load_variants,
    load_steps,
    load_opportunities,
    load_workflow_sample,
)
from backend.api.config import get_settings
from backend.analytics.workflow_generate import generate_workflow

router = APIRouter()


class WorkflowRequest(BaseModel):
    process_id: str
    variant_id: Optional[str] = Field(
        None, description="Specific variant to base workflow on; uses happy path if omitted"
    )
    include_descriptions: bool = Field(True)


@router.post("/workflow/generate")
async def post_workflow_generate(request: WorkflowRequest):
    """Generate a simplified workflow definition for a process.

    Uses the happy-path variant (or specified variant) to produce a
    structured workflow definition. Attempts LLM enrichment if OpenAI
    is configured, otherwise returns a deterministic workflow.
    """
    process = load_process_by_id(request.process_id)
    if process is None:
        raise HTTPException(
            status_code=404, detail=f"Process '{request.process_id}' not found"
        )

    # Load variant data
    variant_data = load_variants(request.process_id)

    # Find the target variant
    target_variant = None
    if variant_data and variant_data.get("variants"):
        variants = variant_data["variants"]
        if request.variant_id:
            target_variant = next(
                (v for v in variants if v.get("variant_id") == request.variant_id),
                None,
            )
        else:
            # Use happy path or most frequent variant
            happy_path_id = variant_data.get("happy_path")
            if happy_path_id:
                target_variant = next(
                    (v for v in variants if v.get("variant_id") == happy_path_id),
                    None,
                )
            if not target_variant and variants:
                target_variant = max(
                    variants, key=lambda v: v.get("frequency", 0)
                )

    if target_variant is None:
        # Fall back to workflow sample fixture
        sample = load_workflow_sample()
        if sample and sample.get("response"):
            return sample["response"]
        raise HTTPException(
            status_code=404,
            detail=f"No variant data available for process '{request.process_id}'",
        )

    # Load enrichment data
    steps_insights = load_steps(request.process_id)
    opportunities = load_opportunities()
    if opportunities:
        opportunities = [
            o for o in opportunities if o.get("process_id") == request.process_id
        ]

    settings = get_settings()

    result = await generate_workflow(
        process_id=request.process_id,
        process_name=process.get("name", request.process_id),
        variant=target_variant,
        steps_insights=steps_insights,
        opportunities=opportunities,
        prefer_llm=settings.has_openai,
    )

    return result
