"""Opportunity viability, market intelligence, and employer readiness tests."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.enums import RunMode, SourceMode, ViabilityState
from app.main import app
from app.services.employer_readiness_engine import EmployerReadinessEngine
from app.services.fixture_service import FixtureService
from app.services.market_intelligence_engine import MarketIntelligenceEngine
from app.services.opportunity_analysis_service import OpportunityAnalysisService
from app.services.orchestration_service import OrchestrationService


def test_market_signals_load_synthetic():
    signals = FixtureService().get_market_signals()
    assert len(signals) >= 4
    assert all(s.source_mode == SourceMode.SYNTHETIC for s in signals)


def test_skill_investment_unlockable_roles():
    engine = MarketIntelligenceEngine()
    scenarios = engine.analyze_skill_investments(
        "ananya-sharma",
        ["sql", "excel", "communication"],
        {"sql": 0.62, "excel": 0.7, "communication": 0.68},
        ["data-analyst-junior", "operations-analyst", "bi-analyst"],
    )
    pbi = next(s for s in scenarios if s.investment_skill == "power_bi")
    assert len(pbi.unlockable_roles) >= 2


def test_opportunity_catalog_validates():
    catalog = FixtureService().get_opportunity_catalog()
    assert len(catalog) >= 3
    assert all(o.source_mode == SourceMode.SYNTHETIC for o in catalog)


def test_employer_readiness_factors():
    assessment = EmployerReadinessEngine().assess("opp-data-analyst")
    assert assessment is not None
    assert assessment.factors
    assert assessment.overall_state in {"READY", "PARTIALLY_READY", "NOT_READY", "UNKNOWN"}


def test_employer_interventions_evidence_based():
    assessment = EmployerReadinessEngine().assess("opp-bi-analyst")
    assert assessment is not None
    unknown_factors = [f for f in assessment.factors if f.status == "UNKNOWN"]
    if unknown_factors:
        assert any(i.issue for i in assessment.interventions)


def test_opportunity_analysis_two_sided():
    bundle = FixtureService().get_ananya_bundle()
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    viabilities = state.get("opportunity_viability", [])
    data_analyst = next(v for v in viabilities if v["opportunity_id"] == "opp-data-analyst")
    assert data_analyst.get("candidate_gaps") or data_analyst.get("candidate_barriers")
    assert data_analyst.get("dimensions", {}).get("employer_readiness") is not None


def test_pathway_effort_linked_for_data_analyst():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    comparison = state.get("opportunity_comparison", {})
    items = comparison.get("items", [])
    da = next(i for i in items if i["opportunity_id"] == "opp-data-analyst")
    assert da.get("pathway_effort_weeks") is not None


def test_proof_required_when_gap_exists():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    da = next(
        v for v in state["opportunity_viability"]
        if v["opportunity_id"] == "opp-data-analyst"
    )
    assert da.get("proof_required") is True


def test_opportunity_comparison_has_recommendation():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    comparison = state["opportunity_comparison"]
    assert comparison.get("recommended_next_step_opportunity_id")
    assert comparison.get("recommended_next_step_rationale")
    assert "hire" not in comparison.get("recommended_next_step_rationale", "").lower()


def test_counterfactual_opportunity_present():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    assert state.get("opportunity_counterfactuals")
    assert state["opportunity_counterfactuals"][0].get("required_changes")


def test_ananya_multiple_viable_pathways():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    viable_states = {
        ViabilityState.IMMEDIATELY_VIABLE.value,
        ViabilityState.VIABLE_WITH_TARGETED_PATHWAY.value,
        ViabilityState.VIABLE_WITH_PATHWAY_AND_ADAPTATION.value,
    }
    count = sum(
        1 for v in state["opportunity_viability"]
        if v["viability_state"] in viable_states
    )
    assert count >= 2


def test_no_protected_attributes_in_viability():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    blob = json.dumps(state).lower()
    forbidden = ["gender", "pregnancy", "disability", "caste", "religion", "race"]
    for term in forbidden:
        assert term not in blob or "protected" not in blob


def test_unknown_employer_stays_unknown():
    assessment = EmployerReadinessEngine().assess("opp-data-analyst")
    accessibility = next(
        (f for f in assessment.factors if f.factor == "ACCESSIBILITY_SUPPORT"),
        None,
    )
    if accessibility and accessibility.status == "UNKNOWN":
        assert accessibility.human_review_required


def test_fallback_without_llm():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.OPPORTUNITY_ANALYSIS)
    assert state.get("engine_mode") == "DEMO_FALLBACK"
    assert state.get("opportunity_viability")


def test_viability_api_endpoint():
    client = TestClient(app)
    response = client.post(
        "/api/runs/viability",
        json={"candidate_id": "ananya-sharma", "job_id": "data-analyst-junior"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["opportunity_viability"]
    assert data["opportunity_comparison"]
    assert "hiring_recommendation" not in data


def test_demo_opportunities_endpoint():
    client = TestClient(app)
    response = client.get("/api/demo/opportunities")
    assert response.status_code == 200
    assert response.json()["source_mode"] == "SYNTHETIC"


def test_demo_market_endpoint():
    client = TestClient(app)
    response = client.get("/api/demo/market")
    assert response.status_code == 200
    data = response.json()
    assert data["source_mode"] == "SYNTHETIC"
    assert "not live" in data.get("note", "").lower() or "Synthetic" in data.get("note", "")


def test_golden_checkpoint_05_ananya():
    golden_path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "golden"
        / "checkpoint_05_ananya.json"
    )
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    state = OrchestrationService().execute_demo_run(
        candidate_id=golden["candidate_id"],
        job_id=golden["job_id"],
        run_mode=RunMode.OPPORTUNITY_ANALYSIS,
    )
    opp_ids = {o["id"] for o in state.get("opportunities", [])}
    for expected in golden["expected_opportunity_ids"]:
        assert expected in opp_ids

    da = next(
        v for v in state["opportunity_viability"]
        if v["opportunity_id"] == "opp-data-analyst"
    )
    assert da["viability_state"] in golden["expected_data_analyst_viability_states"]
    if golden["expected_power_bi_in_data_analyst_gaps"]:
        assert "power_bi" in da.get("candidate_gaps", [])

    ops = next(
        v for v in state["opportunity_viability"]
        if v["opportunity_id"] == "opp-operations-analyst"
    )
    assert ops["viability_state"] in golden["expected_operations_analyst_viability_states"]

    if golden["expected_market_signals_synthetic"]:
        assert all(s["source_mode"] == "SYNTHETIC" for s in state["market_signals"])

    investments = state.get("skill_investments", [])
    if golden["expected_skill_investment_power_bi"]:
        assert any(i["investment_skill"] == "power_bi" for i in investments)

    assert len(state.get("employer_readiness", [])) >= golden["expected_employer_readiness_count_min"]

    comparison = state["opportunity_comparison"]
    assert comparison["recommended_next_step_opportunity_id"] == golden["expected_comparison_recommended_step"]

    agents = {e["agent"] for e in state.get("audit_events", [])}
    assert "market_intelligence" in agents
    assert "opportunity_viability" in agents
    assert "opportunity_comparison" in agents
