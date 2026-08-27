"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "demo_mode": settings.demo_mode,
        "engine_mode": "CHECKPOINT_05",
        "intelligence_layer": "opportunity viability + market intelligence + employer readiness",
        "sap_connection": "SIMULATED",
        "message": "RE:WORK API — Checkpoint 2 intelligence layer",
    }
