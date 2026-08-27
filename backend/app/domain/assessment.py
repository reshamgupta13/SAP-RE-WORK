"""Assessment, gap, barrier, and scoring domain models."""

from typing import Annotated

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.enums import (
    CounterfactualConclusion,
    GapStatus,
    ReviewTag,
    SourceMode,
)


class FitDimensions(DomainModel):
    """Separate explainable dimensions — not one opaque AI score."""

    capability_fit: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_strength: Annotated[float, Field(ge=0.0, le=1.0)]
    readiness: Annotated[float, Field(ge=0.0, le=1.0)]
    barrier_risk: Annotated[float, Field(ge=0.0, le=1.0)]
    pathway_effort: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    accessibility_fit: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    market_opportunity: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    overall_confidence: Annotated[float, Field(ge=0.0, le=1.0)]


class CapabilityAssessmentItem(IdentifiedModel):
    skill_id: str
    label: str
    required_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    candidate_proficiency: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    evidence_strength: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    gap_status: GapStatus
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_refs: list[str] = Field(default_factory=list)
    notes: str | None = None


class CapabilityAssessment(IdentifiedModel):
    candidate_id: str
    job_id: str
    items: list[CapabilityAssessmentItem] = Field(default_factory=list)
    fit_dimensions: FitDimensions | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC


class CapabilityGap(IdentifiedModel):
    run_id: str | None = None
    candidate_id: str
    job_id: str
    skill_id: str | None = None
    requirement_id: str | None = None
    gap_status: GapStatus
    severity: str = "informational"
    notes: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    source_mode: SourceMode = SourceMode.SYNTHETIC


class BarrierAssessment(IdentifiedModel):
    run_id: str | None = None
    requirement_id: str
    requirement_text: str
    review_tag: ReviewTag
    why_may_be_relevant: str | None = None
    why_may_be_proxy: str | None = None
    human_review_required: bool = True
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    source_mode: SourceMode = SourceMode.SYNTHETIC


class CounterfactualAssessment(IdentifiedModel):
    run_id: str | None = None
    requirement_id: str
    requirement_text: str
    supported_task: str | None = None
    required_capability: str | None = None
    candidate_evidence_refs: list[str] = Field(default_factory=list)
    alternative_validation: str | None = None
    conclusion: CounterfactualConclusion
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    human_review_required: bool = True
    source_mode: SourceMode = SourceMode.SYNTHETIC
