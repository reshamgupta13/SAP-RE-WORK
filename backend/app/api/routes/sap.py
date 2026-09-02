"""SAP context and health endpoints."""

from fastapi import APIRouter

from app.adapters.sap import get_sap_provider
from app.adapters.sap.health import SAPHealthService
from app.adapters.sap.odata_config import build_access_plan
from app.core.config import get_settings
from app.domain.enums import IntegrationStatus, SourceMode

router = APIRouter()


@router.get("/health")
def sap_health() -> dict:
    return SAPHealthService().check()


@router.get("/diagnostics")
def sap_diagnostics() -> dict:
    """Detailed SAP OData diagnostics for presenters and connectivity checks."""
    settings = get_settings()
    health = SAPHealthService().check()
    provider = get_sap_provider()
    diagnostics: dict = {}
    if hasattr(provider, "get_diagnostics"):
        diagnostics = provider.get_diagnostics()
    return {
        "sap_mode": settings.sap_mode,
        "demo_mode": settings.demo_mode,
        "source_mode": health.get("source_mode"),
        "configured": health.get("configured"),
        "reachable": health.get("reachable"),
        "authenticated": health.get("authenticated"),
        "metadata_accessible": health.get("metadata_accessible"),
        "odata_base_url_configured": health.get("odata_base_url_configured"),
        "entity_status": health.get("entity_status", diagnostics.get("entity_status", {})),
        "entity_counts": health.get("entity_counts", diagnostics.get("entity_counts", {})),
        "access_plan": diagnostics.get("access_plan") or build_access_plan().to_dict(),
        "last_sync": diagnostics.get("last_sync"),
        "last_error": diagnostics.get("last_error"),
        "message": health.get("message"),
        "fallback_reason": health.get("fallback_reason"),
    }


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
        diagnostics: dict = {}
        if hasattr(provider, "get_diagnostics"):
            diagnostics = provider.get_diagnostics()

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
            "metadata_accessible": health.get("metadata_accessible", False),
            "live_connection": is_live,
            "fallback_reason": health.get("fallback_reason"),
            "message": context.message,
            "sap_mode": settings.sap_mode,
            "entity_status": diagnostics.get("entity_status", health.get("entity_status", {})),
            "entity_counts": diagnostics.get("entity_counts", health.get("entity_counts", {})),
            "access_plan": diagnostics.get("access_plan"),
        }
    except Exception as exc:
        return {
            "source_mode": health.get("source_mode", "SIMULATED"),
            "status": "ERROR",
            "message": str(exc),
            "fallback_reason": health.get("fallback_reason"),
            "configured": health.get("configured", False),
        }


@router.get("/trace")
def sap_trace() -> dict:
    """SAP → RE:WORK trace for jury inspection."""
    from app.services.sap_context_service import SAPContextService

    health = SAPHealthService().check()
    plan = build_access_plan()
    service = SAPContextService()
    boundary = service.contribution_boundary(None)

    pipeline = [
        {"step": 1, "stage": "SAP context retrieved", "agent": "SAP Adapter"},
        {"step": 2, "stage": "Data normalized", "agent": "SAPMapper"},
        {"step": 3, "stage": "Candidate Intelligence", "agent": "Candidate Intelligence Agent"},
        {"step": 4, "stage": "Job requirements understood", "agent": "Job Decomposition Agent"},
        {"step": 5, "stage": "Gap diagnosed", "agent": "Diagnosis"},
        {"step": 6, "stage": "Pathway generated", "agent": "Pathway"},
        {"step": 7, "stage": "Opportunity re-evaluated", "agent": "Opportunity Viability"},
    ]

    return {
        "source_mode": health.get("source_mode"),
        "pipeline": pipeline,
        "from_sap": boundary.get("sap", {}),
        "rework_reasoning": boundary.get("rework", {}),
        "access_plan": plan.to_dict(),
        "entity_status": health.get("entity_status", {}),
    }
