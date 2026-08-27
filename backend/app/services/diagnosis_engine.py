"""Requirement-level diagnosis engine."""

import re

from app.domain.assessment import CapabilityAssessmentItem, RequirementDiagnosis
from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    BarrierType,
    GapStatus,
    RequirementClass,
    ReviewTag,
    SourceMode,
)
from app.domain.job import JobCapability, JobRequirement, JobTask

STATUTORY_KEYWORDS = re.compile(
    r"\b(visa|citizenship|security clearance|work permit|professional license|licensed)\b",
    re.IGNORECASE,
)


class DiagnosisEngine:
    """Deterministic requirement diagnosis — not a hiring engine."""

    def diagnose_requirements(
        self,
        requirements: list[JobRequirement],
        tasks: list[JobTask],
        job_capabilities: list[JobCapability],
        candidate_capabilities: list[CandidateCapability],
        capability_items: list[CapabilityAssessmentItem],
        evidence_by_id: dict[str, CandidateEvidence],
        run_id: str | None = None,
    ) -> list[RequirementDiagnosis]:
        cap_by_skill = {c.skill_id: c for c in candidate_capabilities}
        assessment_by_skill = {i.skill_id: i for i in capability_items}
        task_by_id = {t.id: t for t in tasks}
        diagnoses: list[RequirementDiagnosis] = []

        for req in requirements:
            related_tasks = [task_by_id[tid] for tid in req.linked_task_ids if tid in task_by_id]
            required_caps = self._required_capabilities_for_requirement(
                req, related_tasks, job_capabilities
            )
            diagnosis = self._diagnose_one(
                req,
                related_tasks,
                required_caps,
                cap_by_skill,
                assessment_by_skill,
                evidence_by_id,
                candidate_capabilities,
                run_id,
            )
            diagnoses.append(diagnosis)

        return diagnoses

    def _required_capabilities_for_requirement(
        self,
        req: JobRequirement,
        related_tasks: list[JobTask],
        job_capabilities: list[JobCapability],
    ) -> list[str]:
        skill_ids: set[str] = set()
        for task in related_tasks:
            skill_ids.update(task.capability_ids)
        if req.requirement_class == RequirementClass.DIRECT_CAPABILITY:
            text_lower = req.text.lower()
            for cap in job_capabilities:
                if cap.label.lower() in text_lower or cap.skill_id.replace("_", " ") in text_lower:
                    skill_ids.add(cap.skill_id)
        if req.requirement_class == RequirementClass.EXPERIENCE_REQUIREMENT:
            skill_ids.update({"data_analysis", "sql", "reporting"})
        return sorted(skill_ids)

    def _diagnose_one(
        self,
        req: JobRequirement,
        related_tasks: list[JobTask],
        required_caps: list[str],
        cap_by_skill: dict[str, CandidateCapability],
        assessment_by_skill: dict[str, CapabilityAssessmentItem],
        evidence_by_id: dict[str, CandidateEvidence],
        candidate_capabilities: list[CandidateCapability],
        run_id: str | None,
    ) -> RequirementDiagnosis:
        text_lower = req.text.lower()
        statutory = bool(STATUTORY_KEYWORDS.search(req.text))
        barrier_type = BarrierType.NONE
        human_review = req.review_tag in {
            ReviewTag.POTENTIAL_PROXY,
            ReviewTag.POTENTIAL_EXCLUSIONARY_FACTOR,
            ReviewTag.REQUIRES_REVIEW,
        }
        evidence_refs: list[str] = []
        candidate_cap_refs: list[str] = []
        gap: float | None = None
        diagnosis_type: GapStatus
        rationale: str

        if statutory:
            diagnosis_type = GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
            barrier_type = BarrierType.UNKNOWN
            human_review = True
            rationale = (
                "Requirement may involve statutory or policy constraints; "
                "human review required before any substitution."
            )
        elif req.requirement_class == RequirementClass.WORKPLACE_CONDITION:
            diagnosis_type = GapStatus.WORKPLACE_CONSTRAINT
            barrier_type = BarrierType.WORKPLACE_CONSTRAINT
            human_review = True
            rationale = (
                "Workplace condition recorded; evaluate compatibility with candidate "
                "preferences and whether core tasks require on-site presence."
            )
        elif req.requirement_class == RequirementClass.EXPERIENCE_REQUIREMENT:
            diagnosis_type = GapStatus.ELIGIBILITY_PROXY
            barrier_type = BarrierType.POTENTIAL_PROXY
            human_review = True
            supporting = self._collect_supporting_evidence(required_caps, cap_by_skill)
            evidence_refs = supporting
            candidate_cap_refs = [cap_by_skill[s].id for s in required_caps if s in cap_by_skill]
            rationale = (
                "Historical or continuous experience requirement may proxy for task capability; "
                "relevant capability evidence exists independently of continuity."
            )
        elif req.requirement_class == RequirementClass.CREDENTIAL_REQUIREMENT:
            diagnosis_type = GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
            barrier_type = (
                BarrierType.POTENTIAL_PROXY
                if req.review_tag == ReviewTag.POTENTIAL_EXCLUSIONARY_FACTOR
                else BarrierType.UNKNOWN
            )
            human_review = True
            substitute_caps = [
                c.skill_id
                for c in candidate_capabilities
                if c.evidence_refs
            ]
            if not substitute_caps:
                substitute_caps = [
                    s for s in required_caps if s in cap_by_skill and cap_by_skill[s].evidence_refs
                ]
            if substitute_caps:
                evidence_refs = self._collect_supporting_evidence(substitute_caps, cap_by_skill)
                candidate_cap_refs = [cap_by_skill[s].id for s in substitute_caps if s in cap_by_skill]
                required_caps = substitute_caps
                rationale = (
                    "Credential requirement requires human review; "
                    "direct capability evidence may partially substitute but legal necessity is unknown."
                )
            else:
                rationale = (
                    "Credential requirement requires human review; "
                    "insufficient direct capability evidence to assess substitution."
                )
        elif req.requirement_class == RequirementClass.DIRECT_CAPABILITY:
            skill = self._match_skill_in_text(text_lower, assessment_by_skill)
            if skill and skill in assessment_by_skill:
                item = assessment_by_skill[skill]
                diagnosis_type = item.gap_status
                gap = item.gap
                evidence_refs = item.evidence_refs
                candidate_cap_refs = item.candidate_capability_refs
                rationale = item.rationale or f"Direct capability requirement for {item.label}."
                if diagnosis_type == GapStatus.GENUINE_CAPABILITY_GAP:
                    barrier_type = BarrierType.NONE
                elif diagnosis_type == GapStatus.INSUFFICIENT_EVIDENCE:
                    barrier_type = BarrierType.INSUFFICIENT_EVIDENCE
                    human_review = True
            else:
                diagnosis_type = GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
                barrier_type = BarrierType.UNKNOWN
                human_review = True
                rationale = "Could not map direct capability requirement to assessed skills."
        elif req.requirement_class == RequirementClass.EVIDENCE_REQUIREMENT:
            supporting = self._collect_supporting_evidence(required_caps, cap_by_skill)
            if supporting:
                diagnosis_type = GapStatus.MATCHED
                evidence_refs = supporting
                candidate_cap_refs = [cap_by_skill[s].id for s in required_caps if s in cap_by_skill]
                rationale = "Required evidence type appears present in candidate record."
            else:
                diagnosis_type = GapStatus.INSUFFICIENT_EVIDENCE
                barrier_type = BarrierType.INSUFFICIENT_EVIDENCE
                human_review = True
                rationale = "Required evidence not found in candidate record."
        elif req.requirement_class == RequirementClass.POTENTIAL_PROXY:
            diagnosis_type = GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
            barrier_type = BarrierType.POTENTIAL_PROXY
            human_review = True
            rationale = "Marked as potential proxy; requires contextual human review."
        else:
            diagnosis_type = GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
            barrier_type = BarrierType.UNKNOWN
            human_review = True
            rationale = "Requirement classification uncertain; human review required."

        confidence = self._diagnosis_confidence(diagnosis_type, evidence_refs, evidence_by_id)

        return RequirementDiagnosis(
            id=f"diag-{req.id}",
            run_id=run_id,
            requirement_id=req.id,
            requirement=req.text,
            requirement_type=req.requirement_class,
            diagnosis_type=diagnosis_type,
            barrier_type=barrier_type,
            related_task_ids=[t.id for t in related_tasks],
            required_capabilities=required_caps,
            candidate_capability_refs=candidate_cap_refs,
            evidence_refs=evidence_refs,
            gap=gap,
            confidence=confidence,
            rationale=rationale,
            human_review_required=human_review,
            source_mode=SourceMode.SYNTHETIC,
        )

    def _match_skill_in_text(
        self,
        text_lower: str,
        assessment_by_skill: dict[str, CapabilityAssessmentItem],
    ) -> str | None:
        for skill_id, item in assessment_by_skill.items():
            if item.label.lower() in text_lower or skill_id.replace("_", " ") in text_lower:
                return skill_id
        return None

    def _collect_supporting_evidence(
        self,
        skill_ids: list[str],
        cap_by_skill: dict[str, CandidateCapability],
    ) -> list[str]:
        refs: list[str] = []
        for skill_id in skill_ids:
            cap = cap_by_skill.get(skill_id)
            if cap:
                refs.extend(cap.evidence_refs)
        return list(dict.fromkeys(refs))

    def _diagnosis_confidence(
        self,
        diagnosis_type: GapStatus,
        evidence_refs: list[str],
        evidence_by_id: dict[str, CandidateEvidence],
    ) -> float:
        if diagnosis_type in {
            GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW,
            GapStatus.WORKPLACE_CONSTRAINT,
            GapStatus.ELIGIBILITY_PROXY,
        }:
            base = 0.65
        elif diagnosis_type == GapStatus.INSUFFICIENT_EVIDENCE:
            base = 0.5
        else:
            base = 0.8
        if evidence_refs:
            ev_scores = [evidence_by_id[r].confidence for r in evidence_refs if r in evidence_by_id]
            if ev_scores:
                base = (base * 0.6) + (max(ev_scores) * 0.4)
        return round(min(max(base, 0.0), 1.0), 2)
