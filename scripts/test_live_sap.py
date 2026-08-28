#!/usr/bin/env python3
"""Safe read-only SAP connectivity probe. Never prints secrets."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.adapters.sap.health import SAPHealthService  # noqa: E402
from app.core.config import get_settings  # noqa: E402


def main() -> int:
    settings = get_settings()
    sap_mode = os.getenv("SAP_MODE", settings.sap_mode if hasattr(settings, "sap_mode") else "SIMULATED")
    demo_mode = os.getenv("DEMO_MODE", "true").lower() in {"1", "true", "yes"}

    result = {
        "status": "NOT_CONFIGURED",
        "sap_mode": sap_mode,
        "demo_mode": demo_mode,
        "configured": False,
        "reachable": False,
        "authenticated": False,
        "modules_available": [],
        "message": "",
    }

    if demo_mode:
        result["status"] = "NOT_CONFIGURED"
        result["message"] = "DEMO_MODE=true — SAP runs in SIMULATED mode."
        print(json.dumps(result, indent=2))
        return 0

    if sap_mode.upper() != "LIVE":
        result["message"] = "SAP_MODE is not LIVE."
        print(json.dumps(result, indent=2))
        return 0

    api_url = os.getenv("SAP_API_URL", "")
    client_id = os.getenv("SAP_CLIENT_ID", "")
    client_secret = os.getenv("SAP_CLIENT_SECRET", "")

    result["configured"] = bool(api_url and client_id and client_secret)
    if not result["configured"]:
        result["message"] = "SAP_MODE=LIVE but credentials incomplete."
        print(json.dumps(result, indent=2))
        return 1

    health = SAPHealthService().check()
    result.update({
        "status": "PASS" if health.get("healthy") and health.get("authenticated") else "FAIL",
        "reachable": health.get("reachable", False),
        "authenticated": health.get("authenticated", False),
        "modules_available": health.get("modules_available", []),
        "source_mode": health.get("source_mode"),
        "message": health.get("message"),
        "fallback_reason": health.get("fallback_reason"),
    })

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
