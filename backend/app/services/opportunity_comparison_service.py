"""Opportunity comparison and recommended next step."""

from app.domain.enums import SourceMode, ViabilityState
from app.domain.opportunity_viability import (
    OpportunityComparison,
    OpportunityComparisonItem,
    OpportunityViability,
)


class OpportunityComparisonService:
    """Compare opportunities — recommends next step, not 'best job'."""

    def compare(
        self,
        candidate_id: str,
        viabilities: list[OpportunityViability],
        pathway_weeks: dict[str, float],
        title_map: dict[str, str] | None = None,
    ) -> OpportunityComparison:
        title_map = title_map or {}
        items: list[OpportunityComparisonItem] = []
        for v in viabilities:
            weeks = pathway_weeks.get(v.opportunity_id)
            items.append(
                OpportunityComparisonItem(
                    opportunity_id=v.opportunity_id,
                    title=title_map.get(v.opportunity_id, v.opportunity_id),
                    viability_state=v.viability_state,
                    capability_fit=v.dimensions.capability_fit,
                    pathway_effort_weeks=weeks,
                    proof_effort=v.dimensions.proof_effort,
                    employer_readiness=v.dimensions.employer_readiness,
                    market_opportunity=v.dimensions.market_opportunity,
                    key_barriers=v.candidate_gaps + v.candidate_barriers[:2],
                    key_advantages=self._advantages(v),
                    next_action=self._next_action(v),
                    confidence=v.confidence,
                )
            )

        fastest = self._pick_fastest(items)
        medium = self._pick_medium_term(items)
        highest_effort = self._pick_highest_effort(items)

        rationale_fast = ""
        if fastest:
            item = next(i for i in items if i.opportunity_id == fastest)
            rationale_fast = (
                f"{item.title} offers the fastest viable transition "
                f"(fit {item.capability_fit:.2f}, effort ~{item.pathway_effort_weeks or 2} weeks)."
            )

        return OpportunityComparison(
            id=f"opp-comparison-{candidate_id}",
            candidate_id=candidate_id,
            items=items,
            recommended_next_step_opportunity_id=fastest,
            recommended_next_step_rationale=rationale_fast,
            medium_term_opportunity_id=medium,
            medium_term_rationale=self._medium_rationale(items, medium),
            highest_effort_opportunity_id=highest_effort,
            confidence=round(sum(i.confidence for i in items) / max(len(items), 1), 2),
            source_mode=SourceMode.SYNTHETIC,
        )

    def _advantages(self, v: OpportunityViability) -> list[str]:
        adv = []
        if v.dimensions.capability_fit >= 0.75:
            adv.append("Strong capability fit")
        if v.dimensions.employer_readiness >= 0.75:
            adv.append("Employer readiness supportive")
        if v.dimensions.workplace_compatibility >= 0.8:
            adv.append("Compatible work mode")
        if not v.candidate_gaps:
            adv.append("No critical capability gaps")
        return adv

    def _next_action(self, v: OpportunityViability) -> str:
        if v.viability_state == ViabilityState.IMMEDIATELY_VIABLE:
            return "Explore application with human review."
        if v.proof_required:
            return "Complete proof-of-skill before pursuing."
        if v.pathway_reference:
            return "Follow linked learning pathway."
        return "Gather additional evidence or consult HR."

    def _pick_fastest(self, items: list[OpportunityComparisonItem]) -> str | None:
        viable = [
            i for i in items
            if i.viability_state in {
                ViabilityState.IMMEDIATELY_VIABLE,
                ViabilityState.VIABLE_WITH_TARGETED_PATHWAY,
            }
        ]
        if not viable:
            return items[0].opportunity_id if items else None
        viable.sort(key=lambda i: (i.pathway_effort_weeks or 99, -i.capability_fit))
        return viable[0].opportunity_id

    def _pick_medium_term(self, items: list[OpportunityComparisonItem]) -> str | None:
        data_analyst = next((i for i in items if "data-analyst" in i.opportunity_id), None)
        if data_analyst:
            return data_analyst.opportunity_id
        items.sort(key=lambda i: -i.capability_fit)
        return items[0].opportunity_id if items else None

    def _pick_highest_effort(self, items: list[OpportunityComparisonItem]) -> str | None:
        if not items:
            return None
        items.sort(key=lambda i: -(i.pathway_effort_weeks or 0))
        return items[0].opportunity_id

    def _medium_rationale(
        self,
        items: list[OpportunityComparisonItem],
        opp_id: str | None,
    ) -> str | None:
        if not opp_id:
            return None
        item = next((i for i in items if i.opportunity_id == opp_id), None)
        if not item:
            return None
        return (
            f"{item.title} aligns strongly with core capabilities "
            f"with manageable development effort."
        )
