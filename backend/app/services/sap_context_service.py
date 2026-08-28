"""Load SAP context for a case through the adapter layer only."""

from datetime import datetime, timezone
from typing import Any

from app.adapters.sap import get_sap_provider
from app.domain.sap import SAPContext


class SAPContextService:
    """Aggregates SAP reads into a canonical case bundle with provenance."""

    def load_for_case(self, candidate_id: str, job_id: str) -> dict[str, Any]:
        provider = get_sap_provider()
        now = datetime.now(timezone.utc).isoformat()
        system_ctx = provider.get_context()

        workforce = self._safe_call(
            lambda: provider.get_candidate_context(candidate_id),
            domain="workforce",
            source_mode=system_ctx.source_mode.value,
            retrieved_at=now,
        )
        skills = self._safe_call(
            lambda: [s.model_dump(mode="json") for s in provider.get_employee_skills(candidate_id)],
            domain="skills",
            source_mode=system_ctx.source_mode.value,
            retrieved_at=now,
        )
        role = self._safe_call(
            lambda: provider.get_role_context(job_id),
            domain="role",
            source_mode=system_ctx.source_mode.value,
            retrieved_at=now,
            transform=lambda r: r.model_dump(mode="json") if r else None,
        )
        learning = self._safe_call(
            lambda: [i.model_dump(mode="json") for i in provider.get_learning_items()],
            domain="learning",
            source_mode=system_ctx.source_mode.value,
            retrieved_at=now,
        )
        opportunities = self._safe_call(
            lambda: [o.model_dump(mode="json") for o in provider.get_opportunities()],
            domain="opportunity",
            source_mode=system_ctx.source_mode.value,
            retrieved_at=now,
        )

        return {
            "system": system_ctx.model_dump(mode="json"),
            "workforce_context": workforce,
            "skills_context": skills,
            "role_context": role,
            "learning_context": learning,
            "opportunity_context": opportunities,
            "source_mode": system_ctx.source_mode.value,
            "integration_status": system_ctx.integration_status.value,
            "retrieved_at": now,
        }

    def contribution_boundary(self, bundle: dict[str, Any] | None) -> dict[str, Any]:
        mode = (bundle or {}).get("source_mode", "SIMULATED")
        return {
            "sap": {
                "workforce": "Employee / candidate context from SuccessFactors",
                "skills": "Skills and attributes from Talent Intelligence / Growth Portfolio",
                "roles": "Role definitions and requirements context",
                "learning": "Learning catalog and development items",
                "opportunities": "Internal opportunity marketplace context",
                "enterprise": "Enterprise workflow and system-of-record",
            },
            "rework": {
                "evidence_synthesis": "Merge SAP skills with candidate-supplied evidence",
                "capability_diagnosis": "Genuine gaps vs proxies vs constraints",
                "counterfactuals": "Alternative validation paths for eligibility proxies",
                "minimum_effective_pathway": "Gap-bound learning + proof sequence",
                "proof_of_skill": "Capability verification before reassessment",
                "viability_reasoning": "Two-sided candidate + employer readiness",
                "intervention_simulation": "Projected outcomes — not guarantees",
                "explainability": "Traceable recommendation chains",
                "human_governance": "Human decision separate from AI recommendation",
            },
            "connected_by": "LangGraph agent orchestration",
            "source_mode": mode,
        }

    def _safe_call(
        self,
        fn,
        domain: str,
        source_mode: str,
        retrieved_at: str,
        transform=None,
    ) -> dict[str, Any]:
        try:
            raw = fn()
            data = transform(raw) if transform else raw
            count = len(data) if isinstance(data, list) else (1 if data else 0)
            return {
                "domain": domain,
                "source": "SAP",
                "source_mode": source_mode,
                "retrieved_at": retrieved_at,
                "status": "AVAILABLE",
                "item_count": count,
                "data": data,
            }
        except NotImplementedError as exc:
            return {
                "domain": domain,
                "source": "SAP",
                "source_mode": source_mode,
                "retrieved_at": retrieved_at,
                "status": "UNAVAILABLE",
                "item_count": 0,
                "data": None,
                "message": str(exc),
            }
        except Exception as exc:
            return {
                "domain": domain,
                "source": "SAP",
                "source_mode": source_mode,
                "retrieved_at": retrieved_at,
                "status": "ERROR",
                "item_count": 0,
                "data": None,
                "message": str(exc),
            }

    def parse_system_context(self, bundle: dict[str, Any] | None) -> SAPContext | None:
        if not bundle or not bundle.get("system"):
            return None
        return SAPContext.model_validate(bundle["system"])
