"""OData access plan and entity allow-list configuration.

Entity set names are taken from environment variables and/or verified
`$metadata` via the seven-table registry. They are never invented as live.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.adapters.sap.seven_table_registry import SevenTableRegistry, build_seven_table_registry
from app.core.config import get_settings


@dataclass(frozen=True)
class EntityMapping:
    """Maps a business domain to an OData entity set (when known)."""

    domain: str
    entity_set: str | None
    canonical_target: str
    required: bool = False
    sap_table: str | None = None
    status: str = "PENDING_OFFICIAL_ODATA_METADATA"


@dataclass
class ODataAccessPlan:
    """Controlled allow-list for OData access — no arbitrary entity URLs."""

    service_name: str | None
    entity_mappings: list[EntityMapping] = field(default_factory=list)

    def allowed_entity_sets(self) -> set[str]:
        return {m.entity_set for m in self.entity_mappings if m.entity_set}

    def mapping_for_domain(self, domain: str) -> EntityMapping | None:
        for m in self.entity_mappings:
            if m.domain == domain:
                return m
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_name": self.service_name,
            "entities": [
                {
                    "domain": m.domain,
                    "sap_table": m.sap_table,
                    "entity_set": m.entity_set,
                    "canonical_target": m.canonical_target,
                    "required": m.required,
                    "status": m.status if m.entity_set else "PENDING_OFFICIAL_ODATA_METADATA",
                }
                for m in self.entity_mappings
            ],
        }


def access_plan_from_registry(registry: SevenTableRegistry) -> ODataAccessPlan:
    return ODataAccessPlan(
        service_name=registry.service_name,
        entity_mappings=[
            EntityMapping(
                domain=b.domain,
                entity_set=b.entity_set,
                canonical_target=b.canonical_target,
                sap_table=b.sap_table,
                status=b.status,
                required=b.domain in {"user", "skill", "person_skill", "job"},
            )
            for b in registry.bindings
        ],
    )


def build_access_plan(discovered_entity_sets: list[str] | None = None) -> ODataAccessPlan:
    """Build access plan from settings and optional verified metadata entity sets."""
    registry = build_seven_table_registry(discovered_entity_sets)
    plan = access_plan_from_registry(registry)
    settings = get_settings()
    user_binding = plan.mapping_for_domain("user")
    perskill_binding = plan.mapping_for_domain("person_skill")
    aliases = [
        EntityMapping(
            "person",
            settings.sap_entity_person or (user_binding.entity_set if user_binding else None),
            "CandidateProfile",
        ),
        EntityMapping(
            "qualification",
            settings.sap_entity_qualification
            or (perskill_binding.entity_set if perskill_binding else None),
            "CandidateCapability",
        ),
        EntityMapping("position", settings.sap_entity_position, "RoleContext"),
        EntityMapping("application", settings.sap_entity_application, "ApplicationContext"),
        EntityMapping("learning", settings.sap_entity_learning, "LearningItem"),
        EntityMapping("opportunity", settings.sap_entity_opportunity, "Opportunity"),
    ]
    existing = {m.domain for m in plan.entity_mappings}
    for alias in aliases:
        if alias.domain not in existing:
            plan.entity_mappings.append(alias)
    return plan
