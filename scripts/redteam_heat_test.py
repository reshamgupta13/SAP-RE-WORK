#!/usr/bin/env python3
"""20-run demo heat test — stability without altering business logic."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.domain.enums import CaseStage  # noqa: E402
from app.main import app  # noqa: E402
from app.services.case_service import CaseService  # noqa: E402


def main() -> int:
    client = TestClient(app)
    svc = CaseService()
    runs = 20
    failures: list[str] = []
    durations: list[float] = []

    for i in range(runs):
        start = time.perf_counter()
        try:
            r = client.post("/api/demo/reset")
            if r.status_code != 200:
                failures.append(f"run {i+1}: reset {r.status_code}")
                continue
            case = svc.get_case(svc.FINALE_CASE_ID)
            if not case or case.lifecycle_state.value != "EXPLANATION_READY":
                failures.append(f"run {i+1}: lifecycle {getattr(case, 'lifecycle_state', None)}")
            cr = client.get("/api/demo/control-room")
            if cr.status_code != 200 or not cr.json().get("agent_orchestrator"):
                failures.append(f"run {i+1}: control room incomplete")
        except Exception as exc:
            failures.append(f"run {i+1}: {exc}")
        durations.append(time.perf_counter() - start)

    report = {
        "runs": runs,
        "failures": failures,
        "pass_rate": round((runs - len(failures)) / runs, 2),
        "avg_seconds": round(sum(durations) / max(len(durations), 1), 2),
        "max_seconds": round(max(durations) if durations else 0, 2),
        "status": "PASS" if not failures else "FAIL",
    }
    out = ROOT / "artifacts" / "redteam_heat_test.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
