"""SAP integration context models."""

from datetime import datetime

from pydantic import Field

from app.domain.base import DomainModel
from app.domain.enums import IntegrationStatus, SourceMode


class SAPCapabilityStatus(DomainModel):
    name: str
    status: IntegrationStatus
    source_mode: SourceMode
    last_sync: datetime | None = None
    entity_count: int | None = None


class SAPContext(DomainModel):
    """Canonical SAP workforce context with explicit provenance."""

    source: str = "SAP"
    source_mode: SourceMode
    system_name: str
    integration_status: IntegrationStatus
    last_sync: datetime | None = None
    retrieved_entities: list[str] = Field(default_factory=list)
    capabilities: list[SAPCapabilityStatus] = Field(default_factory=list)
    message: str | None = None
