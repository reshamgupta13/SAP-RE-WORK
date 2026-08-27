"""Run orchestration API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.adapters.llm import get_llm_provider
from app.adapters.sap import get_sap_provider
from app.agents.candidate_intelligence import CandidateIntelligenceAgent
from app.agents.job_decomposition import JobDecompositionAgent
from app.domain.candidate import CandidateEvidence, CandidateProfile
from app.domain.enums import AuditStatus, EngineMode, RunMode
from app.domain.job import JobProfile
from app.domain.sap import SAPContext
from app.services.audit import AuditTimer, new_audit_event
from app.services.fixture_service import FixtureService
from app.services.orchestration_service import OrchestrationService

router = APIRouter()
_orchestration = OrchestrationService()
_fixtures = FixtureService()


class DemoRunRequest(BaseModel):
    candidate_id: str = "ananya-sharma"
    job_id: str = "data-analyst-junior"


class CandidateIntelligenceRequest(BaseModel):
    candidate_id: str = Field(default="ananya-sharma")


class JobDecompositionRequest(BaseModel):
    job_id: str = Field(default="data-analyst-junior")


@router.post("/diagnose")
def run_diagnose(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.ANALYZE_ONLY,
    )
    return _orchestration.build_diagnosis_response(state)


@router.post("/pathway")
def run_pathway(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.GENERATE_PATHWAY,
    )
    return _orchestration.build_pathway_response(state)


@router.post("/proof")
def run_proof(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.FULL_DEMO_REPLAY,
    )
    return _orchestration.build_proof_response(state)


@router.post("/reassess")
def run_reassess(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.FULL_DEMO_REPLAY,
    )
    return _orchestration.build_proof_response(state)


@router.post("/market")
def run_market(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.OPPORTUNITY_ANALYSIS,
    )
    return _orchestration.build_viability_response(state)


@router.post("/opportunities")
def run_opportunities(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.OPPORTUNITY_ANALYSIS,
    )
    return _orchestration.build_viability_response(state)


@router.post("/viability")
def run_viability(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        run_mode=RunMode.OPPORTUNITY_ANALYSIS,
    )
    return _orchestration.build_viability_response(state)


@router.post("")
def create_run(body: DemoRunRequest) -> dict[str, Any]:
    state = _orchestration.execute_demo_run(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
    )
    return _orchestration.build_response(state)


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    state = _orchestration.get_run(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")
    return _orchestration.build_response(state)


@router.post("/candidate-intelligence")
def run_candidate_intelligence(body: CandidateIntelligenceRequest) -> dict[str, Any]:
    if body.candidate_id != "ananya-sharma":
        raise HTTPException(status_code=404, detail="Demo candidate not found")
    timer = AuditTimer()
    bundle = _fixtures.get_ananya_bundle()
    profile = bundle["profile"]
    evidence = bundle["evidence"]
    sap_ctx = get_sap_provider().get_context()
    llm = get_llm_provider()
    agent = CandidateIntelligenceAgent(llm, _fixtures)
    capabilities, rationale = agent.run(profile, evidence, sap_ctx)
    event = new_audit_event(
        agent="candidate_intelligence",
        run_id=None,
        engine_mode=agent.engine_mode,
        status=AuditStatus.SUCCESS,
        rationale=rationale,
        confidence=sum(c.confidence for c in capabilities) / max(len(capabilities), 1),
        latency_ms=timer.elapsed_ms(),
    )
    return {
        "engine_mode": agent.engine_mode.value,
        "candidate": profile.model_dump(mode="json"),
        "candidate_evidence": [e.model_dump(mode="json") for e in evidence],
        "candidate_capabilities": [c.model_dump(mode="json") for c in capabilities],
        "sap_context": sap_ctx.model_dump(mode="json"),
        "audit_event": event.model_dump(mode="json"),
    }


@router.post("/job-decomposition")
def run_job_decomposition(body: JobDecompositionRequest) -> dict[str, Any]:
    job = _fixtures.get_data_analyst_job()
    if body.job_id != job.id:
        raise HTTPException(status_code=404, detail="Demo job not found")
    timer = AuditTimer()
    llm = get_llm_provider()
    agent = JobDecompositionAgent(llm)
    outcomes, tasks, capabilities, requirements, rationale = agent.run(job)
    event = new_audit_event(
        agent="job_decomposition",
        run_id=None,
        engine_mode=agent.engine_mode,
        status=AuditStatus.SUCCESS,
        rationale=rationale,
        confidence=0.75,
        latency_ms=timer.elapsed_ms(),
    )
    return {
        "engine_mode": agent.engine_mode.value,
        "job": job.model_dump(mode="json"),
        "role_outcomes": [o.model_dump(mode="json") for o in outcomes],
        "job_tasks": [t.model_dump(mode="json") for t in tasks],
        "job_capabilities": [c.model_dump(mode="json") for c in capabilities],
        "requirement_analyses": [r.model_dump(mode="json") for r in requirements],
        "audit_event": event.model_dump(mode="json"),
    }
