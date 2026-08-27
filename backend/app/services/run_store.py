"""In-memory run storage for Checkpoint 2."""

from typing import Any

from app.orchestration.state import ReworkGraphState


class RunStore:
    def __init__(self) -> None:
        self._runs: dict[str, ReworkGraphState] = {}

    def save(self, run_id: str, state: ReworkGraphState) -> None:
        self._runs[run_id] = state

    def get(self, run_id: str) -> ReworkGraphState | None:
        return self._runs.get(run_id)

    def list_ids(self) -> list[str]:
        return list(self._runs.keys())


run_store = RunStore()
