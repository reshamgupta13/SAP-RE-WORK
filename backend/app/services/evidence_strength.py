"""Deterministic evidence strength scoring."""

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    RecencyStatus,
    VerificationStatus,
)

VERIFICATION_WEIGHT: dict[CapabilityVerificationStatus, float] = {
    CapabilityVerificationStatus.VERIFIED: 0.9,
    CapabilityVerificationStatus.SUPPORTED: 0.75,
    CapabilityVerificationStatus.UNVERIFIED: 0.55,
    CapabilityVerificationStatus.SELF_REPORTED: 0.4,
}

EVIDENCE_TYPE_WEIGHT: dict[EvidenceType, float] = {
    EvidenceType.ASSESSMENT: 0.95,
    EvidenceType.PROJECT: 0.85,
    EvidenceType.WORK_HISTORY: 0.8,
    EvidenceType.RESUME: 0.65,
    EvidenceType.CERTIFICATION: 0.8,
    EvidenceType.PORTFOLIO: 0.75,
    EvidenceType.SELF_REPORTED: 0.35,
    EvidenceType.SAP_PROFILE: 0.7,
    EvidenceType.SAP_SKILL: 0.75,
    EvidenceType.SAP_LEARNING: 0.65,
    EvidenceType.OTHER: 0.5,
}

RECENCY_WEIGHT: dict[RecencyStatus, float] = {
    RecencyStatus.RECENT: 1.0,
    RecencyStatus.AGING: 0.85,
    RecencyStatus.STALE: 0.7,
    RecencyStatus.UNKNOWN: 0.6,
}


def compute_evidence_strength(
    capability: CandidateCapability | None,
    evidence_by_id: dict[str, CandidateEvidence],
) -> float:
    """Heuristic evidence strength — not a calibrated probability."""
    if capability is None or not capability.evidence_refs:
        return 0.15

    items = [evidence_by_id[r] for r in capability.evidence_refs if r in evidence_by_id]
    if not items:
        return 0.15

    verification = capability.verification_status or CapabilityVerificationStatus.UNVERIFIED
    base = VERIFICATION_WEIGHT.get(verification, 0.5)

    type_scores = [EVIDENCE_TYPE_WEIGHT.get(e.type, 0.5) for e in items]
    type_component = max(type_scores)

    recency = capability.recency_status or RecencyStatus.UNKNOWN
    recency_component = RECENCY_WEIGHT.get(recency, 0.6)

    count_bonus = min(0.1, 0.03 * len(items))
    item_confidence = max(e.confidence for e in items)

    blended = (base * 0.35) + (type_component * 0.3) + (recency_component * 0.2) + (item_confidence * 0.15)
    blended += count_bonus
    return round(min(max(blended, 0.0), 1.0), 2)


def evidence_strength_from_items(evidence_items: list[CandidateEvidence]) -> float:
    if not evidence_items:
        return 0.15
    scores: list[float] = []
    for ev in evidence_items:
        verification = CapabilityVerificationStatus.SELF_REPORTED
        if ev.type != EvidenceType.SELF_REPORTED:
            if ev.verification_status == VerificationStatus.VERIFIED:
                verification = CapabilityVerificationStatus.VERIFIED
            elif ev.verification_status == VerificationStatus.UNVERIFIED:
                verification = CapabilityVerificationStatus.UNVERIFIED
            else:
                verification = CapabilityVerificationStatus.SUPPORTED
        base = VERIFICATION_WEIGHT.get(verification, 0.5)
        type_w = EVIDENCE_TYPE_WEIGHT.get(ev.type, 0.5)
        scores.append((base * 0.5) + (type_w * 0.3) + (ev.confidence * 0.2))
    return round(min(max(max(scores), 0.0), 1.0), 2)
