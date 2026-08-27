"""Market intelligence over structured synthetic signals."""

from app.domain.enums import SourceMode
from app.domain.opportunity_viability import MarketIntelligenceSignal, SkillInvestmentScenario
from app.services.fixture_service import FixtureService


class MarketIntelligenceEngine:
    """Reason over structured market signals — not fake labor statistics."""

    def __init__(self, fixture_service: FixtureService | None = None) -> None:
        self._fixtures = fixture_service or FixtureService()

    def load_signals(self) -> list[MarketIntelligenceSignal]:
        return self._fixtures.get_market_signals()

    def analyze_skill_investments(
        self,
        candidate_id: str,
        candidate_skill_ids: list[str],
        candidate_proficiency: dict[str, float],
        target_opportunity_ids: list[str],
    ) -> list[SkillInvestmentScenario]:
        signals = self.load_signals()
        investment_skills = ["power_bi", "python", "data_modeling"]
        scenarios: list[SkillInvestmentScenario] = []

        for skill in investment_skills:
            if skill in candidate_skill_ids and candidate_proficiency.get(skill, 0) >= 0.7:
                continue
            related = [s for s in signals if s.skill == skill or skill in (s.notes or "")]
            unlock_roles: set[str] = set()
            signal_refs: list[str] = []
            for sig in related:
                unlock_roles.update(sig.unlockable_role_ids)
                signal_refs.append(sig.id)
            if not unlock_roles:
                unlock_roles = set(target_opportunity_ids)

            current = candidate_proficiency.get(skill, 0.2)
            target = 0.65 if skill == "power_bi" else 0.6
            effort = round((target - current) * 16, 1) if current < target else 2.0

            scenarios.append(
                SkillInvestmentScenario(
                    id=f"invest-{candidate_id}-{skill}",
                    candidate_id=candidate_id,
                    investment_skill=skill,
                    current_proficiency=current,
                    target_proficiency=target,
                    unlockable_roles=sorted(unlock_roles),
                    additional_opportunities=[
                        r for r in unlock_roles if r not in target_opportunity_ids
                    ],
                    estimated_effort_weeks=max(2.0, effort / 4),
                    proof_requirement=f"assess-{skill}-{candidate_id}",
                    market_signal_refs=signal_refs,
                    confidence=0.72 if signal_refs else 0.5,
                    rationale=self._investment_rationale(skill, unlock_roles, signal_refs),
                    source_mode=SourceMode.SYNTHETIC,
                )
            )

        scenarios.sort(key=lambda s: len(s.unlockable_roles), reverse=True)
        return scenarios

    def market_opportunity_score(self, role_id: str, signals: list[MarketIntelligenceSignal]) -> float:
        role_signals = [s for s in signals if s.role_id == role_id or role_id in s.unlockable_role_ids]
        if not role_signals:
            return 0.5
        return round(max(s.strength for s in role_signals), 2)

    def _investment_rationale(
        self,
        skill: str,
        unlock_roles: set[str],
        signal_refs: list[str],
    ) -> str:
        label = skill.replace("_", " ").title()
        roles = ", ".join(sorted(unlock_roles)[:3])
        if signal_refs:
            return (
                f"{label} investment may unlock roles including {roles} "
                "based on synthetic market signals (demo data)."
            )
        return f"{label} may expand opportunity set under current catalog assumptions."
