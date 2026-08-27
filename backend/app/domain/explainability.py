"""Explainability and review handoff models."""

from typing import Annotated, Any

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.enums import ConfidenceLabel, SourceMode


class EvidenceChainNode(DomainModel):
    node_type: str
    label: str
    ref_id: str | None = None
    children: list["EvidenceChainNode"] = Field(default_factory=list)


class ExplainabilityReport(IdentifiedModel):
    run_id: str | None = None
    what: str
    why: str
    evidence_refs: list[str] = Field(default_factory=list)
    evidence_chain: list[EvidenceChainNode] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    confidence_label: ConfidenceLabel
    alternatives: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    human_decision_required: bool = True
    source_modes: list[str] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class ReviewableRecommendation(IdentifiedModel):
    """AI recommendation handoff to HR — not a hiring decision."""

    run_id: str
    candidate_id: str
    recommendation_summary: str
    recommendation_type: str
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    confidence_label: ConfidenceLabel
    assumptions: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    intervention_ids: list[str] = Field(default_factory=list)
    pathway_id: str | None = None
    risks: list[str] = Field(default_factory=list)
    human_review_required: bool = True
    ai_recommendation_preserved: dict[str, Any] = Field(default_factory=dict)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class GovernanceAuditEntry(IdentifiedModel):
    run_id: str | None = None
    actor_type: str
    actor_id: str
    action: str
    timestamp: str
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    reason: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC
