#!/usr/bin/env python3
"""Run benchmark evaluation against scenario catalog."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.domain.enums import CaseStage
from app.services.case_service import CaseService
from app.services.explainability_integrity_service import ExplainabilityIntegrityService


def main() -> int:
    scenarios_path = ROOT / "fixtures" / "benchmark" / "scenarios.json"
    with open(scenarios_path, encoding="utf-8") as f:
        catalog = json.load(f)

    service = CaseService()
    integrity = ExplainabilityIntegrityService()
    results = []

    # S01 — full Ananya case
    case = service.create_case(case_id="bench-s01")
    case = service.execute(case.id, execute_until=CaseStage.FINALE)
    s01_errors = integrity.validate(case.snapshot)
    results.append({
        "id": "S01",
        "status": "EXECUTED",
        "lifecycle": case.lifecycle_state.value,
        "integrity_errors": s01_errors,
        "scores": {
            "explainability_integrity": 2 if not s01_errors else 0,
            "governance_correctness": 2 if case.ai_recommendation else 0,
        },
    })

    for scenario in catalog["scenarios"]:
        if scenario["id"] == "S01":
            continue
        results.append({
            "id": scenario["id"],
            "type": scenario["type"],
            "status": scenario.get("status", "METADATA_ONLY"),
            "scores": None,
            "note": "Fixture not yet implemented — metadata catalog entry only.",
        })

    report = {
        "benchmark_version": catalog["benchmark_version"],
        "executed_count": sum(1 for r in results if r.get("status") == "EXECUTED"),
        "catalog_count": len(catalog["scenarios"]),
        "results": results,
    }

    out_dir = ROOT / "artifacts" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "latest_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Benchmark report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
