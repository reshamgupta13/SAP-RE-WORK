"""LangGraph workflow — intelligence, diagnosis, pathway, and proof-of-skill."""

from typing import Any

from langgraph.graph import END, StateGraph

from app.adapters.llm import get_llm_provider
from app.adapters.sap import get_sap_provider
from app.agents.candidate_intelligence import CandidateIntelligenceAgent
from app.agents.job_decomposition import JobDecompositionAgent
from app.domain.assessment import CapabilityAssessmentItem, CapabilityGap
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.enums import AuditStatus, EngineMode, PathwayStatus, RunMode
from app.domain.job import JobCapability, JobProfile, JobRequirement, JobTask
from app.domain.pathway import ProofSubmission
from app.domain.sap import SAPContext
from app.orchestration.state import ReworkGraphState
from app.services.audit import AuditTimer, new_audit_event
from app.services.capability_update_service import CapabilityUpdateService
from app.services.diagnosis_service import DiagnosisService
from app.services.fixture_service import FixtureService
from app.services.pathway_engine import PathwayEngine
from app.services.proof_of_skill_engine import ProofOfSkillEngine
from app.services.explainability_service import ExplainabilityService
from app.services.intervention_simulator import InterventionSimulator
from app.services.opportunity_analysis_service import OpportunityAnalysisService
from app.services.sap_context_service import SAPContextService


def _audit_dict(event) -> dict[str, Any]:
    return event.model_dump(mode="json")


