#!/usr/bin/env python3
"""SAP OData connectivity diagnostic. Never prints secrets."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.adapters.sap.health import SAPHealthService  # noqa: E402
from app.adapters.sap.odata_config import build_access_plan  # noqa: E402
from app.core.config import get_settings  # noqa: E402


def main() -> int:
    settings = get_settings()
    sap_mode = os.getenv("SAP_MODE", settings.sap_mode)
    demo_mode = os.getenv("DEMO_MODE", str(settings.demo_mode)).lower() in {"1", "true", "yes"}
    plan = build_access_plan()

    result = {
        "sap_configuration": {
            "sap_mode": sap_mode,
            "demo_mode": demo_mode,
            "url_configured": bool(settings.sap_odata_base_url or settings.sap_api_url),
            "odata_service": settings.sap_odata_service,
            "auth_mode": settings.sap_auth_mode,
            "timeout_seconds": settings.sap_timeout_seconds,
        },
        "connectivity": {
            "endpoint_reachable": False,
            "authentication": False,
            "metadata": False,
        },
        "entities": {},
        "source_mode": "SIMULATED",
        "status": "NOT_CONFIGURED",
        "message": "",
    }

    if demo_mode:
        result["message"] = "DEMO_MODE=true — SAP runs in SIMULATED mode."
        result["source_mode"] = "SIMULATED"
        print(json.dumps(result, indent=2))
        return 0

    if sap_mode.upper() != "LIVE":
        result["message"] = "SAP_MODE is not LIVE."
        result["source_mode"] = "SIMULATED"
        print(json.dumps(result, indent=2))
        return 0

    for entity in plan.entity_mappings:
        result["entities"][entity.domain] = (
            "CONFIGURED" if entity.entity_set else "PENDING_OFFICIAL_ODATA_METADATA"
        )

    health = SAPHealthService().check()
    result["connectivity"]["endpoint_reachable"] = health.get("reachable", False)
    result["connectivity"]["authentication"] = health.get("authenticated", False)
    result["connectivity"]["metadata"] = health.get("metadata_accessible", False)
    result["source_mode"] = health.get("source_mode", "NOT_CONNECTED")
    result["message"] = health.get("message", "")
    result["entity_status"] = health.get("entity_status", {})
    result["fallback_reason"] = health.get("fallback_reason")

    if health.get("healthy"):
        result["status"] = "LIVE" if result["source_mode"] == "LIVE" else "PARTIAL"
    elif result["source_mode"] == "ERROR":
        result["status"] = "ERROR"
    else:
        result["status"] = "NOT_CONNECTED"

    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"LIVE", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
