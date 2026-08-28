"""Agent orchestrator view — visible agent execution with SAP traceability."""

from typing import Any

from app.domain.enums import AuditStatus

ORCHESTRATOR_NODES: list[dict[str, str]] = [
    {"agent": "load_candidate", "label": "SAP Context Load", "stage": "DISCOVER", "kind": "integration"},
    {"agent": "candidate_intelligence", "label": "Candidate Intelligence", "stage": "DISCOVER", "kind": "agent"},
    {"agent": "load_job", "label": "Role Context Load", "stage": "DECOMPOSE", "kind": "integration"},
    {"agent": "job_decomposition", "label": "Job Decomposition", "stage": "DECOMPOSE", "kind": "agent"},
    {"agent": "diagnosis", "label": "Diagnosis", "stage": "DIAGNOSE", "kind": "engine"},
    {"agent": "counterfactual_analysis", "label": "Counterfactual", "stage": "COUNTERFACTUAL", "kind": "engine"},
    {"agent": "pathway_generation", "label": "Pathway", "stage": "DEVELOP", "kind": "engine"},
    {"agent": "proof_of_skill", "label": "Proof", "stage": "PROVE", "kind": "engine"},
    {"agent": "capability_refresh", "label": "Capability Update", "stage": "PROVE", "kind": "integration"},
    {"agent": "reassessment", "label": "Reassessment", "stage": "REASSESS", "kind": "engine"},
    {"agent": "market_intelligence", "label": "Market", "stage": "MARKET", "kind": "engine"},
    {"agent": "opportunity_viability", "label": "Opportunity", "stage": "VIABILITY", "kind": "engine"},
    {"agent": "employer_readiness", "label": "Employer Readiness", "stage": "VIABILITY", "kind": "engine"},
    {"agent": "intervention_simulation", "label": "Intervention", "stage": "INTERVENT", "kind": "engine"},
    {"agent": "explainability", "label": "Explainability", "stage": "EXPLAIN", "kind": "engine"},
]

NODE_INPUT_SOURCES: dict[str, list[str]] = {
    "load_candidate": ["SAP Adapter", "Candidate Fixture"],
    "candidate_intelligence": ["SAP Workforce Context", "Candidate Evidence", "SAP Skills (if available)"],
    "load_job": ["SAP Role Context", "Job Fixture"],
    "job_decomposition": ["Job Profile", "SAP Role Context"],
    "diagnosis": ["Candidate Capabilities", "Job Requirements", "SAP Role Context", "Evidence"],
    "counterfactual_analysis": ["Diagnosis", "Requirement Analyses"],
    "pathway_generation": ["Capability Gaps", "SAP Learning Catalog"],
    "proof_of_skill": ["Learning Pathway", "Proof Assessment"],
    "capability_refresh": ["Proof Result", "SAP Skills API (simulated write-back)"],
    "reassessment": ["Updated Capabilities", "Job Requirements"],
    "market_intelligence": ["Market Fixtures", "Skill Investments"],
    "opportunity_viability": ["Reassessment", "SAP Opportunity Context"],
    "employer_readiness": ["Employer Fixtures", "Opportunity Context"],
    "intervention_simulation": ["Baseline Viability", "Employer Readiness"],
    "explainability": ["Full Pipeline State"],
}

NODE_OUTPUTS: dict[str, str] = {
    "load_candidate": "SAP case context + candidate profile",
    "candidate_intelligence": "Capability profile",
    "load_job": "Job profile",
    "job_decomposition": "Tasks, capabilities, requirements",
    "diagnosis": "Gaps, proxies, constraints",
    "counterfactual_analysis": "Counterfactual validations",
    "pathway_generation": "Minimum-effective learning pathway",
    "proof_of_skill": "Proof result + evidence",
    "capability_refresh": "Updated capability state",
    "reassessment": "Post-proof diagnosis",
    "market_intelligence": "Market signals",
    "opportunity_viability": "Viability assessment",
    "employer_readiness": "Employer readiness factors",
    "intervention_simulation": "Projected intervention scenarios",
    "explainability": "Decision card + reports",
}


