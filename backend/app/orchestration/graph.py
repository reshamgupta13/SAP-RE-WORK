"""LangGraph workflow — Checkpoint 2 intelligence + Checkpoint 3 diagnosis."""

from typing import Any

from langgraph.graph import END, StateGraph

from app.adapters.llm import get_llm_provider
from app.adapters.sap import get_sap_provider
from app.agents.candidate_intelligence import CandidateIntelligenceAgent
from app.agents.job_decomposition import JobDecompositionAgent
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.enums import AuditStatus, EngineMode
from app.domain.job import JobCapability, JobProfile, JobRequirement, JobTask
from app.domain.sap import SAPContext
from app.orchestration.state import ReworkGraphState
from app.services.audit import AuditTimer, new_audit_event
from app.services.diagnosis_service import DiagnosisService
from app.services.fixture_service import FixtureService


def _audit_dict(event) -> dict[str, Any]:
    return event.model_dump(mode="json")


def build_graph() -> Any:
    fixture_service = FixtureService()
    sap_provider = get_sap_provider()
    diagnosis_service = DiagnosisService()

    def load_candidate(state: ReworkGraphState) -> dict[str, Any]:
        timer = AuditTimer()
        candidate_id = state.get("candidate_id", "ananya-sharma")
        try:
            if candidate_id != "ananya-sharma":
                raise ValueError(f"Unknown demo candidate: {candidate_id}")
            bundle = fixture_service.get_ananya_bundle()
            profile = bundle["profile"]
            evidence = bundle["evidence"]
            sap_ctx = sap_provider.get_context()
            event = new_audit_event(
                agent="load_candidate",
                run_id=state.get("run_id"),
                engine_mode=EngineMode.DEMO_FALLBACK,
                status=AuditStatus.SUCCESS,
                rationale="Loaded demo candidate fixture.",
                input_reference=candidate_id,
                output_reference=profile.id,
                latency_ms=timer.elapsed_ms(),
            )
            return {
                "candidate": profile.model_dump(mode="json"),
                "candidate_evidence": [e.model_dump(mode="json") for e in evidence],
                "sap_context": sap_ctx.model_dump(mode="json"),
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
        try:
            capabilities, rationale = agent.run(profile, evidence, sap_ctx)
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
                source_references=[c.id for c in capabilities],
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
            job = fixture_service.get_data_analyst_job()
            if job.id != job_id:
                raise ValueError(f"Unknown demo job: {job_id}")
            event = new_audit_event(
                agent="load_job",
                run_id=state.get("run_id"),
                engine_mode=EngineMode.DEMO_FALLBACK,
                status=AuditStatus.SUCCESS,
                rationale="Loaded demo job fixture.",
                input_reference=job_id,
                output_reference=job.id,
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
        return {
            "status": "completed",
            "audit_events": [_audit_dict(event)],
        }

    graph = StateGraph(ReworkGraphState)
    graph.add_node("load_candidate", load_candidate)
    graph.add_node("candidate_intelligence", candidate_intelligence)
    graph.add_node("load_job", load_job)
    graph.add_node("job_decomposition", job_decomposition)
    graph.add_node("diagnosis", diagnosis)
    graph.add_node("counterfactual_analysis", counterfactual_analysis)

    graph.set_entry_point("load_candidate")
    graph.add_edge("load_candidate", "candidate_intelligence")
    graph.add_edge("candidate_intelligence", "load_job")
    graph.add_edge("load_job", "job_decomposition")
    graph.add_edge("job_decomposition", "diagnosis")
    graph.add_edge("diagnosis", "counterfactual_analysis")
    graph.add_edge("counterfactual_analysis", END)

    return graph.compile()


def build_checkpoint_graph() -> Any:
    """Backward-compatible alias."""
    return build_graph()
