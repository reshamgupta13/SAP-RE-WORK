"""Employer readiness assessment — two-sided viability."""

from app.domain.enums import SourceMode
from app.domain.opportunity_viability import (
    EmployerIntervention,
    EmployerReadinessAssessment,
    EmployerReadinessFactor,
)
from app.services.fixture_service import FixtureService

READY_SCORE = {"READY": 1.0, "PARTIALLY_READY": 0.6, "NOT_READY": 0.2, "UNKNOWN": 0.4}


class EmployerReadinessEngine:
    """Assess whether employer context supports realistic pathway execution."""

    def __init__(self, fixture_service: FixtureService | None = None) -> None:
        self._fixtures = fixture_service or FixtureService()

    def assess(self, opportunity_id: str) -> EmployerReadinessAssessment | None:
        employer_data = self._fixtures.get_employer_for_opportunity(opportunity_id)
        if not employer_data:
            return None

        factors = [
            EmployerReadinessFactor(
                id=f"erf-{opportunity_id}-{f['factor']}",
                factor=f["factor"],
                status=f["status"],
                source="REWORK",
                confidence=f.get("confidence", 0.5),
                human_review_required=f.get("human_review_required", False),
                evidence_ref=f.get("evidence_ref"),
            )
            for f in employer_data.get("factors", [])
        ]

        scores = [READY_SCORE.get(f.status, 0.4) for f in factors]
        avg = sum(scores) / len(scores) if scores else 0.4
        unknown_count = sum(1 for f in factors if f.status == "UNKNOWN")
        not_ready = sum(1 for f in factors if f.status == "NOT_READY")

        if not_ready > 0:
            overall = "NOT_READY"
        elif unknown_count > len(factors) / 2:
            overall = "UNKNOWN"
        elif avg >= 0.75:
            overall = "READY"
        elif avg >= 0.55:
            overall = "PARTIALLY_READY"
        else:
            overall = "NOT_READY"

        interventions = self._generate_interventions(factors)

        return EmployerReadinessAssessment(
            id=f"employer-readiness-{opportunity_id}",
            opportunity_id=opportunity_id,
            employer_id=employer_data.get("id"),
            overall_state=overall,
            factors=factors,
            interventions=interventions,
            confidence=round(avg, 2),
            source_mode=SourceMode.SYNTHETIC,
        )

    def readiness_score(self, assessment: EmployerReadinessAssessment | None) -> float:
        if not assessment:
            return 0.4
        return assessment.confidence

    def _generate_interventions(
        self,
        factors: list[EmployerReadinessFactor],
    ) -> list[EmployerIntervention]:
        interventions: list[EmployerIntervention] = []
        for factor in factors:
            if factor.status == "NOT_READY":
                interventions.append(
                    EmployerIntervention(
                        id=f"intervention-{factor.id}",
                        issue=f"{factor.factor} is not ready.",
                        recommendation=self._recommendation_for(factor.factor),
                        confidence=0.7,
                        human_review_required=True,
                    )
                )
            elif factor.status == "PARTIALLY_READY":
                interventions.append(
                    EmployerIntervention(
                        id=f"intervention-{factor.id}",
                        issue=f"{factor.factor} is only partially ready.",
                        recommendation=self._recommendation_for(factor.factor),
                        confidence=0.65,
                        human_review_required=True,
                    )
                )
            elif factor.status == "UNKNOWN":
                interventions.append(
                    EmployerIntervention(
                        id=f"intervention-{factor.id}",
                        issue=f"{factor.factor} status is unknown.",
                        recommendation="Confirm employer policy with HR before assuming support.",
                        confidence=0.5,
                        human_review_required=True,
                    )
                )
        return interventions

    def _recommendation_for(self, factor: str) -> str:
        mapping = {
            "MENTORSHIP_AVAILABLE": "Add a 30-day mentor pairing for returning professionals.",
            "STRUCTURED_ONBOARDING": "Introduce structured onboarding with clear 30/60/90 expectations.",
            "HYBRID_OR_REMOTE": "Evaluate hybrid or remote arrangement for task-compatible responsibilities.",
            "FLEXIBLE_WORK": "Offer flexible scheduling where core tasks permit.",
            "PHASED_RESPONSIBILITY": "Introduce phased responsibility ramp rather than immediate full ownership.",
            "LEARNING_SUPPORT": "Provide learning time allocation during transition period.",
            "PROOF_OF_SKILL_ACCEPTANCE": "Accept proof-of-skill assessments as alternative validation.",
            "ACCESSIBILITY_SUPPORT": "Confirm accessibility accommodations with HR and facilities.",
            "MANAGER_SUPPORT": "Clarify manager support expectations during transition.",
        }
        return mapping.get(factor, "Review employer readiness factor with HR.")
