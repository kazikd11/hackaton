"""
Copilot explanation engine.

Owner: Agent 2
Prefix: explain_

Generates natural-language explanations grounded in process evidence.
Supports two modes:
  - Deterministic: Template-based explanations from metrics
  - LLM-enhanced: OpenAI-powered explanations with evidence grounding

Falls back to deterministic if LLM is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def generate_deterministic_explanation(
    question: str,
    context_id: str,
    process_data: Optional[dict] = None,
    opportunities: Optional[list[dict]] = None,
    steps: Optional[list[dict]] = None,
) -> dict:
    """Generate a template-based explanation from evidence data.

    Args:
        question: The user's question.
        context_id: Process ID or 'overview'.
        process_data: Process family dict.
        opportunities: Related opportunities.
        steps: Step insights.

    Returns:
        CopilotExplanation-shaped dict.
    """
    evidence_points: list[str] = []
    answer_parts: list[str] = []

    if context_id == "overview":
        return _explain_overview(question, process_data, opportunities)

    # Process-specific explanation
    if process_data:
        name = process_data.get("name", context_id)
        total_hours = process_data.get("total_hours", 0)
        total_cases = process_data.get("total_cases", 0)
        user_count = process_data.get("user_count", 0)
        variant_count = process_data.get("variant_count", 0)
        copy_paste = process_data.get("copy_paste_count", 0)
        app_switches = process_data.get("app_switch_count", 0)

        answer_parts.append(
            f"The **{name}** process covers {total_cases:,} cases "
            f"involving {user_count} users over {total_hours:.1f} hours."
        )
        evidence_points.append(f"{total_cases:,} total cases observed")
        evidence_points.append(f"{user_count} distinct users")
        evidence_points.append(f"{total_hours:.1f} total hours")

        if variant_count > 0:
            answer_parts.append(
                f"It has {variant_count} observed variants, indicating "
                + (
                    "a highly variable process that may benefit from standardization."
                    if variant_count > 20
                    else (
                        "moderate complexity."
                        if variant_count > 10
                        else "a relatively stable process."
                    )
                )
            )
            evidence_points.append(f"{variant_count} process variants")

        if copy_paste > 0:
            cp_rate = copy_paste / max(total_cases, 1)
            answer_parts.append(
                f"Copy-paste operations total {copy_paste:,} "
                f"({cp_rate:.1f} per case), "
                + (
                    "which is a strong automation signal for data transfer tasks."
                    if cp_rate > 1
                    else "indicating some manual data handling."
                )
            )
            evidence_points.append(f"{copy_paste:,} copy-paste operations ({cp_rate:.1f}/case)")

        if app_switches > 0:
            switch_rate = app_switches / max(total_cases, 1)
            answer_parts.append(
                f"App context switching rate is {switch_rate:.1f} per case "
                f"({app_switches:,} total), "
                + (
                    "suggesting significant fragmentation in the workflow."
                    if switch_rate > 2
                    else "which is within normal range."
                )
            )
            evidence_points.append(f"{app_switches:,} app switches ({switch_rate:.1f}/case)")

    # Add opportunity context
    if opportunities:
        top_opp = max(opportunities, key=lambda o: o.get("score", 0))
        answer_parts.append(
            f"\n\nThe top automation opportunity in this process is "
            f"**{top_opp.get('title', 'Unknown')}** with a score of "
            f"{top_opp.get('score', 0):.2f}. "
            f"The recommendation is: {top_opp.get('recommendation', 'N/A')}."
        )
        evidence_points.append(
            f"Top opportunity: {top_opp.get('title')} (score: {top_opp.get('score', 0):.2f})"
        )

    # Add step-level insights
    if steps:
        high_signal_steps = [
            s for s in steps if s.get("automation_signals")
        ]
        if high_signal_steps:
            step_names = [s.get("step_name", "") for s in high_signal_steps[:3]]
            answer_parts.append(
                f"\nSteps with automation signals: {', '.join(step_names)}."
            )
            for s in high_signal_steps[:3]:
                for sig in s.get("automation_signals", [])[:2]:
                    evidence_points.append(
                        f"{s.get('step_name')}: {sig.get('description', '')}"
                    )

    answer = " ".join(answer_parts) if answer_parts else (
        f"Based on the available data for process '{context_id}', "
        f"this process shows typical patterns. Further analysis with "
        f"more specific questions may reveal additional insights."
    )

    return {
        "question": question,
        "answer": answer,
        "evidence": evidence_points,
        "generated_by": "deterministic",
        "process_id": context_id if context_id != "overview" else None,
        "confidence": 0.85 if process_data else 0.5,
    }


def _explain_overview(
    question: str,
    overview_data: Optional[dict],
    opportunities: Optional[list[dict]],
) -> dict:
    """Generate an overview-level explanation."""
    evidence: list[str] = []
    parts: list[str] = []

    if overview_data:
        parts.append(
            f"The workspace contains {overview_data.get('total_processes', 0)} process families "
            f"with {overview_data.get('total_cases', 0):,} total cases, "
            f"{overview_data.get('total_events', 0):,} events, and "
            f"{overview_data.get('total_hours', 0):.1f} total hours observed "
            f"across {overview_data.get('total_users', 0)} users."
        )
        evidence.append(f"Observation period: {overview_data.get('observation_period', 'N/A')}")
        evidence.append(f"{overview_data.get('total_users', 0)} total users observed")

        families = overview_data.get("process_families", [])
        if families:
            top_family = max(families, key=lambda f: f.get("total_hours", 0))
            parts.append(
                f"\nThe largest process family by time is **{top_family.get('name', '')}** "
                f"with {top_family.get('total_hours', 0):.1f} hours."
            )
            evidence.append(f"Largest family: {top_family.get('name')} ({top_family.get('total_hours', 0):.1f}h)")

    if opportunities:
        sorted_opps = sorted(opportunities, key=lambda o: o.get("score", 0), reverse=True)
        parts.append(
            f"\nThere are {len(sorted_opps)} automation opportunities identified. "
            f"The top opportunity is **{sorted_opps[0].get('title', '')}** "
            f"(score: {sorted_opps[0].get('score', 0):.2f})."
        )
        evidence.append(f"{len(sorted_opps)} total opportunities")
        evidence.append(f"Top: {sorted_opps[0].get('title')} ({sorted_opps[0].get('score', 0):.2f})")

    return {
        "question": question,
        "answer": " ".join(parts) if parts else "Overview data is not yet available.",
        "evidence": evidence,
        "generated_by": "deterministic",
        "process_id": None,
        "confidence": 0.8 if overview_data else 0.4,
    }


async def generate_llm_explanation(
    question: str,
    context_id: str,
    process_data: Optional[dict] = None,
    opportunities: Optional[list[dict]] = None,
    steps: Optional[list[dict]] = None,
) -> Optional[dict]:
    """Generate an LLM-enriched explanation using OpenAI.

    Returns None if LLM is not available or fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        logger.info("OPENAI_API_KEY not set, skipping LLM explanation")
        return None

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)

        evidence_pack = _build_explanation_evidence(
            context_id, process_data, opportunities, steps
        )

        system_prompt = (
            "You are a process automation expert analyzing workplace behavior data. "
            "Answer the user's question using ONLY the evidence provided. "
            "Be specific, cite numbers, and recommend actionable next steps. "
            "Output valid JSON with keys: 'answer' (string), 'evidence' (list of strings), "
            "'confidence' (float 0-1)."
        )

        user_prompt = (
            f"Question: {question}\n\n"
            f"Evidence:\n{json.dumps(evidence_pack, indent=2)}\n\n"
            f"Answer based ONLY on the evidence above. Return JSON."
        )

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            return None

        result = json.loads(content)

        return {
            "question": question,
            "answer": result.get("answer", ""),
            "evidence": result.get("evidence", []),
            "generated_by": "llm",
            "process_id": context_id if context_id != "overview" else None,
            "confidence": result.get("confidence", 0.7),
        }

    except Exception as e:
        logger.warning(f"LLM explanation failed: {e}")
        return None


