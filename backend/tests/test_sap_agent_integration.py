"""SAP + agent orchestration integration tests."""

import json

from fastapi.testclient import TestClient

from app.main import app
from app.services.agent_orchestration_service import AgentOrchestrationService
from app.services.case_service import CaseService
from app.services.sap_context_service import SAPContextService
from app.domain.enums import CaseStage

client = TestClient(app)


def test_sap_context_loads_through_adapter():
    bundle = SAPContextService().load_for_case("ananya-sharma", "data-analyst-junior")
    assert bundle["source_mode"] == "SIMULATED"
    assert bundle["workforce_context"]["source"] == "SAP"
    assert bundle["learning_context"]["status"] == "AVAILABLE"
    assert bundle["learning_context"]["item_count"] > 0


def test_sap_context_unavailable_slice_safe():
    bundle = SAPContextService().load_for_case("unknown-candidate", "data-analyst-junior")
    assert bundle["workforce_context"]["status"] == "AVAILABLE"
    skills = bundle["skills_context"]
    assert skills["status"] in {"AVAILABLE", "UNAVAILABLE", "ERROR"}


def test_agent_orchestrator_from_finale_case():
    svc = CaseService()
    case = svc.execute(svc.get_or_create_finale_case().id, CaseStage.FINALE)
    orch = AgentOrchestrationService().build(case.snapshot or {})
    assert orch["orchestrator"] == "LangGraph"
    assert len(orch["nodes"]) >= 10
    completed = [n for n in orch["nodes"] if n["status"] == "completed"]
    assert len(completed) >= 8
    assert orch["sap_source_mode"] == "SIMULATED"


def test_control_room_shows_agent_orchestrator():
    svc = CaseService()
    case = svc.execute(svc.get_or_create_finale_case().id, CaseStage.FINALE)
    r = client.get(f"/api/cases/{case.id}/control-room")
    assert r.status_code == 200
    body = r.json()
    assert "agent_orchestrator" in body
    assert body["agent_orchestrator"]["nodes"]
    assert body["system_status"]["sap"] == "SIMULATED"
    assert body["sap_judge_panel"]["connected_by"]


def test_sap_agent_flows_present():
    svc = CaseService()
    case = svc.execute(svc.get_or_create_finale_case().id, CaseStage.FINALE)
    flows = AgentOrchestrationService().build(case.snapshot or {})["sap_agent_flows"]
    assert len(flows) >= 2
    assert any("Learning" in f["flow"] for f in flows)


def test_export_includes_agent_trace():
    svc = CaseService()
    case = svc.execute(svc.get_or_create_finale_case().id, CaseStage.FINALE)
    export = svc.export_case(case.id)
    assert "agent_orchestrator" in export
    assert "sap_case_context" in export
    assert "graph_audit_events" in export
    blob = json.dumps(export).lower()
    assert "client_secret" not in blob


def test_sap_contribution_boundary():
    bundle = SAPContextService().load_for_case("ananya-sharma", "data-analyst-junior")
    boundary = SAPContextService().contribution_boundary(bundle)
    assert "sap" in boundary
    assert "rework" in boundary
    assert boundary["connected_by"]
