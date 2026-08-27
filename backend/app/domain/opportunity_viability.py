"""Opportunity viability, market intelligence, and employer readiness models."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.enums import SourceMode, ViabilityState


class MarketIntelligenceSignal(IdentifiedModel):
    """Structured market signal — synthetic demo data, not live labor statistics."""

    role_id: str | None = None
    skill: str | None = None
    signal_type: str
    direction: str
    strength: Annotated[float, Field(ge=0.0, le=1.0)]
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    region: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    timestamp: datetime | None = None
    notes: str | None = None
    unlockable_role_ids: list[str] = Field(default_factory=list)


class SkillInvestmentScenario(IdentifiedModel):
    candidate_id: str
    investment_skill: str
    current_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    target_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    unlockable_roles: list[str] = Field(default_factory=list)
    additional_opportunities: list[str] = Field(default_factory=list)
    estimated_effort_weeks: float | None = None
    proof_requirement: str | None = None
    market_signal_refs: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    rationale: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC


class EmployerReadinessFactor(IdentifiedModel):
    factor: str
    status: str
    source: str = "REWORK"
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    human_review_required: bool = False
    evidence_ref: str | None = None


class EmployerIntervention(IdentifiedModel):
    issue: str
    recommendation: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    human_review_required: bool = True


class EmployerReadinessAssessment(IdentifiedModel):
    opportunity_id: str
    employer_id: str | None = None
    overall_state: str
    factors: list[EmployerReadinessFactor] = Field(default_factory=list)
    interventions: list[EmployerIntervention] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    source_mode: SourceMode = SourceMode.SYNTHETIC


class ViabilityDimensions(DomainModel):
    """Inspectable viability dimensions — not one opaque score."""

    capability_fit: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_strength: Annotated[float, Field(ge=0.0, le=1.0)]
    readiness: Annotated[float, Field(ge=0.0, le=1.0)]
    skill_gap_effort: Annotated[float, Field(ge=0.0, le=1.0)]
    proof_effort: Annotated[float, Field(ge=0.0, le=1.0)]
    workplace_compatibility: Annotated[float, Field(ge=0.0, le=1.0)]
    employer_readiness: Annotated[float, Field(ge=0.0, le=1.0)]
    market_opportunity: Annotated[float, Field(ge=0.0, le=1.0)]


class OpportunityCatalogEntry(IdentifiedModel):
    """Synthetic opportunity catalog entry for viability analysis."""

    title: str
    job_id: str
    family: str | None = None
    location: str | None = None
    work_modes: list[str] = Field(default_factory=list)
    capability_skill_ids: list[str] = Field(default_factory=list)
    min_proficiency: dict[str, float] = Field(default_factory=dict)
    workplace_conditions: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)
    development_options: list[str] = Field(default_factory=list)
    employer_id: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC


class OpportunityViability(IdentifiedModel):
    candidate_id: str
    opportunity_id: str
    target_role_id: str
    dimensions: ViabilityDimensions
    candidate_gaps: list[str] = Field(default_factory=list)
    candidate_barriers: list[str] = Field(default_factory=list)
    employer_requirements: list[str] = Field(default_factory=list)
    employer_readiness_id: str | None = None
    recommended_interventions: list[str] = Field(default_factory=list)
    pathway_reference: str | None = None
    proof_reference: str | None = None
    proof_required: bool = False
    viability_state: ViabilityState
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    rationale: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class OpportunityComparisonItem(DomainModel):
    opportunity_id: str
    title: str
    viability_state: ViabilityState
    capability_fit: Annotated[float, Field(ge=0.0, le=1.0)]
    pathway_effort_weeks: float | None = None
    proof_effort: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    employer_readiness: Annotated[float, Field(ge=0.0, le=1.0)]
    market_opportunity: Annotated[float, Field(ge=0.0, le=1.0)]
    key_barriers: list[str] = Field(default_factory=list)
    key_advantages: list[str] = Field(default_factory=list)
    next_action: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]


class OpportunityComparison(IdentifiedModel):
    candidate_id: str
    items: list[OpportunityComparisonItem] = Field(default_factory=list)
    recommended_next_step_opportunity_id: str | None = None
    recommended_next_step_rationale: str | None = None
    medium_term_opportunity_id: str | None = None
    medium_term_rationale: str | None = None
    highest_effort_opportunity_id: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    source_mode: SourceMode = SourceMode.SYNTHETIC


class OpportunityCounterfactual(IdentifiedModel):
    candidate_id: str
    opportunity_id: str
    current_viability_state: ViabilityState
    target_viability_state: ViabilityState
    required_changes: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    human_review_required: bool = True
    rationale: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC
