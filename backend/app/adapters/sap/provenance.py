"""SAP object provenance — every imported object carries trace metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domain.enums import SourceMode


def sap_provenance(
    *,
    entity_set: str,
    object_id: str | None = None,
    source_mode: SourceMode,
    service: str | None = None,
    mapped_to: str | None = None,
    retrieved_at: datetime | None = None,
) -> dict[str, Any]:
    ts = retrieved_at or datetime.now(timezone.utc)
    return {
        "source": "SAP",
        "source_mode": source_mode.value,
        "service": service,
        "entity_set": entity_set,
        "object_id": object_id,
        "retrieved_at": ts.isoformat(),
        "mapped_to": mapped_to,
    }


def wrap_with_provenance(
    data: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    return {**data, "provenance": provenance}
