"""Aggregate diagnosis summary from assessments and requirement diagnoses."""

from app.domain.assessment import (
    CapabilityAssessmentItem,
    DiagnosisSummary,
    RequirementDiagnosis,
)
from app.domain.enums import GapStatus, OverallDiagnosisState


def build_diagnosis_summary(
    capability_items: list[CapabilityAssessmentItem],
    requirement_diagnoses: list[RequirementDiagnosis],
) -> DiagnosisSummary:
    matched_count = sum(1 for i in capability_items if i.gap_status == GapStatus.MATCHED)
    capability_gap_count = sum(
        1 for i in capability_items if i.gap_status == GapStatus.GENUINE_CAPABILITY_GAP
    )
    insufficient_evidence_count = sum(
        1 for i in capability_items if i.gap_status == GapStatus.INSUFFICIENT_EVIDENCE
    )
    eligibility_proxy_count = sum(
        1 for d in requirement_diagnoses if d.diagnosis_type == GapStatus.ELIGIBILITY_PROXY
    )
    workplace_constraint_count = sum(
        1 for d in requirement_diagnoses if d.diagnosis_type == GapStatus.WORKPLACE_CONSTRAINT
    )
    unknown_count = sum(
        1 for d in requirement_diagnoses
        if d.diagnosis_type == GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
    )

    capability_fit = _capability_fit(capability_items)
    evidence_strength = _avg_evidence_strength(capability_items)
    diagnosis_confidence = _diagnosis_confidence(
        capability_items, requirement_diagnoses, capability_fit, evidence_strength
    )
    overall = _overall_state(
        matched_count,
        capability_gap_count,
        insufficient_evidence_count,
        eligibility_proxy_count,
        workplace_constraint_count,
        unknown_count,
    )

    return DiagnosisSummary(
        matched_count=matched_count,
        capability_gap_count=capability_gap_count,
        insufficient_evidence_count=insufficient_evidence_count,
        eligibility_proxy_count=eligibility_proxy_count,
        workplace_constraint_count=workplace_constraint_count,
        unknown_count=unknown_count,
        overall_diagnosis_state=overall,
        capability_fit=capability_fit,
        evidence_strength=evidence_strength,
        diagnosis_confidence=diagnosis_confidence,
    )


def _capability_fit(items: list[CapabilityAssessmentItem]) -> float:
    if not items:
        return 0.0
    scores: list[float] = []
    for item in items:
        if item.gap_status == GapStatus.MATCHED:
            scores.append(1.0)
        elif item.gap_status == GapStatus.GENUINE_CAPABILITY_GAP:
            req = item.required_proficiency
            cand = item.candidate_proficiency or 0.0
            scores.append(max(0.0, cand / req) if req > 0 else 0.0)
        elif item.gap_status == GapStatus.INSUFFICIENT_EVIDENCE:
            scores.append(0.4)
        else:
            scores.append(0.5)
    return round(sum(scores) / len(scores), 2)


def _avg_evidence_strength(items: list[CapabilityAssessmentItem]) -> float:
    if not items:
        return 0.0
    strengths = [i.evidence_strength or 0.0 for i in items]
    return round(sum(strengths) / len(strengths), 2)


def _diagnosis_confidence(
    capability_items: list[CapabilityAssessmentItem],
    requirement_diagnoses: list[RequirementDiagnosis],
    capability_fit: float,
    evidence_strength: float,
) -> float:
    item_conf = [i.confidence for i in capability_items]
    req_conf = [d.confidence for d in requirement_diagnoses]
    all_conf = item_conf + req_conf
    avg_conf = sum(all_conf) / len(all_conf) if all_conf else 0.5
    blended = (capability_fit * 0.3) + (evidence_strength * 0.3) + (avg_conf * 0.4)
    return round(min(max(blended, 0.0), 1.0), 2)


def _overall_state(
    matched_count: int,
    capability_gap_count: int,
    insufficient_evidence_count: int,
    eligibility_proxy_count: int,
    workplace_constraint_count: int,
    unknown_count: int,
) -> OverallDiagnosisState:
    if insufficient_evidence_count > matched_count and capability_gap_count == 0:
        return OverallDiagnosisState.INSUFFICIENT_EVIDENCE
    if capability_gap_count >= 3 and matched_count == 0:
        return OverallDiagnosisState.NOT_CURRENTLY_READY
    if unknown_count > 0 or eligibility_proxy_count > 0 or workplace_constraint_count > 0:
        if matched_count >= 2 and capability_gap_count <= 1:
            return OverallDiagnosisState.POTENTIALLY_VIABLE
        if matched_count >= 3 and capability_gap_count <= 1:
            return OverallDiagnosisState.MATCH_WITH_GAPS
        return OverallDiagnosisState.REQUIRES_HUMAN_REVIEW
    if capability_gap_count == 0 and insufficient_evidence_count == 0:
        return OverallDiagnosisState.STRONG_MATCH
    if capability_gap_count <= 1 and matched_count >= 2:
        return OverallDiagnosisState.MATCH_WITH_GAPS
    if capability_gap_count > 1:
        return OverallDiagnosisState.NOT_CURRENTLY_READY
    return OverallDiagnosisState.POTENTIALLY_VIABLE
