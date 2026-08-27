"""Structured explainability — not LLM prose blobs."""

from typing import Any

from app.domain.decision import DecisionCard
from app.domain.enums import RecommendationState, SourceMode
from app.domain.explainability import EvidenceChainNode, ExplainabilityReport, ReviewableRecommendation
from app.services.confidence_labels import confidence_label_text, to_confidence_label


class ExplainabilityService:
    def build_reports(self, state: dict[str, Any]) -> dict[str, Any]:
        reports = []
        recommendation = self.build_reviewable_recommendation(state)
        opportunity_id = self._primary_opportunity_id(state)

        reports.append(self._why_opportunity(state, opportunity_id))
        if state.get("learning_path"):
            reports.append(self._why_pathway(state))
        if state.get("interventions"):
            reports.append(self._why_intervention(state))

        return {
            "reports": [r.model_dump(mode="json") for r in reports],
            "reviewable_recommendation": recommendation.model_dump(mode="json"),
            "evidence_chains": self._build_evidence_chains(state, opportunity_id),
        }

    def build_reviewable_recommendation(self, state: dict[str, Any]) -> ReviewableRecommendation:
        run_id = state.get("run_id", "unknown")
        candidate_id = state.get("candidate_id", "ananya-sharma")
        viability = self._primary_viability(state)
        comparison = state.get("opportunity_comparison") or {}
        rec_step = comparison.get("recommended_next_step_opportunity_id")
        opp_title = self._opportunity_title(state, rec_step or viability.get("opportunity_id"))

        confidence = viability.get("confidence", 0.65) if viability else 0.55
        label = to_confidence_label(confidence)

        interventions = state.get("interventions") or []
        int_ids = [i.get("id") for i in interventions[:3] if i.get("id")]

        minimum = state.get("minimum_effective_intervention")
        if minimum and isinstance(minimum, dict):
            int_ids = minimum.get("intervention_ids", int_ids)

        ai_snapshot = {
            "opportunity_viability": viability,
            "opportunity_comparison": comparison,
            "diagnosis_summary": state.get("diagnosis_summary"),
            "minimum_effective_intervention": minimum,
        }

        return ReviewableRecommendation(
            id=f"rec-{run_id}",
            run_id=run_id,
            candidate_id=candidate_id,
            recommendation_summary=(
                f"AI recommendation generated: pursue {opp_title} as next viable opportunity "
                f"with targeted pathway where gaps remain."
            ),
            recommendation_type="OPPORTUNITY_PATHWAY",
            evidence_refs=viability.get("evidence_refs", []) if viability else [],
            confidence=confidence,
            confidence_label=label,
            assumptions=[
                "Projection assumes employer context remains as assessed.",
                "Capability evidence reflects current verified portfolio.",
                "This is a decision support recommendation — not a hiring decision.",
            ],
            alternatives=self._alternatives(state),
            intervention_ids=int_ids,
            pathway_id=(state.get("learning_path") or {}).get("id"),
            risks=self._risks(state),
            human_review_required=True,
            ai_recommendation_preserved=ai_snapshot,
            source_mode=SourceMode.SYNTHETIC,
        )

    def build_decision_card(self, state: dict[str, Any]) -> DecisionCard:
        candidate = state.get("candidate") or {}
        job = state.get("job") or {}
        viability = self._primary_viability(state)
        diagnosis = state.get("reassessment_summary") or state.get("diagnosis_summary") or {}
        gaps = [g.get("skill_id") for g in state.get("capability_gaps", []) if g.get("gap_status") == "GENUINE_CAPABILITY_GAP"]
        proxies = [
            d.get("requirement", "")[:60]
            for d in state.get("requirement_diagnoses", [])
            if d.get("diagnosis_type") == "ELIGIBILITY_PROXY"
        ]

        confidence = viability.get("confidence", diagnosis.get("diagnosis_confidence", 0.6)) if viability else 0.55
        label = to_confidence_label(confidence)

        opp_id = viability.get("opportunity_id") if viability else state.get("job_id")
        opp_title = self._opportunity_title(state, opp_id) or job.get("title", "Target role")

        return DecisionCard(
            id=f"decision-{state.get('run_id', 'demo')}",
            run_id=state.get("run_id"),
            candidate_id=candidate.get("id", state.get("candidate_id")),
            candidate_name=candidate.get("name", "Candidate"),
            target_role_id=job.get("id", state.get("job_id")),
            target_role_title=opp_title,
            recommendation_state=RecommendationState.PATHWAY_RECOMMENDED,
            genuine_gaps=gaps,
            potential_proxies=proxies,
            workplace_constraints=[
                d.get("requirement", "")[:60]
                for d in state.get("requirement_diagnoses", [])
                if d.get("diagnosis_type") == "WORKPLACE_CONSTRAINT"
            ],
            pathway_id=(state.get("learning_path") or {}).get("id"),
            proof_of_skill_id=(state.get("proof_result") or {}).get("id"),
            alternative_opportunity_ids=[
                o.get("opportunity_id")
                for o in state.get("opportunity_viability", [])
                if o.get("opportunity_id") != opp_id
            ],
            market_signal_ids=[s.get("id") for s in state.get("market_signals", [])[:3]],
            confidence=confidence,
            human_decision_required=True,
            what=f"Target opportunity: {opp_title}",
            why=self._why_summary(state, viability, diagnosis),
            evidence_refs=viability.get("evidence_refs", []) if viability else [],
            alternatives=self._alternatives(state),
            source_mode=SourceMode.SYNTHETIC,
        )

    def _why_opportunity(self, state: dict[str, Any], opportunity_id: str | None) -> ExplainabilityReport:
        viability = next(
            (v for v in state.get("opportunity_viability", []) if v.get("opportunity_id") == opportunity_id),
            self._primary_viability(state),
        )
        title = self._opportunity_title(state, opportunity_id)
        gaps = viability.get("candidate_gaps", []) if viability else []
        confidence = viability.get("confidence", 0.65) if viability else 0.55
        label = to_confidence_label(confidence)

        return ExplainabilityReport(
            id=f"explain-opp-{opportunity_id}",
            run_id=state.get("run_id"),
            what=f"Why this opportunity: {title}",
            why=(
                f"Viability state {viability.get('viability_state')} based on capability fit "
                f"{viability.get('dimensions', {}).get('capability_fit')} and employer readiness "
                f"{viability.get('dimensions', {}).get('employer_readiness')}."
            ),
            evidence_refs=viability.get("evidence_refs", []) if viability else [],
            evidence_chain=self._build_evidence_chains(state, opportunity_id),
            confidence=confidence,
            confidence_label=label,
            alternatives=self._alternatives(state),
            assumptions=[
                confidence_label_text(label),
                "Opportunity viability — not traditional job matching score.",
            ],
            human_decision_required=True,
            source_modes=["SYNTHETIC", "SIMULATED"],
            source_mode=SourceMode.SYNTHETIC,
        )

    def _why_pathway(self, state: dict[str, Any]) -> ExplainabilityReport:
        pathway = state.get("learning_path") or {}
        gaps = pathway.get("gap_skill_ids", [])
        confidence = pathway.get("confidence", 0.7)
        label = to_confidence_label(confidence)

        return ExplainabilityReport(
            id=f"explain-pathway-{pathway.get('id', 'pathway')}",
            run_id=state.get("run_id"),
            what="Why this pathway?",
            why=pathway.get("why", "Pathway targets diagnosed genuine capability gaps."),
            evidence_refs=pathway.get("evidence_refs", []),
            evidence_chain=[
                EvidenceChainNode(
                    node_type="RECOMMENDATION",
                    label="Learning pathway",
                    ref_id=pathway.get("id"),
                    children=[
                        EvidenceChainNode(
                            node_type="GAP",
                            label=f"Gap: {', '.join(gaps)}",
                            children=[
                                EvidenceChainNode(
                                    node_type="TASK",
                                    label="Job task requires dashboard capability",
                                )
                            ],
                        )
                    ],
                )
            ],
            confidence=confidence,
            confidence_label=label,
            alternatives=["Self-directed learning without structured milestones"],
            assumptions=["Pathway completion at estimated duration.", "Employer supports learning time."],
            human_decision_required=False,
            source_modes=["SIMULATED"],
            source_mode=SourceMode.SIMULATED,
        )

    def _why_intervention(self, state: dict[str, Any]) -> ExplainabilityReport:
        minimum = state.get("minimum_effective_intervention")
        if isinstance(minimum, dict):
            minimum = minimum
        else:
            minimum = {}
        confidence = minimum.get("confidence", 0.72)
        label = to_confidence_label(confidence)

        return ExplainabilityReport(
            id="explain-intervention-minimum",
            run_id=state.get("run_id"),
            what="Why this intervention?",
            why=(
                "Minimum effective intervention set closes diagnosed gap with lowest projected effort "
                "under SIMULATED PROJECTION assumptions."
            ),
            evidence_refs=[],
            evidence_chain=[],
            confidence=confidence,
            confidence_label=label,
            alternatives=["Larger learning bundles or employer-only adaptations"],
            assumptions=[
                "SIMULATED PROJECTION — not a guaranteed outcome.",
                "Learning completed and proof passed at threshold.",
            ],
            human_decision_required=True,
            source_modes=["SYNTHETIC"],
            source_mode=SourceMode.SYNTHETIC,
        )

    def _build_evidence_chains(
        self,
        state: dict[str, Any],
        opportunity_id: str | None,
    ) -> list[EvidenceChainNode]:
        viability = next(
            (v for v in state.get("opportunity_viability", []) if v.get("opportunity_id") == opportunity_id),
            None,
        )
        if not viability:
            return []

        gaps = viability.get("candidate_gaps", [])
        gap_nodes = [
            EvidenceChainNode(node_type="CAPABILITY", label=f"Gap: {g.replace('_', ' ')}", ref_id=g)
            for g in gaps
        ]
        return [
            EvidenceChainNode(
                node_type="RECOMMENDATION",
                label=self._opportunity_title(state, opportunity_id),
                ref_id=opportunity_id,
                children=[
                    EvidenceChainNode(
                        node_type="DIAGNOSIS",
                        label=(state.get("diagnosis_summary") or {}).get("overall_diagnosis_state", ""),
                        children=gap_nodes,
                    )
                ],
            )
        ]

    def _primary_viability(self, state: dict[str, Any]) -> dict | None:
        for opp_id in ["opp-data-analyst", "opp-operations-analyst"]:
            v = next(
                (v for v in state.get("opportunity_viability", []) if v.get("opportunity_id") == opp_id),
                None,
            )
            if v:
                return v
        viabilities = state.get("opportunity_viability", [])
        return viabilities[0] if viabilities else None

    def _primary_opportunity_id(self, state: dict[str, Any]) -> str | None:
        v = self._primary_viability(state)
        return v.get("opportunity_id") if v else None

    def _opportunity_title(self, state: dict[str, Any], opportunity_id: str | None) -> str:
        if not opportunity_id:
            return "Target opportunity"
        opp = next(
            (o for o in state.get("opportunities", []) if o.get("id") == opportunity_id),
            None,
        )
        return opp.get("title", opportunity_id) if opp else opportunity_id

    def _alternatives(self, state: dict[str, Any]) -> list[str]:
        comparison = state.get("opportunity_comparison") or {}
        alts = comparison.get("alternative_opportunities", [])
        if alts:
            return [a.get("title", a.get("opportunity_id", "")) for a in alts[:3]]
        return [
            o.get("title", o.get("id"))
            for o in state.get("opportunities", [])
            if o.get("id") != self._primary_opportunity_id(state)
        ][:3]

    def _risks(self, state: dict[str, Any]) -> list[str]:
        risks = []
        viability = self._primary_viability(state)
        if viability and viability.get("proof_required"):
            risks.append("Proof-of-skill not yet completed for target gap.")
        if viability and viability.get("candidate_barriers"):
            risks.append("Potential eligibility proxies require human review.")
        diagnosis = state.get("diagnosis_summary") or {}
        if diagnosis.get("eligibility_proxy_count", 0) > 0:
            risks.append("Eligibility proxy flagged — not bias removal claim.")
        return risks

    def _why_summary(
        self,
        state: dict[str, Any],
        viability: dict | None,
        diagnosis: dict,
    ) -> str:
        if not viability:
            return diagnosis.get("summary", "Diagnosis completed with structured factors.")
        return (
            f"Capability fit and evidence support {viability.get('viability_state')} for this opportunity. "
            f"Genuine gaps: {', '.join(viability.get('candidate_gaps', [])) or 'none identified'}."
        )
