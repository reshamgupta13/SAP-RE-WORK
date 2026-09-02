"""Targeted Learning Orchestrator — gap-driven reskilling plans."""

from __future__ import annotations

import uuid
from typing import Any

from app.adapters.learning_resources import get_learning_resource_provider
from app.adapters.llm import get_llm_provider
from app.adapters.sap.mapper import SAPMapper
from app.agents.learning_strategist import LearningStrategistAgent
from app.agents.proof_alignment import ProofAlignmentAgent
from app.agents.resource_curator import ResourceCuratorAgent
from app.domain.assessment import CapabilityAssessmentItem, CapabilityGap
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.enums import EngineMode, GapStatus, SourceMode
from app.domain.job import JobCapability, JobProfile
from app.domain.learning import (
    AgentExecutionStatus,
    GapIntervention,
    InterventionSimulation,
    LearningPlan,
    LearningResource,
    LearningStep,
    LearningTraceLink,
    ProofRequirement,
)
from app.services.diagnosis_service import DiagnosisService
from app.services.learning_plan_validator import LearningPlanValidator
from app.services.sap_catalog_service import SAPCatalogService

_plan_store: dict[str, LearningPlan] = {}


class TargetedLearningService:
    """Generate gap-first learning plans via three AI agents + deterministic validator."""

    def __init__(self) -> None:
        self._catalog = SAPCatalogService()
        self._diagnosis = DiagnosisService()
        self._validator = LearningPlanValidator()
        self._resources = get_learning_resource_provider()
        self._mapper = SAPMapper()

    def get_plan(self, plan_id: str) -> LearningPlan | None:
        return _plan_store.get(plan_id)

    def get_plan_for_pair(self, candidate_id: str, role_id: str) -> LearningPlan | None:
        for plan in _plan_store.values():
            if plan.candidate_id == candidate_id and plan.role_id == role_id:
                return plan
        return None

    def generate(self, candidate_id: str, role_id: str) -> LearningPlan:
        context = self._load_context(candidate_id, role_id)
        run_id = str(uuid.uuid4())

        assessment, gaps, _, counterfactuals, summary = self._diagnosis.run(
            candidate_id=candidate_id,
            job_id=role_id,
            job_capabilities=context["job_capabilities"],
            candidate_capabilities=context["candidate_capabilities"],
            candidate_evidence=context["candidate_evidence"],
            requirements=[],
            tasks=[],
            run_id=run_id,
        )
        items = assessment.items
        diagnosed_gap_ids = {g.id for g in gaps}

        llm = get_llm_provider()
        agents = AgentExecutionStatus(engine_mode=llm.engine_mode)

        strategist_agent = LearningStrategistAgent(llm)
        cf_note = None
        if counterfactuals:
            cf_note = f"{len(counterfactuals)} counterfactual assessments available."

        strategist = strategist_agent.run(
            candidate_name=context["candidate_name"],
            role_title=context["role_title"],
            capability_items=items,
            capability_gaps=gaps,
            counterfactual_summary=cf_note,
        )
        agents.learning_strategist = "completed"
        agents.strategist_summary = strategist.summary_rationale

        curator_agent = ResourceCuratorAgent(llm)
        curator = curator_agent.run(strategist)
        agents.resource_curator = "completed"
        agents.curator_summary = curator.summary_rationale

        proof_agent = ProofAlignmentAgent(llm)
        proof = proof_agent.run(strategist, context["role_title"])
        agents.proof_alignment = "completed"
        agents.proof_summary = proof.summary_rationale

        validation = self._validator.validate(
            strategist, curator, proof, items, gaps, diagnosed_gap_ids
        )
        agents.validator = "completed" if validation.status == "passed" else "failed"

        plan = self._assemble_plan(
            candidate_id=candidate_id,
            role_id=role_id,
            context=context,
            items=items,
            gaps=gaps,
            summary=summary,
            strategist=strategist,
            curator=curator,
            proof=proof,
            validation=validation,
            agents=agents,
        )
        _plan_store[plan.id] = plan
        return plan

    def get_trace(self, plan_id: str) -> dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Learning plan not found: {plan_id}")
        return {
            "plan_id": plan_id,
            "trace": [t.model_dump(mode="json") for t in plan.trace],
            "validation": plan.validation.model_dump(mode="json") if plan.validation else None,
            "agents": plan.agents.model_dump(mode="json") if plan.agents else None,
        }

    def simulate_intervention(self, plan_id: str, gap_id: str | None = None) -> dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Learning plan not found: {plan_id}")

        target_iv = None
        if gap_id:
            target_iv = next((iv for iv in plan.interventions if iv.gap_id == gap_id), None)
        elif plan.interventions:
            target_iv = plan.interventions[0]

        if not target_iv:
            return {
                "message": "No addressable gap to simulate.",
                "is_simulated_projection": True,
                "label": "SIMULATED PROJECTION",
            }

        simulation = InterventionSimulation(
            gap_capability=target_iv.capability,
            intervention_label=f"Focused {target_iv.capability} pathway",
            before_state="Gap present",
            after_state="Gap addressed pending proof",
            readiness_note=(
                f"Expected capability: {target_iv.current_level:.2f} → {target_iv.required_level:.2f} "
                "(pending proof-of-skill verification)"
            ),
            is_simulated_projection=True,
            assumptions=[
                "Learning pathway completed as scheduled.",
                "Proof-of-skill assessment passed at defined threshold.",
                "Role requirements remain unchanged during projection window.",
            ],
        )
        return {
            "simulation": simulation.model_dump(mode="json"),
            "is_simulated_projection": True,
            "label": "SIMULATED PROJECTION",
        }

    def _load_context(self, candidate_id: str, role_id: str) -> dict[str, Any]:
        cand_resp = self._catalog.get_candidate(candidate_id)
        job_resp = self._catalog.get_job(role_id)
        if not cand_resp.get("candidate"):
            raise ValueError(f"Candidate not found: {candidate_id}")
        if not job_resp.get("job"):
            raise ValueError(f"Role not found: {role_id}")

        candidate_raw = cand_resp["candidate"]
        profile = CandidateProfile(
            id=str(candidate_raw.get("user_id") or candidate_id),
            display_name=str(candidate_raw.get("display_name") or candidate_id),
            location=str(candidate_raw.get("location") or ""),
            source="SAP",
            source_mode=SourceMode.MOCKED,
        )

        candidate_capabilities: list[CandidateCapability] = []
        candidate_evidence: list[CandidateEvidence] = []
        for skill_row in cand_resp.get("skills", []):
            cap = self._mapper.map_skill(
                {
                    "SKILL_ID": skill_row.get("skill_id"),
                    "PROFICIENCY": skill_row.get("proficiency"),
                    "EVIDENCE": skill_row.get("evidence_text"),
                    "VALID_FROM": skill_row.get("valid_from"),
                },
                candidate_id=profile.id,
                source_mode=SourceMode.MOCKED,
                skill_name=skill_row.get("skill_name"),
            )
            if cap:
                candidate_capabilities.append(cap)
            ev_data = cand_resp.get("evidence", [])
            for ev in ev_data:
                if ev.get("id") and ev["id"] not in {e.id for e in candidate_evidence}:
                    candidate_evidence.append(CandidateEvidence.model_validate(ev))

        job_capabilities: list[JobCapability] = []
        for req in job_resp.get("requirements", []):
            cap = self._mapper.map_job_capability(
                {
                    "JOB_ID": role_id,
                    "SKILL_ID": req.get("skill_id"),
                    "REQUIRED_PROFICIENCY": req.get("required_proficiency"),
                    "IS_MANDATORY": req.get("is_mandatory"),
                },
                SourceMode.MOCKED,
                skill_name=req.get("skill_name"),
            )
            if cap:
                job_capabilities.append(cap)

        job_raw = job_resp["job"]
        role_title = str(job_raw.get("job_name") or job_raw.get("title") or role_id)

        return {
            "profile": profile,
            "candidate_name": profile.display_name,
            "role_title": role_title,
            "candidate_capabilities": candidate_capabilities,
            "candidate_evidence": candidate_evidence,
            "job_capabilities": job_capabilities,
        }

    def _assemble_plan(
        self,
        *,
        candidate_id: str,
        role_id: str,
        context: dict[str, Any],
        items: list[CapabilityAssessmentItem],
        gaps: list[CapabilityGap],
        summary: Any,
        strategist: Any,
        curator: Any,
        proof: Any,
        validation: Any,
        agents: AgentExecutionStatus,
    ) -> LearningPlan:
        selection_by_step = {s.step_id: s for s in curator.selections}
        proof_by_gap = {p.gap_id: p for p in proof.proofs}

        interventions: list[GapIntervention] = []
        all_steps: list[LearningStep] = []
        proof_requirements: list[ProofRequirement] = []
        seq = 1

        for iv_ext in strategist.interventions:
            steps: list[LearningStep] = []
            for s in iv_ext.steps:
                sel = selection_by_step.get(s.step_id)
                resource_ids = sel.resource_ids if sel else []
                resources: list[LearningResource] = self._resources.get_by_ids(resource_ids)
                if not resources and sel and sel.fallback_intervention:
                    resources = [
                        LearningResource(
                            id=f"structured-{s.step_id}",
                            title=sel.fallback_intervention,
                            type=s.type,
                            capability=iv_ext.capability.lower().replace(" ", "_"),
                            estimated_minutes=s.estimated_minutes,
                            description=sel.fallback_intervention,
                            why_recommended=sel.why_recommended,
                            source_type="structured_intervention",
                        )
                    ]
                step = LearningStep(
                    id=f"step-{s.step_id}-{candidate_id}",
                    gap_id=iv_ext.gap_id,
                    capability=iv_ext.capability,
                    title=s.title,
                    objective=iv_ext.learning_objective,
                    step_type=s.type,
                    intervention_type=iv_ext.intervention_type,
                    estimated_minutes=s.estimated_minutes,
                    rationale=s.rationale,
                    resource_ids=resource_ids,
                    resources=resources,
                    sequence=seq,
                )
                steps.append(step)
                all_steps.append(step)
                seq += 1

            interventions.append(
                GapIntervention(
                    id=f"intervention-{iv_ext.gap_id}",
                    gap_id=iv_ext.gap_id,
                    capability=iv_ext.capability,
                    current_level=iv_ext.current_level,
                    required_level=iv_ext.required_level,
                    target_role=iv_ext.target_role,
                    learning_objective=iv_ext.learning_objective,
                    intervention_type=iv_ext.intervention_type,
                    estimated_effort=iv_ext.estimated_effort,
                    reason=iv_ext.reason,
                    smallest_effective_rationale=iv_ext.smallest_effective_rationale,
                    steps=steps,
                    addressable=iv_ext.addressable,
                    non_addressable_reason=iv_ext.non_addressable_reason,
                )
            )

            proof_ext = proof_by_gap.get(iv_ext.gap_id)
            if proof_ext:
                proof_requirements.append(
                    ProofRequirement(
                        id=f"proof-{iv_ext.gap_id}",
                        proof_type=proof_ext.proof_type,
                        proof_title=proof_ext.proof_title,
                        proof_description=proof_ext.proof_description,
                        acceptance_criteria=proof_ext.acceptance_criteria,
                        linked_capability=proof_ext.linked_capability,
                        required_proficiency=proof_ext.required_proficiency,
                        gap_id=iv_ext.gap_id,
                    )
                )

        trace = self._build_trace(items, gaps, interventions, proof_requirements)
        genuine_gaps = [g for g in gaps if g.gap_status == GapStatus.GENUINE_CAPABILITY_GAP]
        status = "no_intervention_required" if not interventions else "ready"
        if genuine_gaps and not interventions:
            status = "ready"

        return LearningPlan(
            id=f"lp-{candidate_id}-{role_id}-{uuid.uuid4().hex[:8]}",
            candidate_id=candidate_id,
            role_id=role_id,
            candidate_name=context["candidate_name"],
            target_role_title=context["role_title"],
            status=status,
            source_gap_ids=[g.id for g in gaps],
            gaps_addressed=[iv.capability for iv in interventions if iv.addressable],
            gaps_sufficient=strategist.gaps_sufficient,
            interventions=interventions,
            steps=all_steps,
            proof_requirements=proof_requirements,
            validation=validation,
            agents=agents,
            why_this_path=strategist.why_this_path,
            catalog_label=self._resources.get_catalog_label(),
            diagnosis_summary=summary.model_dump(mode="json") if summary else None,
            trace=trace,
        )

    def _build_trace(
        self,
        items: list[CapabilityAssessmentItem],
        gaps: list[CapabilityGap],
        interventions: list[GapIntervention],
        proofs: list[ProofRequirement],
    ) -> list[LearningTraceLink]:
        trace: list[LearningTraceLink] = []
        primary_gap = next(
            (g for g in gaps if g.gap_status == GapStatus.GENUINE_CAPABILITY_GAP),
            gaps[0] if gaps else None,
        )
        if primary_gap:
            item = next((i for i in items if i.skill_id == primary_gap.skill_id), None)
            if item:
                trace.append(
                    LearningTraceLink(
                        stage="role_requirement",
                        label=item.label,
                        detail=f"Required: {item.required_proficiency:.2f} ({item.label})",
                    )
                )
                trace.append(
                    LearningTraceLink(
                        stage="candidate_capability",
                        label=item.label,
                        detail=(
                            f"Demonstrated: {item.candidate_proficiency:.2f}"
                            if item.candidate_proficiency is not None
                            else "Not demonstrated"
                        ),
                    )
                )
                trace.append(
                    LearningTraceLink(
                        stage="diagnosis",
                        label=primary_gap.gap_status.value.replace("_", " ").title(),
                        detail=primary_gap.notes or item.rationale,
                    )
                )

        if interventions:
            iv = interventions[0]
            trace.append(
                LearningTraceLink(
                    stage="learning_objective",
                    label=iv.capability,
                    detail=iv.learning_objective,
                )
            )
            trace.append(
                LearningTraceLink(
                    stage="intervention",
                    label=iv.intervention_type.replace("_", " ").title(),
                    detail=iv.smallest_effective_rationale or iv.reason,
                )
            )

        if proofs:
            p = proofs[0]
            trace.append(
                LearningTraceLink(
                    stage="proof",
                    label=p.proof_title,
                    detail=p.proof_description,
                )
            )
            trace.append(
                LearningTraceLink(
                    stage="reassessment",
                    label="Validate capability",
                    detail=f"Reassess {p.linked_capability} against role requirement after proof.",
                )
            )

        return trace


def clear_plan_store() -> None:
    _plan_store.clear()
