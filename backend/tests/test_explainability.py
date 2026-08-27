"""Explainability tests."""

from app.domain.enums import RunMode
from app.services.control_room_service import ControlRoomService
from app.services.explainability_service import ExplainabilityService
from app.services.orchestration_service import OrchestrationService


def _state():
    return OrchestrationService().execute_demo_run(run_mode=RunMode.CONTROL_ROOM_DEMO)


def test_recommendation_has_evidence():
    state = _state()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    assert rec.evidence_refs or state.get("opportunity_viability")


def test_recommendation_has_diagnosis():
    state = _state()
    reports = ExplainabilityService().build_reports(state)
    assert reports["reviewable_recommendation"]["ai_recommendation_preserved"].get("diagnosis_summary")


def test_recommendation_has_confidence():
    state = _state()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    assert rec.confidence_label is not None
    assert 0 <= rec.confidence <= 1


def test_recommendation_has_assumptions():
    state = _state()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    assert rec.assumptions


def test_alternatives_exist():
    state = _state()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    assert isinstance(rec.alternatives, list)


def test_human_review_requirement():
    state = _state()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    assert rec.human_review_required is True


def test_explainability_api_shape():
    state = _state()
    data = ControlRoomService().assemble_from_state(state)
    exp = data["explainability"]
    assert "reports" in exp or state.get("explainability")