async def generate_explanation(
    question: str,
    context_id: str,
    process_data: Optional[dict] = None,
    opportunities: Optional[list[dict]] = None,
    steps: Optional[list[dict]] = None,
    prefer_llm: bool = True,
) -> dict:
    """Generate an explanation, preferring LLM but falling back to deterministic.

    Args:
        question: The user's question.
        context_id: Process ID or 'overview'.
        process_data: Process/overview data dict.
        opportunities: Related opportunities.
        steps: Step insight data.
        prefer_llm: Whether to attempt LLM generation first.

    Returns:
        CopilotExplanation-shaped dict.
    """
    if prefer_llm:
        result = await generate_llm_explanation(
            question, context_id, process_data, opportunities, steps
        )
        if result:
            return result

    return generate_deterministic_explanation(
        question, context_id, process_data, opportunities, steps
    )


def _build_explanation_evidence(
    context_id: str,
    process_data: Optional[dict],
    opportunities: Optional[list[dict]],
    steps: Optional[list[dict]],
) -> dict:
    """Build a concise evidence pack for LLM explanation."""
    evidence: dict = {"context": context_id}

    if process_data:
        # Send compact version to save tokens
        evidence["process"] = {
            k: v
            for k, v in process_data.items()
            if k
            in (
                "name",
                "total_cases",
                "total_hours",
                "active_hours",
                "user_count",
                "variant_count",
                "copy_paste_count",
                "app_switch_count",
                "top_apps",
                "top_steps",
            )
        }

    if opportunities:
        evidence["opportunities"] = [
            {
                "title": o.get("title"),
                "score": o.get("score"),
                "recommendation": o.get("recommendation"),
                "evidence": o.get("evidence", [])[:3],
            }
            for o in opportunities[:5]
        ]

    if steps:
        evidence["steps"] = [
            {
                "name": s.get("step_name"),
                "app": s.get("app"),
                "frequency": s.get("frequency"),
                "avg_duration_ms": s.get("avg_duration_ms"),
                "signals": [
                    sig.get("signal_type")
                    for sig in s.get("automation_signals", [])
                ],
            }
            for s in steps[:8]
        ]

    return evidence
