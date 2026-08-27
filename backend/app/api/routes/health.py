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
        "engine_mode": "CHECKPOINT_04",
        "intelligence_layer": "pathway + proof-of-skill + reassessment",
        "sap_connection": "SIMULATED",
        "message": "RE:WORK API — Checkpoint 2 intelligence layer",
    }
