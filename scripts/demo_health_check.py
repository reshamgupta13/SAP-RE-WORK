#!/usr/bin/env python3
"""Verify demo readiness — PASS/FAIL gate."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient

from app.adapters.sap.health import SAPHealthService
from app.domain.enums import CaseStage
from app.main import app
from app.services.case_service import CaseService
from app.services.explainability_integrity_service import ExplainabilityIntegrityService


def main() -> int:
    checks: list[dict] = []
    client = TestClient(app)

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": ok, "detail": detail})

    # Backend health
    try:
        r = client.get("/api/health")
        record("api_health", r.status_code == 200 and r.json().get("status") == "ok", str(r.json()))
    except Exception as exc:
        record("api_health", False, str(exc))

    # SAP mode
    sap = SAPHealthService().check()
    record(
        "sap_source_mode",
        sap.get("source_mode") in {"SIMULATED", "LIVE"},
        sap.get("source_mode", ""),
    )

    # Golden case load + replay
    try:
        svc = CaseService()
        case = svc.get_or_create_finale_case()
        start = time.perf_counter()
        case = svc.execute(case.id, CaseStage.FINALE, idempotency_key="demo-health")
        elapsed = time.perf_counter() - start
        record("finale_case_execute", case.lifecycle_state.value == "EXPLANATION_READY", case.lifecycle_state.value)
        record("finale_replay_time", elapsed < 60.0, f"{elapsed:.1f}s")

        errors = ExplainabilityIntegrityService().validate(case.snapshot)
        record("explainability_integrity", len(errors) == 0, "; ".join(errors) or "ok")
        record("decision_card", bool(case.decision_card), "")
    except Exception as exc:
        record("finale_case_execute", False, str(exc))

    # Control room endpoint
    try:
        r = client.get("/api/demo/control-room")
        data = r.json()
        record(
            "control_room_api",
            r.status_code == 200 and data.get("case_id"),
            data.get("case_id", ""),
        )
        record(
            "sap_label_present",
            data.get("system_status", {}).get("sap") in {"SIMULATED", "LIVE"},
            str(data.get("system_status", {}).get("sap")),
        )
    except Exception as exc:
        record("control_room_api", False, str(exc))

    # Case export
    try:
        case_id = CaseService().FINALE_CASE_ID
        r = client.get(f"/api/cases/{case_id}/export")
        record("case_export", r.status_code == 200 and "sap_health" in r.json(), "")
    except Exception as exc:
        record("case_export", False, str(exc))

    all_pass = all(c["pass"] for c in checks)
    report = {"status": "PASS" if all_pass else "FAIL", "checks": checks}
    out = ROOT / "artifacts" / "demo_health_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
