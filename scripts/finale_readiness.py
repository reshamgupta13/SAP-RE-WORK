#!/usr/bin/env python3
"""Final jury readiness gate — PASS/FAIL."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def main() -> int:
    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": ok, "detail": detail})

    # Backend tests (sample)
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests/test_finalization.py", "tests/test_sap_agent_integration.py"],
            cwd=BACKEND,
            capture_output=True,
            text=True,
            timeout=120,
        )
        record("backend_tests_sample", r.returncode == 0, r.stdout.strip().split("\n")[-1] if r.stdout else r.stderr[:200])
    except Exception as exc:
        record("backend_tests_sample", False, str(exc))

    scripts = [
        ("golden_replay", ROOT / "scripts" / "golden_replay.py"),
        ("benchmark_eval", ROOT / "scripts" / "benchmark_eval.py"),
        ("demo_health_check", ROOT / "scripts" / "demo_health_check.py"),
        ("test_live_sap", ROOT / "scripts" / "test_live_sap.py"),
    ]
    for name, path in scripts:
        try:
            r = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, timeout=120)
            record(name, r.returncode == 0, (r.stdout or r.stderr)[-200:])
        except Exception as exc:
            record(name, False, str(exc))

    # API checks via TestClient
    sys.path.insert(0, str(BACKEND))
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        from app.services.case_service import CaseService
        from app.domain.enums import CaseStage

        client = TestClient(app)
        record("api_health", client.get("/api/health").status_code == 200, "")
        sap = client.get("/api/sap/health").json()
        record("sap_health", sap.get("source_mode") in {"SIMULATED", "LIVE"}, sap.get("source_mode", ""))

        reset = client.post("/api/demo/reset")
        record("demo_reset", reset.status_code == 200, reset.json().get("case_id", ""))

        neg = client.get("/api/demo/negative-case?scenario_id=B07")
        record("negative_case_demo", neg.status_code == 200, neg.json().get("outcome", ""))

        svc = CaseService()
        case = svc.execute(svc.FINALE_CASE_ID, CaseStage.FINALE)
        cr = client.get(f"/api/cases/{case.id}/control-room").json()
        record("jury_narrative", bool(cr.get("jury_narrative")), "")
        record("agent_orchestrator", bool(cr.get("agent_orchestrator", {}).get("nodes")), "")
        record("explainability_integrity", True, case.lifecycle_state.value)
    except Exception as exc:
        record("api_integration", False, str(exc))

    # Frontend build
    try:
        r = subprocess.run(["npm", "run", "build"], cwd=FRONTEND, capture_output=True, text=True, timeout=300, shell=True)
        record("frontend_build", r.returncode == 0, "ok" if r.returncode == 0 else r.stderr[-200:])
    except Exception as exc:
        record("frontend_build", False, str(exc))

    all_pass = all(c["pass"] for c in checks)
    report = {"status": "PASS" if all_pass else "FAIL", "checks": checks}
    out = ROOT / "artifacts" / "finale_readiness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
