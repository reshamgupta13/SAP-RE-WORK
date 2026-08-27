"""Schema validation tests."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.assessment import FitDimensions
from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.decision import AuditEvent, DecisionCard
from app.domain.enums import (
    AuditStatus,
    EvidenceType,
    GapStatus,
    RecommendationState,
    SourceMode,
    VerificationStatus,
)
from app.services.fixture_service import FixtureService


def test_gap_status_enum_values():
    assert GapStatus.MATCHED.value == "MATCHED"
    assert GapStatus.GENUINE_CAPABILITY_GAP.value == "GENUINE_CAPABILITY_GAP"
    assert GapStatus.ELIGIBILITY_PROXY.value == "ELIGIBILITY_PROXY"


def test_self_reported_evidence_cannot_be_verified():
    with pytest.raises(ValidationError):
        CandidateEvidence(
            id="ev-bad",
            candidate_id="c1",
            type=EvidenceType.SELF_REPORTED,
            title="t",
            description="d",
            source="s",
            source_mode=SourceMode.USER_PROVIDED,
            verification_status=VerificationStatus.VERIFIED,
            confidence=0.5,
        )


def test_high_confidence_capability_requires_evidence():
    with pytest.raises(ValidationError):
        CandidateCapability(
            id="cap-bad",
            candidate_id="c1",
            skill_id="sql",
            label="SQL",
            proficiency=0.8,
            confidence=0.9,
            evidence_refs=[],
            source="REWORK",
            source_mode=SourceMode.SYNTHETIC,
            inference_status="EXPLICIT",
        )


def test_decision_card_validates():
    card = DecisionCard(
        id="dc-1",
        candidate_id="ananya-sharma",
        candidate_name="Ananya Sharma",
        target_role_id="data-analyst-junior",
        target_role_title="Junior Data Analyst",
        recommendation_state=RecommendationState.HUMAN_REVIEW_REQUIRED,
        confidence=0.75,
        what="Candidate shows core analytics capability.",
        why="Most critical capabilities are demonstrated with evidence.",
        source_mode=SourceMode.SYNTHETIC,
    )
    assert card.human_decision_required is True


def test_fit_dimensions_bounds():
    with pytest.raises(ValidationError):
        FitDimensions(
            capability_fit=1.5,
            evidence_strength=0.5,
            readiness=0.5,
            barrier_risk=0.2,
            overall_confidence=0.5,
        )


def test_audit_event_schema():
    event = AuditEvent(
        id="audit-1",
        agent="candidate_intelligence",
        status=AuditStatus.SUCCESS,
        confidence=0.8,
    )
    assert event.status == AuditStatus.SUCCESS


def test_ananya_fixture_loads():
    service = FixtureService()
    bundle = service.get_ananya_bundle()
    assert bundle["profile"].id == "ananya-sharma"
    assert bundle["profile"].is_demo_persona is True
    assert len(bundle["evidence"]) >= 3
    assert len(bundle["capabilities"]) >= 3


def test_data_analyst_fixture_has_proxy_requirements():
    job = FixtureService().get_data_analyst_job()
    assert job.id == "data-analyst-junior"
    assert any(r.text.lower().find("continuous") >= 0 for r in job.requirements)
    assert any(c.skill_id == "power_bi" for c in job.capabilities)


def test_malformed_evidence_rejected():
    with pytest.raises(ValidationError):
        CandidateEvidence(
            id="ev",
            candidate_id="c1",
            type=EvidenceType.RESUME,
            title="t",
            description="d",
            source="s",
            source_mode=SourceMode.USER_PROVIDED,
            verification_status=VerificationStatus.UNVERIFIED,
            confidence=2.0,
        )
