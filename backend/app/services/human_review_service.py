"""Human review — preserves AI recommendation vs human decision."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.domain.decision import HumanReview
from app.domain.enums import ActorType, HumanReviewAction, SourceMode
from app.domain.explainability import GovernanceAuditEntry
from app.services.explainability_service import ExplainabilityService
from app.services.review_store import review_store


class HumanReviewService:
    def __init__(self) -> None:
        self._explainability = ExplainabilityService()
        self._audit: list[GovernanceAuditEntry] = []

    def submit_review(
        self,
        run_id: str,
        decision_card_id: str,
        action: HumanReviewAction,
        reviewer_id: str,
        reason: str | None = None,
        modified_interventions: list[str] | None = None,
        modified_pathway: str | None = None,
        comments: str | None = None,
        override: dict[str, Any] | None = None,
        ai_recommendation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        review = HumanReview(
            id=f"review-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            decision_card_id=decision_card_id,
            action=action,
            reason=reason,
            reviewer_id=reviewer_id,
            reviewer_role="hr",
            override=override or {},
            modified_interventions=modified_interventions or [],
            modified_pathway=modified_pathway,
            comments=comments,
            review_source="REWORK_UI",
            source_mode=SourceMode.USER_PROVIDED,
            ai_recommendation_snapshot=ai_recommendation or {},
        )
        review_store.save(review)

        audit = GovernanceAuditEntry(
            id=f"audit-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            actor_type=ActorType.HUMAN.value,
            actor_id=reviewer_id,
            action=f"HUMAN_DECISION_{action.value}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            before_state={"ai_recommendation": ai_recommendation or {}},
            after_state={
                "human_decision": action.value,
                "modified_interventions": modified_interventions,
                "modified_pathway": modified_pathway,
            },
            reason=reason,
            source_mode=SourceMode.USER_PROVIDED,
        )
        self._audit.append(audit)

        return {
            "review": review.model_dump(mode="json"),
            "audit_entry": audit.model_dump(mode="json"),
            "message": f"Human decision: {action.value}",
            "ai_recommendation_preserved": True,
        }

    def get_reviews_for_run(self, run_id: str) -> list[dict[str, Any]]:
        return [r.model_dump(mode="json") for r in review_store.list_for_run(run_id)]

    def example_review_payload(self, state: dict[str, Any]) -> dict[str, Any]:
        recommendation = self._explainability.build_reviewable_recommendation(state)
        decision_card = self._explainability.build_decision_card(state)
        return {
            "ai_recommendation": recommendation.model_dump(mode="json"),
            "decision_card_id": decision_card.id,
            "note": "AI recommendation generated — awaiting human decision.",
        }
