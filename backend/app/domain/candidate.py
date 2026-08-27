"""Candidate and evidence domain models."""

from datetime import date
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from app.domain.base import IdentifiedModel, TimestampedModel
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    RecencyStatus,
    SourceMode,
    VerificationStatus,
)


class CandidateProfile(IdentifiedModel):
    display_name: str
    age: int | None = None
    location: str
    work_modes: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    career_aspiration: str | None = None
    sap_user_id: str | None = None
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    is_demo_persona: bool = False
    notes: str | None = None


class CandidateEvidence(IdentifiedModel):
    candidate_id: str
    type: EvidenceType
    title: str
    description: str
    source: str
    source_mode: SourceMode
    occurred_on: date | None = None
    relevance: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    content_reference: str | None = None
    verification_status: VerificationStatus
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5

    @model_validator(mode="after")
    def self_reported_cannot_be_verified(self) -> "CandidateEvidence":
        if self.type == EvidenceType.SELF_REPORTED and self.verification_status == VerificationStatus.VERIFIED:
            raise ValueError("SELF_REPORTED evidence cannot have VERIFIED status")
        return self


class Skill(TimestampedModel):
    """Canonical skill / capability catalog entry."""

    id: Annotated[str, Field(min_length=1, max_length=64)]
    label: str
    description: str | None = None
    sap_attribute_id: str | None = None
    source: str = "REWORK"
    source_mode: SourceMode = SourceMode.SYNTHETIC


class CandidateCapability(IdentifiedModel):
    """Capability instance for a candidate."""

    candidate_id: str
    skill_id: str
    label: str
    proficiency: Annotated[float, Field(ge=0.0, le=1.0)]
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_refs: list[str] = Field(default_factory=list)
    recency: date | None = None
    task_relevance: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    role_relevance: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    source: str
    source_mode: SourceMode
    inference_status: str
    verification_status: CapabilityVerificationStatus | None = None
    recency_status: RecencyStatus | None = None
    raw_confidence: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    system_confidence: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    rationale: str | None = None

    @field_validator("evidence_refs")
    @classmethod
    def evidence_refs_required_for_high_confidence(cls, refs: list[str], info) -> list[str]:
        return refs

    @model_validator(mode="after")
    def verified_requires_evidence(self) -> "CandidateCapability":
        if self.inference_status == "VERIFIED" and not self.evidence_refs:
            raise ValueError("VERIFIED capabilities must reference evidence")
        if self.confidence > 0.7 and not self.evidence_refs:
            raise ValueError("High-confidence capabilities require evidence_refs")
        return self
