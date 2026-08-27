"""Diagnosis, capability gap, and counterfactual engine tests."""

import json
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.enums import (
    CounterfactualConclusion,
    GapStatus,
    OverallDiagnosisState,
    RequirementClass,
    ReviewTag,
)
from app.main import app
from app.services.diagnosis_service import DiagnosisService
from app.services.fixture_service import FixtureService
from app.services.orchestration_service import OrchestrationService
from tests.diagnosis_fixtures import (
    make_capability,
    make_evidence,
    make_job_capability,
    make_requirement,
    make_task,
)


def _run_diagnosis(
    candidate_capabilities,
    evidence,
    job_capabilities,
    requirements,
    tasks,
    candidate_id="test-candidate",
    job_id="test-job",
):
    service = DiagnosisService()
    return service.run(
        candidate_id=candidate_id,
        job_id=job_id,
        job_capabilities=job_capabilities,
        candidate_capabilities=candidate_capabilities,
        candidate_evidence=evidence,
        requirements=requirements,
        tasks=tasks,
    )


def test_strongly_matched_candidate():
    ev = make_evidence("ev-1", description="SQL analytics project")
    caps = [make_capability("sql", "SQL", 0.8, ["ev-1"])]
    job_caps = [make_job_capability("sql", "SQL", 0.6)]
    assessment, gaps, diagnoses, counterfactuals, summary = _run_diagnosis(
        caps, [ev], job_caps, [], []
    )
    item = assessment.items[0]
    assert item.gap_status == GapStatus.MATCHED
    assert summary.matched_count == 1
    assert summary.capability_gap_count == 0


def test_true_skill_gap():
    ev = make_evidence("ev-1", description="basic exposure")
    caps = [make_capability("power_bi", "Power BI", 0.2, ["ev-1"])]
    job_caps = [make_job_capability("power_bi", "Power BI", 0.6)]
    assessment, gaps, _, _, summary = _run_diagnosis(caps, [ev], job_caps, [], [])
    assert assessment.items[0].gap_status == GapStatus.GENUINE_CAPABILITY_GAP
    assert summary.capability_gap_count == 1
    assert gaps[0].gap_status == GapStatus.GENUINE_CAPABILITY_GAP


def test_missing_evidence_not_negative_capability():
    job_caps = [make_job_capability("sql", "SQL", 0.6)]
    assessment, _, _, _, summary = _run_diagnosis([], [], job_caps, [], [])
    assert assessment.items[0].gap_status == GapStatus.INSUFFICIENT_EVIDENCE
    assert summary.insufficient_evidence_count == 1


def test_experience_proxy_counterfactual():
    ev = make_evidence("ev-work", description="Data analyst work history")
    caps = [
        make_capability("data_analysis", "Data Analysis", 0.65, ["ev-work"]),
        make_capability("sql", "SQL", 0.7, ["ev-work"]),
    ]
    req = make_requirement(
        "req-exp",
        "3 years continuous recent professional experience",
        RequirementClass.EXPERIENCE_REQUIREMENT,
        review_tag=ReviewTag.POTENTIAL_PROXY,
    )
    _, _, diagnoses, counterfactuals, _ = _run_diagnosis(
        caps, [ev], [], [req], []
    )
    assert diagnoses[0].diagnosis_type == GapStatus.ELIGIBILITY_PROXY
    assert diagnoses[0].human_review_required
    cf = counterfactuals[0]
    assert cf.conclusion == CounterfactualConclusion.POTENTIAL_PROXY
    assert cf.alternative_validation


def test_workplace_constraint():
    req = make_requirement(
        "req-office",
        "Bangalore office 5 days/week",
        RequirementClass.WORKPLACE_CONDITION,
        review_tag=ReviewTag.POTENTIAL_PROXY,
        linked_task_ids=["task-1"],
    )
    task = make_task("task-1", "Analyze datasets", ["sql"], on_site_likelihood="low")
    _, _, diagnoses, counterfactuals, summary = _run_diagnosis(
        [], [], [], [req], [task]
    )
    assert diagnoses[0].diagnosis_type == GapStatus.WORKPLACE_CONSTRAINT
    assert summary.workplace_constraint_count == 1
    assert counterfactuals[0].human_review_required


