"""Learning, market, matching, and proof-of-skill models."""

from typing import Annotated

from pydantic import Field

from app.domain.base import IdentifiedModel
from app.domain.enums import ReadinessState, SourceMode


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
    hours: float = 0.0
    sap_learning_item_id: str | None = None
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC


class LearningPath(IdentifiedModel):
    target_role_id: str
    candidate_id: str
    current_state: str | None = None
    target_state: str | None = None
    gap_skill_ids: list[str] = Field(default_factory=list)
    learning_item_ids: list[str] = Field(default_factory=list)
    practical_tasks: list[str] = Field(default_factory=list)
    proof_of_skill_id: str | None = None
    duration_weeks: float | None = None
    expected_readiness: ReadinessState | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    source_mode: SourceMode = SourceMode.SYNTHETIC


class ProofOfSkillAssessment(IdentifiedModel):
    skill_id: str
    task_key: str
    rubric_json: dict
    version: str = "1.0"
    source_mode: SourceMode = SourceMode.SYNTHETIC


class ProofOfSkillResult(IdentifiedModel):
    assessment_id: str
    candidate_id: str
    scores_json: dict
    total: Annotated[float, Field(ge=0.0, le=1.0)]
    result: str
    evaluator: str = "rubric"
    human_override: bool = False
    source_mode: SourceMode = SourceMode.SYNTHETIC


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
