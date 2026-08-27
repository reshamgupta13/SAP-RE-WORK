"""Shared factories for diagnosis tests."""

from datetime import date

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    GapStatus,
    RecencyStatus,
    RequirementClass,
    ReviewTag,
    SourceMode,
    VerificationStatus,
)
from app.domain.job import JobCapability, JobRequirement, JobTask


def make_evidence(
    id: str,
    candidate_id: str = "test-candidate",
    title: str = "Evidence",
    description: str = "",
    evidence_type: EvidenceType = EvidenceType.PROJECT,
    verification: VerificationStatus = VerificationStatus.VERIFIED,
    confidence: float = 0.85,
    occurred_on: date | None = date(2024, 1, 1),
) -> CandidateEvidence:
    return CandidateEvidence(
        id=id,
        candidate_id=candidate_id,
        type=evidence_type,
        title=title,
        description=description,
        source="test",
        source_mode=SourceMode.SYNTHETIC,
        occurred_on=occurred_on,
        verification_status=verification,
        confidence=confidence,
    )


def make_capability(
    skill_id: str,
    label: str,
    proficiency: float,
    evidence_refs: list[str],
    candidate_id: str = "test-candidate",
    verification: CapabilityVerificationStatus = CapabilityVerificationStatus.SUPPORTED,
    recency: RecencyStatus = RecencyStatus.RECENT,
) -> CandidateCapability:
    return CandidateCapability(
        id=f"cap-{candidate_id}-{skill_id}",
        candidate_id=candidate_id,
        skill_id=skill_id,
        label=label,
        proficiency=proficiency,
        confidence=0.8,
        evidence_refs=evidence_refs,
        source="test",
        source_mode=SourceMode.SYNTHETIC,
        inference_status="EXPLICIT",
        verification_status=verification,
        recency_status=recency,
        system_confidence=0.8,
    )


def make_job_capability(
    skill_id: str,
    label: str,
    min_proficiency: float,
    job_id: str = "test-job",
    importance: str = "core",
) -> JobCapability:
    return JobCapability(
        id=f"jcap-{job_id}-{skill_id}",
        job_id=job_id,
        skill_id=skill_id,
        label=label,
        min_proficiency=min_proficiency,
        importance=importance,
    )


def make_requirement(
    id: str,
    text: str,
    requirement_class: RequirementClass,
    job_id: str = "test-job",
    review_tag: ReviewTag = ReviewTag.NONE,
    linked_task_ids: list[str] | None = None,
) -> JobRequirement:
    return JobRequirement(
        id=id,
        job_id=job_id,
        text=text,
        requirement_class=requirement_class,
        review_tag=review_tag,
        linked_task_ids=linked_task_ids or [],
    )


def make_task(
    id: str,
    text: str,
    capability_ids: list[str],
    job_id: str = "test-job",
    on_site_likelihood: str = "low",
) -> JobTask:
    return JobTask(
        id=id,
        job_id=job_id,
        text=text,
        capability_ids=capability_ids,
        on_site_likelihood=on_site_likelihood,
    )
