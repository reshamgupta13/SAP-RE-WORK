"""Orchestration execution service."""

import uuid
from typing import Any

from app.domain.enums import EngineMode, RunMode
from app.orchestration.graph import build_graph
from app.orchestration.state import ReworkGraphState
from app.services.run_store import run_store


class OrchestrationService:
    def execute_demo_run(
        self,
        candidate_id: str = "ananya-sharma",
        job_id: str = "data-analyst-junior",
        run_mode: RunMode = RunMode.ANALYZE_ONLY,
    ) -> ReworkGraphState:
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        initial: ReworkGraphState = {
            "run_id": run_id,
            "status": "running",
            "engine_mode": EngineMode.DEMO_FALLBACK.value,
            "run_mode": run_mode.value,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "audit_events": [],
            "errors": [],
            "capability_update_events": [],
        }
        graph = build_graph()
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
            "run_mode": state.get("run_mode"),
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
            "capability_assessments": state.get("capability_assessments", []),
            "capability_gaps": state.get("capability_gaps", []),
            "requirement_diagnoses": state.get("requirement_diagnoses", []),
            "counterfactuals": state.get("counterfactuals", []),
            "diagnosis_summary": state.get("diagnosis_summary"),
            "learning_path": state.get("learning_path"),
            "proof_assessment": state.get("proof_assessment"),
            "proof_submission": state.get("proof_submission"),
            "proof_result": state.get("proof_result"),
            "proof_evidence": state.get("proof_evidence"),
            "capability_update_events": state.get("capability_update_events", []),
            "updated_candidate_capabilities": state.get("updated_candidate_capabilities", []),
            "reassessment_summary": state.get("reassessment_summary"),
            "audit_summary": audit_summary,
            "audit_events": audit_events,
            "errors": state.get("errors", []),
        }

    def build_diagnosis_response(self, state: ReworkGraphState) -> dict[str, Any]:
        base = self.build_response(state)
        return {
            "run_id": base["run_id"],
            "status": base["status"],
            "engine_mode": base["engine_mode"],
            "diagnosis_summary": base.get("diagnosis_summary"),
            "capability_assessments": base.get("capability_assessments", []),
            "capability_gaps": base.get("capability_gaps", []),
            "requirement_diagnoses": base.get("requirement_diagnoses", []),
            "counterfactuals": base.get("counterfactuals", []),
            "audit_summary": base["audit_summary"],
            "errors": base.get("errors", []),
        }

    def build_pathway_response(self, state: ReworkGraphState) -> dict[str, Any]:
        base = self.build_response(state)
        return {
            "run_id": base["run_id"],
            "status": base["status"],
            "engine_mode": base["engine_mode"],
            "learning_path": base.get("learning_path"),
            "proof_assessment": base.get("proof_assessment"),
            "diagnosis_summary": base.get("diagnosis_summary"),
            "capability_gaps": base.get("capability_gaps", []),
            "audit_summary": base["audit_summary"],
            "errors": base.get("errors", []),
        }

    def build_proof_response(self, state: ReworkGraphState) -> dict[str, Any]:
        base = self.build_response(state)
        return {
            "run_id": base["run_id"],
            "status": base["status"],
            "engine_mode": base["engine_mode"],
            "learning_path": base.get("learning_path"),
            "proof_result": base.get("proof_result"),
            "proof_evidence": base.get("proof_evidence"),
            "capability_update_events": base.get("capability_update_events", []),
            "updated_candidate_capabilities": base.get("updated_candidate_capabilities", []),
            "reassessment_summary": base.get("reassessment_summary"),
            "audit_summary": base["audit_summary"],
            "errors": base.get("errors", []),
        }
