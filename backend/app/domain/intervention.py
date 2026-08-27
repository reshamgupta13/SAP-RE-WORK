"""Intervention simulation domain models."""

from typing import Annotated, Any

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.enums import (
    InterventionPriority,
    InterventionType,
    SourceMode,
    ViabilityState,
)


class Intervention(IdentifiedModel):
    type: InterventionType
    title: str
    description: str
    target: str
    preconditions: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC
    estimated_effort_weeks: float | None = None
    expected_effect: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    human_review_required: bool = True
    priority: InterventionPriority | None = None


class InterventionEffect(DomainModel):
    """Simulated projection — not a guaranteed outcome."""

    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    affected_dimensions: list[str] = Field(default_factory=list)
    affected_capabilities: list[str] = Field(default_factory=list)
    affected_barriers: list[str] = Field(default_factory=list)
    affected_employer_factors: list[str] = Field(default_factory=list)
    expected_readiness_change: float | None = None
    expected_viability_change: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    assumptions: list[str] = Field(default_factory=list)
    is_simulated_projection: bool = True


class Scenario(IdentifiedModel):
    """Intervention scenario tree node."""

    candidate_id: str
    opportunity_id: str
    label: str
    parent_scenario_id: str | None = None
    intervention_ids: list[str] = Field(default_factory=list)
    intervention_types: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    before_viability_state: ViabilityState | None = None
    after_viability_state: ViabilityState | None = None
    effect: InterventionEffect | None = None
    total_effort_weeks: float | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    is_simulated_projection: bool = True
    source_mode: SourceMode = SourceMode.SYNTHETIC


class InterventionBundle(IdentifiedModel):
    label: str
    scenario_ids: list[str] = Field(default_factory=list)
    intervention_ids: list[str] = Field(default_factory=list)
    total_effort_weeks: float | None = None
    after_viability_state: ViabilityState | None = None
    is_minimum_effective: bool = False
    rationale: str | None = None
