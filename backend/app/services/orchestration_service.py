"""Orchestration execution service."""

import uuid
from typing import Any

from app.domain.enums import EngineMode
from app.orchestration.graph import build_checkpoint_graph
from app.orchestration.state import ReworkGraphState
from app.services.run_store import run_store


class OrchestrationService:
    def execute_demo_run(
        self,
        candidate_id: str = "ananya-sharma",
        job_id: str = "data-analyst-junior",
    ) -> ReworkGraphState:
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        initial: ReworkGraphState = {
            "run_id": run_id,
            "status": "running",
            "engine_mode": EngineMode.DEMO_FALLBACK.value,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "audit_events": [],
            "errors": [],
        }
        graph = build_checkpoint_graph()
        final_state = graph.invoke(initial)
        if not final_state.get("status"):
            final_state["status"] = "failed" if final_state.get("errors") else "completed"
        run_store.save(run_id, final_state)
        return final_state

    def get_run(self, run_id: str) -> ReworkGraphState | None:
        return run_store.get(run_id)

    def build_response(self, state: ReworkGraphState) -> dict[str, Any]:
        audit_events = state.get("audit_events", [])
        audit_summary = {
            "count": len(audit_events),
            "agents": [e.get("agent") for e in audit_events],
            "failures": [e for e in audit_events if e.get("status") == "FAILURE"],
        }
        return {
            "run_id": state.get("run_id"),
            "status": state.get("status"),
            "engine_mode": state.get("engine_mode"),
            "candidate_id": state.get("candidate_id"),
            "job_id": state.get("job_id"),
            "candidate": state.get("candidate"),
            "job": state.get("job"),
            "sap_context": state.get("sap_context"),
            "candidate_evidence": state.get("candidate_evidence", []),
            "candidate_capabilities": state.get("candidate_capabilities", []),
            "job_tasks": state.get("job_tasks", []),
            "job_capabilities": state.get("job_capabilities", []),
            "role_outcomes": state.get("role_outcomes", []),
            "requirement_analyses": state.get("requirement_analyses", []),
            "audit_summary": audit_summary,
            "audit_events": audit_events,
            "errors": state.get("errors", []),
        }
