"""API integration tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["demo_mode"] is True
    assert data["sap_mode"] == "SIMULATED"


def test_root_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_candidates_returns_ananya():
    response = client.get("/api/demo/candidates")
    assert response.status_code == 200
    data = response.json()
    assert data["source_mode"] == "SYNTHETIC"
    assert data["count"] >= 1
    assert data["candidates"][0]["id"] == "ananya-sharma"


def test_demo_jobs_returns_data_analyst():
    response = client.get("/api/demo/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert data["jobs"][0]["id"] == "data-analyst-junior"


def test_sap_context_simulated():
    response = client.get("/api/sap/context")
    assert response.status_code == 200
    data = response.json()
    assert data["source_mode"] == "SIMULATED"
    assert data["live_connection"] is False
    assert data["sap_context"]["source_mode"] == "SIMULATED"


def test_get_ananya_detail():
    response = client.get("/api/demo/candidates/ananya-sharma")
    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["display_name"] == "Ananya Sharma"
    self_reported = [e for e in body["evidence"] if e["type"] == "SELF_REPORTED"]
    assert len(self_reported) >= 1
    assert self_reported[0]["verification_status"] != "VERIFIED"
