"""Seven SAP table → OData EntitySet → canonical model registry.

Entity set names are taken from configuration and/or verified `$metadata`.
Names are never invented as live. Matching against discovered EntitySets is
allowed only when the set actually appears in metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings

PENDING = "PENDING_OFFICIAL_ODATA_METADATA"

# domain, sap_table, canonical, hints, reject_if_contains
SEVEN_DOMAINS: tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("user", "ZREWORK_USER", "CandidateProfile", ("ZREWORK_USER",), ()),
    ("skill", "ZREWORK_SKILL", "Skill", ("ZREWORK_SKILL",), ("PERSKILL", "JOB_SKIL")),
    ("person_skill", "ZREWORK_PERSKILL", "CandidateCapability", ("ZREWORK_PERSKILL",), ()),
    ("job", "ZREWORK_JOB", "JobProfile", ("ZREWORK_JOB",), ("JOB_SKIL",)),
    ("job_skill", "ZREWORK_JOB_SKIL", "JobCapability", ("ZREWORK_JOB_SKIL", "JOBSKILL"), ()),
    ("organization", "ZREWORK_ORGANIZA", "Organization", ("ZREWORK_ORGANIZA",), ()),
    ("hr", "ZREWORK_HR", "HRReviewer", ("ZREWORK_HR",), ()),
)


@dataclass
class DomainBinding:
    domain: str
    sap_table: str
    canonical_target: str
    entity_set: str | None
    status: str
    hints: tuple[str, ...] = ()
    keys: list[str] = field(default_factory=list)


@dataclass
class SevenTableRegistry:
    service_name: str | None
    bindings: list[DomainBinding] = field(default_factory=list)

    def binding(self, domain: str) -> DomainBinding | None:
        return next((b for b in self.bindings if b.domain == domain), None)

    def allowed_entity_sets(self) -> set[str]:
        return {b.entity_set for b in self.bindings if b.entity_set}

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_name": self.service_name,
            "entities": [
                {
                    "domain": b.domain,
                    "sap_table": b.sap_table,
                    "entity_set": b.entity_set,
                    "canonical_target": b.canonical_target,
                    "status": b.status,
                    "keys": b.keys,
                }
                for b in self.bindings
            ],
        }


def _configured_entity_set(domain: str) -> str | None:
    settings = get_settings()
    mapping = {
        "user": settings.sap_entity_user or settings.sap_entity_person,
        "skill": settings.sap_entity_skill,
        "person_skill": settings.sap_entity_person_skill or settings.sap_entity_qualification,
        "job": settings.sap_entity_job,
        "job_skill": settings.sap_entity_job_skill,
        "organization": settings.sap_entity_organization,
        "hr": settings.sap_entity_hr,
    }
    value = mapping.get(domain)
    return value.strip() if value else None


def match_entity_set(
    hints: tuple[str, ...],
    discovered: list[str],
    *,
    reject_if_contains: tuple[str, ...] = (),
) -> str | None:
    """Return a discovered EntitySet matching a table hint. No invented names."""
    upper = [(name, name.upper()) for name in discovered]

    def rejected(uname: str, hint: str) -> bool:
        for rej in reject_if_contains:
            ru = rej.upper()
            if ru in uname and ru not in hint.upper():
                return True
        return False

    for hint in hints:
        h = hint.upper()
        for name, uname in upper:
            if rejected(uname, h):
                continue
            if uname == h or uname == f"{h}SET" or uname == f"{h}S":
                return name

    for hint in hints:
        h = hint.upper()
        candidates = [
            name
            for name, uname in upper
            if h in uname and not rejected(uname, h)
        ]
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            return min(candidates, key=len)
    return None


def build_seven_table_registry(
    discovered_entity_sets: list[str] | None = None,
    *,
    entity_keys: dict[str, list[str]] | None = None,
) -> SevenTableRegistry:
    settings = get_settings()
    discovered = discovered_entity_sets or []
    keys_by_set = entity_keys or {}
    bindings: list[DomainBinding] = []
    for domain, table, target, hints, rejects in SEVEN_DOMAINS:
        configured = _configured_entity_set(domain)
        entity_set = None
        status = PENDING
        if configured:
            if not discovered or configured in discovered:
                entity_set = configured
                status = "CONFIGURED" if not discovered else "AVAILABLE"
            else:
                status = "MISSING"
        elif discovered:
            matched = match_entity_set(hints, discovered, reject_if_contains=rejects)
            if matched:
                entity_set = matched
                status = "AVAILABLE"
        bindings.append(
            DomainBinding(
                domain=domain,
                sap_table=table,
                canonical_target=target,
                entity_set=entity_set,
                status=status,
                hints=hints,
                keys=keys_by_set.get(entity_set, []) if entity_set else [],
            )
        )
    return SevenTableRegistry(service_name=settings.sap_odata_service, bindings=bindings)
