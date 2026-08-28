"""SAP context and health endpoints."""

from fastapi import APIRouter

from app.adapters.sap import get_sap_provider
from app.adapters.sap.health import SAPHealthService
from app.core.config import get_settings
from app.domain.enums import IntegrationStatus, SourceMode

router = APIRouter()


@router.get("/health")
def sap_health() -> dict:
    return SAPHealthService().check()


@router.get("/context")
def get_sap_context() -> dict:
    settings = get_settings()
    health = SAPHealthService().check()
    provider = get_sap_provider()
    try:
        context = provider.get_context()
        is_live = (
            context.source_mode == SourceMode.LIVE
            and context.integration_status == IntegrationStatus.AVAILABLE
            and health.get("healthy")
        )
        return {
            "sap_context": context.model_dump(mode="json"),
            "source_mode": context.source_mode.value,
            "system_name": context.system_name,
            "available_domains": context.retrieved_entities if is_live else [],
            "last_successful_sync": context.last_sync.isoformat() if context.last_sync and is_live else None,
            "capabilities": [c.model_dump(mode="json") for c in context.capabilities] if is_live else [],
            "configured": health.get("configured", False),
            "reachable": health.get("reachable", False),
            "authenticated": health.get("authenticated", False),
            "live_connection": is_live,
            "fallback_reason": health.get("fallback_reason"),
            "message": context.message,
            "sap_mode": settings.sap_mode,
        }
    except Exception as exc:
        return {
            "source_mode": health.get("source_mode", "SIMULATED"),
            "status": "ERROR",
            "message": str(exc),
            "fallback_reason": health.get("fallback_reason"),
            "configured": health.get("configured", False),
        }
