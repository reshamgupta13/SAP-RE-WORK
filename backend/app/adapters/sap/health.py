"""SAP integration health and capability probe."""

from datetime import datetime, timezone
from typing import Any

from app.adapters.sap import get_sap_provider
from app.core.config import get_settings
from app.domain.enums import IntegrationStatus, SourceMode


class SAPHealthService:
    def check(self) -> dict[str, Any]:
        settings = get_settings()
        configured = settings.sap_mode.upper() == "LIVE"
        source_mode = SourceMode.SIMULATED

        if settings.demo_mode:
            return {
                "configured": False,
                "reachable": True,
                "authenticated": False,
                "metadata_accessible": False,
                "healthy": True,
                "source_mode": SourceMode.SIMULATED.value,
                "modules_available": ["workforce", "skills", "learning", "opportunities"],
                "message": "Demo mode — SAP simulated.",
                "fallback_reason": None,
                "odata_base_url_configured": bool(settings.sap_odata_base_url or settings.sap_api_url),
            }

        if not configured:
            return {
                "configured": False,
                "reachable": False,
                "authenticated": False,
                "metadata_accessible": False,
                "healthy": False,
                "source_mode": SourceMode.SIMULATED.value,
                "modules_available": [],
                "message": "SAP_MODE not set to LIVE — using simulated adapter.",
                "fallback_reason": None,
                "odata_base_url_configured": bool(settings.sap_odata_base_url or settings.sap_api_url),
            }

        odata_url = settings.sap_odata_base_url or settings.sap_api_url
        auth_mode = (settings.sap_auth_mode or "NONE").upper()
        has_url = bool(odata_url)
        has_oauth = auth_mode == "OAUTH2" and bool(
            settings.sap_api_url and settings.sap_client_id and settings.sap_client_secret
        )
        has_basic = auth_mode == "BASIC" and bool(
            (settings.sap_username or settings.sap_client_id)
            and (settings.sap_password or settings.sap_client_secret)
        )
        has_auth = auth_mode == "NONE" or has_oauth or has_basic

        if not has_url:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "metadata_accessible": False,
                "healthy": False,
                "source_mode": SourceMode.NOT_CONNECTED.value,
                "modules_available": [],
                "message": "SAP_MODE=LIVE but OData base URL not configured.",
                "fallback_reason": "missing_odata_url",
                "odata_base_url_configured": False,
            }

        if not has_auth:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "metadata_accessible": False,
                "healthy": False,
                "source_mode": SourceMode.NOT_CONNECTED.value,
                "modules_available": [],
                "message": f"SAP_MODE=LIVE but auth incomplete for mode {auth_mode}.",
                "fallback_reason": "missing_credentials",
                "odata_base_url_configured": True,
            }

        try:
            provider = get_sap_provider()
            ctx = provider.get_context()
            is_live = ctx.source_mode == SourceMode.LIVE and ctx.integration_status == IntegrationStatus.AVAILABLE
            diagnostics: dict[str, Any] = {}
            if hasattr(provider, "get_diagnostics"):
                diagnostics = provider.get_diagnostics()

            return {
                "configured": True,
                "reachable": is_live,
                "authenticated": is_live,
                "metadata_accessible": is_live,
                "healthy": is_live,
                "source_mode": ctx.source_mode.value,
                "modules_available": ctx.retrieved_entities if is_live else [],
                "system_name": ctx.system_name,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": ctx.message,
                "fallback_reason": None if is_live else "connection_failed",
                "odata_base_url_configured": True,
                "entity_status": diagnostics.get("entity_status", {}),
                "entity_counts": diagnostics.get("entity_counts", {}),
                "access_plan": diagnostics.get("access_plan"),
            }
        except NotImplementedError as exc:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "metadata_accessible": False,
                "healthy": False,
                "source_mode": SourceMode.SIMULATED.value,
                "modules_available": [],
                "message": str(exc),
                "fallback_reason": "live_not_implemented",
                "odata_base_url_configured": has_url,
            }
        except Exception as exc:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "metadata_accessible": False,
                "healthy": False,
                "source_mode": SourceMode.ERROR.value,
                "status": "ERROR",
                "modules_available": [],
                "message": str(exc),
                "fallback_reason": "connection_error",
                "odata_base_url_configured": has_url,
            }

    def product_check(self) -> dict[str, Any]:
        """Honest product health — DEMO_MODE does not imply SAP LIVE or fixture data."""
        from app.services.sap_catalog_service import SAPCatalogService

        return SAPCatalogService().connection_state()
