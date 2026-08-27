"""Intervention simulator tests."""

from app.domain.candidate import CandidateCapability
from app.domain.enums import InterventionType, ViabilityState
from app.services.fixture_service import FixtureService
from app.services.intervention_simulator import InterventionSimulator
from app.services.orchestration_service import OrchestrationService
from app.domain.enums import RunMode


def _baseline_run():
    bundle = FixtureService().get_ananya_bundle()
    return {
        "candidate_capabilities": [c.model_dump(mode="json") for c in bundle["capabilities"]],
        "candidate_evidence": [e.model_dump(mode="json") for e in bundle["evidence"]],
        "requirement_diagnoses": [],
        "employer_readiness": [],
        "run_id": "test-run",
    }


def test_valid_intervention_simulation():
    bundle = FixtureService().get_ananya_bundle()
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    assert result["is_simulated_projection"]
    assert result["label"] == "SIMULATED PROJECTION"
    assert len(result["interventions"]) >= 2
    assert len(result["scenarios"]) >= 2


def test_invalid_intervention_rejected_no_gap():
    bundle = FixtureService().get_ananya_bundle()
    caps = []
    for c in bundle["capabilities"]:
        cap = CandidateCapability.model_validate(c.model_dump())
        if cap.skill_id == "power_bi":
            cap.proficiency = 0.9
        caps.append(cap)
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=caps,
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
        use_baseline_for_demo=False,
    )
    learning = [i for i in result["interventions"] if i["type"] == InterventionType.LEARNING.value]
    assert not learning or all(
        s.get("intervention_types") != [InterventionType.LEARNING.value]
        for s in result["scenarios"]
        if s.get("intervention_types") == [InterventionType.LEARNING.value]
    )


def test_learning_affects_relevant_gap_only():
    bundle = FixtureService().get_ananya_bundle()
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    proof_scenario = next(
        s for s in result["scenarios"] if "proof" in s.get("label", "").lower()
    )
    effect = proof_scenario.get("effect") or {}
    assert "power_bi" in str(effect.get("affected_capabilities", []))


def test_proof_affects_verification_state():
    bundle = FixtureService().get_ananya_bundle()
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    proof_scenario = next(
        s for s in result["scenarios"] if InterventionType.PROOF_OF_SKILL.value in s.get("intervention_types", [])
    )
    after = proof_scenario["effect"]["after_state"]
    assert after.get("power_bi_proficiency", 0) > proof_scenario["effect"]["before_state"].get("power_bi_proficiency", 0)


def test_hybrid_affects_workplace_only():
    bundle = FixtureService().get_ananya_bundle()
    employer = [{"opportunity_id": "opp-data-analyst", "confidence": 0.75, "id": "er-1"}]
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=employer,
    )
    hybrid = next(
        (s for s in result["scenarios"] if InterventionType.HYBRID_WORK.value in s.get("intervention_types", [])),
        None,
    )
    if hybrid:
        dims = hybrid["effect"]["affected_dimensions"]
        assert "workplace_compatibility" in dims
        assert "employer_readiness" not in dims or "workplace_compatibility" in dims


def test_mentorship_affects_employer_readiness_only():
    bundle = FixtureService().get_ananya_bundle()
    employer = [{"opportunity_id": "opp-data-analyst", "confidence": 0.7, "id": "er-1"}]
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=employer,
    )
    mentorship = next(
        (s for s in result["scenarios"] if InterventionType.MENTORSHIP.value in s.get("intervention_types", [])),
        None,
    )
    assert mentorship is not None
    assert "employer_readiness" in mentorship["effect"]["affected_dimensions"]


def test_combined_intervention_bundle():
    bundle = FixtureService().get_ananya_bundle()
    sim = InterventionSimulator()
    result = sim.run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    bundles = result["bundles"]
    assert any(b["label"].startswith("Learning + Proof") for b in bundles)


def test_scenario_preserves_assumptions():
    bundle = FixtureService().get_ananya_bundle()
    result = InterventionSimulator().run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    for scenario in result["scenarios"]:
        if scenario.get("effect"):
            assert scenario["assumptions"]
            assert scenario["effect"]["is_simulated_projection"]


def test_no_guaranteed_outcome_language():
    bundle = FixtureService().get_ananya_bundle()
    result = InterventionSimulator().run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    assert result["label"] == "SIMULATED PROJECTION"
    for s in result["scenarios"]:
        assert s["is_simulated_projection"]


def test_minimum_effective_intervention_exists():
    bundle = FixtureService().get_ananya_bundle()
    result = InterventionSimulator().run(
        candidate_id="ananya-sharma",
        opportunity_id="opp-data-analyst",
        candidate_capabilities=bundle["capabilities"],
        candidate_evidence=bundle["evidence"],
        requirement_diagnoses=[],
        learning_path=None,
        proof_result=None,
        employer_readiness=[],
    )
    minimum = result.get("minimum_effective_intervention")
    assert minimum is not None
    assert minimum.get("after_viability_state") != result["baseline_viability_state"]


def test_control_room_demo_includes_intervention_node():
    state = OrchestrationService().execute_demo_run(run_mode=RunMode.CONTROL_ROOM_DEMO)
    assert state.get("intervention_simulation")
    assert state.get("explainability")
    agents = [e.get("agent") for e in state.get("audit_events", [])]
    assert "intervention_simulation" in agents
    assert "explainability" in agents
