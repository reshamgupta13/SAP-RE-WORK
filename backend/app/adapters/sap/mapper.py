"""SAP response → canonical RE:WORK domain mapping."""

from datetime import datetime, timezone
from typing import Any

from app.domain.candidate import CandidateCapability
from app.domain.enums import SourceMode
from app.domain.sap import SAPContext, SAPCapabilityStatus
from app.domain.enums import IntegrationStatus


class SAPMapper:
    """Maps SAP API responses to canonical domain objects. No SAP structs leak upward."""

    @staticmethod
    def map_employee_context(raw: dict[str, Any], source_mode: SourceMode) -> dict[str, Any]:
        return {
            "employee_id": raw.get("userId") or raw.get("personIdExternal") or raw.get("id"),
            "display_name": raw.get("displayName") or raw.get("defaultFullName"),
            "department": raw.get("department"),
            "source": "SAP",
            "source_mode": source_mode.value,
            "external_id": raw.get("userId"),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def map_skill(raw: dict[str, Any], candidate_id: str, source_mode: SourceMode) -> CandidateCapability:
        skill_id = raw.get("skillId") or raw.get("skill_id") or raw.get("name", "unknown")
        proficiency = float(raw.get("proficiencyLevel") or raw.get("proficiency") or 0.5)
        return CandidateCapability(
            id=f"sap-cap-{candidate_id}-{skill_id}",
            candidate_id=candidate_id,
            skill_id=str(skill_id).lower().replace(" ", "_"),
            label=raw.get("label") or str(skill_id),
            proficiency=min(1.0, max(0.0, proficiency / 5.0 if proficiency > 1 else proficiency)),
            confidence=0.7,
            evidence_refs=[],
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
    ) -> SAPContext:
        return SAPContext(
            source="SAP",
            source_mode=source_mode,
            system_name=system_name,
            integration_status=status,
            last_sync=datetime.now(timezone.utc),
            retrieved_entities=modules,
            capabilities=[
                SAPCapabilityStatus(
                    name=m,
                    status=status,
                    source_mode=source_mode,
                    last_sync=datetime.now(timezone.utc),
                )
                for m in modules
            ],
            message=message,
        )
