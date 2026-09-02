"""Structured schemas for targeted learning agent outputs."""

from typing import Annotated

from pydantic import Field

from app.domain.base import DomainModel


class StrategistStepExtract(DomainModel):
    step_id: str
    title: str
    type: str
    rationale: str
    estimated_minutes: int = 45


class GapInterventionExtract(DomainModel):
    gap_id: str
    capability: str
    current_level: Annotated[float, Field(ge=0.0, le=1.0)]
    required_level: Annotated[float, Field(ge=0.0, le=1.0)]
    target_role: str
    learning_objective: str
    intervention_type: str
    estimated_effort: str
    reason: str
    smallest_effective_rationale: str
    addressable: bool = True
    non_addressable_reason: str | None = None
    steps: list[StrategistStepExtract] = Field(default_factory=list)


class LearningStrategistOutput(DomainModel):
    why_this_path: str
    gaps_sufficient: list[str] = Field(default_factory=list)
    interventions: list[GapInterventionExtract] = Field(default_factory=list)
    summary_rationale: str | None = None


class ResourceSelectionExtract(DomainModel):
    step_id: str
    resource_ids: list[str] = Field(default_factory=list)
    why_recommended: str
    fallback_intervention: str | None = None


class ResourceCuratorOutput(DomainModel):
    selections: list[ResourceSelectionExtract] = Field(default_factory=list)
    catalog_note: str = "RE:WORK Prototype Learning Catalog"
    summary_rationale: str | None = None


class ProofAlignmentExtract(DomainModel):
    gap_id: str
    proof_type: str
    proof_title: str
    proof_description: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    linked_capability: str
    required_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]


class ProofAlignmentOutput(DomainModel):
    proofs: list[ProofAlignmentExtract] = Field(default_factory=list)
    summary_rationale: str | None = None
