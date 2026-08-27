"""Job decomposition domain models."""

from typing import Annotated

from pydantic import Field

from app.domain.base import IdentifiedModel
from app.domain.enums import RequirementClass, ReviewTag, SourceMode


class RoleOutcome(IdentifiedModel):
    job_id: str
    text: str
    source_mode: SourceMode = SourceMode.SYNTHETIC


class JobTask(IdentifiedModel):
    job_id: str
    text: str
    on_site_likelihood: str = "unknown"
    importance: str = "core"
    capability_ids: list[str] = Field(default_factory=list)
    source_requirement_ids: list[str] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class JobRequirement(IdentifiedModel):
    job_id: str
    text: str
    requirement_class: RequirementClass
    review_tag: ReviewTag = ReviewTag.NONE
    strength: str = "required"
    why_relevant: str | None = None
    why_may_be_proxy: str | None = None
    linked_task_ids: list[str] = Field(default_factory=list)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    source_mode: SourceMode = SourceMode.SYNTHETIC


class JobCapability(IdentifiedModel):
    job_id: str
    skill_id: str
    label: str
    min_proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    importance: str = "core"
    evidence_expectation: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC


class JobProfile(IdentifiedModel):
    title: str
    raw_text: str
    family: str | None = None
    level: str | None = None
    location: str | None = None
    work_modes: list[str] = Field(default_factory=list)
    sap_requisition_id: str | None = None
    sap_job_role_code: str | None = None
    outcomes: list[RoleOutcome] = Field(default_factory=list)
    tasks: list[JobTask] = Field(default_factory=list)
    requirements: list[JobRequirement] = Field(default_factory=list)
    capabilities: list[JobCapability] = Field(default_factory=list)
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    is_demo_fixture: bool = False
