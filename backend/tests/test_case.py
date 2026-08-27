"""Case graph, lifecycle, SAP, golden replay, and persistence tests."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.enums import CaseLifecycleState, CaseStage, HumanReviewAction
from app.main import app
from app.repositories.in_memory_case_repository import InMemoryCaseRepository
from app.services.case_service import CaseService
from app.services.explainability_integrity_service import ExplainabilityIntegrityService

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]


def test_case_creation():
    svc = CaseService()
    case = svc.create_case(case_id="test-create-1")
    assert case.lifecycle_state == CaseLifecycleState.CASE_CREATED
    assert case.case_version == 1


def test_case_lifecycle_finale():
    svc = CaseService()
    case = svc.create_case(case_id="test-lifecycle-1")
    case = svc.execute(case.id, execute_until=CaseStage.FINALE)
    assert case.lifecycle_state == CaseLifecycleState.EXPLANATION_READY
    assert case.snapshot
    assert case.decision_card
    assert case.explainability


def test_case_version_increments():
    svc = CaseService()
    case = svc.create_case(case_id="test-version-1")
    v1 = case.case_version
    case = svc.execute(case.id, execute_until=CaseStage.DIAGNOSIS)
    assert case.case_version > v1


def test_case_idempotency_proof():
    svc = CaseService()
    case = svc.create_case(case_id="test-idem-1")
    case = svc.execute(case.id, execute_until=CaseStage.FINALE, idempotency_key="replay-1")
    v_after = case.case_version
    case2 = svc.execute(case.id, execute_until=CaseStage.FINALE, idempotency_key="replay-1")
    assert case2.case_version == v_after


def test_intervention_does_not_mutate_case():
    svc = CaseService()
    case = svc.create_case(case_id="test-int-iso")
    case = svc.execute(case.id, execute_until=CaseStage.FINALE)
    snap_id_before = case.latest_snapshot_id
    svc.simulate_interventions(case.id)
    case_after = svc.get_case(case.id)
    assert case_after.latest_snapshot_id == snap_id_before


def test_human_review_preserves_ai():
    svc = CaseService()
    case = svc.create_case(case_id="test-hr-case")
    case = svc.execute(case.id, execute_until=CaseStage.FINALE)
    ai_before = dict(case.ai_recommendation)
    svc.submit_review(case.id, HumanReviewAction.REJECT, "hr-1", reason="test")
    case_after = svc.get_case(case.id)
    assert case_after.ai_recommendation.get("recommendation_summary") == ai_before.get(
        "recommendation_summary"
    )


def test_explainability_integrity():
    svc = CaseService()
    case = svc.execute(svc.create_case(case_id="test-integ").id, CaseStage.FINALE)
    errors = ExplainabilityIntegrityService().validate(case.snapshot)
    assert not errors


def test_sap_health_endpoint():
    r = client.get("/api/sap/health")
    assert r.status_code == 200
    data = r.json()
    assert "source_mode" in data
    assert data["source_mode"] == "SIMULATED"


def test_cases_api_create_and_get():
    r = client.post("/api/cases", json={"candidate_id": "ananya-sharma"})
    assert r.status_code == 200
    case_id = r.json()["id"]
    r2 = client.get(f"/api/cases/{case_id}")
    assert r2.status_code == 200


def test_cases_control_room():
    case = CaseService().get_or_create_finale_case()
    CaseService().execute(case.id, CaseStage.FINALE)
    r = client.get(f"/api/cases/{case.id}/control-room")
    assert r.status_code == 200
    data = r.json()
    assert data.get("case_id") == case.id
    assert data.get("timeline")


def test_what_changed():
    svc = CaseService()
    case = svc.execute(svc.create_case(case_id="test-wc").id, CaseStage.FINALE)
    report = svc.get_what_changed(case.id)
    assert "changes" in report


def test_golden_finale_fixture_exists():
    path = ROOT / "fixtures" / "golden" / "finale_ananya_case.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["case_id"] == "case-ananya-finale"


def test_repository_in_memory():
    repo = InMemoryCaseRepository()
    assert repo.list_cases() == []
