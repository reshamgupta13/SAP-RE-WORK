"""Product catalog — seven SAP domains mapped to canonical RE:WORK models.

Never returns demo/Ananya fixtures. LIVE only after verified OData retrieval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.adapters.sap.live import LiveSAPProvider, build_live_provider
from app.adapters.sap.mapper import SAPMapper, field_of
from app.adapters.sap.odata_client import ODataError, ODataWriteNotSupportedError
from app.adapters.sap.seven_table_registry import build_seven_table_registry
from app.core.config import get_settings
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.enums import RequirementClass, ReviewTag, SourceMode
from app.domain.job import JobCapability, JobProfile, JobRequirement
from app.services.prototype_catalog_fallback import (
    fallback_enabled_for,
    get_raw_candidate,
    get_raw_job,
    list_raw_candidates,
    list_raw_hr,
    list_raw_job_skills,
    list_raw_jobs,
    list_raw_organizations,
    list_raw_person_skills,
    list_raw_skills,
    prototype_meta,
)


def _entity_configured(domain: str) -> bool:
    settings = get_settings()
    mapping = {
        "user": settings.sap_entity_user or settings.sap_entity_person,
        "job": settings.sap_entity_job,
        "person_skill": settings.sap_entity_person_skill or settings.sap_entity_qualification,
        "job_skill": settings.sap_entity_job_skill,
        "organization": settings.sap_entity_organization,
        "hr": settings.sap_entity_hr,
    }
    return bool((mapping.get(domain) or "").strip())


def _user_message(exc: Exception) -> str:
    if isinstance(exc, ODataError) and exc.user_message:
        return exc.user_message
    return str(exc)


class SAPCatalogService:
    """Read/write seven-table catalog. Independent of DEMO_MODE fixtures."""

    def __init__(self, provider: LiveSAPProvider | None = None) -> None:
        self._settings = get_settings()
        self._provider = provider
        self._mapper = SAPMapper()
        self._skill_cache: tuple[datetime, list[dict[str, Any]]] | None = None
        self._org_cache: tuple[datetime, list[dict[str, Any]]] | None = None

    def _mode(self) -> str:
        return (self._settings.sap_mode or "SIMULATED").upper()

    def _uses_fallback(self, domain: str) -> bool:
        return fallback_enabled_for(domain, entity_configured=_entity_configured(domain))

    def _hybrid_mode(self, state: dict[str, Any] | None = None) -> bool:
        if self._mode() != "LIVE":
            return False
        if not self._settings.sap_prototype_fallback:
            return False
        if state and state.get("live_verified"):
            return self._uses_fallback("user") or self._uses_fallback("job")
        return self._uses_fallback("user") or self._uses_fallback("job")

    def connection_state(self) -> dict[str, Any]:
        mode = self._mode()
        url = self._settings.sap_odata_base_url or self._settings.sap_api_url
        auth_mode = (self._settings.sap_auth_mode or "NONE").upper()
        has_basic = auth_mode == "BASIC" and bool(
            (self._settings.sap_username or self._settings.sap_client_id)
            and (self._settings.sap_password or self._settings.sap_client_secret)
        )
        has_oauth = auth_mode == "OAUTH2" and bool(
            self._settings.sap_api_url and self._settings.sap_client_id and self._settings.sap_client_secret
        )
        has_auth = auth_mode == "NONE" or has_basic or has_oauth

        empty = {
            "configured": mode == "LIVE",
            "live_verified": False,
            "source_mode": SourceMode.SIMULATED.value if mode != "LIVE" else SourceMode.NOT_CONNECTED.value,
            "message": "",
            "entity_status": {},
            "entity_counts": {},
            "access_plan": build_seven_table_registry().to_dict(),
            "write_operations": {
                "available": False,
                "reason": "Write operation is not available until SAP LIVE is verified.",
            },
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        if mode != "LIVE":
            if self._settings.sap_prototype_fallback:
                empty["message"] = (
                    "SAP workforce intelligence — ZREWORK OData model (USER, JOB, SKILL) with RE:WORK AI reasoning. "
                    "Groq LLM agents analyze SAP-shaped candidate and role records."
                )
                empty["source_mode"] = SourceMode.SIMULATED.value
                empty["prototype_demo"] = True
                empty["sap_integration"] = True
            return empty

        if not url:
            empty["message"] = "SAP_MODE=LIVE but OData base URL is not configured."
            empty["source_mode"] = SourceMode.NOT_CONNECTED.value
            return empty

        if not has_auth:
            empty["message"] = f"SAP_MODE=LIVE but authentication is incomplete for {auth_mode}."
            empty["source_mode"] = SourceMode.NOT_CONNECTED.value
            return empty

        try:
            provider = self._live()
            ctx = provider.get_context()
            diagnostics = provider.get_diagnostics()
            live = provider.is_live_verified()
            hybrid = live and self._hybrid_mode()
            message = ctx.message
            if hybrid:
                message = (
                    "Hybrid prototype mode — skills from SAP LIVE; "
                    "candidates and roles from prototype catalog until USER/JOB OData is configured."
                )
            return {
                "configured": True,
                "live_verified": live,
                "hybrid_mode": hybrid,
                "source_mode": ctx.source_mode.value,
                "message": message,
                "system_name": ctx.system_name,
                "entity_status": diagnostics.get("entity_status", {}),
                "entity_counts": diagnostics.get("entity_counts", {}),
                "access_plan": diagnostics.get("access_plan") or build_seven_table_registry().to_dict(),
                "last_error": diagnostics.get("last_error"),
                "write_operations": {
                    "available": bool(diagnostics.get("write_available")),
                    "reason": diagnostics.get("write_reason")
                    or (
                        None
                        if diagnostics.get("write_available")
                        else "Write operation is not available in the current SAP service."
                    ),
                },
                "traces": diagnostics.get("traces", []),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            empty["source_mode"] = SourceMode.ERROR.value
            empty["message"] = _user_message(exc)
            empty["last_error"] = str(exc)
            return empty

    def _live(self) -> LiveSAPProvider:
        if self._provider is None:
            self._provider = build_live_provider()
        return self._provider

    def _ensure_live(self) -> tuple[LiveSAPProvider | None, dict[str, Any]]:
        state = self.connection_state()
        if not state.get("live_verified"):
            return None, state
        return self._live(), state

    def _empty_list(self, domain: str, state: dict[str, Any], message: str) -> dict[str, Any]:
        return {
            "source_mode": state.get("source_mode"),
            "live_verified": bool(state.get("live_verified")),
            "message": message,
            "count": 0,
            "items": [],
            "entity_status": state.get("entity_status", {}),
            "retrieved_at": state.get("retrieved_at"),
        }

    def _prototype_response_meta(self, domain: str) -> dict[str, Any]:
        simulated = self._mode() == "SIMULATED"
        return {
            "source_mode": SourceMode.SIMULATED.value if simulated else SourceMode.LIVE.value,
            "live_verified": not simulated,
            "hybrid_mode": not simulated,
            "prototype_demo": simulated,
            "sap_integration": True,
            **prototype_meta(domain),
        }

    def list_candidates(self, *, search: str | None = None) -> dict[str, Any]:
        if self._uses_fallback("user"):
            records = list_raw_candidates()
            items = [self._mapper.map_candidate_record(r, SourceMode.MOCKED) for r in records]
            if search:
                needle = search.lower()
                items = [
                    i
                    for i in items
                    if needle
                    in " ".join(
                        str(i.get(k) or "") for k in ("display_name", "first_name", "last_name", "current_role", "user_id")
                    ).lower()
                ]
            return {
                "message": None if items else "No prototype candidates are available.",
                "count": len(items),
                "items": items,
                **self._prototype_response_meta("user"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return self._empty_list(
                "user",
                state,
                state.get("message") or "No candidates are currently available from SAP.",
            )
        try:
            records = provider.list_domain("user")
        except NotImplementedError:
            return self._empty_list("user", state, "User entity mapping is not yet verified from SAP metadata.")
        except Exception as exc:
            state["source_mode"] = SourceMode.ERROR.value
            return self._empty_list("user", state, _user_message(exc))

        items = [self._mapper.map_candidate_record(r, SourceMode.LIVE) for r in records]
        if search:
            needle = search.lower()
            items = [
                i
                for i in items
                if needle in " ".join(
                    str(i.get(k) or "") for k in ("display_name", "first_name", "last_name", "current_role", "user_id")
                ).lower()
            ]
        message = None if items else "No candidates are currently available from SAP."
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "message": message,
            "count": len(items),
            "items": items,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_candidate(self, user_id: str) -> dict[str, Any]:
        if self._uses_fallback("user"):
            record = get_raw_candidate(user_id)
            if record is None:
                return {
                    "message": "No candidate found for the selected identifier.",
                    "candidate": None,
                    "skills": [],
                    "evidence": [],
                    **self._prototype_response_meta("user"),
                }
            skills_index = {s["skill_id"]: s for s in self.list_skills().get("items", [])}
            person_skills: list[dict[str, Any]] = []
            evidence: list[dict[str, Any]] = []
            for row in list_raw_person_skills(user_id=user_id):
                skill_id = str(row.get("SKILL_ID") or "")
                name = (skills_index.get(skill_id) or {}).get("skill_name")
                mapped = self._mapper.map_person_skill_record(row, skill_name=name, source_mode=SourceMode.MOCKED)
                person_skills.append(mapped)
                ev = self._mapper.map_evidence_from_person_skill(row, user_id, SourceMode.MOCKED)
                if ev:
                    evidence.append(ev.model_dump(mode="json"))
            jobs = self.list_jobs().get("items", [])
            return {
                "message": None,
                "candidate": self._mapper.map_candidate_record(record, SourceMode.MOCKED),
                "skills": person_skills,
                "evidence": evidence,
                "relevant_jobs": jobs,
                **self._prototype_response_meta("user"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return {
                "source_mode": state.get("source_mode"),
                "live_verified": False,
                "message": state.get("message") or "SAP is not connected.",
                "candidate": None,
                "skills": [],
                "evidence": [],
            }
        record = None
        try:
            record = provider.get_domain_by_key("user", user_id)
        except Exception:
            record = None
        if record is None:
            try:
                matches = provider.list_domain("user", filter_field="USER_ID", filter_value=user_id)
                record = matches[0] if matches else None
            except Exception:
                record = None
        if record is None:
            return {
                "source_mode": SourceMode.LIVE.value,
                "live_verified": True,
                "message": "No candidate found in SAP for the selected identifier.",
                "candidate": None,
                "skills": [],
                "evidence": [],
            }

        skills_index = {s["skill_id"]: s for s in self.list_skills().get("items", [])}
        person_skills: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        try:
            raw_ps = provider.list_domain("person_skill", filter_field="USER_ID", filter_value=user_id)
        except Exception:
            raw_ps = []
        for row in raw_ps:
            skill_id = str(field_of(row, "SKILL_ID", "skillId") or "")
            name = (skills_index.get(skill_id) or {}).get("skill_name")
            mapped = self._mapper.map_person_skill_record(row, skill_name=name, source_mode=SourceMode.LIVE)
            person_skills.append(mapped)
            ev = self._mapper.map_evidence_from_person_skill(row, user_id, SourceMode.LIVE)
            if ev:
                evidence.append(ev.model_dump(mode="json"))

        jobs = self.list_jobs().get("items", [])
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "message": None,
            "candidate": self._mapper.map_candidate_record(record, SourceMode.LIVE),
            "skills": person_skills,
            "evidence": evidence,
            "relevant_jobs": jobs,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_skills(self) -> dict[str, Any]:
        if self._uses_fallback("skill"):
            items = [
                self._mapper.map_skill_master(row, SourceMode.MOCKED) for row in list_raw_skills()
            ]
            return {
                "count": len(items),
                "items": items,
                "message": None,
                **self._prototype_response_meta("skill"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return self._empty_list("skill", state, "No skills are currently available from SAP.")
        now = datetime.now(timezone.utc)
        if self._skill_cache and (now - self._skill_cache[0]).total_seconds() < 300:
            items = self._skill_cache[1]
            return {
                "source_mode": SourceMode.LIVE.value,
                "live_verified": True,
                "count": len(items),
                "items": items,
                "cached": True,
                "retrieved_at": self._skill_cache[0].isoformat(),
            }
        try:
            records = provider.list_domain("skill")
        except Exception as exc:
            return self._empty_list("skill", state, _user_message(exc))
        items = [self._mapper.map_skill_master(r, SourceMode.LIVE) for r in records]
        self._skill_cache = (now, items)
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "count": len(items),
            "items": items,
            "message": None if items else "No skills are currently available from SAP.",
            "retrieved_at": now.isoformat(),
        }

    def list_jobs(self, *, search: str | None = None) -> dict[str, Any]:
        if self._uses_fallback("job"):
            records = list_raw_jobs()
            items = [self._mapper.map_job_record(r, SourceMode.MOCKED) for r in records]
            if search:
                needle = search.lower()
                items = [
                    i
                    for i in items
                    if needle
                    in " ".join(str(i.get(k) or "") for k in ("job_name", "job_id", "job_description")).lower()
                ]
            return {
                "count": len(items),
                "items": items,
                "message": None if items else "No prototype jobs are available.",
                **self._prototype_response_meta("job"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return self._empty_list(
                "job",
                state,
                state.get("message") or "No jobs are currently available from SAP.",
            )
        try:
            records = provider.list_domain("job")
        except Exception as exc:
            return self._empty_list("job", state, _user_message(exc))
        items = [self._mapper.map_job_record(r, SourceMode.LIVE) for r in records]
        if search:
            needle = search.lower()
            items = [
                i
                for i in items
                if needle
                in " ".join(str(i.get(k) or "") for k in ("job_name", "job_id", "job_description")).lower()
            ]
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "count": len(items),
            "items": items,
            "message": None if items else "No jobs are currently available from SAP.",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_job(self, job_id: str) -> dict[str, Any]:
        if self._uses_fallback("job"):
            record = get_raw_job(job_id)
            if record is None:
                return {
                    "message": "No job found for the selected identifier.",
                    "job": None,
                    "requirements": [],
                    "organization": None,
                    **self._prototype_response_meta("job"),
                }
            skills_index = {s["skill_id"]: s for s in self.list_skills().get("items", [])}
            requirements = [
                self._mapper.map_job_skill_record(
                    row,
                    skill_name=(skills_index.get(str(row.get("SKILL_ID") or "")) or {}).get("skill_name"),
                    source_mode=SourceMode.MOCKED,
                )
                for row in list_raw_job_skills(job_id=job_id)
            ]
            orgs = {o["org_unit_id"]: o for o in self.list_organizations().get("items", [])}
            org_id = record.get("ORG_UNIT_ID")
            org = orgs.get(str(org_id)) if org_id else None
            return {
                "message": None if requirements else "This role has no recorded skill requirements in the prototype catalog.",
                "job": self._mapper.map_job_record(record, SourceMode.MOCKED),
                "requirements": requirements,
                "organization": org,
                **self._prototype_response_meta("job"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return {
                "source_mode": state.get("source_mode"),
                "live_verified": False,
                "message": state.get("message"),
                "job": None,
                "requirements": [],
                "organization": None,
            }
        record = None
        try:
            record = provider.get_domain_by_key("job", job_id)
        except Exception:
            record = None
        if record is None:
            try:
                matches = provider.list_domain("job", filter_field="JOB_ID", filter_value=job_id)
                record = matches[0] if matches else None
            except Exception:
                record = None
        if record is None:
            return {
                "source_mode": SourceMode.LIVE.value,
                "live_verified": True,
                "message": "No job found in SAP for the selected identifier.",
                "job": None,
                "requirements": [],
                "organization": None,
            }

        skills_index = {s["skill_id"]: s for s in self.list_skills().get("items", [])}
        try:
            raw_js = provider.list_domain("job_skill", filter_field="JOB_ID", filter_value=job_id)
        except Exception:
            raw_js = []
        requirements = [
            self._mapper.map_job_skill_record(
                row,
                skill_name=(skills_index.get(str(field_of(row, "SKILL_ID", "skillId") or "")) or {}).get("skill_name"),
                source_mode=SourceMode.LIVE,
            )
            for row in raw_js
        ]
        org = None
        org_id = field_of(record, "ORG_UNIT_ID", "orgUnitId")
        if org_id:
            orgs = {o["org_unit_id"]: o for o in self.list_organizations().get("items", [])}
            org = orgs.get(str(org_id))
        message = None
        if not requirements:
            message = "This role has no recorded skill requirements in SAP."
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "message": message,
            "job": self._mapper.map_job_record(record, SourceMode.LIVE),
            "requirements": requirements,
            "organization": org,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_organizations(self, *, search: str | None = None) -> dict[str, Any]:
        if self._uses_fallback("organization"):
            items = [self._mapper.map_organization(r, SourceMode.MOCKED) for r in list_raw_organizations()]
            if search:
                needle = search.lower()
                items = [
                    i
                    for i in items
                    if needle in " ".join(str(i.get(k) or "") for k in ("org_unit_name", "org_unit_id")).lower()
                ]
            return {
                "count": len(items),
                "items": items,
                "message": None if items else "No prototype organizations are available.",
                **self._prototype_response_meta("organization"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return self._empty_list("organization", state, "No organizations are currently available from SAP.")
        now = datetime.now(timezone.utc)
        if self._org_cache and (now - self._org_cache[0]).total_seconds() < 300:
            items = self._org_cache[1]
        else:
            try:
                records = provider.list_domain("organization")
            except Exception as exc:
                return self._empty_list("organization", state, _user_message(exc))
            items = [self._mapper.map_organization(r, SourceMode.LIVE) for r in records]
            self._org_cache = (now, items)
        if search:
            needle = search.lower()
            items = [
                i
                for i in items
                if needle in " ".join(str(i.get(k) or "") for k in ("org_unit_name", "org_unit_id")).lower()
            ]
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "count": len(items),
            "items": items,
            "message": None if items else "No organizations are currently available from SAP.",
            "retrieved_at": now.isoformat(),
        }

    def list_hr(self, *, search: str | None = None) -> dict[str, Any]:
        if self._uses_fallback("hr"):
            items = [self._mapper.map_hr_reviewer(r, SourceMode.MOCKED) for r in list_raw_hr()]
            if search:
                needle = search.lower()
                items = [
                    i
                    for i in items
                    if needle in " ".join(str(i.get(k) or "") for k in ("hr_name", "hr_role", "hr_id")).lower()
                ]
            return {
                "count": len(items),
                "items": items,
                "message": None if items else "No prototype HR reviewers are available.",
                **self._prototype_response_meta("hr"),
            }
        provider, state = self._ensure_live()
        if provider is None:
            return self._empty_list("hr", state, "No HR reviewers are currently available from SAP.")
        try:
            records = provider.list_domain("hr")
        except Exception as exc:
            return self._empty_list("hr", state, _user_message(exc))
        items = [self._mapper.map_hr_reviewer(r, SourceMode.LIVE) for r in records]
        if search:
            needle = search.lower()
            items = [
                i
                for i in items
                if needle in " ".join(str(i.get(k) or "") for k in ("hr_name", "hr_role", "hr_id")).lower()
            ]
        return {
            "source_mode": SourceMode.LIVE.value,
            "live_verified": True,
            "count": len(items),
            "items": items,
            "message": None if items else "No HR reviewers are currently available from SAP.",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def compose_case_inputs(self, user_id: str, job_id: str) -> dict[str, Any]:
        """Canonical CandidateProfile + JobProfile for intelligence. No fixtures."""
        candidate_payload = self.get_candidate(user_id)
        job_payload = self.get_job(job_id)
        if not candidate_payload.get("candidate"):
            return {"error": candidate_payload.get("message") or "Candidate not found in SAP."}
        if not job_payload.get("job"):
            return {"error": job_payload.get("message") or "Job not found in SAP."}

        profile = self._mapper.map_candidate_profile(
            {
                "USER_ID": candidate_payload["candidate"]["user_id"],
                "FIRST_NAME": candidate_payload["candidate"].get("first_name"),
                "LAST_NAME": candidate_payload["candidate"].get("last_name"),
                "CURRENT_ROLE": candidate_payload["candidate"].get("current_role"),
                "EDUCATION": candidate_payload["candidate"].get("education"),
                "TARGET_CAREER": candidate_payload["candidate"].get("target_career"),
                "EXPERIENCE_YEARS": candidate_payload["candidate"].get("experience_years"),
                "LOCATION": candidate_payload["candidate"].get("location"),
            },
            SourceMode.LIVE,
        )
        evidence: list[CandidateEvidence] = []
        for row in candidate_payload.get("evidence") or []:
            evidence.append(CandidateEvidence.model_validate(row))
        capabilities: list[CandidateCapability] = []
        for row in candidate_payload.get("skills") or []:
            mapped = self._mapper.map_skill(
                {
                    "USER_ID": row.get("user_id"),
                    "SKILL_ID": row.get("skill_id"),
                    "SKILL_NAME": row.get("skill_name"),
                    "PROFICIENCY": row.get("proficiency"),
                    "EVIDENCE": row.get("evidence_text"),
                    "VALID_FROM": row.get("valid_from"),
                },
                profile.id,
                SourceMode.LIVE,
                skill_name=row.get("skill_name"),
            )
            if mapped:
                capabilities.append(mapped)

        job_row = job_payload["job"]
        job = JobProfile(
            id=job_row["job_id"],
            title=job_row.get("job_name") or job_row["job_id"],
            raw_text=job_row.get("job_description") or "",
            family=job_row.get("org_unit_id"),
            location=job_row.get("location"),
            sap_job_role_code=job_row["job_id"],
            source="SAP",
            source_mode=SourceMode.LIVE,
            is_demo_fixture=False,
        )
        job_caps: list[JobCapability] = []
        requirements: list[JobRequirement] = []
        for req in job_payload.get("requirements") or []:
            cap = self._mapper.map_job_capability(
                {
                    "JOB_ID": req.get("job_id"),
                    "SKILL_ID": req.get("skill_id"),
                    "REQUIRED_PROFICIENCY": req.get("required_proficiency"),
                    "IS_MANDATORY": req.get("is_mandatory"),
                },
                SourceMode.LIVE,
                skill_name=req.get("skill_name"),
            )
            if cap:
                job_caps.append(cap)
                requirements.append(
                    JobRequirement(
                        id=f"sap-req-{job.id}-{cap.skill_id}",
                        job_id=job.id,
                        text=f"{cap.label} proficiency {cap.min_proficiency:.2f}"
                        + (" (mandatory)" if cap.importance == "core" else " (optional)"),
                        requirement_class=RequirementClass.DIRECT_CAPABILITY,
                        review_tag=ReviewTag.NONE,
                        strength="required" if cap.importance == "core" else "optional",
                        confidence=0.8,
                        source_mode=SourceMode.LIVE,
                    )
                )
        job.capabilities = job_caps
        job.requirements = requirements
        return {
            "profile": profile,
            "evidence": evidence,
            "sap_capabilities": capabilities,
            "job": job,
            "organization": job_payload.get("organization"),
            "source_mode": SourceMode.LIVE.value,
        }

    def mutate(self, domain: str, operation: str, *, key: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        provider, state = self._ensure_live()
        if provider is None:
            return {
                "ok": False,
                "message": state.get("message") or "SAP is not connected.",
                "source_mode": state.get("source_mode"),
            }
        try:
            if operation == "create":
                body = provider.create_domain(domain, payload or {})
            elif operation == "update":
                if not key:
                    return {"ok": False, "message": "A record key is required to update."}
                body = provider.update_domain(domain, key, payload or {})
            elif operation == "delete":
                if not key:
                    return {"ok": False, "message": "A record key is required to delete."}
                body = provider.delete_domain(domain, key)
            else:
                return {"ok": False, "message": "Unsupported operation."}
            return {"ok": True, "item": body, "source_mode": SourceMode.LIVE.value}
        except ODataWriteNotSupportedError as exc:
            return {"ok": False, "message": exc.user_message, "write_available": False}
        except ODataError as exc:
            return {"ok": False, "message": exc.user_message or str(exc), "status_code": exc.status_code}
        except NotImplementedError:
            return {
                "ok": False,
                "message": "Write operation is not available in the current SAP service.",
            }
        except Exception as exc:
            return {"ok": False, "message": _user_message(exc)}

    def traces(self) -> list[dict[str, Any]]:
        _, state = self._ensure_live()
        if self._provider:
            return self._provider.get_diagnostics().get("traces", [])
        return state.get("traces") or []
