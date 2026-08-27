"""Orchestrates capability gap, requirement diagnosis, and counterfactual analysis."""

from app.domain.assessment import (
    CapabilityAssessment,
    CapabilityGap,
    CounterfactualAssessment,
    DiagnosisSummary,
    RequirementDiagnosis,
)
from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.job import JobCapability, JobRequirement, JobTask
from app.services.capability_gap_engine import CapabilityGapEngine
from app.services.counterfactual_engine import CounterfactualEngine
from app.services.diagnosis_engine import DiagnosisEngine
from app.services.diagnosis_summary import build_diagnosis_summary


class DiagnosisService:
    """Deterministic diagnosis pipeline — no hiring recommendations."""

    def __init__(self) -> None:
        self._gap_engine = CapabilityGapEngine()
        self._diagnosis_engine = DiagnosisEngine()
        self._counterfactual_engine = CounterfactualEngine()

    def run(
        self,
        candidate_id: str,
        job_id: str,
        job_capabilities: list[JobCapability],
        candidate_capabilities: list[CandidateCapability],
        candidate_evidence: list[CandidateEvidence],
        requirements: list[JobRequirement],
        tasks: list[JobTask],
        run_id: str | None = None,
    ) -> tuple[
        CapabilityAssessment,
        list[CapabilityGap],
        list[RequirementDiagnosis],
        list[CounterfactualAssessment],
        DiagnosisSummary,
    ]:
        evidence_by_id = {e.id: e for e in candidate_evidence}

        assessment, gaps = self._gap_engine.assess(
            candidate_id=candidate_id,
            job_id=job_id,
            job_capabilities=job_capabilities,
            candidate_capabilities=candidate_capabilities,
            evidence_by_id=evidence_by_id,
            run_id=run_id,
        )

        requirement_diagnoses = self._diagnosis_engine.diagnose_requirements(
            requirements=requirements,
            tasks=tasks,
            job_capabilities=job_capabilities,
            candidate_capabilities=candidate_capabilities,
            capability_items=assessment.items,
            evidence_by_id=evidence_by_id,
            run_id=run_id,
        )

        counterfactuals = self._counterfactual_engine.analyze(
            requirement_diagnoses=requirement_diagnoses,
            requirements=requirements,
            tasks=tasks,
            job_capabilities=job_capabilities,
            candidate_capabilities=candidate_capabilities,
            evidence_by_id=evidence_by_id,
            run_id=run_id,
        )

        cf_by_req = {cf.requirement_id: cf.id for cf in counterfactuals}
        for diag in requirement_diagnoses:
            if diag.requirement_id in cf_by_req:
                diag.counterfactual_id = cf_by_req[diag.requirement_id]

        summary = build_diagnosis_summary(assessment.items, requirement_diagnoses)

        return assessment, gaps, requirement_diagnoses, counterfactuals, summary
