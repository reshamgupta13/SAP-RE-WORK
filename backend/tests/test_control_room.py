"""Control Room API tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_control_room_endpoint():
    response = client.get("/api/demo/control-room")
    assert response.status_code == 200
    data = response.json()
    assert data["system_status"]["sap"] == "SIMULATED"
    assert data["candidate"]
    assert data["job"]
    assert data["diagnosis"]
    assert data["pathway"]
    assert data["proof"]
    assert data["market"]
    assert data["viability"]
    assert data["employer_readiness"]
    assert data["interventions"]
    assert data["explainability"]
    assert data["sap_context"]
    assert "SIMULATED" in data["sap_context"]["success_factors"]


def test_scenarios_endpoint():
    response = client.get("/api/demo/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["is_simulated_projection"]
    assert data["label"] == "SIMULATED PROJECTION"
    assert data["scenarios"]


def test_intervention_simulation_post():
    response = client.post(
        "/api/runs/intervention-simulation",
        json={"candidate_id": "ananya-sharma", "opportunity_id": "opp-data-analyst"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_simulated_projection"]


def test_reviews_post():
    cr = client.get("/api/demo/control-room").json()
    run_id = cr["run_id"]
    decision_card_id = cr["decision_card"]["id"]
    response = client.post(
        "/api/reviews",
        json={
            "run_id": run_id,
            "decision_card_id": decision_card_id,
            "action": "APPROVE",
            "reviewer_id": "hr-demo",
            "reason": "Demo approval",
        },
    )
    assert response.status_code == 200
    assert "Human decision" in response.json()["message"]
