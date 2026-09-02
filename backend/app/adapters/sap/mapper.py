"""SAP response → canonical RE:WORK domain mapping.

No component above this mapper should depend on raw SAP property names.
Field aliases cover both ZREWORK_* DDIC-style names and older SF-style names.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from app.adapters.sap.provenance import sap_provenance
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    InferenceStatus,
    IntegrationStatus,
    SourceMode,
    VerificationStatus,
)
from app.domain.job import JobCapability, JobProfile
from app.domain.pathway import LearningItem, Opportunity
from app.domain.sap import SAPCapabilityStatus, SAPContext

# Documented proficiency labels — only these strings are normalized.
PROFICIENCY_LABELS: dict[str, float] = {
    "NOVICE": 0.20,
    "BEGINNER": 0.25,
    "BASIC": 0.30,
    "INTERMEDIATE": 0.50,
    "ADVANCED": 0.80,
    "EXPERT": 0.95,
}


def field_of(raw: dict[str, Any], *keys: str) -> Any:
    """Read the first present non-empty field, case-insensitive."""
    if not raw:
        return None
    exact = {str(k): v for k, v in raw.items()}
    for key in keys:
        if key in exact and exact[key] not in (None, ""):
            return exact[key]
    lower = {str(k).lower(): v for k, v in raw.items()}
    for key in keys:
        value = lower.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def normalize_proficiency(raw: Any) -> float | None:
    """Normalize SAP proficiency. Returns None when the value cannot be validated."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        label = raw.strip().upper().replace(" ", "_")
        if label in PROFICIENCY_LABELS:
            return PROFICIENCY_LABELS[label]
        try:
            raw = float(raw.strip())
        except ValueError:
            return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if 0.0 <= value <= 1.0:
        return round(value, 4)
    if 1.0 < value <= 5.0:
        return round(min(1.0, value / 5.0), 4)
    if 5.0 < value <= 100.0:
        return round(min(1.0, value / 100.0), 4)
    return None


