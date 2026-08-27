"""Canonical case orchestration — single source of truth."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.domain.case import CaseEvent, ReworkCase
from app.domain.enums import (
    ActorType,
    CaseEventType,
    CaseLifecycleState,
    CaseStage,
    EngineMode,
    HumanDecisionStatus,
    HumanReviewAction,
    RunMode,
    SourceMode,
)
from app.repositories import get_case_repository
from app.services.case_snapshot_service import CaseSnapshotService
from app.services.case_timeline_service import CaseTimelineService
from app.services.control_room_service import ControlRoomService
from app.services.explainability_integrity_service import ExplainabilityIntegrityService
from app.services.explainability_service import ExplainabilityService
from app.services.human_review_service import HumanReviewService
from app.services.intervention_simulator import InterventionSimulator
from app.services.orchestration_service import OrchestrationService
from app.services.what_changed_service import WhatChangedService
from app.adapters.sap.health import SAPHealthService


STAGE_TO_RUN_MODE: dict[CaseStage, RunMode] = {
    CaseStage.DIAGNOSIS: RunMode.ANALYZE_ONLY,
    CaseStage.COUNTERFACTUAL: RunMode.ANALYZE_ONLY,
    CaseStage.PATHWAY_GENERATION: RunMode.GENERATE_PATHWAY,
    CaseStage.PROOF_EVALUATION: RunMode.FULL_DEMO_REPLAY,
    CaseStage.REASSESSMENT: RunMode.FULL_DEMO_REPLAY,
    CaseStage.MARKET_INTELLIGENCE: RunMode.OPPORTUNITY_ANALYSIS,
    CaseStage.OPPORTUNITY_VIABILITY: RunMode.OPPORTUNITY_ANALYSIS,
    CaseStage.INTERVENTION_SIMULATION: RunMode.CONTROL_ROOM_DEMO,
    CaseStage.EXPLAINABILITY: RunMode.CONTROL_ROOM_DEMO,
    CaseStage.FINALE: RunMode.CONTROL_ROOM_DEMO,
}

STAGE_TO_LIFECYCLE: dict[CaseStage, CaseLifecycleState] = {
    CaseStage.DISCOVERY: CaseLifecycleState.DISCOVERED,
    CaseStage.DECOMPOSITION: CaseLifecycleState.DECOMPOSED,
    CaseStage.DIAGNOSIS: CaseLifecycleState.DIAGNOSED,
    CaseStage.COUNTERFACTUAL: CaseLifecycleState.COUNTERFACTUAL_ANALYZED,
    CaseStage.PATHWAY_GENERATION: CaseLifecycleState.PATHWAY_GENERATED,
    CaseStage.PROOF_EVALUATION: CaseLifecycleState.PROOF_COMPLETED,
    CaseStage.REASSESSMENT: CaseLifecycleState.REASSESSED,
    CaseStage.MARKET_INTELLIGENCE: CaseLifecycleState.MARKET_ANALYZED,
    CaseStage.OPPORTUNITY_VIABILITY: CaseLifecycleState.OPPORTUNITIES_EVALUATED,
    CaseStage.INTERVENTION_SIMULATION: CaseLifecycleState.INTERVENTIONS_SIMULATED,
    CaseStage.EXPLAINABILITY: CaseLifecycleState.EXPLANATION_READY,
    CaseStage.FINALE: CaseLifecycleState.EXPLANATION_READY,
}


class CaseService:
    FINALE_CASE_ID = "case-ananya-finale"

    def __init__(self) -> None:
        self._repo = get_case_repository()
        self._orchestration = OrchestrationService()
        self._snapshots = CaseSnapshotService()
        self._timeline = CaseTimelineService()
        self._explainability = ExplainabilityService()
        self._integrity = ExplainabilityIntegrityService()
        self._what_changed = WhatChangedService()
        self._intervention = InterventionSimulator()
        self._human_review = HumanReviewService()
        self._control_room = ControlRoomService()
        self._sap_health = SAPHealthService()

    def create_case(
        self,
        candidate_id: str = "ananya-sharma",
        job_id: str = "data-analyst-junior",
        opportunity_id: str = "opp-data-analyst",
        case_id: str | None = None,
    ) -> ReworkCase:
        cid = case_id or f"case-{uuid.uuid4().hex[:12]}"
        case = ReworkCase(
            id=cid,
            candidate_id=candidate_id,
            job_id=job_id,
            opportunity_id=opportunity_id,
            lifecycle_state=CaseLifecycleState.CASE_CREATED,
            case_version=1,
            source_mode=SourceMode.SYNTHETIC,
        )
        self._repo.save_case(case)
        self._record_event(
            case,
            CaseEventType.CASE_CREATED,
            rationale=f"Case created for {candidate_id} → {job_id}",
        )
        return case

    def get_case(self, case_id: str) -> ReworkCase | None:
        return self._repo.get_case(case_id)

    def get_or_create_finale_case(self) -> ReworkCase:
        existing = self._repo.get_case(self.FINALE_CASE_ID)
        if existing:
            return existing
        return self.create_case(
            candidate_id="ananya-sharma",
            job_id="data-analyst-junior",
            opportunity_id="opp-data-analyst",
            case_id=self.FINALE_CASE_ID,
        )

    def execute(
        self,
        case_id: str,
        execute_until: CaseStage = CaseStage.FINALE,
        from_stage: CaseStage | None = None,
        idempotency_key: str | None = None,
    ) -> ReworkCase:
        case = self._repo.get_case(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")

        if idempotency_key:
            existing = self._repo.get_event_by_idempotency(case_id, idempotency_key)
            if existing:
                return self._repo.get_case(case_id) or case

        run_mode = STAGE_TO_RUN_MODE.get(execute_until, RunMode.CONTROL_ROOM_DEMO)

        # Idempotency: skip proof if already completed
        if execute_until == CaseStage.PROOF_EVALUATION and case.lifecycle_state in {
            CaseLifecycleState.PROOF_COMPLETED,
            CaseLifecycleState.REASSESSED,
            CaseLifecycleState.EXPLANATION_READY,
            CaseLifecycleState.DECISION_RECORDED,
        }:
            return case

        state = self._orchestration.execute_demo_run(
            candidate_id=case.candidate_id,
            job_id=case.job_id,
            run_mode=run_mode,
        )
        state["case_id"] = case_id

        return self._finalize_execution(case, state, execute_until, idempotency_key)

    def simulate_interventions(self, case_id: str) -> dict[str, Any]:
        case = self._repo.get_case(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        state = case.snapshot or {}
        from app.domain.candidate import CandidateCapability, CandidateEvidence

        caps = [
            CandidateCapability.model_validate(c)
            for c in state.get("updated_candidate_capabilities", state.get("candidate_capabilities", []))
        ]
        evidence = [CandidateEvidence.model_validate(e) for e in state.get("candidate_evidence", [])]
        result = self._intervention.run(
            candidate_id=case.candidate_id,
            opportunity_id=case.opportunity_id or "opp-data-analyst",
            candidate_capabilities=caps,
            candidate_evidence=evidence,
            requirement_diagnoses=state.get("requirement_diagnoses", []),
            learning_path=state.get("learning_path"),
            proof_result=state.get("proof_result"),
            employer_readiness=state.get("employer_readiness", []),
            run_id=state.get("run_id"),
            use_baseline_for_demo=True,
        )
        result["case_id"] = case_id
        case.intervention_scenarios = result
        self._repo.save_case(case)
        return result

    def submit_review(
        self,
        case_id: str,
        action: HumanReviewAction,
        reviewer_id: str,
        reason: str | None = None,
        modified_interventions: list[str] | None = None,
        modified_pathway: str | None = None,
        reviewed_case_version: int | None = None,
    ) -> dict[str, Any]:
        case = self._repo.get_case(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")

        if reviewed_case_version and reviewed_case_version < case.case_version:
            raise ValueError(
                f"Stale review: case version {case.case_version}, reviewed {reviewed_case_version}"
            )

        ai_rec = case.ai_recommendation or {}
        decision_card = case.decision_card or {}
        result = self._human_review.submit_review(
            run_id=case.latest_run_id or case_id,
            decision_card_id=decision_card.get("id", f"decision-{case_id}"),
            action=action,
            reviewer_id=reviewer_id,
            reason=reason,
            modified_interventions=modified_interventions,
            modified_pathway=modified_pathway,
            ai_recommendation=ai_rec,
        )

        status_map = {
            HumanReviewAction.APPROVE: HumanDecisionStatus.APPROVED,
            HumanReviewAction.MODIFY: HumanDecisionStatus.MODIFIED,
            HumanReviewAction.REJECT: HumanDecisionStatus.REJECTED,
            HumanReviewAction.REQUEST_MORE_EVIDENCE: HumanDecisionStatus.REQUEST_MORE_EVIDENCE,
        }
        case.human_decision_status = status_map.get(action, HumanDecisionStatus.PENDING)
        case.human_decision = result["review"]
        case.ai_recommendation = ai_rec  # preserved

        if action == HumanReviewAction.APPROVE:
            case.lifecycle_state = CaseLifecycleState.DECISION_RECORDED
        elif action == HumanReviewAction.REJECT:
            case.lifecycle_state = CaseLifecycleState.CLOSED
        elif action == HumanReviewAction.REQUEST_MORE_EVIDENCE:
            case.lifecycle_state = CaseLifecycleState.EVIDENCE_PENDING
        elif action == HumanReviewAction.MODIFY:
            case.lifecycle_state = CaseLifecycleState.DECISION_RECORDED

        case.case_version += 1
        self._repo.save_case(case)
        self._record_event(
            case,
            CaseEventType.HUMAN_DECISION_RECORDED,
            actor_type=ActorType.HUMAN,
            actor_id=reviewer_id,
            rationale=reason or action.value,
        )
        return result

    def get_timeline(self, case_id: str) -> list[dict]:
        events = self._repo.list_events(case_id)
        entries = self._timeline.build(events)
        return [e.model_dump(mode="json") for e in entries]

    def get_explainability(self, case_id: str) -> dict[str, Any]:
        case = self._repo.get_case(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        return case.explainability or {}

    def get_decision(self, case_id: str) -> dict[str, Any]:
        case = self._repo.get_case(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        return {
            "case_id": case_id,
            "case_version": case.case_version,
            "decision_card": case.decision_card,
            "ai_recommendation": case.ai_recommendation,
            "human_decision": case.human_decision,
            "human_decision_status": case.human_decision_status.value,
        }

    def get_what_changed(self, case_id: str) -> dict[str, Any]:
        case = self._repo.get_case(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        baseline = self._repo.get_snapshot(case.baseline_snapshot_id or "")
        current = self._repo.get_snapshot(case.latest_snapshot_id or "")
        if not current:
            return {"case_id": case_id, "changes": []}
        report = self._what_changed.compare(case_id, baseline, current)
        return report.model_dump(mode="json")

    def build_control_room_view(self, case_id: str | None = None) -> dict[str, Any]:
        case = self._repo.get_case(case_id or self.FINALE_CASE_ID)
        if not case or not case.snapshot:
            case = self.execute(self.get_or_create_finale_case().id, CaseStage.FINALE)

        sap_health = self._sap_health.check()
        view = self._control_room.assemble_from_state(case.snapshot)
        view["case"] = case.model_dump(mode="json")
        view["case_id"] = case.id
        view["what_changed"] = self.get_what_changed(case.id)
        view["timeline"] = self.get_timeline(case.id)
        view["system_status"]["sap"] = sap_health.get("source_mode", "SIMULATED")
        view["system_status"]["sap_health"] = sap_health
        view["human_decision_status"] = case.human_decision_status.value
        view["sap_judge_panel"] = self._sap_judge_panel(sap_health)
        return view

    def _finalize_execution(
        self,
        case: ReworkCase,
        state: dict[str, Any],
        execute_until: CaseStage,
        idempotency_key: str | None,
    ) -> ReworkCase:
        case.case_version += 1
        snapshot = self._snapshots.from_graph_state(
            case.id,
            case.case_version,
            state,
            rationale=f"Executed until {execute_until.value}",
        )
        self._repo.save_snapshot(snapshot)

        if not case.baseline_snapshot_id and execute_until in {
            CaseStage.DIAGNOSIS,
            CaseStage.COUNTERFACTUAL,
            CaseStage.FINALE,
        }:
            case.baseline_snapshot_id = snapshot.id

        case.latest_snapshot_id = snapshot.id
        case.latest_run_id = state.get("run_id")
        case.snapshot = snapshot.state
        case.engine_mode = EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value))
        case.lifecycle_state = STAGE_TO_LIFECYCLE.get(execute_until, CaseLifecycleState.EXPLANATION_READY)

        case.decision_card = self._explainability.build_decision_card(state).model_dump(mode="json")
        explainability = self._explainability.build_reports(state)
        case.explainability = explainability
        case.ai_recommendation = explainability.get("reviewable_recommendation", {})
        case.intervention_scenarios = state.get("intervention_simulation")
        case.sap_context = state.get("sap_context")

        self._integrity.assert_valid({**state, "ai_recommendation": case.ai_recommendation})

        events = self._audit_to_case_events(state, case.id, snapshot.id)
        for ev in events:
            self._repo.save_event(ev)

        case.timeline_summary = self._timeline.build(self._repo.list_events(case.id))
        self._repo.save_case(case)

        self._record_event(
            case,
            CaseEventType.CASE_EXECUTED,
            rationale=f"Pipeline executed until {execute_until.value}",
            after_snapshot_ref=snapshot.id,
            idempotency_key=idempotency_key,
        )
        return case

    def _audit_to_case_events(
        self,
        state: dict[str, Any],
        case_id: str,
        snapshot_id: str,
    ) -> list[CaseEvent]:
        agent_map = {
            "load_candidate": CaseEventType.CANDIDATE_DISCOVERED,
            "candidate_intelligence": CaseEventType.CANDIDATE_DISCOVERED,
            "job_decomposition": CaseEventType.JOB_DECOMPOSED,
            "diagnosis": CaseEventType.DIAGNOSIS_CREATED,
            "counterfactual_analysis": CaseEventType.COUNTERFACTUAL_CREATED,
            "pathway_generation": CaseEventType.PATHWAY_GENERATED,
            "proof_evaluation": CaseEventType.PROOF_SUBMITTED,
            "capability_update": CaseEventType.CAPABILITY_UPDATED,
            "reassessment": CaseEventType.REASSESSMENT_COMPLETED,
            "market_intelligence": CaseEventType.MARKET_ANALYZED,
            "opportunity_viability": CaseEventType.OPPORTUNITY_EVALUATED,
            "intervention_simulation": CaseEventType.INTERVENTION_SIMULATED,
            "explainability": CaseEventType.EXPLANATION_GENERATED,
        }
        events: list[CaseEvent] = []
        for audit in state.get("audit_events", []):
            agent = audit.get("agent")
            et = agent_map.get(agent)
            if not et:
                continue
            events.append(
                CaseEvent(
                    id=f"evt-{uuid.uuid4().hex[:12]}",
                    event_type=et,
                    case_id=case_id,
                    actor_type=ActorType.AI,
                    actor_id=agent or "system",
                    after_snapshot_ref=snapshot_id,
                    engine_mode=EngineMode(state.get("engine_mode", EngineMode.DEMO_FALLBACK.value)),
                    rationale=audit.get("rationale"),
                    source_mode=SourceMode.SYNTHETIC,
                )
            )
        return events

    def _record_event(
        self,
        case: ReworkCase,
        event_type: CaseEventType,
        rationale: str | None = None,
        actor_type: ActorType = ActorType.SYSTEM,
        actor_id: str = "system",
        after_snapshot_ref: str | None = None,
        idempotency_key: str | None = None,
    ) -> CaseEvent:
        event = CaseEvent(
            id=f"evt-{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            case_id=case.id,
            actor_type=actor_type,
            actor_id=actor_id,
            after_snapshot_ref=after_snapshot_ref,
            rationale=rationale,
            idempotency_key=idempotency_key,
            engine_mode=case.engine_mode,
        )
        return self._repo.save_event(event)

    def _sap_judge_panel(self, health: dict) -> dict[str, Any]:
        return {
            "what_sap_provides": [
                "workforce context",
                "skills/attributes",
                "learning context",
                "opportunity context",
            ],
            "what_rework_adds": [
                "evidence synthesis",
                "capability diagnosis",
                "counterfactuals",
                "intervention simulation",
                "proof-of-skill reasoning",
                "two-sided readiness",
                "explainability",
                "human governance",
            ],
            "source_mode": health.get("source_mode", "SIMULATED"),
            "configured": health.get("configured", False),
            "healthy": health.get("healthy", False),
        }