def build_graph() -> Any:
    fixture_service = FixtureService()
    sap_provider = get_sap_provider()
    diagnosis_service = DiagnosisService()
    pathway_engine = PathwayEngine()
    proof_engine = ProofOfSkillEngine()
    capability_update_service = CapabilityUpdateService()
    opportunity_analysis_service = OpportunityAnalysisService()
    intervention_simulator = InterventionSimulator()
    explainability_service = ExplainabilityService()
    sap_context_service = SAPContextService()

    def load_candidate(state: ReworkGraphState) -> dict[str, Any]:
        timer = AuditTimer()
        candidate_id = state.get("candidate_id", "ananya-sharma")
        job_id = state.get("job_id", "data-analyst-junior")
        try:
            if candidate_id != "ananya-sharma":
                raise ValueError(f"Unknown demo candidate: {candidate_id}")
            bundle = fixture_service.get_ananya_bundle()
            profile = bundle["profile"]
            evidence = bundle["evidence"]
            sap_bundle = sap_context_service.load_for_case(candidate_id, job_id)
            sap_ctx = SAPContext.model_validate(sap_bundle["system"])
            entities = sap_ctx.retrieved_entities or []
            event = new_audit_event(
                agent="load_candidate",
                run_id=state.get("run_id"),
                engine_mode=EngineMode.DEMO_FALLBACK,
                status=AuditStatus.SUCCESS,
                rationale=(
                    f"Loaded SAP context ({sap_ctx.source_mode.value}) and candidate fixture."
                ),
                input_reference=candidate_id,
                output_reference=profile.id,
                source_references=entities,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "candidate": profile.model_dump(mode="json"),
                "candidate_evidence": [e.model_dump(mode="json") for e in evidence],
                "sap_context": sap_ctx.model_dump(mode="json"),
                "sap_case_context": sap_bundle,
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="load_candidate",
                run_id=state.get("run_id"),
                engine_mode=EngineMode.DEMO_FALLBACK,
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def candidate_intelligence(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        llm = get_llm_provider()
        agent = CandidateIntelligenceAgent(llm, fixture_service)
        profile = CandidateProfile.model_validate(state["candidate"])
        evidence = [CandidateEvidence.model_validate(e) for e in state["candidate_evidence"]]
        sap_ctx = SAPContext.model_validate(state["sap_context"])
        sap_bundle = state.get("sap_case_context") or {}
        sap_skills_raw = (sap_bundle.get("skills_context") or {}).get("data") or []
        try:
            capabilities, rationale = agent.run(profile, evidence, sap_ctx, sap_skills_raw)
            avg_conf = sum(c.confidence for c in capabilities) / max(len(capabilities), 1)
            event = new_audit_event(
                agent="candidate_intelligence",
                run_id=state.get("run_id"),
                engine_mode=agent.engine_mode,
                status=AuditStatus.SUCCESS,
                rationale=rationale,
                confidence=avg_conf,
                input_reference=profile.id,
                output_reference=f"{len(capabilities)} capabilities",
                source_references=[c.id for c in capabilities]
                + [f"sap:{sap_ctx.source_mode.value}"],
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "engine_mode": agent.engine_mode.value,
                "candidate_capabilities": [c.model_dump(mode="json") for c in capabilities],
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="candidate_intelligence",
                run_id=state.get("run_id"),
                engine_mode=llm.engine_mode,
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def load_job(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        job_id = state.get("job_id", "data-analyst-junior")
        try:
            sap_role = sap_provider.get_role_context(job_id)
            if sap_role and sap_role.id == job_id:
                job = sap_role
                role_source = "SAP"
            else:
                job = fixture_service.get_data_analyst_job()
                role_source = "REWORK"
            if job.id != job_id:
                raise ValueError(f"Unknown demo job: {job_id}")
            event = new_audit_event(
                agent="load_job",
                run_id=state.get("run_id"),
                engine_mode=EngineMode.DEMO_FALLBACK,
                status=AuditStatus.SUCCESS,
                rationale=f"Loaded job from {role_source} adapter.",
                input_reference=job_id,
                output_reference=job.id,
                source_references=[f"role:{role_source}"],
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "job": job.model_dump(mode="json"),
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="load_job",
                run_id=state.get("run_id"),
                engine_mode=EngineMode.DEMO_FALLBACK,
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def job_decomposition(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        llm = get_llm_provider()
        agent = JobDecompositionAgent(llm)
        job = JobProfile.model_validate(state["job"])
        try:
            outcomes, tasks, capabilities, requirements, rationale = agent.run(job)
            event = new_audit_event(
                agent="job_decomposition",
                run_id=state.get("run_id"),
                engine_mode=agent.engine_mode,
                status=AuditStatus.SUCCESS,
                rationale=rationale,
                confidence=0.75,
                input_reference=job.id,
                output_reference=f"{len(tasks)} tasks",
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "engine_mode": agent.engine_mode.value,
                "role_outcomes": [o.model_dump(mode="json") for o in outcomes],
                "job_tasks": [t.model_dump(mode="json") for t in tasks],
                "job_capabilities": [c.model_dump(mode="json") for c in capabilities],
                "requirement_analyses": [r.model_dump(mode="json") for r in requirements],
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="job_decomposition",
                run_id=state.get("run_id"),
                engine_mode=llm.engine_mode,
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def diagnosis(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        job_id = state.get("job_id", "data-analyst-junior")
        try:
            candidate_caps = [
                CandidateCapability.model_validate(c) for c in state.get("candidate_capabilities", [])
            ]
            evidence = [CandidateEvidence.model_validate(e) for e in state.get("candidate_evidence", [])]
            job_caps = [JobCapability.model_validate(c) for c in state.get("job_capabilities", [])]
            requirements = [
                JobRequirement.model_validate(r) for r in state.get("requirement_analyses", [])
            ]
            tasks = [JobTask.model_validate(t) for t in state.get("job_tasks", [])]

            assessment, gaps, req_diagnoses, counterfactuals, summary = diagnosis_service.run(
                candidate_id=candidate_id,
                job_id=job_id,
                job_capabilities=job_caps,
                candidate_capabilities=candidate_caps,
                candidate_evidence=evidence,
                requirements=requirements,
                tasks=tasks,
                run_id=run_id,
            )

            gap_count = sum(1 for g in gaps if g.gap_status.value == "GENUINE_CAPABILITY_GAP")
            rationale = (
                f"Diagnosed {len(assessment.items)} capabilities; "
                f"{gap_count} genuine gaps; "
                f"{len(req_diagnoses)} requirement diagnoses."
            )
            event = new_audit_event(
                agent="diagnosis",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=rationale,
                confidence=summary.diagnosis_confidence,
                input_reference=f"{candidate_id}:{job_id}",
                output_reference=summary.overall_diagnosis_state.value,
                source_references=[
                    f"evidence:{len(evidence)}",
                    f"sap:{(state.get('sap_case_context') or {}).get('source_mode', 'SIMULATED')}",
                ],
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "capability_assessments": [assessment.model_dump(mode="json")],
                "capability_gaps": [g.model_dump(mode="json") for g in gaps],
                "requirement_diagnoses": [d.model_dump(mode="json") for d in req_diagnoses],
                "counterfactuals": [c.model_dump(mode="json") for c in counterfactuals],
                "diagnosis_summary": summary.model_dump(mode="json"),
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="diagnosis",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def counterfactual_analysis(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        summary = state.get("diagnosis_summary") or {}
        proxy_count = summary.get("eligibility_proxy_count", 0)
        rationale = (
            f"Counterfactual analysis complete; {proxy_count} potential eligibility proxies flagged."
        )
        event = new_audit_event(
            agent="counterfactual_analysis",
            run_id=run_id,
            engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
            status=AuditStatus.SUCCESS,
            rationale=rationale,
            confidence=summary.get("diagnosis_confidence"),
            input_reference=str(len(state.get("counterfactuals", []))),
            output_reference=summary.get("overall_diagnosis_state"),
            latency_ms=timer.elapsed_ms(),
        )
        run_mode = state.get("run_mode", RunMode.ANALYZE_ONLY.value)
        result: dict[str, Any] = {"audit_events": [_audit_dict(event)]}
        if run_mode == RunMode.ANALYZE_ONLY.value:
            result["status"] = "completed"
        return result

    def pathway_generation(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        job_id = state.get("job_id", "data-analyst-junior")
        try:
            gaps = [CapabilityGap.model_validate(g) for g in state.get("capability_gaps", [])]
            assessment = state.get("capability_assessments", [])
            items = []
            if assessment:
                items = [
                    CapabilityAssessmentItem.model_validate(i)
                    for i in assessment[0].get("items", [])
                ]
            job_caps = [JobCapability.model_validate(c) for c in state.get("job_capabilities", [])]
            job = state.get("job") or {}
            role_title = job.get("title")

            pathway = pathway_engine.generate(
                candidate_id=candidate_id,
                target_role_id=job_id,
                run_id=run_id,
                capability_gaps=gaps,
                capability_items=items,
                job_capabilities=job_caps,
                role_title=role_title,
            )
            if pathway is None:
                rationale = "No genuine capability gap requiring a learning pathway."
                event = new_audit_event(
                    agent="pathway_generation",
                    run_id=run_id,
                    engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                    status=AuditStatus.SKIPPED,
                    rationale=rationale,
                    latency_ms=timer.elapsed_ms(),
                )
                return {"audit_events": [_audit_dict(event)]}

            assessment_obj = proof_engine.create_assessment(
                skill_id=pathway.target_capabilities[0],
                candidate_id=candidate_id,
            )
            event = new_audit_event(
                agent="pathway_generation",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=pathway.why,
                confidence=pathway.confidence,
                input_reference=pathway.gap_skill_ids[0],
                output_reference=pathway.id,
                source_references=[
                    f"sap-learning:{len(pathway.learning_items)}",
                    *(pathway.learning_item_ids or []),
                ],
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "learning_path": pathway.model_dump(mode="json"),
                "proof_assessment": assessment_obj.model_dump(mode="json"),
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="pathway_generation",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def proof_of_skill(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        run_mode = state.get("run_mode", RunMode.GENERATE_PATHWAY.value)
        if run_mode not in {
            RunMode.EVALUATE_PROOF.value,
            RunMode.FULL_DEMO_REPLAY.value,
            RunMode.CONTROL_ROOM_DEMO.value,
        }:
            return {}

        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        learning_path = state.get("learning_path")
        if not learning_path:
            return {"errors": ["No learning path available for proof evaluation."]}

        skill_id = learning_path.get("target_capabilities", [None])[0]
        assessment_data = state.get("proof_assessment")
        if not assessment_data:
            assessment_obj = proof_engine.create_assessment(skill_id, candidate_id)
            assessment_data = assessment_obj.model_dump(mode="json")

        try:
            from app.domain.pathway import ProofOfSkillAssessment

            assessment = ProofOfSkillAssessment.model_validate(assessment_data)
            is_demo = run_mode in {RunMode.FULL_DEMO_REPLAY.value, RunMode.CONTROL_ROOM_DEMO.value}

            if is_demo and candidate_id == "ananya-sharma" and skill_id == "power_bi":
                demo = fixture_service.get_proof_demo_fixture()
                submission = ProofSubmission(
                    id=f"submission-{assessment.id}",
                    assessment_id=assessment.id,
                    candidate_id=candidate_id,
                    skill_id=skill_id,
                    responses=demo["submission"]["responses"],
                    artifact_metadata=demo["submission"]["artifact_metadata"],
                    source_mode=assessment.source_mode,
                    is_demo=True,
                )
            else:
                submission_data = state.get("proof_submission")
                if not submission_data:
                    return {"errors": ["Proof submission required for evaluation."]}
                submission = ProofSubmission.model_validate(submission_data)

            result, evidence = proof_engine.evaluate_submission(assessment, submission)
            pathway_status = (
                PathwayStatus.PROOF_SUBMITTED.value
                if result.result.value == "PASSED"
                else PathwayStatus.PROOF_FAILED.value
            )
            updated_path = dict(learning_path)
            updated_path["status"] = pathway_status

            event = new_audit_event(
                agent="proof_evaluation",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=f"Proof evaluation: {result.result.value} (score {result.total:.2f}).",
                confidence=result.total,
                input_reference=assessment.id,
                output_reference=result.id,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "learning_path": updated_path,
                "proof_submission": submission.model_dump(mode="json"),
                "proof_result": result.model_dump(mode="json"),
                "proof_evidence": evidence.model_dump(mode="json"),
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="proof_evaluation",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def capability_refresh(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors") or not state.get("proof_result"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        try:
            from app.domain.pathway import ProofEvidence, ProofOfSkillResult

            proof_result = ProofOfSkillResult.model_validate(state["proof_result"])
            proof_evidence = ProofEvidence.model_validate(state["proof_evidence"])
            candidate_caps = [
                CandidateCapability.model_validate(c)
                for c in state.get("candidate_capabilities", [])
            ]
            evidence_list = [
                CandidateEvidence.model_validate(e) for e in state.get("candidate_evidence", [])
            ]
            job_caps = [JobCapability.model_validate(c) for c in state.get("job_capabilities", [])]
            required = 0.6
            job_cap = next((c for c in job_caps if c.skill_id == proof_result.skill_id), None)
            if job_cap:
                required = job_cap.min_proficiency

            updated_caps, update_event, new_evidence = capability_update_service.apply_proof_result(
                candidate_caps,
                proof_result,
                proof_evidence,
                required_proficiency=required,
                run_id=run_id,
            )

            if new_evidence:
                evidence_list.append(new_evidence)

            write_back = sap_provider.update_skill_progress(
                proof_result.candidate_id,
                proof_result.skill_id,
                {"new_level": update_event.new_level if update_event else None},
            )

            rationale = "Capability updated from proof-of-skill evidence."
            if update_event:
                rationale = (
                    f"{update_event.skill_id}: {update_event.old_level:.2f} → "
                    f"{update_event.new_level:.2f} via assessment."
                )

            event = new_audit_event(
                agent="capability_update",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS if update_event else AuditStatus.SKIPPED,
                rationale=rationale,
                confidence=proof_result.total,
                input_reference=proof_result.id,
                output_reference=update_event.id if update_event else None,
                latency_ms=timer.elapsed_ms(),
            )
            result: dict[str, Any] = {
                "updated_candidate_capabilities": [
                    c.model_dump(mode="json") for c in updated_caps
                ],
                "candidate_evidence": [e.model_dump(mode="json") for e in evidence_list],
                "audit_events": [_audit_dict(event)],
            }
            if update_event:
                result["capability_update_events"] = [update_event.model_dump(mode="json")]
                result["candidate_capabilities"] = result["updated_candidate_capabilities"]
                learning_path = dict(state.get("learning_path", {}))
                learning_path["status"] = PathwayStatus.COMPLETED.value
                result["learning_path"] = learning_path
            return result
        except Exception as exc:
            event = new_audit_event(
                agent="capability_update",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def reassessment(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        job_id = state.get("job_id", "data-analyst-junior")
        try:
            candidate_caps = [
                CandidateCapability.model_validate(c)
                for c in state.get("updated_candidate_capabilities", state.get("candidate_capabilities", []))
            ]
            evidence = [CandidateEvidence.model_validate(e) for e in state.get("candidate_evidence", [])]
            job_caps = [JobCapability.model_validate(c) for c in state.get("job_capabilities", [])]
            requirements = [
                JobRequirement.model_validate(r) for r in state.get("requirement_analyses", [])
            ]
            tasks = [JobTask.model_validate(t) for t in state.get("job_tasks", [])]

            assessment, gaps, req_diagnoses, counterfactuals, summary = diagnosis_service.run(
                candidate_id=candidate_id,
                job_id=job_id,
                job_capabilities=job_caps,
                candidate_capabilities=candidate_caps,
                candidate_evidence=evidence,
                requirements=requirements,
                tasks=tasks,
                run_id=run_id,
            )

            event = new_audit_event(
                agent="reassessment",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=f"Reassessment: {summary.overall_diagnosis_state.value}.",
                confidence=summary.diagnosis_confidence,
                input_reference=f"{candidate_id}:{job_id}",
                output_reference=summary.overall_diagnosis_state.value,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "status": "completed",
                "capability_assessments": [assessment.model_dump(mode="json")],
                "capability_gaps": [g.model_dump(mode="json") for g in gaps],
                "requirement_diagnoses": [d.model_dump(mode="json") for d in req_diagnoses],
                "counterfactuals": [c.model_dump(mode="json") for c in counterfactuals],
                "diagnosis_summary": summary.model_dump(mode="json"),
                "reassessment_summary": summary.model_dump(mode="json"),
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="reassessment",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def route_after_counterfactual(state: ReworkGraphState) -> str:
        mode = state.get("run_mode", RunMode.ANALYZE_ONLY.value)
        if mode == RunMode.ANALYZE_ONLY.value:
            return "end"
        if mode == RunMode.OPPORTUNITY_ANALYSIS.value:
            return "market_intelligence"
        return "pathway_generation"

    def route_after_reassessment(state: ReworkGraphState) -> str:
        mode = state.get("run_mode", RunMode.GENERATE_PATHWAY.value)
        if mode == RunMode.FULL_DEMO_REPLAY.value or mode == RunMode.CONTROL_ROOM_DEMO.value:
            return "market_intelligence"
        return "end"

    def market_intelligence(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        try:
            caps = [
                CandidateCapability.model_validate(c)
                for c in state.get("updated_candidate_capabilities", state.get("candidate_capabilities", []))
            ]
            prof_map = {c.skill_id: c.proficiency for c in caps}
            signals = opportunity_analysis_service._market.load_signals()
            investments = opportunity_analysis_service._market.analyze_skill_investments(
                candidate_id,
                list(prof_map.keys()),
                prof_map,
                [o.job_id for o in opportunity_analysis_service._fixtures.get_opportunity_catalog()],
            )
            event = new_audit_event(
                agent="market_intelligence",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=f"Loaded {len(signals)} synthetic market signals and {len(investments)} skill investment scenarios.",
                confidence=0.75,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "market_signals": [s.model_dump(mode="json") for s in signals],
                "skill_investments": [i.model_dump(mode="json") for i in investments],
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            return {"errors": [str(exc)], "audit_events": [_audit_dict(new_audit_event(
                agent="market_intelligence", run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE, error=str(exc), latency_ms=timer.elapsed_ms(),
            ))]}

    def opportunity_viability_node(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        try:
            caps = [
                CandidateCapability.model_validate(c)
                for c in state.get("updated_candidate_capabilities", state.get("candidate_capabilities", []))
            ]
            evidence = [CandidateEvidence.model_validate(e) for e in state.get("candidate_evidence", [])]
            result = opportunity_analysis_service.run(
                candidate_id=candidate_id,
                candidate_capabilities=caps,
                candidate_evidence=evidence,
                requirement_diagnoses=state.get("requirement_diagnoses", []),
                learning_path=state.get("learning_path"),
                proof_result=state.get("proof_result"),
                run_id=run_id,
            )
            event = new_audit_event(
                agent="opportunity_viability",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=f"Assessed viability for {len(result['opportunity_viability'])} opportunities.",
                confidence=0.78,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "opportunities": [o.model_dump(mode="json") for o in result["opportunities"]],
                "opportunity_viability": [v.model_dump(mode="json") for v in result["opportunity_viability"]],
                "employer_readiness": [e.model_dump(mode="json") for e in result["employer_readiness"]],
                "opportunity_counterfactuals": [c.model_dump(mode="json") for c in result["opportunity_counterfactuals"]],
                "opportunity_comparison": result["opportunity_comparison"].model_dump(mode="json"),
                "market_signals": [s.model_dump(mode="json") for s in result["market_signals"]],
                "skill_investments": [i.model_dump(mode="json") for i in result["skill_investments"]],
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="opportunity_viability",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def employer_readiness_node(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        assessments = state.get("employer_readiness", [])
        event = new_audit_event(
            agent="employer_readiness",
            run_id=run_id,
            engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
            status=AuditStatus.SUCCESS,
            rationale=f"Employer readiness recorded for {len(assessments)} opportunities.",
            latency_ms=timer.elapsed_ms(),
        )
        return {"audit_events": [_audit_dict(event)]}

    def opportunity_comparison_node(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        comparison = state.get("opportunity_comparison") or {}
        rec = comparison.get("recommended_next_step_opportunity_id")
        event = new_audit_event(
            agent="opportunity_comparison",
            run_id=run_id,
            engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
            status=AuditStatus.SUCCESS,
            rationale=f"Opportunity comparison complete; recommended next step: {rec}.",
            confidence=comparison.get("confidence"),
            latency_ms=timer.elapsed_ms(),
        )
        return {"status": "completed", "audit_events": [_audit_dict(event)]}

    def intervention_simulation(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        try:
            caps = [
                CandidateCapability.model_validate(c)
                for c in state.get(
                    "updated_candidate_capabilities",
                    state.get("candidate_capabilities", []),
                )
            ]
            evidence = [
                CandidateEvidence.model_validate(e) for e in state.get("candidate_evidence", [])
            ]
            result = intervention_simulator.run(
                candidate_id=candidate_id,
                opportunity_id="opp-data-analyst",
                candidate_capabilities=caps,
                candidate_evidence=evidence,
                requirement_diagnoses=state.get("requirement_diagnoses", []),
                learning_path=state.get("learning_path"),
                proof_result=state.get("proof_result"),
                employer_readiness=state.get("employer_readiness", []),
                run_id=run_id,
                use_baseline_for_demo=True,
            )
            event = new_audit_event(
                agent="intervention_simulation",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale=f"Simulated {len(result.get('scenarios', []))} intervention scenarios.",
                confidence=0.72,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "intervention_simulation": result,
                "interventions": result.get("interventions", []),
                "scenarios": result.get("scenarios", []),
                "minimum_effective_intervention": result.get("minimum_effective_intervention"),
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="intervention_simulation",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def explainability_node(state: ReworkGraphState) -> dict[str, Any]:
        if state.get("errors"):
            return {}
        timer = AuditTimer()
        run_id = state.get("run_id")
        try:
            merged = dict(state)
            explainability = ExplainabilityService().build_reports(merged)
            event = new_audit_event(
                agent="explainability",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.SUCCESS,
                rationale="Structured explainability reports generated.",
                confidence=0.8,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "status": "completed",
                "explainability": explainability,
                "audit_events": [_audit_dict(event)],
            }
        except Exception as exc:
            event = new_audit_event(
                agent="explainability",
                run_id=run_id,
                engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                status=AuditStatus.FAILURE,
                error=str(exc),
                latency_ms=timer.elapsed_ms(),
            )
            return {"errors": [str(exc)], "audit_events": [_audit_dict(event)]}

    def route_after_opportunity_comparison(state: ReworkGraphState) -> str:
        mode = state.get("run_mode", RunMode.ANALYZE_ONLY.value)
        if mode == RunMode.CONTROL_ROOM_DEMO.value:
            return "intervention_simulation"
        return "end"

    def route_after_pathway(state: ReworkGraphState) -> str:
        mode = state.get("run_mode", RunMode.GENERATE_PATHWAY.value)
        if mode == RunMode.GENERATE_PATHWAY.value:
            return "end"
        if mode in {RunMode.EVALUATE_PROOF.value, RunMode.FULL_DEMO_REPLAY.value, RunMode.CONTROL_ROOM_DEMO.value}:
            return "proof_of_skill"
        return "end"

    graph = StateGraph(ReworkGraphState)
    graph.add_node("load_candidate", load_candidate)
    graph.add_node("candidate_intelligence", candidate_intelligence)
    graph.add_node("load_job", load_job)
    graph.add_node("job_decomposition", job_decomposition)
    graph.add_node("diagnosis", diagnosis)
    graph.add_node("counterfactual_analysis", counterfactual_analysis)
    graph.add_node("pathway_generation", pathway_generation)
    graph.add_node("proof_of_skill", proof_of_skill)
    graph.add_node("capability_refresh", capability_refresh)
    graph.add_node("reassessment", reassessment)
    graph.add_node("market_intelligence", market_intelligence)
    graph.add_node("opportunity_viability", opportunity_viability_node)
    graph.add_node("employer_readiness", employer_readiness_node)
    graph.add_node("opportunity_comparison", opportunity_comparison_node)
    graph.add_node("intervention_simulation", intervention_simulation)
    graph.add_node("explainability", explainability_node)

    graph.set_entry_point("load_candidate")
    graph.add_edge("load_candidate", "candidate_intelligence")
    graph.add_edge("candidate_intelligence", "load_job")
    graph.add_edge("load_job", "job_decomposition")
    graph.add_edge("job_decomposition", "diagnosis")
    graph.add_edge("diagnosis", "counterfactual_analysis")
    graph.add_conditional_edges(
        "counterfactual_analysis",
        route_after_counterfactual,
        {"end": END, "pathway_generation": "pathway_generation", "market_intelligence": "market_intelligence"},
    )
    graph.add_conditional_edges(
        "pathway_generation",
        route_after_pathway,
        {"end": END, "proof_of_skill": "proof_of_skill"},
    )
    graph.add_edge("proof_of_skill", "capability_refresh")
    graph.add_edge("capability_refresh", "reassessment")
    graph.add_conditional_edges(
        "reassessment",
        route_after_reassessment,
        {"end": END, "market_intelligence": "market_intelligence"},
    )
    graph.add_edge("market_intelligence", "opportunity_viability")
    graph.add_edge("opportunity_viability", "employer_readiness")
    graph.add_edge("employer_readiness", "opportunity_comparison")
    graph.add_conditional_edges(
        "opportunity_comparison",
        route_after_opportunity_comparison,
        {"end": END, "intervention_simulation": "intervention_simulation"},
    )
    graph.add_edge("intervention_simulation", "explainability")
    graph.add_edge("explainability", END)

    return graph.compile()


def build_checkpoint_graph() -> Any:
    """Backward-compatible alias."""
    return build_graph()
