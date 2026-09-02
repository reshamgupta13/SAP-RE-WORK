"""Prototype catalog for domains not yet wired to SAP OData.

Used when skills are LIVE but USER/JOB services are not configured yet.
Keeps the product workspace usable without Ananya demo fixtures.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domain.enums import SourceMode

_SOURCE = SourceMode.MOCKED.value

_CANDIDATES: list[dict[str, Any]] = [
    {
        "USER_ID": "USER001",
        "FIRST_NAME": "Shivansh",
        "LAST_NAME": "Gupta",
        "CURRENT_ROLE": "Software Engineer",
        "EDUCATION": "B.Tech Computer Science",
        "TARGET_CAREER": "AI Engineer",
        "EXPERIENCE_YEARS": 3,
        "LOCATION": "Chico, CA",
        "PROFILE_STATUS": "ACTIVE",
    },
    {
        "USER_ID": "USER002",
        "FIRST_NAME": "Mahi",
        "LAST_NAME": "Chauhan",
        "CURRENT_ROLE": "SAP Associate",
        "EDUCATION": "B.S. Information Systems",
        "TARGET_CAREER": "SAP Consultant",
        "EXPERIENCE_YEARS": 2,
        "LOCATION": "Sacramento, CA",
        "PROFILE_STATUS": "ACTIVE",
    },
    {
        "USER_ID": "USER003",
        "FIRST_NAME": "Resham",
        "LAST_NAME": "Gupta",
        "CURRENT_ROLE": "Junior Developer",
        "EDUCATION": "B.S. Computer Science",
        "TARGET_CAREER": "Full Stack Developer",
        "EXPERIENCE_YEARS": 2,
        "LOCATION": "Remote",
        "PROFILE_STATUS": "ACTIVE",
    },
]

_JOBS: list[dict[str, Any]] = [
    {
        "JOB_ID": "JOB001",
        "JOB_NAME": "AI Engineer",
        "JOB_DESCRIPTION": "Build AI-ready data pipelines and models on SAP HANA and enterprise Java services.",
        "ORG_UNIT_ID": "ORG001",
        "LOCATION": "Chico, CA",
        "VALID_FROM": "2026-01-01",
        "VALID_TO": "9999-12-31",
    },
    {
        "JOB_ID": "JOB002",
        "JOB_NAME": "SAP Consultant",
        "JOB_DESCRIPTION": "Advise clients on SAP solutions, OData integrations, and workforce capability alignment.",
        "ORG_UNIT_ID": "ORG002",
        "LOCATION": "Hybrid",
        "VALID_FROM": "2026-01-01",
        "VALID_TO": "9999-12-31",
    },
    {
        "JOB_ID": "JOB003",
        "JOB_NAME": "Full Stack Developer",
        "JOB_DESCRIPTION": "Develop end-to-end enterprise applications with Java, SQL, and SAP OData services.",
        "ORG_UNIT_ID": "ORG001",
        "LOCATION": "Remote",
        "VALID_FROM": "2026-01-01",
        "VALID_TO": "9999-12-31",
    },
]

_PERSON_SKILLS: list[dict[str, Any]] = [
    {"USER_ID": "USER001", "SKILL_ID": "SKILL0001", "PROFICIENCY": 4, "EVIDENCE": "Java backend projects and API development", "VALID_FROM": "2025-06-01"},
    {"USER_ID": "USER001", "SKILL_ID": "SKILL0005", "PROFICIENCY": 4, "EVIDENCE": "SQL analytics and reporting labs", "VALID_FROM": "2025-03-01"},
    {"USER_ID": "USER001", "SKILL_ID": "SKILL0004", "PROFICIENCY": 2, "EVIDENCE": "Introductory HANA workshop only — not demonstrated in production", "VALID_FROM": "2026-01-10"},
    {"USER_ID": "USER002", "SKILL_ID": "SKILL0003", "PROFICIENCY": 4, "EVIDENCE": "SAP fundamentals certification and module configuration labs", "VALID_FROM": "2025-08-01"},
    {"USER_ID": "USER002", "SKILL_ID": "SKILL0001", "PROFICIENCY": 3, "EVIDENCE": "Java coursework for integration projects", "VALID_FROM": "2025-05-01"},
    {"USER_ID": "USER002", "SKILL_ID": "SKILL0002", "PROFICIENCY": 2, "EVIDENCE": "Self-reported OData exposure — not demonstrated with working services", "VALID_FROM": "2026-01-15"},
    {"USER_ID": "USER003", "SKILL_ID": "SKILL0001", "PROFICIENCY": 4, "EVIDENCE": "Full stack Java applications and REST APIs", "VALID_FROM": "2025-07-01"},
    {"USER_ID": "USER003", "SKILL_ID": "SKILL0005", "PROFICIENCY": 4, "EVIDENCE": "Database design and SQL optimization projects", "VALID_FROM": "2025-04-01"},
    {"USER_ID": "USER003", "SKILL_ID": "SKILL0002", "PROFICIENCY": 2, "EVIDENCE": "Basic OData tutorial — no hands-on CRUD service evidence", "VALID_FROM": "2026-02-01"},
]

_JOB_SKILLS: list[dict[str, Any]] = [
    {"JOB_ID": "JOB001", "SKILL_ID": "SKILL0001", "REQUIRED_PROFICIENCY": 0.75, "IS_MANDATORY": True},
    {"JOB_ID": "JOB001", "SKILL_ID": "SKILL0005", "REQUIRED_PROFICIENCY": 0.7, "IS_MANDATORY": True},
    {"JOB_ID": "JOB001", "SKILL_ID": "SKILL0004", "REQUIRED_PROFICIENCY": 0.65, "IS_MANDATORY": True},
    {"JOB_ID": "JOB002", "SKILL_ID": "SKILL0003", "REQUIRED_PROFICIENCY": 0.7, "IS_MANDATORY": True},
    {"JOB_ID": "JOB002", "SKILL_ID": "SKILL0002", "REQUIRED_PROFICIENCY": 0.7, "IS_MANDATORY": True},
    {"JOB_ID": "JOB003", "SKILL_ID": "SKILL0001", "REQUIRED_PROFICIENCY": 0.75, "IS_MANDATORY": True},
    {"JOB_ID": "JOB003", "SKILL_ID": "SKILL0005", "REQUIRED_PROFICIENCY": 0.7, "IS_MANDATORY": True},
    {"JOB_ID": "JOB003", "SKILL_ID": "SKILL0002", "REQUIRED_PROFICIENCY": 0.65, "IS_MANDATORY": True},
]

_ORGANIZATIONS: list[dict[str, Any]] = [
    {"ORG_UNIT_ID": "ORG001", "ORG_UNIT_NAME": "Enterprise Integration", "PARENT_ORG_ID": None},
    {"ORG_UNIT_ID": "ORG002", "ORG_UNIT_NAME": "SAP Practice", "PARENT_ORG_ID": None},
]

_HR: list[dict[str, Any]] = [
    {"HR_ID": "HR001", "HR_NAME": "Alex Rivera", "HR_ROLE": "Workforce Partner", "ORG_UNIT_ID": "ORG001"},
]


def fallback_enabled_for(domain: str, *, entity_configured: bool | None = None) -> bool:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.sap_prototype_fallback:
        return False
    allowed = {"user", "job", "person_skill", "job_skill", "organization", "hr", "skill"}
    if settings.sap_mode.upper() == "SIMULATED":
        return domain in allowed
    if settings.sap_mode.upper() != "LIVE":
        return False
    if entity_configured:
        return False
    return domain in allowed


_SKILLS: list[dict[str, Any]] = [
    {"SKILL_ID": "SKILL0001", "SKILL_NAME": "JAVA", "DESCRIPTION": "Java programming"},
    {"SKILL_ID": "SKILL0002", "SKILL_NAME": "ODATA", "DESCRIPTION": "SAP OData services"},
    {"SKILL_ID": "SKILL0003", "SKILL_NAME": "SAP", "DESCRIPTION": "SAP platform fundamentals"},
    {"SKILL_ID": "SKILL0004", "SKILL_NAME": "HANA", "DESCRIPTION": "SAP HANA database"},
    {"SKILL_ID": "SKILL0005", "SKILL_NAME": "SQL", "DESCRIPTION": "Structured query language"},
]


def list_raw_skills() -> list[dict[str, Any]]:
    return [dict(row) for row in _SKILLS]


def list_raw_candidates() -> list[dict[str, Any]]:
    return [dict(row) for row in _CANDIDATES]


def list_raw_jobs() -> list[dict[str, Any]]:
    return [dict(row) for row in _JOBS]


def get_raw_candidate(user_id: str) -> dict[str, Any] | None:
    return next((dict(row) for row in _CANDIDATES if row["USER_ID"] == user_id), None)


def get_raw_job(job_id: str) -> dict[str, Any] | None:
    return next((dict(row) for row in _JOBS if row["JOB_ID"] == job_id), None)


def list_raw_person_skills(*, user_id: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(row) for row in _PERSON_SKILLS]
    if user_id:
        rows = [row for row in rows if row["USER_ID"] == user_id]
    return rows


def list_raw_job_skills(*, job_id: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(row) for row in _JOB_SKILLS]
    if job_id:
        rows = [row for row in rows if row["JOB_ID"] == job_id]
    return rows


def list_raw_organizations() -> list[dict[str, Any]]:
    return [dict(row) for row in _ORGANIZATIONS]


def list_raw_hr() -> list[dict[str, Any]]:
    return [dict(row) for row in _HR]


def prototype_meta(domain: str) -> dict[str, Any]:
    return {
        "source_mode": _SOURCE,
        "prototype_fallback": True,
        "domain": domain,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
