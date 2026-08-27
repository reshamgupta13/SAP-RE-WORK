"""Case persistence repository interface."""

from abc import ABC, abstractmethod

from app.domain.case import CaseEvent, CaseSnapshot, ReworkCase


class CaseRepository(ABC):
    @abstractmethod
    def save_case(self, case: ReworkCase) -> ReworkCase:
        ...

    @abstractmethod
    def get_case(self, case_id: str) -> ReworkCase | None:
        ...

    @abstractmethod
    def list_cases(self) -> list[ReworkCase]:
        ...

    @abstractmethod
    def save_snapshot(self, snapshot: CaseSnapshot) -> CaseSnapshot:
        ...

    @abstractmethod
    def get_snapshot(self, snapshot_id: str) -> CaseSnapshot | None:
        ...

    @abstractmethod
    def save_event(self, event: CaseEvent) -> CaseEvent:
        ...

    @abstractmethod
    def list_events(self, case_id: str) -> list[CaseEvent]:
        ...

    @abstractmethod
    def get_event_by_idempotency(self, case_id: str, key: str) -> CaseEvent | None:
        ...
