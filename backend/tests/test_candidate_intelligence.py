"""Candidate Intelligence Agent tests."""

from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.candidate_intelligence import CandidateIntelligenceAgent
from app.domain.enums import CapabilityVerificationStatus, EngineMode
from app.services.fixture_service import FixtureService


def _agent() -> CandidateIntelligenceAgent:
    return CandidateIntelligenceAgent(DeterministicFallbackProvider(), FixtureService())


def test_ananya_sql_detected():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    skill_ids = {c.skill_id for c in caps}
    assert "sql" in skill_ids


def test_ananya_excel_detected():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    assert any(c.skill_id == "excel" for c in caps)


def test_ananya_analytics_when_evidence_supports():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    assert any(c.skill_id == "data_analysis" for c in caps)


def test_career_gap_not_a_skill():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    labels = [c.label.lower() for c in caps]
    assert "career gap" not in labels
    assert "caregiving" not in " ".join(labels)


def test_no_fabricated_capability_without_evidence():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    assert not any(c.skill_id == "java" for c in caps)


def test_evidence_refs_preserved():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    sql_cap = next(c for c in caps if c.skill_id == "sql")
    assert len(sql_cap.evidence_refs) >= 1


def test_verification_status_preserved():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    power_bi = next(c for c in caps if c.skill_id == "power_bi")
    assert power_bi.verification_status == CapabilityVerificationStatus.SELF_REPORTED


def test_confidence_exists():
    bundle = FixtureService().get_ananya_bundle()
    caps, _ = _agent().run(bundle["profile"], bundle["evidence"], None)
    assert all(0.0 <= c.confidence <= 1.0 for c in caps)
    assert all(c.system_confidence is not None for c in caps)


def test_engine_mode_demo_fallback():
    agent = _agent()
    assert agent.engine_mode == EngineMode.DEMO_FALLBACK
