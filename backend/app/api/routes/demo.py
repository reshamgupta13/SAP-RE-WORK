"""Demo fixture endpoints."""

from fastapi import APIRouter, HTTPException

from app.services.fixture_service import FixtureService

router = APIRouter()
_fixture_service = FixtureService()


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