def _truthy(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().upper() in {"X", "TRUE", "YES", "1", "MANDATORY"}


class SAPMapper:
    """Maps SAP OData responses to canonical domain objects. No SAP structs leak upward."""

    @staticmethod
    def map_candidate_profile(raw: dict[str, Any], source_mode: SourceMode) -> CandidateProfile:
        user_id = str(
            field_of(raw, "USER_ID", "userId", "personIdExternal", "id") or "unknown"
        )
        first = field_of(raw, "FIRST_NAME", "firstName", "first_name") or ""
        last = field_of(raw, "LAST_NAME", "lastName", "last_name") or ""
        display = field_of(raw, "displayName", "defaultFullName") or f"{first} {last}".strip() or user_id
        location = field_of(raw, "LOCATION", "location") or ""
        aspiration = field_of(raw, "TARGET_CAREER", "careerAspiration", "target_career")
        notes_parts = []
        role = field_of(raw, "CURRENT_ROLE", "jobTitle", "positionTitle", "current_role")
        education = field_of(raw, "EDUCATION", "education")
        if role:
            notes_parts.append(f"Current role: {role}")
        if education:
            notes_parts.append(f"Education: {education}")
        years = field_of(raw, "EXPERIENCE_YEARS", "experienceYears")
        if years not in (None, ""):
            notes_parts.append(f"Experience years: {years}")
        return CandidateProfile(
            id=user_id,
            display_name=display,
            location=str(location),
            career_aspiration=str(aspiration) if aspiration else None,
            sap_user_id=user_id,
            source="SAP",
            source_mode=source_mode,
            is_demo_persona=False,
            notes="; ".join(notes_parts) or None,
        )

    @staticmethod
    def map_candidate_record(raw: dict[str, Any], source_mode: SourceMode) -> dict[str, Any]:
        profile = SAPMapper.map_candidate_profile(raw, source_mode)
        user_id = profile.id
        return {
            "user_id": user_id,
            "first_name": field_of(raw, "FIRST_NAME", "firstName") or "",
            "last_name": field_of(raw, "LAST_NAME", "lastName") or "",
            "display_name": profile.display_name,
            "current_role": field_of(raw, "CURRENT_ROLE", "jobTitle", "positionTitle"),
            "education": field_of(raw, "EDUCATION", "education"),
            "target_career": field_of(raw, "TARGET_CAREER", "target_career"),
            "experience_years": field_of(raw, "EXPERIENCE_YEARS", "experienceYears"),
            "location": profile.location,
            "profile_status": field_of(raw, "PROFILE_STATUS", "profileStatus"),
            "source": "SAP",
            "source_mode": source_mode.value,
            "provenance": sap_provenance(
                entity_set="user",
                object_id=user_id,
                source_mode=source_mode,
                mapped_to="CandidateProfile",
            ),
        }

    @staticmethod
    def map_employee_context(
        raw: dict[str, Any],
        source_mode: SourceMode,
        *,
        entity_set: str = "Person",
        service: str | None = None,
    ) -> dict[str, Any]:
        object_id = field_of(raw, "USER_ID", "userId", "personIdExternal", "id")
        first = field_of(raw, "FIRST_NAME", "firstName") or ""
        last = field_of(raw, "LAST_NAME", "lastName") or ""
        display = field_of(raw, "displayName", "defaultFullName") or f"{first} {last}".strip() or object_id
        return {
            "employee_id": object_id,
            "display_name": display,
            "department": field_of(raw, "department", "ORG_UNIT_ID"),
            "organization": field_of(raw, "organization", "orgUnit", "ORG_UNIT_ID"),
            "role_title": field_of(raw, "CURRENT_ROLE", "jobTitle", "positionTitle"),
            "source": "SAP",
            "source_mode": source_mode.value,
            "external_id": object_id,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "provenance": sap_provenance(
                entity_set=entity_set,
                object_id=str(object_id) if object_id else None,
                source_mode=source_mode,
                service=service,
                mapped_to="CandidateProfile",
            ),
        }

    @staticmethod
    def map_skill_master(raw: dict[str, Any], source_mode: SourceMode) -> dict[str, Any]:
        skill_id = str(field_of(raw, "SKILL_ID", "skillId", "skill_id", "id", "name") or "unknown")
        name = field_of(raw, "SKILL_NAME", "skillName", "label", "name") or skill_id
        return {
            "skill_id": skill_id,
            "skill_name": name,
            "description": field_of(raw, "DESCRIPTION", "description"),
            "source_mode": source_mode.value,
        }

    @staticmethod
    def map_person_skill_record(
        raw: dict[str, Any],
        *,
        skill_name: str | None = None,
        source_mode: SourceMode = SourceMode.LIVE,
    ) -> dict[str, Any]:
        user_id = str(field_of(raw, "USER_ID", "userId", "personIdExternal") or "")
        skill_id = str(field_of(raw, "SKILL_ID", "skillId", "skill_id", "name") or "unknown")
        proficiency = normalize_proficiency(field_of(raw, "PROFICIENCY", "proficiencyLevel", "proficiency"))
        evidence_text = field_of(raw, "EVIDENCE", "evidence")
        return {
            "user_id": user_id,
            "skill_id": skill_id,
            "skill_name": skill_name or skill_id,
            "proficiency": proficiency,
            "proficiency_unknown": proficiency is None,
            "evidence_text": evidence_text,
            "valid_from": field_of(raw, "VALID_FROM", "validFrom"),
            "valid_to": field_of(raw, "VALID_TO", "validTo"),
            "source_mode": source_mode.value,
        }

    @staticmethod
    def map_skill(
        raw: dict[str, Any],
        candidate_id: str,
        source_mode: SourceMode,
        *,
        entity_set: str = "Qualification",
        service: str | None = None,
        skill_name: str | None = None,
    ) -> CandidateCapability | None:
        skill_id = str(field_of(raw, "SKILL_ID", "skillId", "skill_id", "name") or "unknown")
        proficiency = normalize_proficiency(field_of(raw, "PROFICIENCY", "proficiencyLevel", "proficiency"))
        if proficiency is None:
            return None
        evidence_text = field_of(raw, "EVIDENCE", "evidence")
        evidence_refs: list[str] = []
        confidence = 0.55
        if evidence_text:
            evidence_refs = [f"sap-evidence-{candidate_id}-{skill_id}"]
            confidence = 0.7
        label = skill_name or field_of(raw, "SKILL_NAME", "label") or str(skill_id)
        valid_from = field_of(raw, "VALID_FROM", "validFrom")
        recency = None
        if isinstance(valid_from, date):
            recency = valid_from
        return CandidateCapability(
            id=f"sap-cap-{candidate_id}-{skill_id}",
            candidate_id=candidate_id,
            skill_id=str(skill_id).lower().replace(" ", "_"),
            label=str(label),
            proficiency=proficiency,
            confidence=confidence,
            evidence_refs=evidence_refs,
            recency=recency,
            source="SAP_RECORDED",
            source_mode=source_mode,
            inference_status=InferenceStatus.EXPLICIT.value,
            verification_status=CapabilityVerificationStatus.UNVERIFIED,
        )

    @staticmethod
    def map_evidence_from_person_skill(
        raw: dict[str, Any],
        candidate_id: str,
        source_mode: SourceMode,
    ) -> CandidateEvidence | None:
        text = field_of(raw, "EVIDENCE", "evidence")
        if not text:
            return None
        skill_id = str(field_of(raw, "SKILL_ID", "skillId", "name") or "skill")
        return CandidateEvidence(
            id=f"sap-evidence-{candidate_id}-{skill_id}",
            candidate_id=candidate_id,
            type=EvidenceType.SAP_SKILL,
            title=f"Recorded evidence for {skill_id}",
            description=str(text),
            source="SAP",
            source_mode=source_mode,
            verification_status=VerificationStatus.UNVERIFIED,
            confidence=0.6,
        )

    @staticmethod
    def map_job(
        raw: dict[str, Any],
        source_mode: SourceMode,
        *,
        entity_set: str = "Job",
        service: str | None = None,
    ) -> JobProfile:
        job_id = str(field_of(raw, "JOB_ID", "jobCode", "jobId", "id") or "unknown")
        title = field_of(raw, "JOB_NAME", "title", "jobTitle") or job_id
        description = field_of(raw, "JOB_DESCRIPTION", "description", "jobDescription") or ""
        org = field_of(raw, "ORG_UNIT_ID", "orgUnitId")
        return JobProfile(
            id=job_id,
            title=str(title),
            raw_text=str(description),
            family=str(org) if org else None,
            location=field_of(raw, "LOCATION", "location"),
            sap_job_role_code=job_id,
            source="SAP",
            source_mode=source_mode,
            is_demo_fixture=False,
        )

    @staticmethod
    def map_job_record(raw: dict[str, Any], source_mode: SourceMode) -> dict[str, Any]:
        job = SAPMapper.map_job(raw, source_mode)
        return {
            "job_id": job.id,
            "job_name": job.title,
            "job_description": job.raw_text or None,
            "org_unit_id": field_of(raw, "ORG_UNIT_ID", "orgUnitId"),
            "valid_from": field_of(raw, "VALID_FROM", "validFrom"),
            "valid_to": field_of(raw, "VALID_TO", "validTo"),
            "location": job.location,
            "source_mode": source_mode.value,
        }

    @staticmethod
    def map_job_skill_record(
        raw: dict[str, Any],
        *,
        skill_name: str | None = None,
        source_mode: SourceMode = SourceMode.LIVE,
    ) -> dict[str, Any]:
        required = normalize_proficiency(
            field_of(raw, "REQUIRED_PROFICIENCY", "requiredProficiency", "minProficiency")
        )
        mandatory = _truthy(field_of(raw, "IS_MANDATORY", "isMandatory", "mandatory"))
        return {
            "job_id": str(field_of(raw, "JOB_ID", "jobId", "jobCode") or ""),
            "skill_id": str(field_of(raw, "SKILL_ID", "skillId") or "unknown"),
            "skill_name": skill_name,
            "required_proficiency": required,
            "is_mandatory": mandatory,
            "source_mode": source_mode.value,
        }

    @staticmethod
    def map_job_capability(
        raw: dict[str, Any],
        source_mode: SourceMode,
        *,
        skill_name: str | None = None,
    ) -> JobCapability | None:
        record = SAPMapper.map_job_skill_record(raw, skill_name=skill_name, source_mode=source_mode)
        if record["required_proficiency"] is None:
            return None
        job_id = record["job_id"] or "unknown"
        skill_id = record["skill_id"]
        return JobCapability(
            id=f"sap-jobcap-{job_id}-{skill_id}",
            job_id=job_id,
            skill_id=str(skill_id).lower().replace(" ", "_"),
            label=skill_name or str(skill_id),
            min_proficiency=record["required_proficiency"],
            importance="core" if record["is_mandatory"] else "optional",
            source_mode=source_mode,
        )

    @staticmethod
    def map_organization(raw: dict[str, Any], source_mode: SourceMode) -> dict[str, Any]:
        org_id = str(field_of(raw, "ORG_UNIT_ID", "orgUnitId", "id") or "unknown")
        return {
            "org_unit_id": org_id,
            "org_unit_name": field_of(raw, "ORG_UNIT_NAME", "orgUnitName", "name"),
            "parent_org_unit": field_of(raw, "PARENT_ORG_UNIT", "parentOrgUnit"),
            "source_mode": source_mode.value,
        }

    @staticmethod
    def map_hr_reviewer(raw: dict[str, Any], source_mode: SourceMode) -> dict[str, Any]:
        hr_id = str(field_of(raw, "HR_ID", "hrId", "id") or "unknown")
        return {
            "hr_id": hr_id,
            "hr_name": field_of(raw, "HR_NAME", "hrName", "name"),
            "hr_role": field_of(raw, "HR_ROLE", "hrRole", "role"),
            "hr_org_id": field_of(raw, "HR_ORG_ID", "hrOrgId"),
            "hr_access_level": field_of(raw, "HR_ACCESS_LEVEL", "hrAccessLevel"),
            "hr_location": field_of(raw, "HR_LOCATION", "hrLocation"),
            "hr_status": field_of(raw, "HR_STATUS", "hrStatus"),
            "source_mode": source_mode.value,
        }

    @staticmethod
    def map_learning_item(
        raw: dict[str, Any],
        source_mode: SourceMode,
        *,
        entity_set: str = "Learning",
        service: str | None = None,
    ) -> LearningItem:
        item_id = str(field_of(raw, "id", "learningId") or "unknown")
        return LearningItem(
            id=f"sap-learning-{item_id}",
            title=field_of(raw, "title", "name") or item_id,
            description=field_of(raw, "description"),
            hours=float(field_of(raw, "durationHours", "duration") or 0),
            sap_learning_item_id=item_id,
            source="SAP",
            source_mode=source_mode,
        )

    @staticmethod
    def map_opportunity(
        raw: dict[str, Any],
        source_mode: SourceMode,
        *,
        entity_set: str = "Opportunity",
        service: str | None = None,
    ) -> Opportunity:
        opp_id = str(field_of(raw, "id", "opportunityId") or "unknown")
        return Opportunity(
            id=f"sap-opp-{opp_id}",
            job_id=str(field_of(raw, "jobId", "jobCode", "JOB_ID") or opp_id),
            title=field_of(raw, "title", "roleTitle", "JOB_NAME") or opp_id,
            location=field_of(raw, "location", "LOCATION") or "Unknown",
            sap_opportunity_id=opp_id,
            source="SAP",
            source_mode=source_mode,
        )

    @staticmethod
    def map_context(
        system_name: str,
        source_mode: SourceMode,
        modules: list[str],
        status: IntegrationStatus = IntegrationStatus.AVAILABLE,
        message: str | None = None,
        *,
        entity_counts: dict[str, int] | None = None,
        entity_status: dict[str, str] | None = None,
        service: str | None = None,
        last_retrieval: datetime | None = None,
    ) -> SAPContext:
        now = last_retrieval or datetime.now(timezone.utc)
        counts = entity_counts or {}
        statuses = entity_status or {}
        return SAPContext(
            source="SAP",
            source_mode=source_mode,
            system_name=system_name,
            integration_status=status,
            last_sync=now,
            retrieved_entities=modules,
            capabilities=[
                SAPCapabilityStatus(
                    name=m,
                    status=IntegrationStatus.AVAILABLE
                    if statuses.get(m) == "AVAILABLE"
                    else (
                        IntegrationStatus.UNAVAILABLE
                        if statuses.get(m) in {"MISSING", "PENDING_OFFICIAL_ODATA_METADATA"}
                        else status
                    ),
                    source_mode=source_mode,
                    last_sync=now,
                    entity_count=counts.get(m),
                )
                for m in modules
            ],
            message=message,
        )
