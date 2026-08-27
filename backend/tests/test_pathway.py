"""Pathway, proof-of-skill, capability refresh, and reassessment tests."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.adapters.sap_learning.simulated import SimulatedSAPLearningProvider
from app.domain.enums import GapStatus, PathwayStatus, ProofResultStatus, RunMode
from app.domain.pathway import ProofOfSkillAssessment, ProofSubmission
from app.main import app
from app.services.fixture_service import FixtureService
from app.services.orchestration_service import OrchestrationService
from app.services.pathway_engine import PathwayEngine
from app.services.proof_of_skill_engine import ProofOfSkillEngine
from tests.diagnosis_fixtures import make_capability, make_evidence, make_job_capability


def test_power_bi_gap_generates_power_bi_pathway():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.GENERATE_PATHWAY)
    pathway = state.get("learning_path")
    assert pathway is not None
    assert "power_bi" in pathway["target_capabilities"]
    assert pathway["target_role_id"] == "data-analyst-junior"


def test_pathway_bound_to_target_role():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.GENERATE_PATHWAY)
    pathway = state["learning_path"]
    assert pathway["candidate_id"] == "ananya-sharma"
    assert pathway["target_role_id"] == "data-analyst-junior"
    assert pathway.get("why")


def test_pathway_contains_practical_task():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.GENERATE_PATHWAY)
    assert state["learning_path"]["practical_tasks"]
    milestones = state["learning_path"]["milestones"]
    assert any(m.get("practice_task") for m in milestones)


def test_pathway_contains_proof_requirement():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.GENERATE_PATHWAY)
    milestones = state["learning_path"]["milestones"]
    assert any(m.get("proof_requirement") for m in milestones)
    assert state.get("proof_assessment")


def test_no_unrelated_course_spam():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.GENERATE_PATHWAY)
    items = state["learning_path"]["learning_items"]
    assert len(items) <= 4
    for item in items:
        assert item.get("capability") == "power_bi" or "power_bi" in item.get("skill_alignment", [])


def test_learning_source_mode_preserved():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.GENERATE_PATHWAY)
    for item in state["learning_path"]["learning_items"]:
        assert item.get("source_mode") in {"SIMULATED", "SYNTHETIC"}


def test_simulated_sap_learning_provider():
    provider = SimulatedSAPLearningProvider()
    items = provider.search_learning_items("power_bi", 0.4, {"role_id": "data-analyst-junior"})
    assert items
    assert provider.get_source_mode() == "SIMULATED"


def test_missing_sap_learning_falls_back():
    engine = PathwayEngine()
    from app.domain.assessment import CapabilityGap, CapabilityAssessmentItem
    from app.domain.enums import GapStatus

    gap = CapabilityGap(
        id="gap-1",
        candidate_id="c1",
        job_id="j1",
        skill_id="unknown_skill",
        gap_status=GapStatus.GENUINE_CAPABILITY_GAP,
        confidence=0.7,
    )
    item = CapabilityAssessmentItem(
        id="a1",
        skill_id="unknown_skill",
        label="Unknown",
        required_proficiency=0.6,
        candidate_proficiency=0.2,
        gap_status=GapStatus.GENUINE_CAPABILITY_GAP,
        confidence=0.7,
    )
    job_cap = make_job_capability("unknown_skill", "Unknown", 0.6)
    pathway = engine.generate("c1", "j1", "run-1", [gap], [item], [job_cap])
    assert pathway is not None
    assert pathway.learning_items


def test_proof_assessment_schema_validates():
    engine = ProofOfSkillEngine()
    assessment = engine.create_assessment("power_bi", "ananya-sharma")
    validated = ProofOfSkillAssessment.model_validate(assessment.model_dump())
    assert validated.rubric_criteria
    assert validated.task_description


def test_proof_submission_evaluates():
    engine = ProofOfSkillEngine()
    assessment = engine.create_assessment("power_bi", "test-candidate")
    submission = ProofSubmission(
        id="sub-1",
        assessment_id=assessment.id,
        candidate_id="test-candidate",
        skill_id="power_bi",
        responses={
            "data_preparation": 0.85,
            "dashboard_construction": 0.8,
            "visualization_quality": 0.75,
            "business_insight": 0.82,
            "communication": 0.78,
        },
    )
    result, evidence = engine.evaluate_submission(assessment, submission)
    assert result.result == ProofResultStatus.PASSED
    assert evidence.overall_result == ProofResultStatus.PASSED


def test_failed_proof_does_not_improve_capability():
    from app.services.capability_update_service import CapabilityUpdateService
    from app.domain.pathway import ProofEvidence, ProofOfSkillResult

    engine = ProofOfSkillEngine()
    assessment = engine.create_assessment("power_bi", "test-candidate")
    submission = ProofSubmission(
        id="sub-fail",
        assessment_id=assessment.id,
        candidate_id="test-candidate",
        skill_id="power_bi",
        responses={"data_preparation": 0.3, "dashboard_construction": 0.2},
    )
    result, evidence = engine.evaluate_submission(assessment, submission)
    assert result.result == ProofResultStatus.FAILED

    caps = [make_capability("power_bi", "Power BI", 0.22, ["ev-1"])]
    updated, event, _ = CapabilityUpdateService().apply_proof_result(
        caps, result, evidence, 0.6
    )
    assert event is None
    assert updated[0].proficiency == 0.22


def test_full_demo_replay_updates_capability():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.FULL_DEMO_REPLAY)
    assert state.get("capability_update_events")
    update = state["capability_update_events"][0]
    assert update["skill_id"] == "power_bi"
    assert update["new_level"] > update["old_level"]
    assert state["proof_result"]["is_demo"] is True


def test_reassessment_power_bi_no_longer_genuine_gap():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.FULL_DEMO_REPLAY)
    items = state["capability_assessments"][0]["items"]
    pbi = next(i for i in items if i["skill_id"] == "power_bi")
    assert pbi["gap_status"] != GapStatus.GENUINE_CAPABILITY_GAP.value


def test_no_hiring_recommendation_in_pathway_response():
    blob = json.dumps(OrchestrationService().build_proof_response(
        OrchestrationService().execute_demo_run(run_mode=RunMode.FULL_DEMO_REPLAY)
    )).lower()
    assert "hiring_recommendation" not in blob
    assert "candidate hired" not in blob


def test_pathway_api_endpoint():
    client = TestClient(app)
    response = client.post(
        "/api/runs/pathway",
        json={"candidate_id": "ananya-sharma", "job_id": "data-analyst-junior"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["learning_path"]
    assert data["learning_path"]["target_capabilities"] == ["power_bi"]


def test_proof_api_endpoint():
    client = TestClient(app)
    response = client.post(
        "/api/runs/proof",
        json={"candidate_id": "ananya-sharma", "job_id": "data-analyst-junior"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["proof_result"]
    assert data["reassessment_summary"]


def test_golden_checkpoint_04_ananya():
    golden_path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "golden"
        / "checkpoint_04_ananya.json"
    )
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    state = OrchestrationService().execute_demo_run(
        candidate_id=golden["candidate_id"],
        job_id=golden["job_id"],
        run_mode=RunMode.FULL_DEMO_REPLAY,
    )
    pathway = state["learning_path"]
    assert golden["expected_gap_skill_id"] in pathway["gap_skill_ids"]
    assert pathway["target_capabilities"] == [golden["expected_pathway_target_capability"]]
    assert len(pathway["milestones"]) >= golden["expected_milestone_count_min"]
    assert state["proof_assessment"]["skill_id"] == golden["expected_proof_assessment_skill"]
    if golden["expected_demo_proof"]:
        assert state["proof_result"]["is_demo"]
    assert state["capability_update_events"][0]["skill_id"] == golden["expected_capability_update_skill"]
    if golden["expected_pathway_completed"]:
        assert pathway["status"] == PathwayStatus.COMPLETED.value
    if golden["expected_power_bi_no_longer_genuine_gap"]:
        items = state["capability_assessments"][0]["items"]
        pbi = next(i for i in items if i["skill_id"] == "power_bi")
        assert pbi["gap_status"] != GapStatus.GENUINE_CAPABILITY_GAP.value

    agents = {e["agent"] for e in state.get("audit_events", [])}
    assert "pathway_generation" in agents
    assert "proof_evaluation" in agents
    assert "capability_update" in agents
    assert "reassessment" in agents
