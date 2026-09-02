"""Enterprise domain mapping — seven conceptual SAP tables, no fake LIVE."""

from app.services.enterprise_domain_service import PENDING, EnterpriseDomainService


def test_enterprise_context_seven_domains():
    ctx = EnterpriseDomainService().build()
    domains = ctx["domains"]
    assert set(domains) == {
        "candidate",
        "skills",
        "person_skills",
        "jobs",
        "job_skills",
        "organizations",
        "hr_reviewer",
    }
    assert ctx["source_mode"] != "LIVE"
    assert ctx["odata_status"]["live_verified"] is False
    assert "SIMULATED" in ctx["odata_status"]["label"]


def test_candidate_does_not_invent_contact_fields():
    candidate = EnterpriseDomainService().build()["domains"]["candidate"]
    assert candidate["email"] is None
    assert candidate["phone"] is None
    assert candidate["experience_years"] is None
    assert candidate["user_id"] == "ananya-sharma"
    assert candidate["first_name"] == "Ananya"


def test_person_skills_carry_evidence_not_frontend_math():
    rows = EnterpriseDomainService().build()["domains"]["person_skills"]
    sql = next(r for r in rows if r["skill_id"] == "sql")
    assert sql["proficiency"] == 0.62
    assert sql["evidence"]
    assert all("title" in e for e in sql["evidence"])


def test_job_skills_mark_core_as_mandatory():
    rows = EnterpriseDomainService().build()["domains"]["job_skills"]
    target = [r for r in rows if r["job_id"] == "data-analyst-junior"]
    assert target
    assert all(r["is_mandatory"] is True for r in target)


def test_trace_does_not_claim_live_entity_sets():
    traces = EnterpriseDomainService().build()["sap_trace"]
    assert traces
    assert all(t["odata_entity"] == PENDING for t in traces)
    assert all(t["odata_method"] == "GET_ENTITYSET" for t in traces)
    assert {t["sap_table"] for t in traces} == {
        "ZREWORK_USER",
        "ZREWORK_SKILL",
        "ZREWORK_PERSKILL",
        "ZREWORK_JOB",
        "ZREWORK_JOB_SKIL",
        "ZREWORK_ORGANIZA",
        "ZREWORK_HR",
    }


def test_write_operations_disabled_until_live():
    ctx = EnterpriseDomainService().build()
    assert ctx["write_operations"]["available"] is False


def test_enterprise_context_api():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    resp = client.get("/api/demo/enterprise-context")
    assert resp.status_code == 200
    body = resp.json()
    assert "domains" in body
    assert body["source_mode"] != "LIVE"
    cr = client.get("/api/demo/control-room").json()
    assert cr["enterprise_context"]["domains"]["candidate"]["user_id"] == "ananya-sharma"
