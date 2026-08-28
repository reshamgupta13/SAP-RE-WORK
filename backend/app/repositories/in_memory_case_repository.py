"""In-memory case repository for tests and demo mode."""

from app.domain.case import CaseEvent, CaseSnapshot, ReworkCase
from app.repositories.case_repository import CaseRepository


class InMemoryCaseRepository(CaseRepository):
    def __init__(self) -> None:
        self._cases: dict[str, ReworkCase] = {}
        self._snapshots: dict[str, CaseSnapshot] = {}
        self._events: dict[str, CaseEvent] = {}
        self._events_by_case: dict[str, list[str]] = {}
        self._idempotency: dict[str, str] = {}

    def save_case(self, case: ReworkCase) -> ReworkCase:
        self._cases[case.id] = case
        return case

    def get_case(self, case_id: str) -> ReworkCase | None:
        return self._cases.get(case_id)

    def list_cases(self) -> list[ReworkCase]:
        return list(self._cases.values())

    def save_snapshot(self, snapshot: CaseSnapshot) -> CaseSnapshot:
        self._snapshots[snapshot.id] = snapshot
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> CaseSnapshot | None:
        return self._snapshots.get(snapshot_id)

    def save_event(self, event: CaseEvent) -> CaseEvent:
        self._events[event.id] = event
        self._events_by_case.setdefault(event.case_id, []).append(event.id)
        if event.idempotency_key:
            self._idempotency[f"{event.case_id}:{event.idempotency_key}"] = event.id
        return event

    def list_events(self, case_id: str) -> list[CaseEvent]:
        ids = self._events_by_case.get(case_id, [])
        return [self._events[i] for i in ids if i in self._events]

    def get_event_by_idempotency(self, case_id: str, key: str) -> CaseEvent | None:
        event_id = self._idempotency.get(f"{case_id}:{key}")
        return self._events.get(event_id) if event_id else None

    def clear_case(self, case_id: str) -> None:
        self._cases.pop(case_id, None)
        event_ids = self._events_by_case.pop(case_id, [])
        for eid in event_ids:
            ev = self._events.pop(eid, None)
            if ev and ev.idempotency_key:
                self._idempotency.pop(f"{case_id}:{ev.idempotency_key}", None)
        stale_snapshots = [sid for sid, snap in self._snapshots.items() if snap.case_id == case_id]
        for sid in stale_snapshots:
            self._snapshots.pop(sid, None)


in_memory_case_repository = InMemoryCaseRepository()
