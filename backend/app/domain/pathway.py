"""Learning, market, matching, and proof-of-skill models."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from app.domain.base import IdentifiedModel
from app.domain.enums import (
    MilestoneStatus,
    PathwayStatus,
    ProofResultStatus,
    ReadinessState,
    SourceMode,
)


class MarketSignal(IdentifiedModel):
    skill_id: str
    window: str
    demand_index: Annotated[float, Field(ge=0.0, le=1.0)]
    trend: str
    opportunity_count: int = 0
    adjacent_role_ids: list[str] = Field(default_factory=list)
    notes: str | None = None
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC


class LearningItem(IdentifiedModel):
    title: str
    description: str | None = None
    capability: str | None = None
    difficulty: str = "intermediate"
    hours: float = 0.0
    estimated_duration: float | None = None
    sap_learning_item_id: str | None = None
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    skill_alignment: list[str] = Field(default_factory=list)
    completion_criteria: str | None = None


class PathwayMilestone(IdentifiedModel):
    sequence: int
    objective: str
    capability: str
    starting_level: Annotated[float, Field(ge=0.0, le=1.0)]
    target_level: Annotated[float, Field(ge=0.0, le=1.0)]
    learning_item_ids: list[str] = Field(default_factory=list)
    practice_task: str | None = None
    proof_requirement: str | None = None
    completion_criteria: str | None = None
    status: MilestoneStatus = MilestoneStatus.PENDING


class LearningPath(IdentifiedModel):
    target_role_id: str
    candidate_id: str
    created_from_run_id: str | None = None
    status: PathwayStatus = PathwayStatus.DRAFT
    current_state: str | None = None
    target_state: str | None = None
    target_capabilities: list[str] = Field(default_factory=list)
    gap_skill_ids: list[str] = Field(default_factory=list)
    milestones: list[PathwayMilestone] = Field(default_factory=list)
    learning_item_ids: list[str] = Field(default_factory=list)
    learning_items: list[LearningItem] = Field(default_factory=list)
    practical_tasks: list[str] = Field(default_factory=list)
    proof_of_skill_id: str | None = None
    duration_weeks: float | None = None
    estimated_duration_hours: float | None = None
    expected_readiness: ReadinessState | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    why: str | None = None
    what: str | None = None
    how: str | None = None
    success_criteria: str | None = None
    is_demo: bool = False
    source_mode: SourceMode = SourceMode.SYNTHETIC


class ProofRubricCriterion(IdentifiedModel):
    criterion: str
    weight: Annotated[float, Field(ge=0.0, le=1.0)]
    description: str | None = None


class ProofOfSkillAssessment(IdentifiedModel):
    skill_id: str
    task_key: str
    task_description: str | None = None
    rubric_json: dict[str, Any] = Field(default_factory=dict)
    rubric_criteria: list[ProofRubricCriterion] = Field(default_factory=list)
    version: str = "1.0"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    is_demo: bool = False


class ProofSubmission(IdentifiedModel):
    assessment_id: str
    candidate_id: str
    skill_id: str
    responses: dict[str, Any] = Field(default_factory=dict)
    artifact_metadata: dict[str, Any] = Field(default_factory=dict)
    source_mode: SourceMode = SourceMode.SYNTHETIC
    is_demo: bool = False


class ProofCriterionResult(IdentifiedModel):
    criterion: str
    weight: Annotated[float, Field(ge=0.0, le=1.0)]
    score: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence: str | None = None
    feedback: str | None = None


class ProofOfSkillResult(IdentifiedModel):
    assessment_id: str
    candidate_id: str
    skill_id: str
    scores_json: dict[str, Any] = Field(default_factory=dict)
    criterion_results: list[ProofCriterionResult] = Field(default_factory=list)
    total: Annotated[float, Field(ge=0.0, le=1.0)]
    result: ProofResultStatus
    evaluator: str = "rubric"
    human_override: bool = False
    source_mode: SourceMode = SourceMode.SYNTHETIC
    is_demo: bool = False


class ProofEvidence(IdentifiedModel):
    assessment_id: str
    candidate_id: str
    capability: str
    criterion_results: list[ProofCriterionResult] = Field(default_factory=list)
    overall_result: ProofResultStatus
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    verification_status: str = "VERIFIED_BY_ASSESSMENT"
    timestamp: datetime | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC
    is_demo: bool = False


class CapabilityUpdateEvent(IdentifiedModel):
    candidate_id: str
    skill_id: str
    old_level: Annotated[float, Field(ge=0.0, le=1.0)]
    new_level: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_ref: str
    reason: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    run_id: str | None = None


class Opportunity(IdentifiedModel):
    job_id: str
    title: str
    location: str
    work_modes: list[str] = Field(default_factory=list)
    language: str | None = None
    source: str = "REWORK"
    sap_opportunity_id: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC


class RecommendationEvidence(IdentifiedModel):
    recommendation_id: str
    ref_type: str
    ref_id: str
    source_mode: SourceMode = SourceMode.SYNTHETIC


class MatchRecommendation(IdentifiedModel):
    run_id: str | None = None
    opportunity_id: str
    candidate_id: str
    readiness_state: ReadinessState
    fit_dimensions: dict = Field(default_factory=dict)
    reasons: list[str] = Field(default_factory=list)
    gap_ids: list[str] = Field(default_factory=list)
    pathway_id: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    alternatives: list[str] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC
