"""Counterfactual analysis — would direct capability evidence change readiness?"""

import re

from app.domain.assessment import CounterfactualAssessment, RequirementDiagnosis
from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    CounterfactualConclusion,
    GapStatus,
    RequirementClass,
    SourceMode,
)
from app.domain.job import JobCapability, JobRequirement, JobTask

STATUTORY_KEYWORDS = re.compile(
    r"\b(visa|citizenship|security clearance|work permit|professional license|licensed)\b",
    re.IGNORECASE,
)


class CounterfactualEngine:
    """Deterministic counterfactual reasoning — no discrimination verdicts."""

    def analyze(
        self,
        requirement_diagnoses: list[RequirementDiagnosis],
        requirements: list[JobRequirement],
        tasks: list[JobTask],
        job_capabilities: list[JobCapability],
        candidate_capabilities: list[CandidateCapability],
        evidence_by_id: dict[str, CandidateEvidence],
        run_id: str | None = None,
    ) -> list[CounterfactualAssessment]:
        req_by_id = {r.id: r for r in requirements}
        task_by_id = {t.id: t for t in tasks}
        cap_by_skill = {c.skill_id: c for c in candidate_capabilities}
        counterfactuals: list[CounterfactualAssessment] = []

        for diag in requirement_diagnoses:
            req = req_by_id.get(diag.requirement_id)
            if not req:
                continue
            cf = self._analyze_one(
                diag,
                req,
                task_by_id,
                job_capabilities,
                cap_by_skill,
                evidence_by_id,
                run_id,
            )
            counterfactuals.append(cf)

        return counterfactuals

    def _analyze_one(
        self,
        diag: RequirementDiagnosis,
        req: JobRequirement,
        task_by_id: dict[str, JobTask],
        job_capabilities: list[JobCapability],
        cap_by_skill: dict[str, CandidateCapability],
        evidence_by_id: dict[str, CandidateEvidence],
        run_id: str | None,
    ) -> CounterfactualAssessment:
        related_tasks = [task_by_id[tid] for tid in diag.related_task_ids if tid in task_by_id]
        required_caps = diag.required_capabilities
        evidence_refs = list(diag.evidence_refs)
        supported_task = related_tasks[0].text if related_tasks else None
        primary_cap = required_caps[0] if required_caps else None
        statutory = bool(STATUTORY_KEYWORDS.search(req.text))

        if statutory:
            conclusion = CounterfactualConclusion.REQUIRES_HUMAN_REVIEW
            rationale = (
                "Statutory or policy-linked requirement; "
                "cannot recommend automatic substitution."
            )
            alt_validation = None
            human_review = True
            confidence = 0.7
        elif req.requirement_class == RequirementClass.WORKPLACE_CONDITION:
            low_site_tasks = [
                t for t in related_tasks if t.on_site_likelihood in {"low", "unknown"}
            ]
            if low_site_tasks and len(low_site_tasks) == len(related_tasks):
                conclusion = CounterfactualConclusion.REQUIRES_HUMAN_REVIEW
                rationale = (
                    "Linked core tasks have low on-site likelihood; "
                    "hybrid or remote arrangement may be viable subject to employer policy."
                )
                alt_validation = "Hybrid or remote-compatible arrangement if policy allows."
            else:
                conclusion = CounterfactualConclusion.REQUIREMENT_APPEARS_JOB_RELEVANT
                rationale = "Workplace condition may reflect genuine on-site task needs."
                alt_validation = None
            human_review = True
            confidence = 0.68
        elif req.requirement_class == RequirementClass.EXPERIENCE_REQUIREMENT:
            supporting = self._supporting_capability_evidence(required_caps, cap_by_skill)
            evidence_refs = list(dict.fromkeys(evidence_refs + supporting))
            if supporting:
                conclusion = CounterfactualConclusion.POTENTIAL_PROXY
                rationale = (
                    "If continuous experience were replaced by direct evidence of analytics capability, "
                    "candidate has supporting project and work-history evidence."
                )
                alt_validation = "Proof-of-skill assessment plus supervised transition period."
                human_review = True
                confidence = 0.72
            else:
                conclusion = CounterfactualConclusion.INSUFFICIENT_EVIDENCE
                rationale = "Insufficient capability evidence to test experience counterfactual."
                alt_validation = "Collect direct work samples before substituting experience."
                human_review = True
                confidence = 0.55
        elif req.requirement_class == RequirementClass.CREDENTIAL_REQUIREMENT:
            substitute = [s for s, cap in cap_by_skill.items() if cap.evidence_refs]
            if not substitute:
                substitute = [
                    s for s in required_caps if s in cap_by_skill and cap_by_skill[s].evidence_refs
                ]
            if substitute:
                conclusion = CounterfactualConclusion.REQUIRES_HUMAN_REVIEW
                rationale = (
                    "Credential may not be the only path; "
                    "direct capability evidence exists but legal or professional necessity is unknown."
                )
                alt_validation = "Direct capability demonstration plus HR policy review."
                evidence_refs = self._refs_for_skills(substitute, cap_by_skill)
            else:
                conclusion = CounterfactualConclusion.INSUFFICIENT_EVIDENCE
                rationale = "Insufficient evidence to assess credential substitution."
                alt_validation = None
            human_review = True
            confidence = 0.6
        elif diag.diagnosis_type == GapStatus.GENUINE_CAPABILITY_GAP:
            conclusion = CounterfactualConclusion.REQUIREMENT_APPEARS_JOB_RELEVANT
            rationale = (
                "Capability gap persists with available evidence; "
                "removing this requirement would not resolve the demonstrated gap."
            )
            alt_validation = "Bounded upskilling or proof-of-skill for the specific capability."
            human_review = diag.human_review_required
            confidence = diag.confidence
        elif diag.diagnosis_type == GapStatus.MATCHED:
            conclusion = CounterfactualConclusion.REQUIREMENT_APPEARS_JOB_RELEVANT
            rationale = "Requirement aligns with evidenced candidate capability."
            alt_validation = None
            human_review = False
            confidence = diag.confidence
        elif diag.diagnosis_type == GapStatus.INSUFFICIENT_EVIDENCE:
            conclusion = CounterfactualConclusion.INSUFFICIENT_EVIDENCE
            rationale = "More evidence needed before counterfactual can be assessed."
            alt_validation = "Request targeted work samples or assessments."
            human_review = True
            confidence = 0.5
        else:
            conclusion = CounterfactualConclusion.REQUIRES_HUMAN_REVIEW
            rationale = diag.rationale or "Requires contextual human review."
            alt_validation = None
            human_review = True
            confidence = diag.confidence

        return CounterfactualAssessment(
            id=f"cf-{req.id}",
            run_id=run_id,
            requirement_id=req.id,
            requirement_text=req.text,
            related_task_ids=diag.related_task_ids,
            required_capabilities=required_caps,
            supported_task=supported_task,
            required_capability=primary_cap,
            candidate_evidence_refs=evidence_refs,
            alternative_validation=alt_validation,
            conclusion=conclusion,
            confidence=confidence,
            human_review_required=human_review,
            rationale=rationale,
            source_mode=SourceMode.SYNTHETIC,
        )

    def _supporting_capability_evidence(
        self,
        skill_ids: list[str],
        cap_by_skill: dict[str, CandidateCapability],
    ) -> list[str]:
        refs: list[str] = []
        for skill_id in skill_ids:
            cap = cap_by_skill.get(skill_id)
            if cap and cap.evidence_refs:
                refs.extend(cap.evidence_refs)
        return refs

    def _refs_for_skills(
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