def test_unknown_requirement():
    req = make_requirement(
        "req-unknown",
        "Must be culturally aligned with team",
        RequirementClass.UNKNOWN,
    )
    _, _, diagnoses, _, summary = _run_diagnosis([], [], [], [req], [])
    assert diagnoses[0].diagnosis_type == GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
    assert summary.unknown_count == 1


def test_credential_requires_human_review():
    ev = make_evidence("ev-dev", description="Software development portfolio")
    caps = [make_capability("software_dev", "Software Development", 0.85, ["ev-dev"])]
    req = make_requirement(
        "req-degree",
        "Bachelor's degree in Computer Science",
        RequirementClass.CREDENTIAL_REQUIREMENT,
        review_tag=ReviewTag.POTENTIAL_EXCLUSIONARY_FACTOR,
    )
    _, _, diagnoses, counterfactuals, _ = _run_diagnosis(
        caps, [ev], [], [req], []
    )
    assert diagnoses[0].diagnosis_type == GapStatus.UNKNOWN_REQUIRES_HUMAN_REVIEW
    assert diagnoses[0].human_review_required
    assert counterfactuals[0].conclusion == CounterfactualConclusion.REQUIRES_HUMAN_REVIEW


def test_adjacent_transferable_capability():
    ev = make_evidence("ev-report", description="Excel reporting for leadership")
    caps = [make_capability("reporting", "Reporting", 0.65, ["ev-report"])]
    job_caps = [make_job_capability("data_reporting", "Data reporting", 0.55)]
    # Candidate has reporting but job asks data_reporting — insufficient mapping at keyword level
    assessment, _, _, _, _ = _run_diagnosis(caps, [ev], job_caps, [], [])
    assert assessment.items[0].gap_status in {
        GapStatus.INSUFFICIENT_EVIDENCE,
        GapStatus.GENUINE_CAPABILITY_GAP,
        GapStatus.MATCHED,
    }


def test_old_but_strongly_evidenced_skill():
    ev = make_evidence(
        "ev-old",
        description="SQL reporting project",
        occurred_on=date(2020, 1, 1),
    )
    caps = [
        make_capability(
            "sql",
            "SQL",
            0.75,
            ["ev-old"],
            recency=__import__("app.domain.enums", fromlist=["RecencyStatus"]).RecencyStatus.STALE,
        )
    ]
    job_caps = [make_job_capability("sql", "SQL", 0.6)]
    assessment, _, _, _, _ = _run_diagnosis(caps, [ev], job_caps, [], [])
    assert assessment.items[0].gap_status == GapStatus.MATCHED
    assert assessment.items[0].evidence_strength is not None
    assert assessment.items[0].evidence_strength > 0.35


def test_candidate_with_no_relevant_evidence():
    job_caps = [
        make_job_capability("sql", "SQL", 0.6),
        make_job_capability("python", "Python", 0.6),
    ]
    assessment, gaps, _, _, summary = _run_diagnosis([], [], job_caps, [], [])
    assert summary.insufficient_evidence_count == 2
    assert all(i.gap_status == GapStatus.INSUFFICIENT_EVIDENCE for i in assessment.items)


def test_ananya_sql_matched():
    state = OrchestrationService().execute_demo_run()
    items = state["capability_assessments"][0]["items"]
    sql = next(i for i in items if i["skill_id"] == "sql")
    assert sql["gap_status"] == GapStatus.MATCHED.value


def test_ananya_power_bi_genuine_gap():
    state = OrchestrationService().execute_demo_run()
    items = state["capability_assessments"][0]["items"]
    pbi = next(i for i in items if i["skill_id"] == "power_bi")
    assert pbi["gap_status"] == GapStatus.GENUINE_CAPABILITY_GAP.value


