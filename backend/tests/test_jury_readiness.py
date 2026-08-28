"""Jury readiness: demo reset, narrative, negative case."""

from fastapi.testclient import TestClient

from app.domain.enums import CaseStage
from app.main import app
from app.services.case_service import CaseService

client = TestClient(app)


def test_demo_reset_endpoint():
    r = client.post("/api/demo/reset")
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"] == "case-ananya-finale"
    assert body["status"] == "reset"


def test_negative_case_demo():
    r = client.get("/api/demo/negative-case?scenario_id=B07")
    assert r.status_code == 200
    body = r.json()
    assert body["scenario_id"] == "B07"
    assert body["outcome"] in {"INSUFFICIENT_EVIDENCE", "NOT_CURRENTLY_READY", "REQUIRES_HUMAN_REVIEW", "MATCH_WITH_GAPS"}


def test_control_room_jury_narrative():
    svc = CaseService()
    case = svc.execute(svc.get_or_create_finale_case().id, CaseStage.FINALE)
    r = client.get(f"/api/cases/{case.id}/control-room")
    assert r.status_code == 200
    body = r.json()
    assert "jury_narrative" in body
    assert body["jury_narrative"]["rejection_story"]["traditional_filters"]
    assert body["operator_guide"]


def test_reset_clears_human_decision():
    svc = CaseService()
    case = svc.reset_finale_case()
    assert case.human_decision_status.value == "PENDING"
    assert case.lifecycle_state.value == "EXPLANATION_READY"
