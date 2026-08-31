#!/usr/bin/env python3
"""Final demo prototype acceptance gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def main() -> int:
    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": ok, "detail": detail})

    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=BACKEND,
            capture_output=True,
            text=True,
            timeout=180,
        )
        record("pytest", r.returncode == 0, (r.stdout or r.stderr).strip().split("\n")[-1])
    except Exception as exc:
        record("pytest", False, str(exc))

    for script in ["golden_replay.py", "benchmark_eval.py", "demo_health_check.py", "redteam_heat_test.py"]:
        path = ROOT / "scripts" / script
        try:
            r = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, timeout=120)
            record(script, r.returncode == 0, (r.stdout or "")[-120:])
        except Exception as exc:
            record(script, False, str(exc))

    try:
        r = subprocess.run(
            ["npm", "run", "build"],
            cwd=ROOT / "frontend",
            capture_output=True,
            text=True,
            timeout=300,
            shell=True,
        )
        record("frontend_build", r.returncode == 0, "ok" if r.returncode == 0 else r.stderr[-200:])
    except Exception as exc:
        record("frontend_build", False, str(exc))

    ok = all(c["pass"] for c in checks)
    report = {"status": "PASS" if ok else "FAIL", "prototype": "FINAL_DEMO_READY", "checks": checks}
    out = ROOT / "artifacts" / "prototype_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
