"""Case timeline from event log."""

from app.domain.case import CaseEvent, CaseTimelineEntry
from app.domain.enums import CaseEventType, CaseLifecycleState


TIMELINE_LABELS = {
    CaseEventType.CANDIDATE_DISCOVERED: "Candidate analyzed",
    CaseEventType.JOB_DECOMPOSED: "Job decomposed",
    CaseEventType.DIAGNOSIS_CREATED: "Diagnosis completed",
    CaseEventType.COUNTERFACTUAL_CREATED: "Counterfactual analysis",
    CaseEventType.PATHWAY_GENERATED: "Pathway created",
    CaseEventType.PROOF_SUBMITTED: "Proof completed",
    CaseEventType.CAPABILITY_UPDATED: "Capability verified",
    CaseEventType.REASSESSMENT_COMPLETED: "Reassessment completed",
    CaseEventType.MARKET_ANALYZED: "Market analyzed",
    CaseEventType.OPPORTUNITY_EVALUATED: "Opportunity viability evaluated",
    CaseEventType.INTERVENTION_SIMULATED: "Intervention simulated",
    CaseEventType.EXPLANATION_GENERATED: "Explanation ready",
    CaseEventType.HUMAN_DECISION_RECORDED: "HR decision recorded",
}


LIFECYCLE_FOR_EVENT = {
    CaseEventType.CANDIDATE_DISCOVERED: CaseLifecycleState.DISCOVERED,
    CaseEventType.JOB_DECOMPOSED: CaseLifecycleState.DECOMPOSED,
    CaseEventType.DIAGNOSIS_CREATED: CaseLifecycleState.DIAGNOSED,
    CaseEventType.COUNTERFACTUAL_CREATED: CaseLifecycleState.COUNTERFACTUAL_ANALYZED,
    CaseEventType.PATHWAY_GENERATED: CaseLifecycleState.PATHWAY_GENERATED,
    CaseEventType.PROOF_SUBMITTED: CaseLifecycleState.PROOF_COMPLETED,
    CaseEventType.CAPABILITY_UPDATED: CaseLifecycleState.PROOF_COMPLETED,
    CaseEventType.REASSESSMENT_COMPLETED: CaseLifecycleState.REASSESSED,
    CaseEventType.MARKET_ANALYZED: CaseLifecycleState.MARKET_ANALYZED,
    CaseEventType.OPPORTUNITY_EVALUATED: CaseLifecycleState.OPPORTUNITIES_EVALUATED,
    CaseEventType.INTERVENTION_SIMULATED: CaseLifecycleState.INTERVENTIONS_SIMULATED,
    CaseEventType.EXPLANATION_GENERATED: CaseLifecycleState.EXPLANATION_READY,
    CaseEventType.HUMAN_DECISION_RECORDED: CaseLifecycleState.DECISION_RECORDED,
}


class CaseTimelineService:
    def build(self, events: list[CaseEvent]) -> list[CaseTimelineEntry]:
        entries: list[CaseTimelineEntry] = []
        idx = 0
        for event in sorted(events, key=lambda e: e.timestamp):
            if event.event_type == CaseEventType.CASE_EXECUTED:
                continue
            label = TIMELINE_LABELS.get(event.event_type, event.event_type.value)
            entries.append(
                CaseTimelineEntry(
                    index=idx,
                    label=label,
                    event_type=event.event_type.value,
                    timestamp=event.timestamp.isoformat(),
                    lifecycle_state=LIFECYCLE_FOR_EVENT.get(event.event_type),
                    summary=event.rationale,
                    evidence_refs=event.evidence_refs,
                    snapshot_ref=event.after_snapshot_ref,
                )
            )
            idx += 1
        return entries

    def finale_labels(self, state: dict) -> list[CaseTimelineEntry]:
        """Structured timeline for Ananya demo story."""
        labels = [
            ("Candidate analyzed", "CANDIDATE_DISCOVERED"),
            ("Job decomposed", "JOB_DECOMPOSED"),
            ("Power BI gap identified", "DIAGNOSIS_CREATED"),
            ("Experience proxy identified", "COUNTERFACTUAL_CREATED"),
            ("Pathway created", "PATHWAY_GENERATED"),
            ("Proof completed", "PROOF_SUBMITTED"),
            ("Capability verified", "CAPABILITY_UPDATED"),
            ("Opportunity viability changed", "OPPORTUNITY_EVALUATED"),
            ("Employer readiness evaluated", "OPPORTUNITY_EVALUATED"),
            ("Intervention simulated", "INTERVENTION_SIMULATED"),
            ("HR decision", "HUMAN_DECISION_RECORDED"),
        ]
        entries = []
        for i, (label, et) in enumerate(labels):
            entries.append(
                CaseTimelineEntry(
                    index=i,
                    label=label,
                    event_type=et,
                    summary=label,
                )
            )
        return entries