class AgentOrchestrationService:
    """Builds inspectable agent execution view from graph audit events."""

    def build(self, state: dict[str, Any]) -> dict[str, Any]:
        audit_by_agent = self._index_audit(state.get("audit_events", []))
        sap_bundle = state.get("sap_case_context") or {}
        sap_mode = sap_bundle.get("source_mode") or (
            (state.get("sap_context") or {}).get("source_mode", "SIMULATED")
        )
        engine_mode = state.get("engine_mode", "DEMO_FALLBACK")

        nodes = []
        for spec in ORCHESTRATOR_NODES:
            agent = spec["agent"]
            audit = audit_by_agent.get(agent)
            status = self._status(audit)
            nodes.append({
                "agent": agent,
                "label": spec["label"],
                "stage": spec["stage"],
                "kind": spec["kind"],
                "status": status,
                "duration_ms": audit.get("latency_ms") if audit else None,
                "engine_mode": (audit or {}).get("engine_mode", engine_mode),
                "confidence": self._confidence_label(audit),
                "confidence_raw": audit.get("confidence") if audit else None,
                "evidence_count": self._evidence_count(agent, state, audit),
                "source_mode": sap_mode if spec["kind"] == "integration" else "REWORK",
                "input_sources": NODE_INPUT_SOURCES.get(agent, []),
                "output": NODE_OUTPUTS.get(agent, ""),
                "rationale": (audit or {}).get("rationale"),
                "error": (audit or {}).get("error"),
            })

        completed = sum(1 for n in nodes if n["status"] in {"completed", "skipped"})
        return {
            "orchestrator": "LangGraph",
            "engine_mode": engine_mode,
            "sap_source_mode": sap_mode,
            "progress": round(completed / max(len(nodes), 1), 2),
            "nodes": nodes,
            "sap_agent_flows": self._sap_flows(state),
            "human_governance": {
                "ai_recommendation": "Separate from human decision",
                "human_decision_required": True,
                "status": state.get("human_decision_status", "PENDING"),
            },
        }

    def _index_audit(self, events: list[dict]) -> dict[str, dict]:
        indexed: dict[str, dict] = {}
        for ev in events:
            agent = ev.get("agent")
            if agent:
                indexed[agent] = ev
        return indexed

    def _status(self, audit: dict | None) -> str:
        if not audit:
            return "pending"
        raw = audit.get("status", "")
        if raw == AuditStatus.SUCCESS.value:
            return "completed"
        if raw == AuditStatus.SKIPPED.value:
            return "skipped"
        if raw == AuditStatus.FAILURE.value:
            return "failed"
        return "pending"

    def _confidence_label(self, audit: dict | None) -> str:
        if not audit or audit.get("confidence") is None:
            return "UNCERTAIN"
        c = float(audit["confidence"])
        if c >= 0.75:
            return "HIGH"
        if c >= 0.55:
            return "MEDIUM"
        if c >= 0.35:
            return "LOW"
        return "UNCERTAIN"

    def _evidence_count(self, agent: str, state: dict, audit: dict | None) -> int:
        if agent == "candidate_intelligence":
            return len(state.get("candidate_evidence", []))
        if agent == "diagnosis":
            return len(state.get("candidate_evidence", []))
        if audit and audit.get("source_references"):
            return len(audit["source_references"])
        return 0

    def _sap_flows(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        bundle = state.get("sap_case_context") or {}
        sap_mode = bundle.get("source_mode", "SIMULATED")
        flows: list[dict[str, Any]] = []

        workforce = bundle.get("workforce_context", {})
        if workforce.get("status") == "AVAILABLE":
            flows.append({
                "flow": "SAP workforce context → Candidate Intelligence",
                "sap_input": "Workforce / growth portfolio context",
                "agent": "candidate_intelligence",
                "rework_output": "Evidence-backed capability profile",
                "source_mode": sap_mode,
                "note": workforce.get("data", {}).get("message")
                or "SAP context supplied; capabilities derived from evidence by RE:WORK",
            })

        role = bundle.get("role_context", {})
        if role.get("status") == "AVAILABLE" and role.get("data"):
            flows.append({
                "flow": "SAP role context → Job Decomposition → Diagnosis",
                "sap_input": "Role requirements context",
                "agent": "diagnosis",
                "rework_output": "Genuine gaps and eligibility proxies",
                "source_mode": sap_mode,
            })

        learning = bundle.get("learning_context", {})
        if learning.get("status") == "AVAILABLE":
            count = learning.get("item_count", 0)
            flows.append({
                "flow": "SAP Learning catalog → Pathway Engine",
                "sap_input": f"{count} learning items",
                "agent": "pathway_generation",
                "rework_output": "Minimum-effective pathway for diagnosed gap",
                "source_mode": sap_mode,
            })

        pathway = state.get("learning_path") or {}
        if pathway.get("learning_items"):
            first = pathway["learning_items"][0]
            flows.append({
                "flow": "Power BI gap → SAP Learning → Pathway",
                "sap_input": first.get("title", "Learning item"),
                "agent": "pathway_generation",
                "rework_output": pathway.get("id", "pathway"),
                "source_mode": first.get("source_mode", sap_mode),
            })

        opp = bundle.get("opportunity_context", {})
        if opp.get("status") == "AVAILABLE":
            flows.append({
                "flow": "SAP Opportunity context → Viability Engine",
                "sap_input": f"{opp.get('item_count', 0)} opportunities",
                "agent": "opportunity_viability",
                "rework_output": "Viability + intervention reasoning",
                "source_mode": sap_mode,
            })

        return flows
