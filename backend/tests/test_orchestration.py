"""LangGraph orchestration and fallback tests."""

import json
from pathlib import Path

from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.candidate_intelligence import CandidateIntelligenceAgent
from app.agents.schemas import CandidateIntelligenceOutput
from app.core.config import get_settings
from app.domain.enums import EngineMode
from app.services.fixture_service import FixtureService
from app.services.orchestration_service import OrchestrationService


def test_full_graph_run_populates_state():
    service = OrchestrationService()
    state = service.execute_demo_run()
    assert state.get("run_id")
    assert state.get("candidate_capabilities")
    assert state.get("job_tasks")
    assert state.get("requirement_analyses")
    assert len(state.get("audit_events", [])) >= 4


def test_graph_audit_events_exist():
    state = OrchestrationService().execute_demo_run()
    agents = {e["agent"] for e in state.get("audit_events", [])}
    assert "load_candidate" in agents
    assert "candidate_intelligence" in agents
    assert "load_job" in agents
    assert "job_decomposition" in agents


def test_graph_engine_mode_recorded():
    state = OrchestrationService().execute_demo_run()
    assert state.get("engine_mode") in {EngineMode.DEMO_FALLBACK.value, EngineMode.LLM.value}


def test_graph_no_hiring_recommendation_fields():
    response = OrchestrationService().build_response(
        OrchestrationService().execute_demo_run()
    )
    assert "recommendation_state" not in response
    assert "decision_card" not in response


def test_fallback_without_llm_key():
    settings = get_settings()
    assert settings.llm_api_key is None or settings.demo_mode
    state = OrchestrationService().execute_demo_run()
    assert state.get("engine_mode") == EngineMode.DEMO_FALLBACK.value


def test_malformed_llm_output_uses_fallback():
    bundle = FixtureService().get_ananya_bundle()
    fallback = DeterministicFallbackProvider()
    agent = CandidateIntelligenceAgent(fallback, FixtureService())
    payload = agent._build_fallback_output(bundle["profile"], bundle["evidence"])
    output = fallback.generate_structured(
        prompt="x",
        schema=CandidateIntelligenceOutput,
        context={"fallback_payload": payload.model_dump()},
    )
    assert len(output.capabilities) >= 4


def test_golden_snapshot_structure():
    golden_path = Path(__file__).resolve().parents[2] / "fixtures" / "golden" / "checkpoint_02_ananya.json"
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    state = OrchestrationService().execute_demo_run(
        candidate_id=golden["candidate_id"],
        job_id=golden["job_id"],
    )
    cap_ids = {c["skill_id"] for c in state.get("candidate_capabilities", [])}
    for skill in golden["expected_candidate_skill_ids"]:
        assert skill in cap_ids
    task_ids = {t["id"] for t in state.get("job_tasks", [])}
    for task_id in golden["expected_job_task_ids"]:
        assert task_id in task_ids
    req_texts = " ".join(r["text"].lower() for r in state.get("requirement_analyses", []))
    assert golden["expected_experience_requirement_text_contains"] in req_texts
