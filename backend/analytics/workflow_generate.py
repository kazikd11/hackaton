"""
Workflow definition generator.

Owner: Agent 2
Prefix: workflow_

Generates simplified workflow definitions from process step/variant data.
Supports two modes:
  - Deterministic: Converts the happy-path variant into a structured workflow
  - LLM-enhanced: Uses OpenAI to enrich with descriptions and conditions

Falls back to deterministic if LLM is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def generate_deterministic_workflow(
    process_id: str,
    process_name: str,
    variant: dict,
    steps_insights: Optional[list[dict]] = None,
) -> dict:
    """Generate a workflow definition from a variant path (no LLM needed).

    Args:
        process_id: Slug ID of the process family.
        process_name: Human-readable process name.
        variant: VariantPath dict with 'steps', 'variant_id'.
        steps_insights: Optional step insight data for enrichment.

    Returns:
        WorkflowDefinition-shaped dict.
    """
    raw_steps = variant.get("steps", [])
    variant_id = variant.get("variant_id", "unknown")

    if not raw_steps:
        return _empty_workflow(process_id, process_name, variant_id)

    # Build lookup for step insights
    insight_map: dict[str, dict] = {}
    if steps_insights:
        for si in steps_insights:
            insight_map[si.get("step_name", "")] = si

    workflow_steps: list[dict] = []

    # Start node
    workflow_steps.append(
        {
            "id": "wf-start",
            "type": "start",
            "label": f"{process_name} Started",
            "description": f"The {process_name.lower()} workflow begins.",
            "app": None,
            "next_steps": [f"wf-step-0"],
            "condition": None,
        }
    )

    # Detect divergence points (where a step appears multiple times)
    step_occurrences: dict[str, int] = {}
    for s in raw_steps:
        step_occurrences[s] = step_occurrences.get(s, 0) + 1

    for i, step_name in enumerate(raw_steps):
        step_id = f"wf-step-{i}"
        next_id = f"wf-step-{i + 1}" if i < len(raw_steps) - 1 else "wf-end"

        insight = insight_map.get(step_name, {})
        app = insight.get("app")

        # Determine if this is a decision point (step appears multiple times
        # in the variant, suggesting a loop or branch)
        if step_occurrences.get(step_name, 0) > 1 and i > 0:
            step_type = "decision"
            description = f"Decide whether to continue with {step_name} or proceed to next step."
        else:
            step_type = "action"
            # Generate description from insight data
            if insight:
                dur_s = insight.get("avg_duration_ms", 0) / 1000
                description = (
                    f"Perform {step_name}"
                    + (f" in {app}" if app else "")
                    + f" (avg {dur_s:.0f}s)."
                )
            else:
                description = f"Perform {step_name}."

        workflow_steps.append(
            {
                "id": step_id,
                "type": step_type,
                "label": step_name,
                "description": description,
                "app": app,
                "next_steps": [next_id],
                "condition": None,
            }
        )

    # End node
    workflow_steps.append(
        {
            "id": "wf-end",
            "type": "end",
            "label": f"{process_name} Complete",
            "description": f"The {process_name.lower()} workflow is finished.",
            "app": None,
            "next_steps": [],
            "condition": None,
        }
    )

    return {
        "process_id": process_id,
        "process_name": process_name,
        "title": f"{process_name} Workflow — Happy Path",
        "description": (
            f"Automated workflow based on the most frequent variant "
            f"({variant_id}) with {len(raw_steps)} steps."
        ),
        "steps": workflow_steps,
        "generated_by": "deterministic",
        "source_variant": variant_id,
    }


async def generate_llm_workflow(
    process_id: str,
    process_name: str,
    variant: dict,
    steps_insights: Optional[list[dict]] = None,
    opportunities: Optional[list[dict]] = None,
) -> Optional[dict]:
    """Generate an LLM-enriched workflow definition using OpenAI.

    Returns None if LLM is not available or fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        logger.info("OPENAI_API_KEY not set, skipping LLM workflow generation")
        return None

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)

        # Build evidence pack
        evidence = _build_evidence_pack(
            process_name, variant, steps_insights, opportunities
        )

        system_prompt = (
            "You are a process automation expert. Generate a structured workflow "
            "definition from the process evidence provided. Output valid JSON matching "
            "the WorkflowDefinition schema with steps that include 'id', 'type' "
            "(start/action/decision/end), 'label', 'description', 'app', 'next_steps', "
            "and 'condition' fields. Keep descriptions concise and actionable. "
            "Add decision points where the data shows branching behavior."
        )

        user_prompt = (
            f"Generate a workflow definition for the '{process_name}' process.\n\n"
            f"Evidence:\n{json.dumps(evidence, indent=2)}\n\n"
            f"Return ONLY valid JSON matching the WorkflowDefinition schema."
        )

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            return None

        result = json.loads(content)

        # Ensure required fields are present
        result.setdefault("process_id", process_id)
        result.setdefault("process_name", process_name)
        result.setdefault("title", f"{process_name} Workflow")
        result["generated_by"] = "llm"
        result.setdefault("source_variant", variant.get("variant_id"))

        return result

    except Exception as e:
        logger.warning(f"LLM workflow generation failed: {e}")
        return None


