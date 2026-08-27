"""Orchestrates market intelligence, viability, and opportunity comparison."""

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import GapStatus, SourceMode
from app.domain.opportunity_viability import (
    EmployerReadinessAssessment,
    MarketIntelligenceSignal,
    OpportunityCounterfactual,
    OpportunityViability,
    SkillInvestmentScenario,
)
from app.services.employer_readiness_engine import EmployerReadinessEngine
from app.services.fixture_service import FixtureService
from app.services.market_intelligence_engine import MarketIntelligenceEngine
from app.services.opportunity_comparison_service import OpportunityComparisonService
from app.services.opportunity_viability_engine import OpportunityViabilityEngine


class OpportunityAnalysisService:
    """Full opportunity viability analysis — not job matching."""

    def __init__(self) -> None:
        self._fixtures = FixtureService()
        self._market = MarketIntelligenceEngine(self._fixtures)
        self._employer = EmployerReadinessEngine(self._fixtures)
        self._viability = OpportunityViabilityEngine()
        self._comparison = OpportunityComparisonService()

    def run(
        self,
        candidate_id: str,
        candidate_capabilities: list[CandidateCapability],
        candidate_evidence: list[CandidateEvidence],
        requirement_diagnoses: list[dict],
        learning_path: dict | None,
        proof_result: dict | None,
        run_id: str | None = None,
    ) -> dict:
        opportunities = self._fixtures.get_opportunity_catalog()
        signals = self._market.load_signals()

        evidence_by_id = {e.id: e for e in candidate_evidence}
        prof_map = {c.skill_id: c.proficiency for c in candidate_capabilities}
        skill_ids = list(prof_map.keys())

        skill_investments = self._market.analyze_skill_investments(
            candidate_id,
            skill_ids,
            prof_map,
            [o.job_id for o in opportunities],
        )

        barriers = [
            d.get("requirement", "")[:80]
            for d in requirement_diagnoses
            if d.get("diagnosis_type") in {"ELIGIBILITY_PROXY", "WORKPLACE_CONSTRAINT"}
        ]

        pathway_ref = learning_path.get("id") if learning_path else None
        pathway_weeks = learning_path.get("duration_weeks") if learning_path else None
        proof_ref = proof_result.get("id") if proof_result else None
        proof_passed = proof_result and proof_result.get("result") == "PASSED"

        employer_assessments: list[EmployerReadinessAssessment] = []
        viabilities: list[OpportunityViability] = []
        counterfactuals: list[OpportunityCounterfactual] = []
        pathway_weeks_map: dict[str, float] = {}

        for opp in opportunities:
            employer = self._employer.assess(opp.id)
            if employer:
                employer_assessments.append(employer)
            employer_score = self._employer.readiness_score(employer)

            market_score = self._market.market_opportunity_score(opp.job_id, signals)

            opp_pathway_ref = pathway_ref if (
                learning_path and learning_path.get("target_role_id") == opp.job_id
            ) else None
            opp_pathway_weeks = pathway_weeks if opp_pathway_ref else (
                8.0 if "power_bi" in opp.capability_skill_ids else 4.0
            )
            if opp.id == "opp-operations-analyst":
                opp_pathway_weeks = 2.0
            elif opp.id == "opp-bi-analyst":
                opp_pathway_weeks = 12.0
            pathway_weeks_map[opp.id] = opp_pathway_weeks

            viability, _ = self._viability.assess_opportunity(
                candidate_id=candidate_id,
                opportunity=opp,
                candidate_capabilities=candidate_capabilities,
                candidate_evidence_by_id=evidence_by_id,
                employer_assessment_id=employer.id if employer else None,
                employer_score=employer_score,
                market_score=market_score,
                pathway_reference=opp_pathway_ref,
                proof_reference=proof_ref if opp_pathway_ref else None,
                proof_passed=bool(proof_passed and opp_pathway_ref),
                pathway_weeks=opp_pathway_weeks,
                candidate_barriers=barriers,
                run_id=run_id,
            )
            viabilities.append(viability)

            if employer:
                cf = self._viability.build_counterfactual(
                    viability,
                    [i.recommendation for i in employer.interventions],
                )
                counterfactuals.append(cf)

        comparison = self._comparison.compare(
            candidate_id,
            viabilities,
            pathway_weeks_map,
            {o.id: o.title for o in opportunities},
        )

        return {
            "market_signals": signals,
            "skill_investments": skill_investments,
            "opportunities": opportunities,
            "opportunity_viability": viabilities,
            "employer_readiness": employer_assessments,
            "opportunity_comparison": comparison,
            "opportunity_counterfactuals": counterfactuals,
        }
