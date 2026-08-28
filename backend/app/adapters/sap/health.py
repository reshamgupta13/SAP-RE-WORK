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
                "healthy": True,
                "source_mode": SourceMode.SIMULATED.value,
                "modules_available": ["workforce", "skills", "learning", "opportunities"],
                "message": "Demo mode — SAP simulated.",
                "fallback_reason": None,
            }

        if not configured:
            return {
                "configured": False,
                "reachable": False,
                "authenticated": False,
                "healthy": False,
                "source_mode": SourceMode.SIMULATED.value,
                "modules_available": [],
                "message": "SAP_MODE not set to LIVE — using simulated adapter.",
                "fallback_reason": None,
            }

        has_creds = bool(
            settings.sap_api_url and settings.sap_client_id and settings.sap_client_secret
        )
        if not has_creds:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "healthy": False,
                "source_mode": SourceMode.NOT_CONNECTED.value,
                "modules_available": [],
                "message": "SAP_MODE=LIVE but credentials incomplete.",
                "fallback_reason": "missing_credentials",
            }

        try:
            provider = get_sap_provider()
            ctx = provider.get_context()
            is_live = ctx.source_mode == SourceMode.LIVE and ctx.integration_status == IntegrationStatus.AVAILABLE
            return {
                "configured": True,
                "reachable": is_live,
                "authenticated": is_live,
                "healthy": is_live,
                "source_mode": ctx.source_mode.value,
                "modules_available": ctx.retrieved_entities if is_live else [],
                "system_name": ctx.system_name,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "message": ctx.message,
                "fallback_reason": None if is_live else "connection_failed",
            }
        except NotImplementedError as exc:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "healthy": False,
                "source_mode": SourceMode.SIMULATED.value,
                "modules_available": [],
                "message": str(exc),
                "fallback_reason": "live_not_implemented",
            }
        except Exception as exc:
            return {
                "configured": True,
                "reachable": False,
                "authenticated": False,
                "healthy": False,
                "source_mode": SourceMode.ERROR.value,
                "status": "ERROR",
                "modules_available": [],
                "message": str(exc),
                "fallback_reason": "connection_error",
            }