async def generate_workflow(
    process_id: str,
    process_name: str,
    variant: dict,
    steps_insights: Optional[list[dict]] = None,
    opportunities: Optional[list[dict]] = None,
    prefer_llm: bool = True,
) -> dict:
    """Generate a workflow definition, preferring LLM but falling back to deterministic.

    Args:
        process_id: Process family slug.
        process_name: Human-readable process name.
        variant: VariantPath dict to base workflow on.
        steps_insights: Step insight data for enrichment.
        opportunities: Related automation opportunities.
        prefer_llm: Whether to attempt LLM generation first.

    Returns:
        WorkflowDefinition-shaped dict.
    """
    if prefer_llm:
        result = await generate_llm_workflow(
            process_id, process_name, variant, steps_insights, opportunities
        )
        if result:
            return result

    return generate_deterministic_workflow(
        process_id, process_name, variant, steps_insights
    )


def _empty_workflow(
    process_id: str,
    process_name: str,
    variant_id: str,
) -> dict:
    """Return a minimal empty workflow when no steps are available."""
    return {
        "process_id": process_id,
        "process_name": process_name,
        "title": f"{process_name} Workflow",
        "description": "No variant steps available to generate a workflow.",
        "steps": [
            {
                "id": "wf-start",
                "type": "start",
                "label": "Start",
                "description": None,
                "app": None,
                "next_steps": ["wf-end"],
                "condition": None,
            },
            {
                "id": "wf-end",
                "type": "end",
                "label": "End",
                "description": None,
                "app": None,
                "next_steps": [],
                "condition": None,
            },
        ],
        "generated_by": "deterministic",
        "source_variant": variant_id,
    }


def _build_evidence_pack(
    process_name: str,
    variant: dict,
    steps_insights: Optional[list[dict]],
    opportunities: Optional[list[dict]],
) -> dict:
    """Build a concise evidence pack for LLM consumption."""
    evidence: dict = {
        "process_name": process_name,
        "variant_steps": variant.get("steps", []),
        "variant_frequency": variant.get("frequency", 0),
        "avg_duration_ms": variant.get("avg_duration_ms", 0),
    }

    if steps_insights:
        evidence["step_details"] = [
            {
                "name": s.get("step_name"),
                "app": s.get("app"),
                "avg_duration_ms": s.get("avg_duration_ms"),
                "frequency": s.get("frequency"),
                "copy_paste_count": s.get("copy_count", 0) + s.get("paste_count", 0),
                "signals": [
                    sig.get("signal_type")
                    for sig in s.get("automation_signals", [])
                ],
            }
            for s in steps_insights[:10]  # limit to avoid token overflow
        ]

    if opportunities:
        evidence["opportunities"] = [
            {
                "title": o.get("title"),
                "score": o.get("score"),
                "recommendation": o.get("recommendation"),
            }
            for o in opportunities[:5]  # limit
        ]

    return evidence
