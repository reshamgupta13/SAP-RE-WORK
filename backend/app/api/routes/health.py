"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.paths import resolve_fixtures_dir

router = APIRouter()


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "demo_mode": settings.demo_mode,
        "sap_mode": settings.sap_mode,
        "persistence_mode": settings.persistence_mode,
    }


@router.get("/health/ready")
def health_ready() -> dict:
    settings = get_settings()
    fixtures = resolve_fixtures_dir(settings.fixtures_dir)
    checks = {
        "fixtures": "ok" if fixtures.exists() else "missing",
    }
    return {
        "status": "ready" if all(v == "ok" for v in checks.values()) else "degraded",
        "checks": checks,
        "sap_mode": settings.sap_mode,
        "persistence_mode": settings.persistence_mode,
    }
