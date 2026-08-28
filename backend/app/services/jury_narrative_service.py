"""Jury-facing narrative payloads — backend source of truth."""

from typing import Any


class JuryNarrativeService:
    """Builds guided jury story from canonical case state."""

    NEGATIVE_CASES = [
        {"id": "B07", "title": "Insufficient evidence", "outcome": "INSUFFICIENT_EVIDENCE"},
        {"id": "B14", "title": "No viable opportunities", "outcome": "NOT_CURRENTLY_VIABLE"},
        {"id": "B20", "title": "Displaced worker — domain mismatch", "outcome": "NOT_CURRENTLY_VIABLE"},
    ]

    def build(self, state: dict[str, Any]) -> dict[str, Any]:
        diagnosis = state.get("diagnosis_summary") or {}
        card = state.get("decision_card") or {}
        gaps = [g.get("skill_id") or g.get("label") for g in state.get("capability_gaps", []) if g.get("gap_status") == "GENUINE_CAPABILITY_GAP"]
        proxies = card.get("potential_proxies") or []
        constraints = card.get("workplace_constraints") or []
        pathway = state.get("learning_path") or {}
        proof = state.get("proof_result") or {}
        viability = self._primary_viability(state)
        employer = self._primary_employer(state)
        sap_mode = (state.get("sap_case_context") or {}).get("source_mode", "SIMULATED")
        engine = state.get("engine_mode", "DEMO_FALLBACK")

        return {
            "rejection_story": {
                "title": "Why was she rejected?",
                "traditional_filters": [
                    "Career gap after caregiving break",
                    "Continuous experience requirement (3 years)",
                    "5-day Bangalore office requirement",
                    "Power BI not evidenced at required level",
                ],
                "rework_discovery": [
                    "Strong analytics capability evidenced (SQL, Excel, MIS projects)",
                    f"Genuine gap: {', '.join(gaps) or 'Power BI'}",
                    f"Potential eligibility proxy: {', '.join(proxies) or 'continuous experience'}",
                    f"Workplace constraint: {', '.join(constraints) or 'onsite location'}",
                    "Counterfactual: capability can be demonstrated via proof-of-skill",
                    f"Minimum-effective pathway: {pathway.get('title') or pathway.get('id') or 'learning + proof'}",
                ],
            },
            "what_can_change": {
                "title": "What can change?",
                "note": "Intervention scenarios are SIMULATED PROJECTIONS — not guarantees.",
                "minimum_intervention": (state.get("intervention_simulation") or {}).get("minimum_effective_intervention"),
            },
            "what_proves_it": {
                "title": "What proves it?",
                "proof_status": proof.get("result", "PENDING"),
                "skill": proof.get("skill_id", "power_bi"),
                "source_mode": (proof.get("source_mode") or "SYNTHETIC"),
                "is_demo": proof.get("is_demo", True),
            },
            "who_decides": {
                "title": "Who decides?",
                "ai_recommendation": card.get("what") or diagnosis.get("headline"),
                "human_decision_required": True,
            },
            "sap_boundary": {
                "title": "Where SAP ends. RE:WORK begins.",
                "sap": [
                    "Workforce context",
                    "Skills / attributes",
                    "Learning catalog",
                    "Opportunity context",
                    "Enterprise workflow",
                ],
                "rework": [
                    "Evidence reasoning",
                    "Capability diagnosis",
                    "Counterfactuals",
                    "Intervention simulation",
                    "Proof-of-skill",
                    "Two-sided readiness",
                    "Explainability",
                    "Human governance",
                ],
                "connected_by": "LangGraph agent orchestration",
                "source_mode": sap_mode,
            },
            "engine_labels": {
                "candidate_intelligence": engine,
                "job_decomposition": engine,
                "diagnosis": "DETERMINISTIC_ENGINE",
                "pathway": "DETERMINISTIC_ENGINE",
                "proof": "DETERMINISTIC_ENGINE" if proof else "PENDING",
                "viability": "DETERMINISTIC_ENGINE",
                "sap": f"SAP_{sap_mode}",
                "market": "SYNTHETIC",
            },
            "evidence_chain_example": self._power_bi_chain(state),
            "employer_readiness": employer.get("overall_state") if employer else "UNKNOWN",
            "projected_viability": viability.get("viability_state") if viability else "UNKNOWN",
            "negative_case_options": self.NEGATIVE_CASES,
        }

    def build_negative_case(self, scenario_id: str) -> dict[str, Any]:
        from app.services.benchmark_runner import BenchmarkRunner
        from app.services.benchmark_scenarios import all_scenarios

        scenario = next((s for s in all_scenarios() if s["id"] == scenario_id), None)
        if not scenario:
            return {"error": f"Unknown scenario: {scenario_id}"}

        runner = BenchmarkRunner()
        result = runner._run_scenario(scenario)
        return {
            "scenario_id": scenario_id,
            "title": scenario["title"],
            "outcome": result["actual"]["diagnosis_state"],
            "message": (
                "RE:WORK does not force a positive outcome when evidence or capability "
                "does not support viability."
            ),
            "actual": result["actual"],
            "expected": scenario.get("expected", {}),
            "governance_violations": result.get("governance_violations", []),
            "source_mode": "SYNTHETIC",
        }

    def _primary_viability(self, state: dict) -> dict:
        for v in state.get("opportunity_viability", []):
            if v.get("opportunity_id") == "opp-data-analyst":
                return v
        items = state.get("opportunity_viability", [])
        return items[0] if items else {}

    def _primary_employer(self, state: dict) -> dict:
        for e in state.get("employer_readiness", []):
            if e.get("opportunity_id") == "opp-data-analyst":
                return e
        items = state.get("employer_readiness", [])
        return items[0] if items else {}

    def _power_bi_chain(self, state: dict) -> list[dict[str, str]]:
        return [
            {"step": "Claim", "value": "Power BI is the primary capability gap"},
            {"step": "Diagnosis", "value": (state.get("diagnosis_summary") or {}).get("overall_diagnosis_state", "")},
            {"step": "Job requirement", "value": "Dashboard / reporting task"},
            {"step": "Candidate capability", "value": "Power BI — supported but below required proficiency"},
            {"step": "Evidence", "value": ", ".join((state.get("decision_card") or {}).get("evidence_refs", [])[:3]) or "candidate evidence"},
            {"step": "Source", "value": "REWORK (derived from evidence + job decomposition)"},
        ]
