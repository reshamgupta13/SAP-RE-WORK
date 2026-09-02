"""Map canonical RE:WORK case data onto the seven conceptual SAP domains.

These names describe the intended SAP table foundation. They are not live
OData entity sets. LIVE is never claimed from this mapping.
"""

from __future__ import annotations

from typing import Any

from app.adapters.sap.health import SAPHealthService
from app.adapters.sap.odata_config import build_access_plan
from app.services.fixture_service import FixtureService

PENDING = "PENDING_OFFICIAL_ODATA_METADATA"

# Conceptual SAP table names — product mapping only, never shown as live entities.
TABLE_CANDIDATE = "ZREWORK_USER"
TABLE_SKILL = "ZREWORK_SKILL"
TABLE_PERSON_SKILL = "ZREWORK_PERSKILL"
TABLE_JOB = "ZREWORK_JOB"
TABLE_JOB_SKILL = "ZREWORK_JOB_SKIL"
TABLE_ORG = "ZREWORK_ORGANIZA"
TABLE_HR = "ZREWORK_HR"


class EnterpriseDomainService:
    """Presentation mapping from existing fixtures + case snapshot. No new diagnosis."""

    def __init__(self) -> None:
        self._fixtures = FixtureService()

    def build(
        self,
        state: dict[str, Any] | None = None,
        sap_health: dict[str, Any] | None = None,
        *,
        allow_demo_fallback: bool = True,
    ) -> dict[str, Any]:
        snapshot = state or {}
        health = sap_health if sap_health is not None else SAPHealthService().check()
        source_mode = health.get("source_mode") or snapshot.get("source_mode") or "SIMULATED"
        if source_mode == "LIVE" and not health.get("healthy") and not health.get("live_verified"):
            source_mode = health.get("source_mode", "NOT_CONNECTED")

        bundle = self._fixtures.get_ananya_bundle() if allow_demo_fallback else None
        profile = snapshot.get("candidate")
        if profile is None and bundle is not None:
            profile = bundle["profile"].model_dump(mode="json")
        profile = profile or {}
        evidence = snapshot.get("candidate_evidence")
        if evidence is None and bundle is not None:
            evidence = [e.model_dump(mode="json") for e in bundle["evidence"]]
        evidence = evidence or []
        capabilities = snapshot.get("updated_candidate_capabilities") or snapshot.get("candidate_capabilities")
        if capabilities is None and bundle is not None:
            capabilities = [c.model_dump(mode="json") for c in bundle["capabilities"]]
        capabilities = capabilities or []
        job = snapshot.get("job")
        if job is None and bundle is not None:
            job = self._fixtures.get_data_analyst_job().model_dump(mode="json")
        job = job or {}
        catalog = {"opportunities": snapshot.get("opportunities") or []}
        if allow_demo_fallback:
            catalog = self._fixtures.get_opportunity_catalog_bundle()
        self._allow_demo_fallback = allow_demo_fallback
        assessments = []
        cap_assess = snapshot.get("capability_assessments") or []
        if cap_assess:
            assessments = cap_assess[0].get("items") or []

        candidate = self._map_candidate(profile, evidence)
        skills = self._map_skills(capabilities, job)
        person_skills = self._map_person_skills(capabilities, evidence, assessments)
        jobs = self._map_jobs(job, catalog)
        job_skills = self._map_job_skills(job, catalog)
        organizations = self._map_organizations(job, catalog)
        hr = self._map_hr()
        fit_rows = self._map_fit_rows(assessments, snapshot.get("requirement_diagnoses") or [])
        proof_delta = self._map_proof_delta(snapshot)

        domains = {
            "candidate": candidate,
            "skills": skills,
            "person_skills": person_skills,
            "jobs": jobs,
            "job_skills": job_skills,
            "organizations": organizations,
            "hr_reviewer": hr,
        }

        return {
            "source_mode": source_mode,
            "odata_status": self._odata_status(health, source_mode),
            "write_operations": {
                "available": False,
                "reason": "OData CREATE/UPDATE/DELETE require a verified live service.",
                "csrf_required_when_live": True,
            },
            "domains": domains,
            "capability_fit": fit_rows,
            "proof_delta": proof_delta,
            "sap_trace": self._trace(domains, source_mode, health),
            "access_plan": build_access_plan().to_dict(),
        }

    def _odata_status(self, health: dict[str, Any], source_mode: str) -> dict[str, Any]:
        live = source_mode == "LIVE" and bool(health.get("healthy") or health.get("live_verified"))
        return {
            "label": self._status_label(source_mode, live),
            "source_mode": source_mode,
            "live_verified": live,
            "service": health.get("system_name") or None,
            "metadata_accessible": bool(health.get("metadata_accessible")),
            "entity_mappings": PENDING,
        }

    @staticmethod
    def _status_label(source_mode: str, live: bool) -> str:
        if live:
            return "SAP • LIVE • VERIFIED"
        if source_mode == "NOT_CONNECTED":
            return "SAP • NOT CONNECTED"
        if source_mode == "ERROR":
            return "SAP • ERROR"
        return "SAP • SIMULATED"

    def _map_candidate(self, profile: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        name = str(profile.get("display_name") or profile.get("name") or "")
        parts = name.split(None, 1)
        first = parts[0] if parts else None
        last = parts[1] if len(parts) > 1 else None
        work = next((e for e in evidence if e.get("type") == "WORK_HISTORY"), None)
        return {
            "user_id": profile.get("id") or profile.get("sap_user_id"),
            "first_name": first,
            "last_name": last,
            "current_role": (work or {}).get("title"),
            "education": None,
            "target_career": profile.get("career_aspiration"),
            "location": profile.get("location"),
            "work_modes": profile.get("work_modes") or [],
            "profile_status": "DEMO" if profile.get("is_demo_persona") else "ACTIVE",
            "created_on": profile.get("created_at"),
            "last_updated": profile.get("updated_at"),
            "notes": profile.get("notes"),
            "source_mode": profile.get("source_mode", "SYNTHETIC"),
            "email": None,
            "phone": None,
            "experience_years": None,
        }

    def _map_skills(self, capabilities: list[dict[str, Any]], job: dict[str, Any]) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        for cap in capabilities:
            sid = str(cap.get("skill_id"))
            if sid not in seen:
                seen[sid] = {
                    "skill_id": sid,
                    "skill_name": cap.get("label") or sid,
                    "description": None,
                    "source_mode": cap.get("source_mode", "SYNTHETIC"),
                }
        for jcap in job.get("capabilities") or []:
            sid = str(jcap.get("skill_id"))
            if sid not in seen:
                seen[sid] = {
                    "skill_id": sid,
                    "skill_name": jcap.get("label") or sid,
                    "description": jcap.get("evidence_expectation"),
                    "source_mode": jcap.get("source_mode", "SYNTHETIC"),
                }
            elif not seen[sid].get("description"):
                seen[sid]["description"] = jcap.get("evidence_expectation")
        return list(seen.values())

    def _map_person_skills(
        self,
        capabilities: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
        assessments: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        evidence_by_id = {e.get("id"): e for e in evidence}
        assess_by_skill = {a.get("skill_id"): a for a in assessments}
        rows = []
        for cap in capabilities:
            sid = cap.get("skill_id")
            linked = []
            for ref in cap.get("evidence_refs") or []:
                ev = evidence_by_id.get(ref)
                if ev:
                    linked.append(
                        {
                            "id": ev.get("id"),
                            "title": ev.get("title"),
                            "type": ev.get("type"),
                            "verification_status": ev.get("verification_status"),
                            "description": ev.get("description"),
                            "occurred_on": ev.get("occurred_on"),
                            "source_mode": ev.get("source_mode"),
                            "confidence": ev.get("confidence"),
                        }
                    )
            assess = assess_by_skill.get(sid) or {}
            rows.append(
                {
                    "user_id": cap.get("candidate_id"),
                    "skill_id": sid,
                    "skill_name": cap.get("label") or sid,
                    "proficiency": cap.get("proficiency"),
                    "confidence": cap.get("confidence"),
                    "verification_status": cap.get("verification_status"),
                    "inference_status": cap.get("inference_status"),
                    "valid_from": cap.get("recency"),
                    "valid_to": None,
                    "recency_status": assess.get("recency_status") or cap.get("recency_status"),
                    "gap_status": assess.get("gap_status"),
                    "evidence": linked,
                    "source_mode": cap.get("source_mode", "SYNTHETIC"),
                }
            )
        return rows

    def _map_jobs(self, job: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = [
            {
                "job_id": job.get("id"),
                "job_name": job.get("title"),
                "job_description": job.get("raw_text"),
                "org_unit_id": job.get("family") or job.get("org_unit_id"),
                "location": job.get("location"),
                "family": job.get("family"),
                "level": job.get("level"),
                "work_modes": job.get("work_modes") or [],
                "valid_from": job.get("created_at"),
                "valid_to": None,
                "is_target": True,
                "source_mode": job.get("source_mode", "SYNTHETIC"),
                "required_skill_count": len(job.get("capabilities") or []),
                "mandatory_skill_count": sum(
                    1 for c in job.get("capabilities") or [] if c.get("importance") == "core"
                ),
            }
        ]
        seen = {job.get("id")}
        for opp in catalog.get("opportunities") or []:
            jid = opp.get("job_id")
            if jid in seen:
                continue
            seen.add(jid)
            skills = opp.get("capability_skill_ids") or []
            jobs.append(
                {
                    "job_id": jid,
                    "job_name": opp.get("title"),
                    "job_description": None,
                    "org_unit_id": opp.get("family"),
                    "location": opp.get("location"),
                    "family": opp.get("family"),
                    "level": None,
                    "work_modes": opp.get("work_modes") or [],
                    "valid_from": opp.get("created_at"),
                    "valid_to": None,
                    "is_target": False,
                    "source_mode": opp.get("source_mode", "SYNTHETIC"),
                    "required_skill_count": len(skills),
                    "mandatory_skill_count": len(skills),
                    "opportunity_id": opp.get("id"),
                }
            )
        return jobs

    def _map_job_skills(self, job: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
        rows = []
        for jcap in job.get("capabilities") or []:
            rows.append(
                {
                    "job_id": jcap.get("job_id") or job.get("id"),
                    "skill_id": jcap.get("skill_id"),
                    "skill_name": jcap.get("label"),
                    "required_proficiency": jcap.get("min_proficiency"),
                    "is_mandatory": jcap.get("importance") == "core",
                    "evidence_expectation": jcap.get("evidence_expectation"),
                    "source_mode": jcap.get("source_mode", "SYNTHETIC"),
                }
            )
        existing = {(r["job_id"], r["skill_id"]) for r in rows}
        for opp in catalog.get("opportunities") or []:
            jid = opp.get("job_id")
            mins = opp.get("min_proficiency") or {}
            for sid, req in mins.items():
                key = (jid, sid)
                if key in existing:
                    continue
                rows.append(
                    {
                        "job_id": jid,
                        "skill_id": sid,
                        "skill_name": sid,
                        "required_proficiency": req,
                        "is_mandatory": True,
                        "evidence_expectation": None,
                        "source_mode": opp.get("source_mode", "SYNTHETIC"),
                    }
                )
                existing.add(key)
        return rows

    def _map_organizations(self, job: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
        family = job.get("family") or "analytics"
        return [
            {
                "org_unit_id": "shared-services",
                "org_unit_name": "Shared Services",
                "parent_org_unit": None,
                "source_mode": "SYNTHETIC",
            },
            {
                "org_unit_id": family,
                "org_unit_name": str(family).replace("_", " ").title(),
                "parent_org_unit": "shared-services",
                "location": job.get("location"),
                "source_mode": job.get("source_mode", "SYNTHETIC"),
            },
        ]

    def _map_hr(self) -> dict[str, Any]:
        if not getattr(self, "_allow_demo_fallback", True):
            return {}
        return {
            "hr_id": "hr-demo-reviewer",
            "hr_name": "Demo Talent Reviewer",
            "hr_role": "Talent Reviewer",
            "hr_org_id": "analytics",
            "hr_access_level": "REVIEW",
            "hr_location": "India",
            "hr_status": "ACTIVE",
            "source_mode": "SYNTHETIC",
        }

    def _map_fit_rows(
        self,
        assessments: list[dict[str, Any]],
        requirement_diagnoses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        skill_rows = []
        for item in assessments:
            skill_rows.append(
                {
                    "skill_id": item.get("skill_id"),
                    "skill_name": item.get("label") or item.get("skill_id"),
                    "candidate_proficiency": item.get("candidate_proficiency"),
                    "required_proficiency": item.get("required_proficiency"),
                    "gap_status": item.get("gap_status"),
                    "rationale": item.get("rationale"),
                    "evidence_refs": item.get("evidence_refs") or [],
                    "kind": "capability",
                }
            )
        review_rows = []
        for req in requirement_diagnoses:
            dtype = req.get("diagnosis_type") or req.get("gap_status")
            if dtype in {"ELIGIBILITY_PROXY", "WORKPLACE_CONSTRAINT", "UNKNOWN_REQUIRES_HUMAN_REVIEW"}:
                review_rows.append(
                    {
                        "requirement_text": req.get("requirement_text") or req.get("text"),
                        "diagnosis_type": dtype,
                        "review_tag": req.get("review_tag"),
                        "rationale": req.get("rationale"),
                        "kind": "requirement",
                    }
                )
        return {"skills": skill_rows, "requirements": review_rows}

    def _map_proof_delta(self, snapshot: dict[str, Any]) -> dict[str, Any] | None:
        proof = snapshot.get("proof_result")
        if not proof:
            return None
        return {
            "skill_id": proof.get("skill_id"),
            "result": proof.get("result"),
            "total": proof.get("total"),
            "is_demo": proof.get("is_demo", True),
            "source_mode": proof.get("source_mode", "SYNTHETIC"),
            "message": "New evidence changed the diagnosis." if proof.get("result") == "PASSED" else None,
        }

    def _trace(self, domains: dict[str, Any], source_mode: str, health: dict[str, Any]) -> list[dict[str, Any]]:
        counts = {
            TABLE_CANDIDATE: 1 if domains.get("candidate") else 0,
            TABLE_SKILL: len(domains.get("skills") or []),
            TABLE_PERSON_SKILL: len(domains.get("person_skills") or []),
            TABLE_JOB: len(domains.get("jobs") or []),
            TABLE_JOB_SKILL: len(domains.get("job_skills") or []),
            TABLE_ORG: len(domains.get("organizations") or []),
            TABLE_HR: 1 if domains.get("hr_reviewer") else 0,
        }
        rows = [
            (TABLE_CANDIDATE, "Candidate", "CandidateProfile", "Candidate Intelligence"),
            (TABLE_SKILL, "Capability catalog", "Skill", "Candidate Intelligence"),
            (TABLE_PERSON_SKILL, "Candidate skills", "CandidateCapability", "Candidate Intelligence"),
            (TABLE_JOB, "Job", "JobProfile", "Job Decomposition"),
            (TABLE_JOB_SKILL, "Job requirements", "JobCapability", "Job Decomposition"),
            (TABLE_ORG, "Organization", "OrgContext", "Employer Readiness"),
            (TABLE_HR, "HR reviewer", "HumanReview", "Human Review"),
        ]
        return [
            {
                "sap_table": table,
                "product_label": label,
                "odata_entity": PENDING,
                "odata_method": "GET_ENTITYSET",
                "rework_model": model,
                "agent": agent,
                "record_count": counts[table],
                "source_mode": source_mode,
                "service": health.get("system_name"),
            }
            for table, label, model, agent in rows
        ]
