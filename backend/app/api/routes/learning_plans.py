"""Targeted learning plan API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.targeted_learning_service import TargetedLearningService

router = APIRouter()
_service = TargetedLearningService()


class GenerateLearningPlanRequest(BaseModel):
    candidate_id: str
    role_id: str


class SimulateInterventionRequest(BaseModel):
    gap_id: str | None = None


@router.post("/generate")
def generate_learning_plan(body: GenerateLearningPlanRequest) -> dict[str, Any]:
    try:
        plan = _service.generate(body.candidate_id, body.role_id)
        return _plan_response(plan)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{candidate_id}/{role_id}")
def get_learning_plan(candidate_id: str, role_id: str) -> dict[str, Any]:
    plan = _service.get_plan_for_pair(candidate_id, role_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No learning plan found for this candidate/role pair.")
    return _plan_response(plan)


@router.get("/plan/{plan_id}")
def get_plan_by_id(plan_id: str) -> dict[str, Any]:
    plan = _service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found.")
    return _plan_response(plan)


@router.get("/plan/{plan_id}/trace")
def get_plan_trace(plan_id: str) -> dict[str, Any]:
    try:
        return _service.get_trace(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/plan/{plan_id}/simulate")
def simulate_intervention(plan_id: str, body: SimulateInterventionRequest | None = None) -> dict[str, Any]:
    gap_id = body.gap_id if body else None
    try:
        return _service.simulate_intervention(plan_id, gap_id=gap_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/catalog/resources")
def list_learning_resources() -> dict[str, Any]:
    from app.adapters.learning_resources import get_learning_resource_provider

    provider = get_learning_resource_provider()
    resources = provider.list_resources()
    return {
        "catalog_label": provider.get_catalog_label(),
        "source_type": provider.get_source_type(),
        "count": len(resources),
        "resources": [r.model_dump(mode="json") for r in resources],
    }


def _plan_response(plan: Any) -> dict[str, Any]:
    data = plan.model_dump(mode="json")
    data["learning_plan_id"] = plan.id
    if plan.agents:
        data["agents"] = {
            "learning_strategist": plan.agents.learning_strategist,
            "resource_curator": plan.agents.resource_curator,
            "proof_alignment": plan.agents.proof_alignment,
            "validator": plan.agents.validator,
            "engine_mode": plan.agents.engine_mode.value,
        }
    return data
