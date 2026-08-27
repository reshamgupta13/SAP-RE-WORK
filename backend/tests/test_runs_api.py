"""API tests for run orchestration."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_run_endpoint():
    response = client.post(
        "/api/runs",
        json={"candidate_id": "ananya-sharma", "job_id": "data-analyst-junior"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"]
    assert data["engine_mode"] == "DEMO_FALLBACK"
    assert len(data["candidate_capabilities"]) >= 4
    assert len(data["job_tasks"]) >= 3
    assert data["audit_summary"]["count"] >= 4


def test_get_run_endpoint():
    create = client.post("/api/runs", json={})
    run_id = create.json()["run_id"]
    response = client.get(f"/api/runs/{run_id}")
    assert response.status_code == 200
    assert response.json()["run_id"] == run_id


def test_candidate_intelligence_endpoint():
    response = client.post("/api/runs/candidate-intelligence", json={"candidate_id": "ananya-sharma"})
    assert response.status_code == 200
    data = response.json()
    assert data["engine_mode"] == "DEMO_FALLBACK"
    skill_ids = {c["skill_id"] for c in data["candidate_capabilities"]}
    assert "sql" in skill_ids


def test_job_decomposition_endpoint():
    response = client.post("/api/runs/job-decomposition", json={"job_id": "data-analyst-junior"})
    assert response.status_code == 200
    data = response.json()
    assert data["engine_mode"] == "DEMO_FALLBACK"
    assert any(r["requirement_class"] == "EXPERIENCE_REQUIREMENT" for r in data["requirement_analyses"])


def test_sap_context_still_simulated():
    response = client.get("/api/sap/context")
    assert response.json()["source_mode"] == "SIMULATED"
