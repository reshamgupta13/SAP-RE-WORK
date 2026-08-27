"""Deterministic capability gap comparison."""

from app.domain.assessment import CapabilityAssessment, CapabilityAssessmentItem, CapabilityGap
from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import GapStatus, RecencyStatus, SourceMode
from app.domain.job import JobCapability
from app.services.evidence_strength import compute_evidence_strength

EVIDENCE_SUFFICIENT_THRESHOLD = 0.35
GAP_TOLERANCE = 0.02


class CapabilityGapEngine:
    """Compare required job capabilities against evidenced candidate capabilities."""

    def assess(
        self,
        candidate_id: str,
        job_id: str,
        job_capabilities: list[JobCapability],
        candidate_capabilities: list[CandidateCapability],
        evidence_by_id: dict[str, CandidateEvidence],
        run_id: str | None = None,
    ) -> tuple[CapabilityAssessment, list[CapabilityGap]]:
        candidate_by_skill = {c.skill_id: c for c in candidate_capabilities}
        items: list[CapabilityAssessmentItem] = []
        gaps: list[CapabilityGap] = []

        for job_cap in job_capabilities:
            candidate_cap = candidate_by_skill.get(job_cap.skill_id)
            evidence_strength = compute_evidence_strength(candidate_cap, evidence_by_id)
            required = job_cap.min_proficiency
            candidate_level = candidate_cap.proficiency if candidate_cap else None
            gap_value: float | None = None
            gap_status: GapStatus
            rationale: str
            human_review = False

            if candidate_cap is None:
                gap_status = GapStatus.INSUFFICIENT_EVIDENCE
                rationale = (
                    f"No evidenced capability for {job_cap.label}; "
                    "absence of evidence is not evidence of absence."
                )
                human_review = job_cap.importance == "core"
            elif evidence_strength < EVIDENCE_SUFFICIENT_THRESHOLD:
                gap_status = GapStatus.INSUFFICIENT_EVIDENCE
                rationale = (
                    f"Insufficient evidence to assess {job_cap.label} against role requirement."
                )
                human_review = True
            elif candidate_level is not None and candidate_level + GAP_TOLERANCE >= required:
                gap_status = GapStatus.MATCHED
                gap_value = max(0.0, required - candidate_level)
                rationale = (
                    f"{job_cap.label} meets or exceeds required proficiency "
                    f"({candidate_level:.2f} vs {required:.2f})."
                )
            else:
                gap_status = GapStatus.GENUINE_CAPABILITY_GAP
                gap_value = round(required - (candidate_level or 0.0), 2)
                rationale = (
                    f"{job_cap.label} is below role threshold based on available evidence "
                    f"({candidate_level:.2f} vs required {required:.2f})."
                )
                human_review = job_cap.importance == "core"

            confidence = self._item_confidence(evidence_strength, gap_status, candidate_cap)
            evidence_refs = list(candidate_cap.evidence_refs) if candidate_cap else []
            cap_refs = [candidate_cap.id] if candidate_cap else []

            item = CapabilityAssessmentItem(
                id=f"assess-{job_id}-{job_cap.skill_id}",
                skill_id=job_cap.skill_id,
                label=job_cap.label,
                required_proficiency=required,
                candidate_proficiency=candidate_level,
                evidence_strength=evidence_strength,
                gap=gap_value,
                gap_status=gap_status,
                confidence=confidence,
                evidence_refs=evidence_refs,
                candidate_capability_refs=cap_refs,
                recency_status=candidate_cap.recency_status if candidate_cap else RecencyStatus.UNKNOWN,
                human_review_required=human_review,
                rationale=rationale,
            )
            items.append(item)

            if gap_status != GapStatus.MATCHED:
                gaps.append(
                    CapabilityGap(
                        id=f"gap-{job_id}-{job_cap.skill_id}",
                        run_id=run_id,
                        candidate_id=candidate_id,
                        job_id=job_id,
                        skill_id=job_cap.skill_id,
                        gap_status=gap_status,
                        severity="critical" if job_cap.importance == "core" else "informational",
                        notes=rationale,
                        confidence=confidence,
                        source_mode=SourceMode.SYNTHETIC,
                    )
                )

        capability_fit = self._capability_fit(items)
        evidence_strength_avg = self._avg_evidence_strength(items)
        assessment = CapabilityAssessment(
            id=f"cap-assessment-{candidate_id}-{job_id}",
            candidate_id=candidate_id,
            job_id=job_id,
            items=items,
            source_mode=SourceMode.SYNTHETIC,
        )
        return assessment, gaps

    def _item_confidence(
        self,
        evidence_strength: float,
        gap_status: GapStatus,
        candidate_cap: CandidateCapability | None,
    ) -> float:
        base = evidence_strength
        if candidate_cap and candidate_cap.system_confidence is not None:
            base = (base * 0.5) + (candidate_cap.system_confidence * 0.5)
        if gap_status == GapStatus.INSUFFICIENT_EVIDENCE:
            base *= 0.75
        return round(min(max(base, 0.0), 1.0), 2)

    def _capability_fit(self, items: list[CapabilityAssessmentItem]) -> float:
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

    def _avg_evidence_strength(self, items: list[CapabilityAssessmentItem]) -> float:
        if not items:
            return 0.0
        strengths = [i.evidence_strength or 0.0 for i in items]
        return round(sum(strengths) / len(strengths), 2)
