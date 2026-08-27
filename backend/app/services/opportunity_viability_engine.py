"""Opportunity viability calculation — not job matching."""

from app.domain.assessment import CapabilityAssessmentItem
from app.domain.candidate import CandidateCapability
from app.domain.enums import GapStatus, SourceMode, ViabilityState
from app.domain.job import JobCapability
from app.domain.opportunity_viability import (
    OpportunityCatalogEntry,
    OpportunityCounterfactual,
    OpportunityViability,
    ViabilityDimensions,
)
from app.services.capability_gap_engine import CapabilityGapEngine
from app.services.employer_readiness_engine import EmployerReadinessEngine
from app.services.evidence_strength import compute_evidence_strength
from app.services.market_intelligence_engine import MarketIntelligenceEngine


class OpportunityViabilityEngine:
    """Determine HOW and UNDER WHAT CONDITIONS a candidate can reach an opportunity."""

    def __init__(self) -> None:
        self._gap_engine = CapabilityGapEngine()
        self._employer_engine = EmployerReadinessEngine()
        self._market_engine = MarketIntelligenceEngine()

    def assess_opportunity(
        self,
        candidate_id: str,
        opportunity: OpportunityCatalogEntry,
        candidate_capabilities: list[CandidateCapability],
        candidate_evidence_by_id: dict,
        employer_assessment_id: str | None,
        employer_score: float,
        market_score: float,
        pathway_reference: str | None,
        proof_reference: str | None,
        proof_passed: bool,
        pathway_weeks: float | None,
        candidate_barriers: list[str],
        run_id: str | None = None,
    ) -> tuple[OpportunityViability, list[CapabilityAssessmentItem]]:
        job_caps = [
            JobCapability(
                id=f"jcap-{opportunity.job_id}-{skill}",
                job_id=opportunity.job_id,
                skill_id=skill,
                label=skill.replace("_", " ").title(),
                min_proficiency=opportunity.min_proficiency.get(skill, 0.55),
                importance="core",
            )
            for skill in opportunity.capability_skill_ids
        ]

        assessment, gaps = self._gap_engine.assess(
            candidate_id=candidate_id,
            job_id=opportunity.job_id,
            job_capabilities=job_caps,
            candidate_capabilities=candidate_capabilities,
            evidence_by_id=candidate_evidence_by_id,
            run_id=run_id,
        )

        capability_fit = self._avg_fit(assessment.items)
        evidence_strength = self._avg_evidence(assessment.items, candidate_capabilities, candidate_evidence_by_id)
        genuine_gaps = [i.skill_id for i in assessment.items if i.gap_status == GapStatus.GENUINE_CAPABILITY_GAP]
        insufficient = [i.skill_id for i in assessment.items if i.gap_status == GapStatus.INSUFFICIENT_EVIDENCE]

        skill_gap_effort = min(1.0, len(genuine_gaps) * 0.25 + len(insufficient) * 0.15)
        pathway_effort_weeks = pathway_weeks or (8.0 if genuine_gaps else 2.0)
        skill_gap_effort = min(1.0, pathway_effort_weeks / 12.0)

        proof_required = bool(genuine_gaps) and not proof_passed
        proof_effort = 0.2 if proof_passed else (0.7 if proof_required else 0.3)

        workplace_compat = self._workplace_compatibility(opportunity, candidate_work_modes=None)
        readiness = capability_fit * 0.5 + evidence_strength * 0.3 + (1 - skill_gap_effort) * 0.2
        if proof_passed and genuine_gaps:
            readiness = min(1.0, readiness + 0.15)

        dimensions = ViabilityDimensions(
            capability_fit=round(capability_fit, 2),
            evidence_strength=round(evidence_strength, 2),
            readiness=round(readiness, 2),
            skill_gap_effort=round(skill_gap_effort, 2),
            proof_effort=round(proof_effort, 2),
            workplace_compatibility=round(workplace_compat, 2),
            employer_readiness=round(employer_score, 2),
            market_opportunity=round(market_score, 2),
        )

        viability_state = self._determine_state(
            dimensions,
            genuine_gaps,
            insufficient,
            employer_score,
            workplace_compat,
            proof_required,
            proof_passed,
            candidate_barriers,
        )

        interventions = []
        if employer_score < 0.7:
            interventions.append("Employer readiness improvements may be needed.")

        viability = OpportunityViability(
            id=f"viability-{candidate_id}-{opportunity.id}",
            candidate_id=candidate_id,
            opportunity_id=opportunity.id,
            target_role_id=opportunity.job_id,
            dimensions=dimensions,
            candidate_gaps=genuine_gaps,
            candidate_barriers=candidate_barriers,
            employer_requirements=opportunity.experience_requirements,
            employer_readiness_id=employer_assessment_id,
            recommended_interventions=interventions,
            pathway_reference=pathway_reference if genuine_gaps else None,
            proof_reference=proof_reference if proof_passed else None,
            proof_required=proof_required,
            viability_state=viability_state,
            confidence=round((dimensions.readiness + employer_score) / 2, 2),
            rationale=self._rationale(opportunity, dimensions, viability_state, genuine_gaps),
            evidence_refs=[e for c in candidate_capabilities for e in c.evidence_refs],
            source_mode=SourceMode.SYNTHETIC,
        )
        return viability, assessment.items

    def build_counterfactual(
        self,
        viability: OpportunityViability,
        employer_interventions: list[str],
    ) -> OpportunityCounterfactual:
        changes: list[str] = []
        if viability.candidate_gaps:
            for gap in viability.candidate_gaps:
                changes.append(f"Close {gap.replace('_', ' ')} capability gap via targeted pathway.")
        if viability.proof_required:
            changes.append("Complete defined proof-of-skill assessment.")
        if viability.dimensions.employer_readiness < 0.7:
            changes.extend(employer_interventions[:2])
        if viability.dimensions.workplace_compatibility < 0.6:
            changes.append("Resolve workplace mode compatibility with employer policy.")

        target = ViabilityState.VIABLE_WITH_PATHWAY_AND_ADAPTATION
        if not viability.candidate_gaps and viability.dimensions.employer_readiness >= 0.7:
            target = ViabilityState.IMMEDIATELY_VIABLE
        elif viability.candidate_gaps and viability.dimensions.employer_readiness >= 0.7:
            target = ViabilityState.VIABLE_WITH_TARGETED_PATHWAY

        return OpportunityCounterfactual(
            id=f"opp-cf-{viability.opportunity_id}",
            candidate_id=viability.candidate_id,
            opportunity_id=viability.opportunity_id,
            current_viability_state=viability.viability_state,
            target_viability_state=target,
            required_changes=changes,
            confidence=viability.confidence,
            human_review_required=True,
            rationale="Counterfactual lists changes that could improve opportunity viability.",
            source_mode=SourceMode.SYNTHETIC,
        )

    def _determine_state(
        self,
        d: ViabilityDimensions,
        genuine_gaps: list[str],
        insufficient: list[str],
        employer_score: float,
        workplace_compat: float,
        proof_required: bool,
        proof_passed: bool,
        barriers: list[str],
    ) -> ViabilityState:
        if barriers and any("proxy" in b.lower() or "eligibility" in b.lower() for b in barriers):
            if genuine_gaps:
                return ViabilityState.REQUIRES_HUMAN_REVIEW
        if insufficient and len(insufficient) > len(genuine_gaps):
            return ViabilityState.INSUFFICIENT_EVIDENCE
        if not genuine_gaps and d.capability_fit >= 0.75 and employer_score >= 0.7:
            return ViabilityState.IMMEDIATELY_VIABLE
        if genuine_gaps and proof_passed and d.capability_fit >= 0.7:
            return ViabilityState.VIABLE_WITH_TARGETED_PATHWAY
        if genuine_gaps and employer_score < 0.6:
            return ViabilityState.VIABLE_WITH_PATHWAY_AND_ADAPTATION
        if genuine_gaps and employer_score >= 0.65:
            return ViabilityState.VIABLE_WITH_TARGETED_PATHWAY
        if workplace_compat < 0.5:
            return ViabilityState.VIABLE_WITH_EMPLOYER_ADAPTATION
        if genuine_gaps:
            return ViabilityState.VIABLE_WITH_TARGETED_PATHWAY
        if d.capability_fit < 0.4:
            return ViabilityState.NOT_CURRENTLY_VIABLE
        return ViabilityState.REQUIRES_HUMAN_REVIEW

    def _workplace_compatibility(
        self,
        opportunity: OpportunityCatalogEntry,
        candidate_work_modes: list[str] | None,
    ) -> float:
        if "hybrid" in opportunity.work_modes or "remote" in opportunity.work_modes:
            return 0.85
        if "onsite" in opportunity.work_modes:
            return 0.55
        return 0.7

    def _avg_fit(self, items: list[CapabilityAssessmentItem]) -> float:
        if not items:
            return 0.0
        scores = []
        for i in items:
            if i.gap_status == GapStatus.MATCHED:
                scores.append(1.0)
            elif i.gap_status == GapStatus.GENUINE_CAPABILITY_GAP:
                req = i.required_proficiency
                cand = i.candidate_proficiency or 0
                scores.append(cand / req if req > 0 else 0)
            else:
                scores.append(0.4)
        return sum(scores) / len(scores)

    def _avg_evidence(
        self,
        items: list[CapabilityAssessmentItem],
        caps: list[CandidateCapability],
        evidence_by_id: dict,
    ) -> float:
        cap_by_skill = {c.skill_id: c for c in caps}
        strengths = []
        for item in items:
            cap = cap_by_skill.get(item.skill_id)
            strengths.append(compute_evidence_strength(cap, evidence_by_id))
        return sum(strengths) / len(strengths) if strengths else 0.4

    def _rationale(
        self,
        opportunity: OpportunityCatalogEntry,
        d: ViabilityDimensions,
        state: ViabilityState,
        gaps: list[str],
    ) -> str:
        gap_text = ", ".join(gaps) if gaps else "no critical capability gaps"
        return (
            f"{opportunity.title}: viability {state.value}. "
            f"Capability fit {d.capability_fit:.2f}, gaps: {gap_text}. "
            f"Employer readiness {d.employer_readiness:.2f}, market {d.market_opportunity:.2f}."
        )
