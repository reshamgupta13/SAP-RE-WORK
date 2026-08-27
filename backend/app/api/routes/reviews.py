"""Human review API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.domain.enums import HumanReviewAction
from app.services.human_review_service import HumanReviewService
from app.services.orchestration_service import OrchestrationService

router = APIRouter()
_review_service = HumanReviewService()
_orchestration = OrchestrationService()


class ReviewRequest(BaseModel):
    run_id: str
    decision_card_id: str
    action: HumanReviewAction
    reviewer_id: str = Field(default="hr-demo-reviewer")
    reason: str | None = None
    modified_interventions: list[str] = Field(default_factory=list)
    modified_pathway: str | None = None
    comments: str | None = None
    override: dict[str, Any] = Field(default_factory=dict)


@router.post("")
def submit_review(body: ReviewRequest) -> dict[str, Any]:
    state = _orchestration.get_run(body.run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")

    ai_recommendation = (state.get("explainability") or {}).get("reviewable_recommendation")
    if not ai_recommendation:
        from app.services.explainability_service import ExplainabilityService

        ai_recommendation = ExplainabilityService().build_reviewable_recommendation(state).model_dump(
            mode="json"
        )

    return _review_service.submit_review(
        run_id=body.run_id,
        decision_card_id=body.decision_card_id,
        action=body.action,
        reviewer_id=body.reviewer_id,
        reason=body.reason,
        modified_interventions=body.modified_interventions,
        modified_pathway=body.modified_pathway,
        comments=body.comments,
        override=body.override,
        ai_recommendation=ai_recommendation,
    )
