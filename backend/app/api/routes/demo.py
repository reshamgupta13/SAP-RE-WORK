"""Demo fixture endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.case_service import CaseService
from app.services.control_room_service import ControlRoomService
from app.services.fixture_service import FixtureService

router = APIRouter()
_fixture_service = FixtureService()
_control_room = ControlRoomService()
_case_service = CaseService()


@router.get("/candidates")
def list_demo_candidates() -> dict:
    profiles = _fixture_service.list_demo_candidates()
    return {
        "source_mode": "SYNTHETIC",
        "count": len(profiles),
        "candidates": [p.model_dump(mode="json") for p in profiles],
    }


@router.get("/candidates/{candidate_id}")
def get_demo_candidate(candidate_id: str) -> dict:
    if candidate_id != "ananya-sharma":
        raise HTTPException(status_code=404, detail="Demo candidate not found")
    bundle = _fixture_service.get_ananya_bundle()
    return {
        "source_mode": bundle["profile"].source_mode.value,
        "profile": bundle["profile"].model_dump(mode="json"),
        "evidence": [e.model_dump(mode="json") for e in bundle["evidence"]],
        "capabilities": [c.model_dump(mode="json") for c in bundle["capabilities"]],
    }


@router.get("/jobs")
def list_demo_jobs() -> dict:
    jobs = _fixture_service.list_demo_jobs()
    return {
        "source_mode": "SYNTHETIC",
        "count": len(jobs),
        "jobs": [j.model_dump(mode="json") for j in jobs],
    }


@router.get("/jobs/{job_id}")
def get_demo_job(job_id: str) -> dict:
    job = _fixture_service.get_data_analyst_job()
    if job_id != job.id:
        raise HTTPException(status_code=404, detail="Demo job not found")
    return {
        "source_mode": job.source_mode.value,
        "job": job.model_dump(mode="json"),
    }


@router.get("/opportunities")
def list_demo_opportunities() -> dict:
    catalog = _fixture_service.get_opportunity_catalog()
    return {
        "source_mode": "SYNTHETIC",
        "count": len(catalog),
        "opportunities": [o.model_dump(mode="json") for o in catalog],
    }


@router.get("/market")
def list_demo_market_signals() -> dict:
    signals = _fixture_service.get_market_signals()
    return {
        "source_mode": "SYNTHETIC",
        "count": len(signals),
        "note": "Synthetic demo signals — not live labor market statistics.",
        "signals": [s.model_dump(mode="json") for s in signals],
    }


@router.get("/control-room")
def get_control_room() -> dict[str, Any]:
    return _case_service.build_control_room_view()


@router.get("/scenarios")
def get_scenarios() -> dict[str, Any]:
    return _control_room.get_scenarios()


@router.post("/reset")
def reset_demo() -> dict[str, Any]:
    """Reset canonical finale case — restores case-ananya-finale from fixture."""
    case = _case_service.reset_finale_case()
    return {
        "status": "reset",
        "case_id": case.id,
        "lifecycle_state": case.lifecycle_state.value,
        "human_decision_status": case.human_decision_status.value,
        "message": "Finale case reset and re-executed.",
    }


@router.get("/negative-case")
def negative_case_demo(scenario_id: str = "B07") -> dict[str, Any]:
    """Judge mode: show a case RE:WORK refuses to force a positive outcome."""
    return _case_service.get_negative_case_demo(scenario_id)