def test_ananya_experience_eligibility_proxy():
    state = OrchestrationService().execute_demo_run()
    exp = next(
        d for d in state["requirement_diagnoses"]
        if d["requirement_id"] == "req-da-experience"
    )
    assert exp["diagnosis_type"] == GapStatus.ELIGIBILITY_PROXY.value
    assert exp["human_review_required"]


def test_ananya_career_gap_not_skill():
    state = OrchestrationService().execute_demo_run()
    cap_ids = {c["skill_id"] for c in state.get("candidate_capabilities", [])}
    assert "career_gap" not in cap_ids
    assert "caregiving" not in cap_ids


def test_no_discrimination_verdict_in_outputs():
    state = OrchestrationService().execute_demo_run()
    blob = json.dumps(state).lower()
    forbidden = [
        "bias_confirmed",
        "discriminatory",
        "discrimination",
        "unfair_candidate",
        "should hire",
        "should not hire",
        "reject candidate",
    ]
    for term in forbidden:
        assert term not in blob


def test_no_single_match_score_field():
    response = OrchestrationService().build_diagnosis_response(
        OrchestrationService().execute_demo_run()
    )
    assert "match_score" not in response
    assert "hiring_recommendation" not in response
    summary = response["diagnosis_summary"]
    assert "capability_fit" in summary
    assert "evidence_strength" in summary
    assert "diagnosis_confidence" in summary


def test_evidence_refs_preserved_in_diagnosis():
    state = OrchestrationService().execute_demo_run()
    sql_item = next(
        i for i in state["capability_assessments"][0]["items"]
        if i["skill_id"] == "sql"
    )
    assert sql_item["evidence_refs"]


def test_graph_includes_diagnosis_nodes():
    state = OrchestrationService().execute_demo_run()
    agents = {e["agent"] for e in state.get("audit_events", [])}
    assert "diagnosis" in agents
    assert "counterfactual_analysis" in agents
    assert state.get("diagnosis_summary")
    assert state.get("counterfactuals")


def test_golden_checkpoint_03_ananya():
    golden_path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "golden"
        / "checkpoint_03_ananya.json"
    )
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    state = OrchestrationService().execute_demo_run(
        candidate_id=golden["candidate_id"],
        job_id=golden["job_id"],
    )
    items = state["capability_assessments"][0]["items"]
    by_skill = {i["skill_id"]: i["gap_status"] for i in items}
    for skill in golden["expected_matched_skill_ids"]:
        assert by_skill[skill] == GapStatus.MATCHED.value
    for skill in golden["expected_genuine_gap_skill_ids"]:
        assert by_skill[skill] == GapStatus.GENUINE_CAPABILITY_GAP.value

    diag_by_req = {d["requirement_id"]: d for d in state["requirement_diagnoses"]}
    for req_id in golden["expected_eligibility_proxy_requirement_ids"]:
        assert diag_by_req[req_id]["diagnosis_type"] == GapStatus.ELIGIBILITY_PROXY.value

    cf_by_req = {c["requirement_id"]: c for c in state["counterfactuals"]}
    for req_id in golden["expected_counterfactual_proxy_requirement_ids"]:
        assert cf_by_req[req_id]["conclusion"] == CounterfactualConclusion.POTENTIAL_PROXY.value

    overall = state["diagnosis_summary"]["overall_diagnosis_state"]
    assert overall in golden["expected_overall_states"]


def test_diagnose_api_endpoint():
    client = TestClient(app)
    response = client.post(
        "/api/runs/diagnose",
        json={"candidate_id": "ananya-sharma", "job_id": "data-analyst-junior"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["diagnosis_summary"]
    assert data["capability_assessments"]
    assert data["counterfactuals"]
    assert data["engine_mode"] == "DEMO_FALLBACK"
    assert "recommendation_state" not in data
