"""Finalization: demo health, benchmark, failure modes."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.enums import CaseStage, HumanReviewAction
from app.main import app
from app.services.benchmark_runner import BenchmarkRunner
from app.services.case_service import CaseService

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]


def test_benchmark_all_executable():
    report = BenchmarkRunner().run_all()
    assert report["executed_count"] >= 20
    assert report["failed"] == 0


def test_negative_scenarios_count():
    report = BenchmarkRunner().run_all()
    negative = [r for r in report["results"] if r["expected"].get("negative_outcome")]
    assert len(negative) >= 5


def test_case_export_no_secrets():
    svc = CaseService()
    case = svc.execute(svc.get_or_create_finale_case().id, CaseStage.FINALE)
    export = svc.export_case(case.id)
    blob = json.dumps(export).lower()
    assert "client_secret" not in blob
    assert "password" not in blob
    r = client.get(f"/api/cases/{case.id}/export")
    assert r.status_code == 200


def test_sap_health_simulated():
    r = client.get("/api/sap/health")
    assert r.json()["source_mode"] == "SIMULATED"


def test_stale_human_review_blocked():
    svc = CaseService()
    case = svc.create_case(case_id="test-stale-review")
    case = svc.execute(case.id, CaseStage.FINALE)
    try:
        svc.submit_review(
            case.id,
            HumanReviewAction.APPROVE,
            "hr-1",
            reviewed_case_version=case.case_version - 1,
        )
        assert False, "Should reject stale version"
    except ValueError:
        pass


def test_intervention_isolated_from_case():
    svc = CaseService()
    case = svc.execute(svc.create_case(case_id="test-iso-final").id, CaseStage.FINALE)
    snap_id = case.latest_snapshot_id
    svc.simulate_interventions(case.id)
    assert svc.get_case(case.id).latest_snapshot_id == snap_id


def test_executable_pack_fixture_exists():
    path = ROOT / "fixtures" / "benchmark" / "executable_pack.json"
    if not path.exists():
        BenchmarkRunner().export_fixtures_json(path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert len(data["scenarios"]) >= 20
