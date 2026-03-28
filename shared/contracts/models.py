"""
Shared contract models for the Process-to-Automation Copilot.

Owner: Agent 2
Consumers: Backend API routes, Frontend TypeScript types (mirrored)

All response shapes are defined here as Pydantic v2 models.
Do NOT add ad-hoc fields without updating this file and the examples.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────


class RecommendationType(str, Enum):
    RPA_INTEGRATION = "RPA/Integration"
    WORKFLOW_AUTOMATION = "Workflow automation"
    ASSISTIVE_COPILOT = "Assistive copilot"
    MONITOR_ONLY = "Monitor only"


class WorkflowStepType(str, Enum):
    ACTION = "action"
    DECISION = "decision"
    START = "start"
    END = "end"
    PARALLEL = "parallel"


# ── Building Blocks ───────────────────────────────────────────────────────


class ProcessFamilySummary(BaseModel):
    """Compact summary of a process family for overview lists."""

    id: str = Field(..., description="URL-safe slug, e.g. 'communication'")
    name: str = Field(..., description="Human-readable name, e.g. 'Communication'")
    total_cases: int = Field(..., description="Number of observed cases/sessions")
    total_events: int = Field(..., description="Total activity events")
    total_hours: float = Field(..., description="Total active hours")
    user_count: int = Field(..., description="Distinct users observed")
    top_apps: list[str] = Field(
        default_factory=list, description="Most-used applications"
    )


class ScoreComponents(BaseModel):
    """Individual components of the automation opportunity score."""

    manual_effort: float = Field(
        ..., ge=0, le=1, description="Normalized manual effort signal"
    )
    time_cost: float = Field(
        ..., ge=0, le=1, description="Normalized time cost signal"
    )
    handoff: float = Field(
        ..., ge=0, le=1, description="Normalized handoff/context-switch signal"
    )
    repetition: float = Field(
        ..., ge=0, le=1, description="Normalized repetition signal"
    )
    variance: float = Field(
        ..., ge=0, le=1, description="Normalized variant complexity signal"
    )
    coverage_penalty: float = Field(
        ..., ge=0, le=1, description="Observation coverage penalty"
    )


class GraphNode(BaseModel):
    """Node in a process graph."""

    id: str
    label: str
    app: Optional[str] = None
    avg_duration_ms: Optional[float] = None
    frequency: Optional[int] = None
    type: str = Field(
        default="step", description="Node type: start, end, step, decision"
    )


class GraphEdge(BaseModel):
    """Edge in a process graph."""

    source: str
    target: str
    frequency: int = 1
    label: Optional[str] = None


class VariantPath(BaseModel):
    """Single variant path through a process."""

    variant_id: str
    steps: list[str] = Field(..., description="Ordered step names")
    frequency: int = Field(..., description="Times this variant was observed")
    avg_duration_ms: float = Field(..., description="Average total duration in ms")
    percentage: float = Field(
        ..., ge=0, le=100, description="Percentage of all cases"
    )


class WorkflowStep(BaseModel):
    """Single step in a generated workflow definition."""

    id: str
    type: WorkflowStepType
    label: str
    description: Optional[str] = None
    app: Optional[str] = None
    next_steps: list[str] = Field(
        default_factory=list, description="IDs of successor steps"
    )
    condition: Optional[str] = Field(
        None, description="Condition label for decision branches"
    )


class AutomationSignal(BaseModel):
    """A specific automation signal detected in a step."""

    signal_type: str = Field(
        ...,
        description="Type: copy_paste, app_switch, high_duration, high_repetition, manual_entry",
    )
    description: str
    severity: str = Field(
        ..., description="low, medium, high"
    )
    evidence: Optional[str] = Field(
        None, description="Supporting metric or data point"
    )


# ── Top-Level Response Models ─────────────────────────────────────────────


class ProcessOverview(BaseModel):
    """Response for GET /overview"""

    total_processes: int
    total_cases: int
    total_events: int
    total_hours: float
    total_users: int
    observation_period: str = Field(
        ..., description="e.g. '2026-03-01 to 2026-03-20'"
    )
    process_families: list[ProcessFamilySummary]
    top_applications: list[dict] = Field(
        default_factory=list,
        description="Top apps with name and hours, e.g. [{'name': 'Teams', 'hours': 852.1}]",
    )


class ProcessFamily(BaseModel):
    """Response for GET /processes — detailed process family info."""

    id: str
    name: str
    description: Optional[str] = None
    total_cases: int
    total_events: int
    total_hours: float
    active_hours: float
    passive_hours: float
    user_count: int
    avg_case_duration_ms: float
    top_apps: list[str]
    top_steps: list[str] = Field(
        default_factory=list, description="Most frequent step names"
    )
    variant_count: int = Field(0, description="Number of distinct variants")
    copy_paste_count: int = Field(0, description="Total copy-paste operations")
    app_switch_count: int = Field(0, description="Total app context switches")


class VariantSummary(BaseModel):
    """Response for GET /processes/{id}/variants"""

    process_id: str
    process_name: str
    total_cases: int
    variant_count: int
    variants: list[VariantPath]
    happy_path: Optional[str] = Field(
        None, description="variant_id of the most frequent path"
    )


class ProcessGraph(BaseModel):
    """Response for GET /processes/{id}/graph"""

    process_id: str
    process_name: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class StepInsight(BaseModel):
    """Response for GET /processes/{id}/steps"""

    step_name: str
    app: Optional[str] = None
    frequency: int = Field(..., description="Total occurrences")
    avg_duration_ms: float
    total_duration_ms: float
    user_count: int
    click_count: int = 0
    text_entry_count: int = 0
    copy_count: int = 0
    paste_count: int = 0
    automation_signals: list[AutomationSignal] = Field(default_factory=list)


class AutomationOpportunity(BaseModel):
    """Response for GET /opportunities"""

    id: str
    process_id: str
    process_name: str
    title: str = Field(..., description="Short description of the opportunity")
    description: str = Field(
        ..., description="Longer explanation of why this is an opportunity"
    )
    score: float = Field(..., ge=0, le=1, description="Composite automation score")
    score_components: ScoreComponents
    recommendation: RecommendationType
    affected_steps: list[str] = Field(
        default_factory=list, description="Step names affected"
    )
    estimated_hours_saved: Optional[float] = Field(
        None, description="Estimated weekly hours saved if automated"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Human-readable evidence points",
    )


class WorkflowDefinition(BaseModel):
    """Response for POST /workflow/generate"""

    process_id: str
    process_name: str
    title: str
    description: Optional[str] = None
    steps: list[WorkflowStep]
    generated_by: str = Field(
        ..., description="'llm' or 'deterministic'"
    )
    source_variant: Optional[str] = Field(
        None, description="variant_id used as basis"
    )


class WorkflowGenerateRequest(BaseModel):
    """Request body for POST /workflow/generate"""

    process_id: str
    variant_id: Optional[str] = Field(
        None, description="Specific variant to base workflow on; uses happy path if omitted"
    )
    include_descriptions: bool = Field(
        True, description="Whether to generate step descriptions"
    )


class CopilotExplanation(BaseModel):
    """Response for POST /copilot/explain"""

    question: str
    answer: str
    evidence: list[str] = Field(
        default_factory=list,
        description="Data points supporting the explanation",
    )
    generated_by: str = Field(
        ..., description="'llm' or 'deterministic'"
    )
    process_id: Optional[str] = None
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Confidence level of the answer"
    )


class CopilotExplainRequest(BaseModel):
    """Request body for POST /copilot/explain"""

    context: str = Field(
        ...,
        description="Process ID or 'overview' for general questions",
    )
    question: str = Field(
        ..., description="The user's question"
    )
    include_evidence: bool = Field(
        True, description="Whether to include supporting evidence"
    )
