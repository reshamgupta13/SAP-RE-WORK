"""Validate explainability reference integrity."""

from typing import Any


class ExplainabilityIntegrityService:
    def validate(self, state: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        evidence_ids = {e.get("id") for e in state.get("candidate_evidence", [])}
        capability_rows = state.get("updated_candidate_capabilities") or state.get("candidate_capabilities") or []
        cap_ids = {c.get("skill_id") for c in capability_rows}
        gap_ids = {
            g.get("skill_id")
            for g in state.get("capability_gaps", [])
            if g.get("skill_id")
        }
        task_ids = {t.get("id") for t in state.get("job_tasks", [])}

        explainability = state.get("explainability") or {}
        rec = explainability.get("reviewable_recommendation") or state.get("ai_recommendation") or {}

        for ref in rec.get("evidence_refs", []):
            if ref and ref not in evidence_ids:
                errors.append(f"Recommendation evidence ref missing: {ref}")

        pathway = state.get("learning_path")
        if pathway:
            for gap in pathway.get("gap_skill_ids", []):
                if gap not in cap_ids and gap not in gap_ids:
                    errors.append(f"Pathway gap not in capabilities: {gap}")

        proof = state.get("proof_result")
        if proof:
            skill = proof.get("skill_id")
            if skill and skill not in cap_ids:
                errors.append(f"Proof skill not in capabilities: {skill}")

        for report in explainability.get("reports", []):
            for ref in report.get("evidence_refs", []):
                if ref and ref not in evidence_ids:
                    errors.append(f"Explainability evidence ref missing: {ref}")

        human = state.get("human_decision") or {}
        if human.get("action") and not rec.get("recommendation_summary"):
            errors.append("Human decision without AI recommendation snapshot")

        if not errors and not cap_ids:
            errors.append("No candidate capabilities in state")

        return errors

    def assert_valid(self, state: dict[str, Any]) -> None:
        errors = self.validate(state)
        if errors:
            raise ValueError("Explainability integrity failed: " + "; ".join(errors))
