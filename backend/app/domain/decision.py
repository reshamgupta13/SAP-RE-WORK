"""Decision card, human review, audit, and outcome models."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.assessment import FitDimensions
from app.domain.enums import (
    AuditStatus,
    HumanReviewAction,
    RecommendationState,
    SourceMode,
)


class DecisionCard(IdentifiedModel):
    """Central inspectable recommendation object for UI and API."""

    run_id: str | None = None
    candidate_id: str
    candidate_name: str
    target_role_id: str
    target_role_title: str
    recommendation_state: RecommendationState
    capability_fit: FitDimensions | None = None
    genuine_gaps: list[str] = Field(default_factory=list)
    potential_proxies: list[str] = Field(default_factory=list)
    workplace_constraints: list[str] = Field(default_factory=list)
    pathway_id: str | None = None
    proof_of_skill_id: str | None = None
    alternative_opportunity_ids: list[str] = Field(default_factory=list)
    market_signal_ids: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    human_decision_required: bool = True
    what: str
    why: str
    evidence_refs: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class HumanReview(IdentifiedModel):
    run_id: str
    decision_card_id: str
    action: HumanReviewAction
    reason: str | None = None
    reviewer_id: str
    reviewer_role: str = "hr"
    override: dict[str, Any] = Field(default_factory=dict)
    comments: str | None = None


class Outcome(IdentifiedModel):
    run_id: str
    kind: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class AuditEvent(IdentifiedModel):
    run_id: str | None = None
    agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_reference: str | None = None
    output_reference: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    source_references: list[str] = Field(default_factory=list)
    status: AuditStatus
    latency_ms: int | None = None
    error: str | None = None
    human_override: bool = False
    rationale: str | None = None
