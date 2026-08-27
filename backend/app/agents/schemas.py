"""Structured schemas for agent LLM outputs."""

from datetime import date
from typing import Annotated

from pydantic import Field

from app.domain.base import DomainModel


class CandidateCapabilityExtract(DomainModel):
    skill_id: str
    label: str
    proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    raw_confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_refs: list[str]
    inference_status: str
    verification_status: str
    recency_status: str
    rationale: str


class CandidateIntelligenceOutput(DomainModel):
    capabilities: list[CandidateCapabilityExtract]
    summary_rationale: str | None = None


class JobTaskExtract(DomainModel):
    id: str
    text: str
    on_site_likelihood: str = "unknown"
    importance: str = "core"
    capability_ids: list[str] = Field(default_factory=list)
    source_requirement_ids: list[str] = Field(default_factory=list)


class JobCapabilityExtract(DomainModel):
    id: str
    skill_id: str
    label: str
    min_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    importance: str = "core"
    evidence_expectation: str | None = None
    linked_task_ids: list[str] = Field(default_factory=list)


class RequirementAnalysisExtract(DomainModel):
    id: str
    text: str
    requirement_class: str
    review_tag: str = "NONE"
    strength: str = "required"
    why_relevant: str | None = None
    why_may_be_proxy: str | None = None
    linked_task_ids: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    rationale: str | None = None


class RoleOutcomeExtract(DomainModel):
    id: str
    text: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5


class JobDecompositionOutput(DomainModel):
    outcomes: list[RoleOutcomeExtract] = Field(default_factory=list)
    tasks: list[JobTaskExtract]
    capabilities: list[JobCapabilityExtract]
    requirements: list[RequirementAnalysisExtract]
    summary_rationale: str | None = None
