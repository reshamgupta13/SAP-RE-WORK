"""Canonical case API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.domain.enums import CaseStage, HumanReviewAction
from app.services.case_service import CaseService

router = APIRouter()
_case_service = CaseService()


class CreateCaseRequest(BaseModel):
    candidate_id: str = "ananya-sharma"
    job_id: str = "data-analyst-junior"
    opportunity_id: str = "opp-data-analyst"
    execute_until: CaseStage | None = None


class ExecuteCaseRequest(BaseModel):
    execute_until: CaseStage = CaseStage.FINALE
    from_stage: CaseStage | None = None
    idempotency_key: str | None = None


class ReviewCaseRequest(BaseModel):
    action: HumanReviewAction
    reviewer_id: str = "hr-demo-reviewer"
    reason: str | None = None
    modified_interventions: list[str] = Field(default_factory=list)
    modified_pathway: str | None = None
    reviewed_case_version: int | None = None


@router.post("")
def create_case(body: CreateCaseRequest) -> dict[str, Any]:
    case = _case_service.create_case(
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        opportunity_id=body.opportunity_id,
    )
    if body.execute_until is not None:
        try:
            case = _case_service.execute(case.id, execute_until=body.execute_until)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return case.model_dump(mode="json")


@router.get("/{case_id}")
def get_case(case_id: str) -> dict[str, Any]:
    case = _case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.model_dump(mode="json")


@router.post("/{case_id}/execute")
def execute_case(case_id: str, body: ExecuteCaseRequest) -> dict[str, Any]:
    try:
        case = _case_service.execute(
            case_id,
            execute_until=body.execute_until,
            from_stage=body.from_stage,
            idempotency_key=body.idempotency_key,
        )
        return case.model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{case_id}/timeline")
def get_timeline(case_id: str) -> dict[str, Any]:
    if not _case_service.get_case(case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case_id": case_id, "timeline": _case_service.get_timeline(case_id)}


@router.get("/{case_id}/explainability")
def get_explainability(case_id: str) -> dict[str, Any]:
    try:
        return _case_service.get_explainability(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{case_id}/interventions/simulate")
def simulate_interventions(case_id: str) -> dict[str, Any]:
    try:
        return _case_service.simulate_interventions(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{case_id}/review")
def review_case(case_id: str, body: ReviewCaseRequest) -> dict[str, Any]:
    try:
        return _case_service.submit_review(
            case_id,
            action=body.action,
            reviewer_id=body.reviewer_id,
            reason=body.reason,
            modified_interventions=body.modified_interventions,
            modified_pathway=body.modified_pathway,
            reviewed_case_version=body.reviewed_case_version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{case_id}/decision")
def get_decision(case_id: str) -> dict[str, Any]:
    try:
        return _case_service.get_decision(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{case_id}/what-changed")
def what_changed(case_id: str) -> dict[str, Any]:
    try:
        return _case_service.get_what_changed(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{case_id}/control-room")
def case_control_room(case_id: str) -> dict[str, Any]:
    if not _case_service.get_case(case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    return _case_service.build_control_room_view(case_id)


@router.get("/{case_id}/export")
def export_case(case_id: str) -> dict[str, Any]:
    try:
        return _case_service.export_case(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
