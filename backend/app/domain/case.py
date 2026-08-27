"""Canonical case graph domain models."""

from datetime import datetime
from typing import Any

from pydantic import Field

from app.domain.base import DomainModel, IdentifiedModel
from app.domain.enums import (
    ActorType,
    CaseEventType,
    CaseLifecycleState,
    EngineMode,
    HumanDecisionStatus,
    SourceMode,
)


class CaseSnapshot(IdentifiedModel):
    """Full validated case state at a point in time."""

    case_id: str
    case_version: int
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    engine_mode: EngineMode | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC
  # Structured state — mirrors graph output without chain-of-thought
    state: dict[str, Any] = Field(default_factory=dict)
    rationale_summary: str | None = None


class CaseEvent(IdentifiedModel):
    event_type: CaseEventType
    case_id: str
    actor_type: ActorType
    actor_id: str = "system"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    before_snapshot_ref: str | None = None
    after_snapshot_ref: str | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC
    engine_mode: EngineMode | None = None
    rationale: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    idempotency_key: str | None = None


class CaseTimelineEntry(DomainModel):
    index: int
    label: str
    event_type: str
    timestamp: str | None = None
    lifecycle_state: CaseLifecycleState | None = None
    summary: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    snapshot_ref: str | None = None


class WhatChangedItem(DomainModel):
    dimension: str
    before: str
    after: str
    evidence_refs: list[str] = Field(default_factory=list)


class WhatChangedReport(DomainModel):
    case_id: str
    baseline_label: str = "Before RE:WORK analysis"
    current_label: str = "Current state"
    changes: list[WhatChangedItem] = Field(default_factory=list)
    source_mode: SourceMode = SourceMode.SYNTHETIC


class ReworkCase(IdentifiedModel):
    """Canonical source of truth for one candidate/opportunity journey."""

    candidate_id: str
    job_id: str
    opportunity_id: str | None = None
    lifecycle_state: CaseLifecycleState = CaseLifecycleState.CASE_CREATED
    case_version: int = 1
    engine_mode: EngineMode | None = None
    source_mode: SourceMode = SourceMode.SYNTHETIC
    latest_run_id: str | None = None
    latest_snapshot_id: str | None = None
    baseline_snapshot_id: str | None = None
    human_decision_status: HumanDecisionStatus = HumanDecisionStatus.PENDING
    ai_recommendation: dict[str, Any] = Field(default_factory=dict)
    human_decision: dict[str, Any] = Field(default_factory=dict)
    # Embedded projection fields (from latest snapshot)
    snapshot: dict[str, Any] = Field(default_factory=dict)
    decision_card: dict[str, Any] | None = None
    explainability: dict[str, Any] | None = None
    intervention_scenarios: dict[str, Any] | None = None
    sap_context: dict[str, Any] | None = None
    timeline_summary: list[CaseTimelineEntry] = Field(default_factory=list)
