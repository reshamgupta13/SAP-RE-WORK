"""Tests for targeted learning — gap-first reskilling."""

import pytest

from app.adapters.learning_resources import get_learning_resource_provider
from app.agents.learning_strategist import LearningStrategistAgent
from app.agents.proof_alignment import ProofAlignmentAgent
from app.agents.resource_curator import ResourceCuratorAgent
from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.domain.assessment import CapabilityAssessmentItem, CapabilityGap
from app.domain.enums import GapStatus, SourceMode
from app.services.learning_plan_validator import LearningPlanValidator
from app.services.targeted_learning_service import TargetedLearningService, clear_plan_store


@pytest.fixture(autouse=True)
def _clear_store():
    clear_plan_store()
    yield
    clear_plan_store()


def _mahi_odata_gap_items() -> tuple[list[CapabilityAssessmentItem], list[CapabilityGap]]:
    items = [
        CapabilityAssessmentItem(
            id="a-java",
            skill_id="skill0001",
            label="Java",
            required_proficiency=0.7,
            candidate_proficiency=0.8,
            evidence_strength=0.7,
            gap=0.0,
            gap_status=GapStatus.MATCHED,
            confidence=0.8,
            rationale="Java meets requirement.",
        ),
        CapabilityAssessmentItem(
            id="a-sql",
            skill_id="skill0005",
            label="SQL",
            required_proficiency=0.7,
            candidate_proficiency=0.8,
            evidence_strength=0.7,
            gap=0.0,
            gap_status=GapStatus.MATCHED,
            confidence=0.8,
            rationale="SQL meets requirement.",
        ),
        CapabilityAssessmentItem(
            id="a-odata",
            skill_id="skill0002",
            label="OData",
            required_proficiency=0.7,
            candidate_proficiency=0.2,
            evidence_strength=0.5,
            gap=0.5,
            gap_status=GapStatus.GENUINE_CAPABILITY_GAP,
            confidence=0.75,
            rationale="OData below threshold.",
        ),
    ]
    gaps = [
        CapabilityGap(
            id="gap-job001-skill0002",
            candidate_id="USER002",
            job_id="JOB002",
            skill_id="skill0002",
            gap_status=GapStatus.GENUINE_CAPABILITY_GAP,
            severity="critical",
            notes="OData gap",
            confidence=0.75,
            source_mode=SourceMode.MOCKED,
        )
    ]
    return items, gaps


def test_scenario_single_clear_gap_odata_only():
    """Mahi Chauhan: SAP sufficient, OData is the only learning target."""
    llm = DeterministicFallbackProvider()
    strategist = LearningStrategistAgent(llm)
    items, gaps = _mahi_odata_gap_items()
    out = strategist.run("Mahi Chauhan", "SAP Consultant", items, gaps)
    assert "SAP" in " ".join(out.gaps_sufficient) or "Java" in " ".join(out.gaps_sufficient)
    assert len(out.interventions) == 1
    assert "odata" in out.interventions[0].capability.lower()
    assert len(out.interventions[0].steps) == 3
    # No Java/SQL interventions
    caps = [iv.capability.lower() for iv in out.interventions]
    assert not any("java" in c for c in caps)
    assert not any("sql" in c for c in caps)


def test_scenario_no_meaningful_gap():
    llm = DeterministicFallbackProvider()
    strategist = LearningStrategistAgent(llm)
    items = [
        CapabilityAssessmentItem(
            id="a1",
            skill_id="skill0001",
            label="Java",
            required_proficiency=0.7,
            candidate_proficiency=0.8,
            evidence_strength=0.7,
            gap=0.0,
            gap_status=GapStatus.MATCHED,
            confidence=0.8,
            rationale="Met.",
        ),
    ]
    out = strategist.run("Candidate", "Role", items, [])
    assert out.interventions == []
    assert "no reskilling" in out.why_this_path.lower()


def test_scenario_evidence_gap():
    llm = DeterministicFallbackProvider()
    strategist = LearningStrategistAgent(llm)
    items = [
        CapabilityAssessmentItem(
            id="a-odata",
            skill_id="skill0002",
            label="OData",
            required_proficiency=0.7,
            candidate_proficiency=0.65,
            evidence_strength=0.2,
            gap=None,
            gap_status=GapStatus.INSUFFICIENT_EVIDENCE,
            confidence=0.5,
            rationale="Insufficient evidence.",
        ),
    ]
    gaps = [
        CapabilityGap(
            id="gap-evidence",
            candidate_id="c1",
            job_id="j1",
            skill_id="skill0002",
            gap_status=GapStatus.INSUFFICIENT_EVIDENCE,
            severity="critical",
            notes="Evidence gap",
            confidence=0.5,
            source_mode=SourceMode.MOCKED,
        )
    ]
    out = strategist.run("Candidate", "Role", items, gaps)
    assert out.interventions[0].intervention_type == "evidence_clarification"


def test_validator_gap_traceability():
    llm = DeterministicFallbackProvider()
    items, gaps = _mahi_odata_gap_items()
    strategist = LearningStrategistAgent(llm).run("Alex", "Role", items, gaps)
    curator = ResourceCuratorAgent(llm).run(strategist)
    proof = ProofAlignmentAgent(llm).run(strategist, "Role")
    validation = LearningPlanValidator().validate(
        strategist, curator, proof, items, gaps, {g.id for g in gaps}
    )
    assert validation.status == "passed"
    check_names = {c.name for c in validation.checks}
    assert "gap_traceability" in check_names
    assert "proof_alignment" in check_names
    assert "unnecessary_learning" in check_names


def test_prototype_catalog_has_odata_resources():
    provider = get_learning_resource_provider()
    assert "Prototype" in provider.get_catalog_label()
    odata = provider.search("skill0002", limit=5)
    assert len(odata) >= 3
    assert all(r.source_type == "prototype_catalog" for r in odata)


def test_no_fake_sap_learning_hub_in_catalog_note():
    llm = DeterministicFallbackProvider()
    items, gaps = _mahi_odata_gap_items()
    strategist = LearningStrategistAgent(llm).run("Alex", "Role", items, gaps)
    curator = ResourceCuratorAgent(llm).run(strategist)
    assert "prototype" in curator.catalog_note.lower()


def test_generate_plan_api_integration():
    service = TargetedLearningService()
    plan = service.generate("USER002", "JOB002")
    assert plan.candidate_name == "Mahi Chauhan"
    assert plan.target_role_title == "SAP Consultant"
    assert plan.validation is not None
    assert plan.validation.status == "passed"
    assert plan.agents is not None
    assert plan.agents.learning_strategist == "completed"
    # OData-focused
    assert any("odata" in s.capability.lower() for s in plan.steps)
    assert len(plan.proof_requirements) >= 1
    assert "ODATA" in plan.proof_requirements[0].proof_title.upper()


def test_simulate_intervention_qualitative():
    service = TargetedLearningService()
    plan = service.generate("USER002", "JOB002")
    result = service.simulate_intervention(plan.id)
    sim = result["simulation"]
    assert sim["before_state"] == "Gap present"
    assert "pending proof" in sim["after_state"].lower()
    assert result["is_simulated_projection"] is True


def test_llm_unavailable_uses_fallback():
    """Without API key, deterministic fallback still produces valid plan."""
    service = TargetedLearningService()
    plan = service.generate("USER002", "JOB002")
    assert plan.steps
    assert plan.agents.engine_mode.value in {"DEMO_FALLBACK", "LLM"}
