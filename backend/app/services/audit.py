"""Audit event helpers."""

import time
import uuid
from datetime import datetime, timezone

from app.domain.decision import AuditEvent
from app.domain.enums import AuditStatus, EngineMode


def new_audit_event(
    agent: str,
    run_id: str | None,
    engine_mode: EngineMode,
    status: AuditStatus,
    rationale: str | None = None,
    confidence: float | None = None,
    input_reference: str | None = None,
    output_reference: str | None = None,
    source_references: list[str] | None = None,
    latency_ms: int | None = None,
    error: str | None = None,
) -> AuditEvent:
    return AuditEvent(
        id=f"audit-{agent}-{uuid.uuid4().hex[:8]}",
        run_id=run_id,
        agent=agent,
        timestamp=datetime.now(timezone.utc),
        engine_mode=engine_mode,
        input_reference=input_reference,
        output_reference=output_reference,
        confidence=confidence,
        source_references=source_references or [],
        status=status,
        latency_ms=latency_ms,
        error=error,
        rationale=rationale,
    )


class AuditTimer:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    def elapsed_ms(self) -> int:
        return int((time.perf_counter() - self._start) * 1000)
