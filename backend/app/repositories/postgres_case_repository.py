"""PostgreSQL case repository."""

from datetime import datetime

from app.domain.case import CaseEvent, CaseSnapshot, ReworkCase
from app.domain.enums import (
    ActorType,
    CaseEventType,
    CaseLifecycleState,
    EngineMode,
    HumanDecisionStatus,
    SourceMode,
)
from app.repositories.case_repository import CaseRepository


class PostgresCaseRepository(CaseRepository):
    def __init__(self) -> None:
        from app.core.database import SessionLocal
        from app.db.models import Base, CaseEventRecord, CaseRecord, CaseSnapshotRecord
        from app.core.database import get_engine

        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        self._Session = SessionLocal
        self._CaseRecord = CaseRecord
        self._CaseSnapshotRecord = CaseSnapshotRecord
        self._CaseEventRecord = CaseEventRecord

    def save_case(self, case: ReworkCase) -> ReworkCase:
        with self._Session() as session:
            rec = session.get(self._CaseRecord, case.id)
            data = {
                "ai_recommendation": case.ai_recommendation,
                "human_decision": case.human_decision,
                "snapshot": case.snapshot,
                "decision_card": case.decision_card,
                "explainability": case.explainability,
                "intervention_scenarios": case.intervention_scenarios,
                "sap_context": case.sap_context,
                "timeline_summary": [t.model_dump(mode="json") for t in case.timeline_summary],
            }
            if rec is None:
                rec = self._CaseRecord(
                    id=case.id,
                    candidate_id=case.candidate_id,
                    job_id=case.job_id,
                    opportunity_id=case.opportunity_id,
                    lifecycle_state=case.lifecycle_state.value,
                    case_version=case.case_version,
                    engine_mode=case.engine_mode.value if case.engine_mode else None,
                    source_mode=case.source_mode.value,
                    latest_run_id=case.latest_run_id,
                    latest_snapshot_id=case.latest_snapshot_id,
                    baseline_snapshot_id=case.baseline_snapshot_id,
                    human_decision_status=case.human_decision_status.value,
                    data=data,
                )
                session.add(rec)
            else:
                rec.lifecycle_state = case.lifecycle_state.value
                rec.case_version = case.case_version
                rec.engine_mode = case.engine_mode.value if case.engine_mode else None
                rec.latest_run_id = case.latest_run_id
                rec.latest_snapshot_id = case.latest_snapshot_id
                rec.baseline_snapshot_id = case.baseline_snapshot_id
                rec.human_decision_status = case.human_decision_status.value
                rec.data = data
                rec.updated_at = datetime.utcnow()
            session.commit()
        return case

    def get_case(self, case_id: str) -> ReworkCase | None:
        with self._Session() as session:
            rec = session.get(self._CaseRecord, case_id)
            if not rec:
                return None
            return self._to_case(rec)

    def list_cases(self) -> list[ReworkCase]:
        with self._Session() as session:
            return [self._to_case(r) for r in session.query(self._CaseRecord).all()]

    def save_snapshot(self, snapshot: CaseSnapshot) -> CaseSnapshot:
        with self._Session() as session:
            rec = self._CaseSnapshotRecord(
                id=snapshot.id,
                case_id=snapshot.case_id,
                case_version=snapshot.case_version,
                engine_mode=snapshot.engine_mode.value if snapshot.engine_mode else None,
                source_mode=snapshot.source_mode.value,
                state=snapshot.state,
                rationale_summary=snapshot.rationale_summary,
                captured_at=snapshot.captured_at,
            )
            session.merge(rec)
            session.commit()
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> CaseSnapshot | None:
        with self._Session() as session:
            rec = session.get(self._CaseSnapshotRecord, snapshot_id)
            if not rec:
                return None
            return CaseSnapshot(
                id=rec.id,
                case_id=rec.case_id,
                case_version=rec.case_version,
                engine_mode=EngineMode(rec.engine_mode) if rec.engine_mode else None,
                source_mode=SourceMode(rec.source_mode),
                state=rec.state,
                rationale_summary=rec.rationale_summary,
                captured_at=rec.captured_at,
            )

    def save_event(self, event: CaseEvent) -> CaseEvent:
        with self._Session() as session:
            existing = None
            if event.idempotency_key:
                existing = session.query(self._CaseEventRecord).filter_by(
                    case_id=event.case_id,
                    idempotency_key=event.idempotency_key,
                ).first()
            if existing:
                return self._to_event(existing)
            rec = self._CaseEventRecord(
                id=event.id,
                case_id=event.case_id,
                event_type=event.event_type.value,
                actor_type=event.actor_type.value,
                actor_id=event.actor_id,
                before_snapshot_ref=event.before_snapshot_ref,
                after_snapshot_ref=event.after_snapshot_ref,
                source_mode=event.source_mode.value,
                engine_mode=event.engine_mode.value if event.engine_mode else None,
                rationale=event.rationale,
                evidence_refs=event.evidence_refs,
                idempotency_key=event.idempotency_key,
                timestamp=event.timestamp,
            )
            session.add(rec)
            session.commit()
        return event

    def list_events(self, case_id: str) -> list[CaseEvent]:
        with self._Session() as session:
            rows = session.query(self._CaseEventRecord).filter_by(case_id=case_id).all()
            return [self._to_event(r) for r in rows]

    def get_event_by_idempotency(self, case_id: str, key: str) -> CaseEvent | None:
        with self._Session() as session:
            rec = session.query(self._CaseEventRecord).filter_by(
                case_id=case_id, idempotency_key=key
            ).first()
            return self._to_event(rec) if rec else None

    def _to_case(self, rec) -> ReworkCase:
        from app.domain.case import CaseTimelineEntry

        data = rec.data or {}
        timeline = [
            CaseTimelineEntry.model_validate(t) for t in data.get("timeline_summary", [])
        ]
        return ReworkCase(
            id=rec.id,
            candidate_id=rec.candidate_id,
            job_id=rec.job_id,
            opportunity_id=rec.opportunity_id,
            lifecycle_state=CaseLifecycleState(rec.lifecycle_state),
            case_version=rec.case_version,
            engine_mode=EngineMode(rec.engine_mode) if rec.engine_mode else None,
            source_mode=SourceMode(rec.source_mode),
            latest_run_id=rec.latest_run_id,
            latest_snapshot_id=rec.latest_snapshot_id,
            baseline_snapshot_id=rec.baseline_snapshot_id,
            human_decision_status=HumanDecisionStatus(rec.human_decision_status),
            ai_recommendation=data.get("ai_recommendation", {}),
            human_decision=data.get("human_decision", {}),
            snapshot=data.get("snapshot", {}),
            decision_card=data.get("decision_card"),
            explainability=data.get("explainability"),
            intervention_scenarios=data.get("intervention_scenarios"),
            sap_context=data.get("sap_context"),
            timeline_summary=timeline,
            created_at=rec.created_at,
        )

    def _to_event(self, rec) -> CaseEvent:
        return CaseEvent(
            id=rec.id,
            event_type=CaseEventType(rec.event_type),
            case_id=rec.case_id,
            actor_type=ActorType(rec.actor_type),
            actor_id=rec.actor_id,
            before_snapshot_ref=rec.before_snapshot_ref,
            after_snapshot_ref=rec.after_snapshot_ref,
            source_mode=SourceMode(rec.source_mode),
            engine_mode=EngineMode(rec.engine_mode) if rec.engine_mode else None,
            rationale=rec.rationale,
            evidence_refs=rec.evidence_refs or [],
            idempotency_key=rec.idempotency_key,
            timestamp=rec.timestamp,
        )
