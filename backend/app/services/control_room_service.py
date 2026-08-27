"""Aggregated Control Room demo payload — backend is source of truth."""

from typing import Any

from app.domain.enums import EngineMode, RunMode, SourceMode
from app.services.explainability_service import ExplainabilityService
from app.services.fixture_service import FixtureService
from app.services.human_review_service import HumanReviewService
from app.services.intervention_simulator import InterventionSimulator
from app.services.orchestration_service import OrchestrationService


class ControlRoomService:
    PIPELINE_STAGES = [
        ("DISCOVER", "load_candidate"),
        ("DECOMPOSE", "job_decomposition"),
        ("DIAGNOSE", "diagnosis"),
        ("COUNTERFACTUAL", "counterfactual_analysis"),
        ("DEVELOP", "pathway_generation"),
        ("PROVE", "proof_evaluation"),
        ("REASSESS", "reassessment"),
        ("MARKET", "market_intelligence"),
        ("VIABILITY", "opportunity_viability"),
        ("REVIEW", "intervention_simulation"),
    ]

    def __init__(self) -> None:
        self._orchestration = OrchestrationService()
        self._fixtures = FixtureService()
        self._intervention = InterventionSimulator()
        self._explainability = ExplainabilityService()
        self._human_review = HumanReviewService()

    def build_control_room(self) -> dict[str, Any]:
        state = self._orchestration.execute_demo_run(
            run_mode=RunMode.CONTROL_ROOM_DEMO,
        )
        return self._assemble(state)

    def assemble_from_state(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._assemble(state)

    def _assemble(self, state: dict[str, Any]) -> dict[str, Any]:
        intervention_data = state.get("intervention_simulation") or {}
        explainability_data = state.get("explainability") or {}

        decision_card = self._explainability.build_decision_card(state)
        human_review_example = self._human_review.example_review_payload(state)

        primary_viability = next(
            (
                v for v in state.get("opportunity_viability", [])
                if v.get("opportunity_id") == "opp-data-analyst"
            ),
            state.get("opportunity_viability", [{}])[0] if state.get("opportunity_viability") else {},
        )

        employer = next(
            (
                e for e in state.get("employer_readiness", [])
                if e.get("opportunity_id") == "opp-data-analyst"
            ),
            state.get("employer_readiness", [{}])[0] if state.get("employer_readiness") else {},
        )

        return {
            "source_mode": SourceMode.SYNTHETIC.value,
            "system_status": {
                "sap": "SIMULATED",
                "ai_engine": state.get("engine_mode", EngineMode.DEMO_FALLBACK.value),
                "pipeline_progress": self._pipeline_progress(state),
                "demo_mode": True,
            },
            "active_case": {
                "candidate_name": (state.get("candidate") or {}).get("name", "Ananya Sharma"),
                "target_opportunity": "Data Analyst",
                "capability_fit": primary_viability.get("dimensions", {}).get("capability_fit"),
                "current_diagnosis": (
                    (state.get("reassessment_summary") or state.get("diagnosis_summary") or {})
                ).get("overall_diagnosis_state"),
                "opportunity_viability": primary_viability.get("viability_state"),
                "employer_readiness": employer.get("overall_state"),
            },
            "run_id": state.get("run_id"),
            "candidate": state.get("candidate"),
            "job": state.get("job"),
            "diagnosis": {
                "summary": state.get("diagnosis_summary"),
                "reassessment_summary": state.get("reassessment_summary"),
                "capability_gaps": state.get("capability_gaps", []),
                "requirement_diagnoses": state.get("requirement_diagnoses", []),
                "counterfactuals": state.get("counterfactuals", []),
            },
            "counterfactual": state.get("opportunity_counterfactuals", []),
            "pathway": state.get("learning_path"),
            "proof": {
                "assessment": state.get("proof_assessment"),
                "result": state.get("proof_result"),
                "evidence": state.get("proof_evidence"),
            },
            "reassessment": state.get("reassessment_summary"),
            "market": {
                "signals": state.get("market_signals", []),
                "skill_investments": state.get("skill_investments", []),
            },
            "viability": {
                "opportunities": state.get("opportunities", []),
                "assessments": state.get("opportunity_viability", []),
                "comparison": state.get("opportunity_comparison"),
            },
            "employer_readiness": state.get("employer_readiness", []),
            "interventions": intervention_data,
            "explainability": explainability_data,
            "human_review": human_review_example,
            "human_reviews": self._human_review.get_reviews_for_run(state.get("run_id", "")),
            "decision_card": decision_card.model_dump(mode="json"),
            "candidate_capabilities": state.get(
                "updated_candidate_capabilities",
                state.get("candidate_capabilities", []),
            ),
            "sap_context": self._sap_context_view(state),
            "pipeline": self._pipeline_detail(state),
            "label_simulated_projection": "SIMULATED PROJECTION",
        }

    def _pipeline_progress(self, state: dict[str, Any]) -> float:
        agents = {e.get("agent") for e in state.get("audit_events", [])}
        completed = 0
        for _, agent in self.PIPELINE_STAGES:
            if agent in agents:
                completed += 1
        return round(completed / len(self.PIPELINE_STAGES), 2)

    def _pipeline_detail(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        agents = {e.get("agent") for e in state.get("audit_events", [])}
        stages = []
        for stage, agent in self.PIPELINE_STAGES:
            status = "completed" if agent in agents else "pending"
            if stage == "REVIEW" and state.get("intervention_simulation"):
                status = "active"
            stages.append({"stage": stage, "agent": agent, "status": status})
        return stages

    def _sap_context_view(self, state: dict[str, Any]) -> dict[str, Any]:
        sap = state.get("sap_context") or {}
        return {
            "success_factors": "SIMULATED",
            "talent_intelligence": "SIMULATED",
            "learning": "SIMULATED",
            "opportunity_marketplace": "SIMULATED",
            "btp": "NOT_CONNECTED",
            "raw": sap,
            "note": "No live SAP integration has been claimed or implemented.",
        }

    def get_scenarios(self) -> dict[str, Any]:
        state = self._orchestration.execute_demo_run(run_mode=RunMode.CONTROL_ROOM_DEMO)
        intervention = state.get("intervention_simulation") or {}
        return {
            "scenarios": intervention.get("scenarios", []),
            "bundles": intervention.get("bundles", []),
            "minimum_effective_intervention": intervention.get("minimum_effective_intervention"),
            "is_simulated_projection": True,
            "label": "SIMULATED PROJECTION",
        }
