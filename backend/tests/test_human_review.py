"""Human review tests."""

from app.domain.enums import HumanReviewAction, RunMode
from app.services.explainability_service import ExplainabilityService
from app.services.human_review_service import HumanReviewService
from app.services.orchestration_service import OrchestrationService


def _run():
    return OrchestrationService().execute_demo_run(run_mode=RunMode.CONTROL_ROOM_DEMO)


def test_approve_review():
    state = _run()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    card = ExplainabilityService().build_decision_card(state)
    svc = HumanReviewService()
    result = svc.submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.APPROVE,
        reviewer_id="hr-1",
        reason="Evidence supports pathway.",
        ai_recommendation=rec.model_dump(mode="json"),
    )
    assert result["message"].startswith("Human decision")
    assert result["ai_recommendation_preserved"]


def test_modify_review():
    state = _run()
    card = ExplainabilityService().build_decision_card(state)
    result = HumanReviewService().submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.MODIFY,
        reviewer_id="hr-1",
        modified_interventions=["int-learning-power_bi"],
        modified_pathway="pathway-modified",
    )
    review = result["review"]
    assert review["action"] == "MODIFY"
    assert review["modified_pathway"] == "pathway-modified"


def test_request_more_evidence():
    state = _run()
    card = ExplainabilityService().build_decision_card(state)
    result = HumanReviewService().submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.REQUEST_MORE_EVIDENCE,
        reviewer_id="hr-1",
    )
    assert result["review"]["action"] == "REQUEST_MORE_EVIDENCE"


def test_reject_review():
    state = _run()
    card = ExplainabilityService().build_decision_card(state)
    result = HumanReviewService().submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.REJECT,
        reviewer_id="hr-1",
        reason="Insufficient evidence for proxy substitution.",
    )
    assert result["review"]["action"] == "REJECT"


def test_original_recommendation_preserved():
    state = _run()
    rec = ExplainabilityService().build_reviewable_recommendation(state)
    card = ExplainabilityService().build_decision_card(state)
    snapshot = rec.model_dump(mode="json")
    result = HumanReviewService().submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.MODIFY,
        reviewer_id="hr-1",
        ai_recommendation=snapshot,
    )
    audit = result["audit_entry"]
    assert audit["before_state"]["ai_recommendation"] == snapshot


def test_human_override_logged():
    state = _run()
    card = ExplainabilityService().build_decision_card(state)
    result = HumanReviewService().submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.MODIFY,
        reviewer_id="hr-1",
        override={"pathway_weeks": 10},
    )
    assert result["audit_entry"]["actor_type"] == "HUMAN"


def test_human_decision_does_not_alter_ai_output():
    state = _run()
    rec_before = ExplainabilityService().build_reviewable_recommendation(state)
    card = ExplainabilityService().build_decision_card(state)
    HumanReviewService().submit_review(
        run_id=state["run_id"],
        decision_card_id=card.id,
        action=HumanReviewAction.REJECT,
        reviewer_id="hr-1",
        ai_recommendation=rec_before.model_dump(mode="json"),
    )
    rec_after = ExplainabilityService().build_reviewable_recommendation(state)
    assert rec_before.recommendation_summary == rec_after.recommendation_summary
