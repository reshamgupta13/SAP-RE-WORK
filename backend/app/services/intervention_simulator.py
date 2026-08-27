"""Intervention scenario simulation — SIMULATED PROJECTION, not guaranteed outcomes."""

import uuid
from typing import Any

from app.domain.candidate import CandidateCapability
from app.domain.enums import (
    CapabilityVerificationStatus,
    GapStatus,
    InterventionPriority,
    InterventionType,
    SourceMode,
    ViabilityState,
)
from app.domain.intervention import Intervention, InterventionBundle, InterventionEffect, Scenario
from app.domain.opportunity_viability import OpportunityCatalogEntry, OpportunityViability
from app.services.fixture_service import FixtureService
from app.services.opportunity_analysis_service import OpportunityAnalysisService


class InterventionSimulator:
    """Answer: what is the smallest evidence-based intervention that changes viability?"""

    DEFAULT_OPPORTUNITY = "opp-data-analyst"
    DEMO_ASSUMPTIONS = [
        "Learning pathway completed as scheduled.",
        "Proof-of-skill assessment passed at defined threshold.",
        "Employer maintains stated support posture.",
        "Role requirements remain unchanged during projection window.",
    ]

    def __init__(
        self,
        fixture_service: FixtureService | None = None,
        opportunity_service: OpportunityAnalysisService | None = None,
    ) -> None:
        self._fixtures = fixture_service or FixtureService()
        self._opportunity_service = opportunity_service or OpportunityAnalysisService()

    def run(
        self,
        candidate_id: str,
        opportunity_id: str,
        candidate_capabilities: list[CandidateCapability],
        candidate_evidence: list,
        requirement_diagnoses: list[dict[str, Any]],
        learning_path: dict[str, Any] | None,
        proof_result: dict[str, Any] | None,
        employer_readiness: list[dict[str, Any]],
        run_id: str | None = None,
        use_baseline_for_demo: bool = True,
    ) -> dict[str, Any]:
        catalog = self._fixtures.get_opportunity_catalog()
        opportunity = next((o for o in catalog if o.id == opportunity_id), None)
        if not opportunity:
            raise ValueError(f"Unknown opportunity: {opportunity_id}")

        sim_caps = list(candidate_capabilities)
        if use_baseline_for_demo and candidate_id == "ananya-sharma" and opportunity_id == self.DEFAULT_OPPORTUNITY:
            sim_caps = list(self._fixtures.get_ananya_bundle()["capabilities"])

        baseline_viability, baseline_gaps = self._assess_viability(
            candidate_id,
            opportunity,
            sim_caps,
            candidate_evidence,
            requirement_diagnoses,
            learning_path=None,
            proof_result=None,
            employer_readiness=employer_readiness,
            run_id=run_id,
        )

        interventions = self._build_intervention_catalog(
            opportunity_id,
            baseline_gaps,
            learning_path,
            proof_result,
            employer_readiness,
            opportunity,
        )

        base_scenario = self._base_scenario(
            candidate_id,
            opportunity_id,
            baseline_viability,
            run_id,
        )

        scenarios: list[Scenario] = [base_scenario]
        scenario_map: dict[str, Scenario] = {base_scenario.id: base_scenario}

        for intervention in interventions:
            if not self._is_valid(intervention, baseline_gaps, proof_result):
                continue
            scenario = self._simulate_single(
                intervention,
                candidate_id,
                opportunity,
                sim_caps,
                candidate_evidence,
                requirement_diagnoses,
                employer_readiness,
                baseline_viability,
                base_scenario.id,
                run_id,
            )
            scenarios.append(scenario)
            scenario_map[scenario.id] = scenario

        bundles, bundle_scenarios = self._build_bundles(
            interventions,
            candidate_id,
            opportunity,
            sim_caps,
            candidate_evidence,
            requirement_diagnoses,
            employer_readiness,
            baseline_viability,
            base_scenario.id,
            run_id,
        )
        for s in bundle_scenarios:
            if s.id not in scenario_map:
                scenarios.append(s)
                scenario_map[s.id] = s

        minimum = self._find_minimum_effective(scenarios, baseline_viability.viability_state)
        if minimum:
            for b in bundles:
                if minimum.intervention_ids and set(b.intervention_ids) == set(minimum.intervention_ids):
                    b.is_minimum_effective = True

        return {
            "interventions": [i.model_dump(mode="json") for i in interventions],
            "scenarios": [s.model_dump(mode="json") for s in scenarios],
            "bundles": [b.model_dump(mode="json") for b in bundles],
            "minimum_effective_intervention": minimum.model_dump(mode="json") if minimum else None,
            "baseline_viability_state": baseline_viability.viability_state.value,
            "is_simulated_projection": True,
            "label": "SIMULATED PROJECTION",
        }

    def simulate_custom(
        self,
        candidate_id: str,
        opportunity_id: str,
        intervention_types: list[InterventionType],
        state: dict[str, Any],
    ) -> dict[str, Any]:
        caps = [CandidateCapability.model_validate(c) for c in state.get("candidate_capabilities", [])]
        evidence = state.get("candidate_evidence", [])
        result = self.run(
            candidate_id=candidate_id,
            opportunity_id=opportunity_id,
            candidate_capabilities=caps,
            candidate_evidence=evidence,
            requirement_diagnoses=state.get("requirement_diagnoses", []),
            learning_path=state.get("learning_path"),
            proof_result=state.get("proof_result"),
            employer_readiness=state.get("employer_readiness", []),
            run_id=state.get("run_id"),
            use_baseline_for_demo=False,
        )
        catalog = {i["type"]: i for i in result["interventions"]}
        selected = []
        for t in intervention_types:
            item = catalog.get(t.value)
            if item:
                selected.append(item)
        if not selected:
            return {"error": "No valid interventions for requested types.", "is_simulated_projection": True}

        opportunity = next(
            o for o in self._fixtures.get_opportunity_catalog() if o.id == opportunity_id
        )
        baseline = OpportunityViability.model_validate(
            next(
                s for s in result["scenarios"]
                if s.get("parent_scenario_id") is None
            )
        )
        # Re-run bundle simulation for selected types only
        bundle_scenarios = self._simulate_bundle_types(
            [InterventionType(t) for t in intervention_types],
            candidate_id,
            opportunity,
            caps,
            evidence,
            state.get("requirement_diagnoses", []),
            state.get("employer_readiness", []),
            OpportunityViability.model_validate(
                next(s for s in result["scenarios"] if not s.get("parent_scenario_id"))
            ),
            result["scenarios"][0]["id"],
            state.get("run_id"),
        )
        return {
            "scenarios": [s.model_dump(mode="json") for s in bundle_scenarios],
            "is_simulated_projection": True,
            "label": "SIMULATED PROJECTION",
        }

    def _assess_viability(
        self,
        candidate_id: str,
        opportunity: OpportunityCatalogEntry,
        caps: list[CandidateCapability],
        evidence: list,
        requirement_diagnoses: list,
        learning_path: dict | None,
        proof_result: dict | None,
        employer_readiness: list,
        run_id: str | None,
    ) -> tuple[OpportunityViability, list[str]]:
        from app.domain.candidate import CandidateEvidence

        ev_objs = [CandidateEvidence.model_validate(e) for e in evidence]
        analysis = self._opportunity_service.run(
            candidate_id=candidate_id,
            candidate_capabilities=caps,
            candidate_evidence=ev_objs,
            requirement_diagnoses=requirement_diagnoses,
            learning_path=learning_path,
            proof_result=proof_result,
            run_id=run_id,
        )
        viability = next(
            v for v in analysis["opportunity_viability"] if v.opportunity_id == opportunity.id
        )
        return viability, viability.candidate_gaps

    def _build_intervention_catalog(
        self,
        opportunity_id: str,
        gaps: list[str],
        learning_path: dict | None,
        proof_result: dict | None,
        employer_readiness: list[dict],
        opportunity: OpportunityCatalogEntry,
    ) -> list[Intervention]:
        interventions: list[Intervention] = []

        if gaps:
            skill = gaps[0]
            weeks = learning_path.get("estimated_duration_weeks", 8) if learning_path else 8.0
            interventions.append(
                Intervention(
                    id=f"int-learning-{skill}",
                    type=InterventionType.LEARNING,
                    title=f"{skill.replace('_', ' ').title()} learning pathway",
                    description=f"Targeted learning to close {skill.replace('_', ' ')} capability gap.",
                    target=f"candidate:{skill}",
                    preconditions=[f"Genuine gap identified for {skill}."],
                    evidence_refs=[],
                    source_mode=SourceMode.SYNTHETIC,
                    estimated_effort_weeks=weeks,
                    expected_effect=f"Improve {skill} proficiency toward role threshold.",
                    confidence=0.72,
                    human_review_required=False,
                    priority=InterventionPriority.HIGH_IMPACT_HIGH_EFFORT,
                )
            )
            interventions.append(
                Intervention(
                    id=f"int-proof-{skill}",
                    type=InterventionType.PROOF_OF_SKILL,
                    title=f"{skill.replace('_', ' ').title()} proof-of-skill",
                    description="Structured assessment to verify demonstrated capability.",
                    target=f"candidate:{skill}",
                    preconditions=[f"Learning pathway in progress or completed for {skill}."],
                    evidence_refs=[],
                    source_mode=SourceMode.SYNTHETIC,
                    estimated_effort_weeks=1.0,
                    expected_effect=f"Verify {skill} capability with structured evidence.",
                    confidence=0.78,
                    human_review_required=True,
                    priority=InterventionPriority.HIGH_IMPACT_LOW_EFFORT,
                )
            )

        employer = next(
            (e for e in employer_readiness if e.get("opportunity_id") == opportunity_id),
            None,
        )
        employer_score = employer.get("confidence", 0.7) if employer else 0.7

        interventions.append(
            Intervention(
                id=f"int-mentorship-{opportunity_id}",
                type=InterventionType.MENTORSHIP,
                title="Assigned mentorship",
                description="Pair candidate with mentor for guided transition support.",
                target="employer:mentorship",
                preconditions=["Employer mentorship capacity available or can be arranged."],
                evidence_refs=[employer.get("id", "")] if employer else [],
                source_mode=SourceMode.SYNTHETIC,
                estimated_effort_weeks=12.0,
                expected_effect="Improve employer readiness and onboarding confidence.",
                confidence=0.65,
                human_review_required=True,
                priority=InterventionPriority.HIGH_IMPACT_HIGH_EFFORT,
            )
        )

        if "hybrid" in opportunity.work_modes or "remote" in opportunity.work_modes:
            interventions.append(
                Intervention(
                    id=f"int-hybrid-{opportunity_id}",
                    type=InterventionType.HYBRID_WORK,
                    title="Hybrid work arrangement",
                    description="Enable hybrid work mode for workplace compatibility.",
                    target="employer:work_mode",
                    preconditions=["Role supports hybrid or remote modes."],
                    evidence_refs=[],
                    source_mode=SourceMode.SYNTHETIC,
                    estimated_effort_weeks=0.5,
                    expected_effect="Improve workplace compatibility dimension only.",
                    confidence=0.7,
                    human_review_required=True,
                    priority=InterventionPriority.LOW_IMPACT_LOW_EFFORT,
                )
            )

        if employer_score < 0.75:
            interventions.append(
                Intervention(
                    id=f"int-onboarding-{opportunity_id}",
                    type=InterventionType.STRUCTURED_ONBOARDING,
                    title="Structured onboarding program",
                    description="Employer-led structured onboarding for role transition.",
                    target="employer:onboarding",
                    preconditions=["Employer can commit to structured onboarding."],
                    evidence_refs=[employer.get("id", "")] if employer else [],
                    source_mode=SourceMode.SYNTHETIC,
                    estimated_effort_weeks=4.0,
                    expected_effect="Improve employer readiness score.",
                    confidence=0.68,
                    human_review_required=True,
                    priority=InterventionPriority.HIGH_IMPACT_LOW_EFFORT,
                )
            )

        if not proof_result or proof_result.get("result") != "PASSED":
            interventions.append(
                Intervention(
                    id=f"int-evidence-sub-{opportunity_id}",
                    type=InterventionType.EVIDENCE_SUBSTITUTION,
                    title="Evidence substitution for experience proxy",
                    description=(
                        "Potential eligibility barrier reduced under this scenario: "
                        "replace continuous experience requirement with direct capability evidence."
                    ),
                    target="requirement:experience_proxy",
                    preconditions=["Counterfactual analysis flagged potential eligibility proxy."],
                    evidence_refs=[],
                    source_mode=SourceMode.SYNTHETIC,
                    estimated_effort_weeks=2.0,
                    expected_effect="Reduce potential eligibility proxy barrier under scenario.",
                    confidence=0.55,
                    human_review_required=True,
                    priority=InterventionPriority.UNKNOWN,
                )
            )

        return interventions

    def _is_valid(
        self,
        intervention: Intervention,
        gaps: list[str],
        proof_result: dict | None,
    ) -> bool:
        if intervention.type == InterventionType.LEARNING:
            return bool(gaps)
        if intervention.type == InterventionType.PROOF_OF_SKILL:
            return bool(gaps) and not (proof_result and proof_result.get("result") == "PASSED")
        if intervention.type in {
            InterventionType.MENTORSHIP,
            InterventionType.STRUCTURED_ONBOARDING,
            InterventionType.HYBRID_WORK,
            InterventionType.REMOTE_WORK,
        }:
            return True
        if intervention.type == InterventionType.EVIDENCE_SUBSTITUTION:
            return True
        return False

    def _base_scenario(
        self,
        candidate_id: str,
        opportunity_id: str,
        viability: OpportunityViability,
        run_id: str | None,
    ) -> Scenario:
        return Scenario(
            id=f"scenario-base-{opportunity_id}",
            candidate_id=candidate_id,
            opportunity_id=opportunity_id,
            label="Current state",
            parent_scenario_id=None,
            intervention_ids=[],
            intervention_types=[],
            assumptions=["Baseline from current assessed state."],
            before_viability_state=viability.viability_state,
            after_viability_state=viability.viability_state,
            effect=None,
            total_effort_weeks=0.0,
            confidence=viability.confidence,
            is_simulated_projection=True,
            source_mode=SourceMode.SYNTHETIC,
        )

    def _simulate_single(
        self,
        intervention: Intervention,
        candidate_id: str,
        opportunity: OpportunityCatalogEntry,
        caps: list[CandidateCapability],
        evidence: list,
        requirement_diagnoses: list,
        employer_readiness: list,
        baseline_viability: OpportunityViability,
        parent_id: str,
        run_id: str | None,
    ) -> Scenario:
        modified_caps = [CandidateCapability.model_validate(c.model_dump()) for c in caps]
        modified_employer = [dict(e) for e in employer_readiness]
        proof_result = None
        learning_path = None
        affected_dims: list[str] = []
        affected_caps: list[str] = []
        affected_barriers: list[str] = []
        affected_employer: list[str] = []

        if intervention.type == InterventionType.LEARNING:
            skill = intervention.target.split(":")[-1]
            for cap in modified_caps:
                if cap.skill_id == skill:
                    before = cap.proficiency
                    cap.proficiency = min(0.55, before + 0.25)
                    affected_caps.append(skill)
            affected_dims.append("skill_gap_effort")
            learning_path = {"target_capabilities": [skill], "estimated_duration_weeks": intervention.estimated_effort_weeks}

        elif intervention.type == InterventionType.PROOF_OF_SKILL:
            skill = intervention.target.split(":")[-1]
            for cap in modified_caps:
                if cap.skill_id == skill:
                    cap.proficiency = max(cap.proficiency, opportunity.min_proficiency.get(skill, 0.6))
                    cap.verification_status = CapabilityVerificationStatus.VERIFIED
                    affected_caps.append(skill)
            proof_result = {"result": "PASSED", "skill_id": skill, "total": 0.82}
            affected_dims.extend(["readiness", "proof_effort", "evidence_strength"])

        elif intervention.type == InterventionType.MENTORSHIP:
            for er in modified_employer:
                if er.get("opportunity_id") == opportunity.id:
                    er["confidence"] = min(1.0, er.get("confidence", 0.7) + 0.1)
            affected_dims.append("employer_readiness")
            affected_employer.append("mentorship")

        elif intervention.type == InterventionType.HYBRID_WORK:
            affected_dims.append("workplace_compatibility")
            affected_employer.append("work_mode")

        elif intervention.type == InterventionType.STRUCTURED_ONBOARDING:
            for er in modified_employer:
                if er.get("opportunity_id") == opportunity.id:
                    er["confidence"] = min(1.0, er.get("confidence", 0.7) + 0.12)
            affected_dims.append("employer_readiness")
            affected_employer.append("onboarding")

        elif intervention.type == InterventionType.EVIDENCE_SUBSTITUTION:
            affected_barriers.append("potential_eligibility_proxy")
            affected_dims.append("readiness")

        new_viability, _ = self._assess_viability(
            candidate_id,
            opportunity,
            modified_caps,
            evidence,
            requirement_diagnoses,
            learning_path,
            proof_result,
            modified_employer,
            run_id,
        )

        before_state = {
            "viability_state": baseline_viability.viability_state.value,
            "readiness": baseline_viability.dimensions.readiness,
            "employer_readiness": baseline_viability.dimensions.employer_readiness,
            "workplace_compatibility": baseline_viability.dimensions.workplace_compatibility,
        }
        after_state = {
            "viability_state": new_viability.viability_state.value,
            "readiness": new_viability.dimensions.readiness,
            "employer_readiness": new_viability.dimensions.employer_readiness,
            "workplace_compatibility": new_viability.dimensions.workplace_compatibility,
        }
        if affected_caps:
            skill = affected_caps[0]
            before_cap = next(c for c in caps if c.skill_id == skill)
            after_cap = next(c for c in modified_caps if c.skill_id == skill)
            after_state[f"{skill}_proficiency"] = after_cap.proficiency
            before_state[f"{skill}_proficiency"] = before_cap.proficiency

        effect = InterventionEffect(
            before_state=before_state,
            after_state=after_state,
            affected_dimensions=affected_dims,
            affected_capabilities=affected_caps,
            affected_barriers=affected_barriers,
            affected_employer_factors=affected_employer,
            expected_readiness_change=round(
                new_viability.dimensions.readiness - baseline_viability.dimensions.readiness, 2
            ),
            expected_viability_change=(
                f"{baseline_viability.viability_state.value} → {new_viability.viability_state.value}"
                if new_viability.viability_state != baseline_viability.viability_state
                else None
            ),
            confidence=intervention.confidence,
            assumptions=list(self.DEMO_ASSUMPTIONS),
            is_simulated_projection=True,
        )

        return Scenario(
            id=f"scenario-{intervention.id}",
            candidate_id=candidate_id,
            opportunity_id=opportunity.id,
            label=intervention.title,
            parent_scenario_id=parent_id,
            intervention_ids=[intervention.id],
            intervention_types=[intervention.type.value],
            assumptions=list(self.DEMO_ASSUMPTIONS),
            before_viability_state=baseline_viability.viability_state,
            after_viability_state=new_viability.viability_state,
            effect=effect,
            total_effort_weeks=intervention.estimated_effort_weeks,
            confidence=intervention.confidence,
            is_simulated_projection=True,
            source_mode=SourceMode.SYNTHETIC,
        )

    def _build_bundles(
        self,
        interventions: list[Intervention],
        candidate_id: str,
        opportunity: OpportunityCatalogEntry,
        caps: list[CandidateCapability],
        evidence: list,
        requirement_diagnoses: list,
        employer_readiness: list,
        baseline_viability: OpportunityViability,
        parent_id: str,
        run_id: str | None,
    ) -> tuple[list[InterventionBundle], list[Scenario]]:
        bundles_def = [
            ("bundle-a", "Learning only", [InterventionType.LEARNING]),
            ("bundle-b", "Learning + Proof", [InterventionType.LEARNING, InterventionType.PROOF_OF_SKILL]),
            (
                "bundle-c",
                "Learning + Proof + Mentorship",
                [InterventionType.LEARNING, InterventionType.PROOF_OF_SKILL, InterventionType.MENTORSHIP],
            ),
            (
                "bundle-d",
                "Learning + Proof + Hybrid Work",
                [InterventionType.LEARNING, InterventionType.PROOF_OF_SKILL, InterventionType.HYBRID_WORK],
            ),
        ]
        type_map = {i.type: i for i in interventions}
        bundles: list[InterventionBundle] = []
        all_bundle_scenarios: list[Scenario] = []

        for bundle_id, label, types in bundles_def:
            available = [type_map[t] for t in types if t in type_map]
            if not available:
                continue
            scenarios = self._simulate_bundle_types(
                types,
                candidate_id,
                opportunity,
                caps,
                evidence,
                requirement_diagnoses,
                employer_readiness,
                baseline_viability,
                parent_id,
                run_id,
            )
            if not scenarios:
                continue
            final = scenarios[-1]
            all_bundle_scenarios.extend(scenarios)
            bundles.append(
                InterventionBundle(
                    id=bundle_id,
                    label=label,
                    scenario_ids=[s.id for s in scenarios],
                    intervention_ids=[i.id for i in available],
                    total_effort_weeks=sum(i.estimated_effort_weeks or 0 for i in available),
                    after_viability_state=final.after_viability_state,
                    is_minimum_effective=False,
                    rationale=f"Bundle projection: {label}.",
                )
            )

        return bundles, all_bundle_scenarios

    def _simulate_bundle_types(
        self,
        types: list[InterventionType],
        candidate_id: str,
        opportunity: OpportunityCatalogEntry,
        caps: list[CandidateCapability],
        evidence: list,
        requirement_diagnoses: list,
        employer_readiness: list,
        baseline_viability: OpportunityViability,
        parent_id: str,
        run_id: str | None,
    ) -> list[Scenario]:
        interventions = self._build_intervention_catalog(
            opportunity.id,
            baseline_viability.candidate_gaps,
            None,
            None,
            employer_readiness,
            opportunity,
        )
        type_map = {i.type: i for i in interventions}
        scenarios: list[Scenario] = []
        current_parent = parent_id

        for t in types:
            intervention = type_map.get(t)
            if not intervention or not self._is_valid(intervention, baseline_viability.candidate_gaps, None):
                continue
            scenario = self._simulate_single(
                intervention,
                candidate_id,
                opportunity,
                caps,
                evidence,
                requirement_diagnoses,
                employer_readiness,
                baseline_viability,
                current_parent,
                run_id,
            )
            scenarios.append(scenario)
            current_parent = scenario.id
            # Apply cumulative effects to caps for next step
            if intervention.type == InterventionType.LEARNING:
                skill = intervention.target.split(":")[-1]
                for cap in caps:
                    if cap.skill_id == skill:
                        cap.proficiency = min(0.55, cap.proficiency + 0.25)
            elif intervention.type == InterventionType.PROOF_OF_SKILL:
                skill = intervention.target.split(":")[-1]
                for cap in caps:
                    if cap.skill_id == skill:
                        cap.proficiency = max(cap.proficiency, opportunity.min_proficiency.get(skill, 0.6))

        return scenarios

    def _find_minimum_effective(
        self,
        scenarios: list[Scenario],
        baseline_state: ViabilityState,
    ) -> Scenario | None:
        changed = [
            s for s in scenarios
            if s.after_viability_state and s.after_viability_state != baseline_state and s.effect
        ]
        if not changed:
            return None
        return min(changed, key=lambda s: s.total_effort_weeks or 999)
