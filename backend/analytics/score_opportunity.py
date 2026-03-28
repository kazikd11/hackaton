"""
Opportunity scoring engine.

Owner: Agent 2
Prefix: score_

Implements the fixed scoring formula:
  score = 0.30*manual_effort + 0.25*time_cost + 0.20*handoff
        + 0.15*repetition + 0.10*variance - 0.10*coverage_penalty

All component values are normalized to [0, 1] using min-max scaling
within each process family.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ── Score weights (frozen per spec) ────────────────────────────────────────

WEIGHTS = {
    "manual_effort": 0.30,
    "time_cost": 0.25,
    "handoff": 0.20,
    "repetition": 0.15,
    "variance": 0.10,
    "coverage_penalty": -0.10,
}

# ── Recommendation thresholds ─────────────────────────────────────────────

RECOMMENDATION_RULES = [
    # (label, min_score, required_components)
    ("RPA/Integration", 0.70, {"repetition": 0.60, "manual_effort": 0.50}),
    ("Workflow automation", 0.50, {"handoff": 0.50}),
    ("Assistive copilot", 0.40, {"variance": 0.50}),
    ("Monitor only", 0.0, {}),
]


@dataclass
class RawMetrics:
    """Raw (un-normalized) metrics for a single scoring target."""

    manual_effort: float = 0.0
    time_cost: float = 0.0
    handoff: float = 0.0
    repetition: float = 0.0
    variance: float = 0.0
    coverage_penalty: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "manual_effort": self.manual_effort,
            "time_cost": self.time_cost,
            "handoff": self.handoff,
            "repetition": self.repetition,
            "variance": self.variance,
            "coverage_penalty": self.coverage_penalty,
        }


@dataclass
class NormalizedComponents:
    """Normalized [0, 1] score components."""

    manual_effort: float
    time_cost: float
    handoff: float
    repetition: float
    variance: float
    coverage_penalty: float

    def as_dict(self) -> dict[str, float]:
        return {
            "manual_effort": self.manual_effort,
            "time_cost": self.time_cost,
            "handoff": self.handoff,
            "repetition": self.repetition,
            "variance": self.variance,
            "coverage_penalty": self.coverage_penalty,
        }


def _min_max_normalize(
    values: list[float],
) -> list[float]:
    """Normalize a list of values to [0, 1] using min-max scaling.

    If all values are equal, returns 0.5 for each.
    """
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def normalize_within_family(
    metrics_list: list[RawMetrics],
) -> list[NormalizedComponents]:
    """Normalize raw metrics within a process family using min-max scaling.

    Each component is normalized independently across all items in the family.
    """
    if not metrics_list:
        return []

    component_names = [
        "manual_effort",
        "time_cost",
        "handoff",
        "repetition",
        "variance",
        "coverage_penalty",
    ]

    # Extract per-component arrays
    raw_arrays: dict[str, list[float]] = {}
    for name in component_names:
        raw_arrays[name] = [getattr(m, name) for m in metrics_list]

    # Normalize each component independently
    normalized_arrays: dict[str, list[float]] = {}
    for name in component_names:
        normalized_arrays[name] = _min_max_normalize(raw_arrays[name])

    # Reassemble into NormalizedComponents
    results: list[NormalizedComponents] = []
    for i in range(len(metrics_list)):
        results.append(
            NormalizedComponents(
                **{name: normalized_arrays[name][i] for name in component_names}
            )
        )
    return results


def compute_score(components: NormalizedComponents) -> float:
    """Compute the composite automation opportunity score.

    Formula:
      score = 0.30*manual_effort + 0.25*time_cost + 0.20*handoff
            + 0.15*repetition + 0.10*variance - 0.10*coverage_penalty

    Returns a value in [0, 1] (clamped).
    """
    raw = (
        WEIGHTS["manual_effort"] * components.manual_effort
        + WEIGHTS["time_cost"] * components.time_cost
        + WEIGHTS["handoff"] * components.handoff
        + WEIGHTS["repetition"] * components.repetition
        + WEIGHTS["variance"] * components.variance
        + WEIGHTS["coverage_penalty"] * components.coverage_penalty  # note: weight is -0.10
    )
    return max(0.0, min(1.0, raw))


def classify_recommendation(
    score: float,
    components: NormalizedComponents,
) -> str:
    """Classify the automation recommendation type.

    Checks rules in priority order:
    1. RPA/Integration — high score, high repetition, high manual effort
    2. Workflow automation — moderate+ score, high handoff
    3. Assistive copilot — moderate score, high variance
    4. Monitor only — everything else
    """
    comp_dict = components.as_dict()
    for label, min_score, required in RECOMMENDATION_RULES:
        if score >= min_score:
            if all(comp_dict.get(k, 0) >= v for k, v in required.items()):
                return label
    return "Monitor only"


def score_opportunities(
    metrics_list: list[RawMetrics],
) -> list[tuple[float, NormalizedComponents, str]]:
    """Score and classify a batch of opportunities within the same family.

    Args:
        metrics_list: Raw metrics for each opportunity.

    Returns:
        List of (score, normalized_components, recommendation) tuples.
    """
    normalized = normalize_within_family(metrics_list)
    results: list[tuple[float, NormalizedComponents, str]] = []
    for comp in normalized:
        s = compute_score(comp)
        rec = classify_recommendation(s, comp)
        results.append((s, comp, rec))
    return results


# ── Metric extraction helpers ──────────────────────────────────────────────
# These extract RawMetrics from cache/fixtures.
# In live mode, Agent 1's cached analytics provide the inputs.
# In fixture mode, we read from the fixture opportunities directly.


def extract_metrics_from_step_insights(
    steps: list[dict],
    process_family: dict,
    headcount_coverage: Optional[float] = None,
) -> RawMetrics:
    """Extract raw metrics from step insight data.

    Args:
        steps: List of step insight dicts (matching StepInsight contract).
        process_family: Process family dict (matching ProcessFamily contract).
        headcount_coverage: Ratio of measured/expected users (0-1).

    Returns:
        RawMetrics for the process family.
    """
    if not steps:
        return RawMetrics()

    # Manual effort: weighted combination of click density, text entry, and active time ratio
    total_clicks = sum(s.get("click_count", 0) for s in steps)
    total_text = sum(s.get("text_entry_count", 0) for s in steps)
    total_events = sum(s.get("frequency", 0) for s in steps)
    active_hours = process_family.get("active_hours", 0)
    total_hours = process_family.get("total_hours", 1)
    active_ratio = active_hours / total_hours if total_hours > 0 else 0

    manual_effort = min(
        1.0,
        (total_clicks + total_text) / max(total_events, 1) * 0.1  # intensity
        + active_ratio * 0.5,  # active time weight
    )

    # Time cost: total hours (log-scaled for large values)
    import math

    time_cost = min(1.0, math.log1p(total_hours) / 10)

    # Handoff: app switch rate per case
    app_switches = process_family.get("app_switch_count", 0)
    total_cases = process_family.get("total_cases", 1)
    handoff = min(1.0, app_switches / max(total_cases, 1) / 5)  # 5 switches/case = 1.0

    # Repetition: copy/paste density + variant concentration
    total_copies = sum(s.get("copy_count", 0) for s in steps)
    total_pastes = sum(s.get("paste_count", 0) for s in steps)
    copy_paste_rate = (total_copies + total_pastes) / max(total_events, 1)
    repetition = min(1.0, copy_paste_rate * 5)  # scale

    # Variance: number of variants (more = higher variance)
    variant_count = process_family.get("variant_count", 1)
    variance = min(1.0, variant_count / 30)  # 30 variants = 1.0

    # Coverage penalty: inverse of headcount coverage
    if headcount_coverage is not None:
        coverage_penalty = max(0.0, 1.0 - headcount_coverage)
    else:
        coverage_penalty = 0.15  # default moderate penalty

    return RawMetrics(
        manual_effort=manual_effort,
        time_cost=time_cost,
        handoff=handoff,
        repetition=repetition,
        variance=variance,
        coverage_penalty=coverage_penalty,
    )
