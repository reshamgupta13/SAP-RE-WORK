"""Targeted learning domain models — gap-driven reskilling plans."""

from typing import Annotated, Any

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.enums import EngineMode, SourceMode


class LearningResource(IdentifiedModel):
    title: str
    type: str  # concept | hands_on | practice | assessment | documentation
    capability: str
    difficulty: str = "intermediate"
    estimated_minutes: int = 30
    description: str | None = None
    why_recommended: str | None = None
    source_type: str = "prototype_catalog"
    level: str | None = None
    objective: str | None = None
    expected_evidence: str | None = None


class LearningStep(IdentifiedModel):
    gap_id: str
    capability: str
    title: str
    objective: str
    step_type: str  # concept | hands_on | assessment | practice
    intervention_type: str = "focused_skill_build"
    estimated_minutes: int = 45
    rationale: str
    resource_ids: list[str] = Field(default_factory=list)
    resources: list[LearningResource] = Field(default_factory=list)
    status: str = "not_started"
    sequence: int = 1


class ProofRequirement(IdentifiedModel):
    proof_type: str
    proof_title: str
    proof_description: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    linked_capability: str
    required_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    gap_id: str | None = None


class GapIntervention(IdentifiedModel):
    gap_id: str
    capability: str
    current_level: Annotated[float, Field(ge=0.0, le=1.0)]
    required_level: Annotated[float, Field(ge=0.0, le=1.0)]
    target_role: str
    learning_objective: str
    intervention_type: str
    estimated_effort: str
    reason: str
    smallest_effective_rationale: str | None = None
    steps: list[LearningStep] = Field(default_factory=list)
    addressable: bool = True
    non_addressable_reason: str | None = None


class ValidationCheck(DomainModel):
    name: str
    status: str  # passed | failed | warning
    message: str | None = None


class LearningPlanValidation(DomainModel):
    status: str  # passed | failed | repaired
    checks: list[ValidationCheck] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class AgentExecutionStatus(DomainModel):
    learning_strategist: str = "pending"
    resource_curator: str = "pending"
    proof_alignment: str = "pending"
    validator: str = "pending"
    engine_mode: EngineMode = EngineMode.DEMO_FALLBACK
    strategist_summary: str | None = None
    curator_summary: str | None = None
    proof_summary: str | None = None


class LearningTraceLink(DomainModel):
    stage: str
    label: str
    detail: str


class InterventionSimulation(DomainModel):
    gap_capability: str
    intervention_label: str
    before_state: str
    after_state: str
    readiness_note: str | None = None
    is_simulated_projection: bool = True
    assumptions: list[str] = Field(default_factory=list)


class LearningPlan(IdentifiedModel):
    candidate_id: str
    role_id: str
    candidate_name: str | None = None
    target_role_title: str | None = None
    status: str = "draft"  # draft | ready | no_intervention_required
    source_gap_ids: list[str] = Field(default_factory=list)
    gaps_addressed: list[str] = Field(default_factory=list)
    gaps_sufficient: list[str] = Field(default_factory=list)
    interventions: list[GapIntervention] = Field(default_factory=list)
    steps: list[LearningStep] = Field(default_factory=list)
    proof_requirements: list[ProofRequirement] = Field(default_factory=list)
    validation: LearningPlanValidation | None = None
    agents: AgentExecutionStatus | None = None
    why_this_path: str | None = None
    catalog_label: str = "RE:WORK Prototype Learning Catalog"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    diagnosis_summary: dict[str, Any] | None = None
    trace: list[LearningTraceLink] = Field(default_factory=list)
    generated_by: str = "targeted_learning_orchestrator"
