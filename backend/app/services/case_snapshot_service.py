"""Build and store case snapshots from orchestration state."""

import uuid
from typing import Any

from app.domain.case import CaseSnapshot
from app.domain.enums import EngineMode, SourceMode
from app.services.orchestration_service import OrchestrationService


class CaseSnapshotService:
    def __init__(self) -> None:
        self._orchestration = OrchestrationService()

    def from_graph_state(
        self,
        case_id: str,
        case_version: int,
        state: dict[str, Any],
        rationale: str | None = None,
    ) -> CaseSnapshot:
        clean_state = self._orchestration.build_response(state)
        clean_state["case_id"] = case_id
        engine = state.get("engine_mode")
        return CaseSnapshot(
            id=f"snap-{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            case_version=case_version,
            engine_mode=EngineMode(engine) if engine else None,
            source_mode=SourceMode.SYNTHETIC,
            state=clean_state,
            rationale_summary=rationale,
        )

    def state_dict(self, snapshot: CaseSnapshot) -> dict[str, Any]:
        return snapshot.state
