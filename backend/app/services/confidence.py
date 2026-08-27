"""Confidence derivation from evidence quality."""

from datetime import date, datetime, timezone

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    RecencyStatus,
    VerificationStatus,
)


def compute_recency_status(occurred_on: date | None) -> RecencyStatus:
    if occurred_on is None:
        return RecencyStatus.UNKNOWN
    today = datetime.now(timezone.utc).date()
    months = (today.year - occurred_on.year) * 12 + (today.month - occurred_on.month)
    if months <= 18:
        return RecencyStatus.RECENT
    if months <= 36:
        return RecencyStatus.AGING
    return RecencyStatus.STALE


def map_evidence_verification(evidence: CandidateEvidence) -> CapabilityVerificationStatus:
    if evidence.type == EvidenceType.SELF_REPORTED:
        return CapabilityVerificationStatus.SELF_REPORTED
    if evidence.verification_status == VerificationStatus.VERIFIED:
        return CapabilityVerificationStatus.VERIFIED
    if evidence.verification_status == VerificationStatus.UNVERIFIED:
        return CapabilityVerificationStatus.UNVERIFIED
    return CapabilityVerificationStatus.SUPPORTED


def derive_system_confidence(
    evidence_items: list[CandidateEvidence],
    raw_confidence: float,
    verification: CapabilityVerificationStatus,
) -> float:
    if not evidence_items:
        return min(raw_confidence, 0.35)

    weights = {
        CapabilityVerificationStatus.VERIFIED: 0.95,
        CapabilityVerificationStatus.SUPPORTED: 0.8,
        CapabilityVerificationStatus.UNVERIFIED: 0.55,
        CapabilityVerificationStatus.SELF_REPORTED: 0.4,
    }
    evidence_strength = max(e.confidence for e in evidence_items)
    base = weights.get(verification, 0.5)
    blended = (raw_confidence * 0.4) + (evidence_strength * 0.4) + (base * 0.2)
    return round(min(max(blended, 0.0), 1.0), 2)


def apply_confidence_to_capability(
    capability: CandidateCapability,
    evidence_by_id: dict[str, CandidateEvidence],
) -> CandidateCapability:
    refs = capability.evidence_refs
    evidence_items = [evidence_by_id[r] for r in refs if r in evidence_by_id]
    if capability.verification_status is None and evidence_items:
        capability.verification_status = map_evidence_verification(evidence_items[0])
    if capability.recency_status is None:
        dates = [e.occurred_on for e in evidence_items if e.occurred_on]
        capability.recency_status = compute_recency_status(max(dates) if dates else capability.recency)
    if capability.raw_confidence is None:
        capability.raw_confidence = capability.confidence
    capability.system_confidence = derive_system_confidence(
        evidence_items,
        capability.raw_confidence or capability.confidence,
        capability.verification_status or CapabilityVerificationStatus.UNVERIFIED,
    )
    capability.confidence = capability.system_confidence
    return capability
