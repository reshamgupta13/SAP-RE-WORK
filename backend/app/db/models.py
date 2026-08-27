"""SQLAlchemy models for case persistence."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CaseRecord(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String(128))
    job_id: Mapped[str] = mapped_column(String(128))
    opportunity_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lifecycle_state: Mapped[str] = mapped_column(String(64))
    case_version: Mapped[int] = mapped_column(Integer, default=1)
    engine_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_mode: Mapped[str] = mapped_column(String(32))
    latest_run_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    latest_snapshot_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    baseline_snapshot_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    human_decision_status: Mapped[str] = mapped_column(String(32))
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CaseSnapshotRecord(Base):
    __tablename__ = "case_snapshots"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(128), index=True)
    case_version: Mapped[int] = mapped_column(Integer)
    engine_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_mode: Mapped[str] = mapped_column(String(32))
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    rationale_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CaseEventRecord(Base):
    __tablename__ = "case_events"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(128), index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    actor_type: Mapped[str] = mapped_column(String(16))
    actor_id: Mapped[str] = mapped_column(String(128))
    before_snapshot_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    after_snapshot_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_mode: Mapped[str] = mapped_column(String(32))
    engine_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    idempotency_key: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
