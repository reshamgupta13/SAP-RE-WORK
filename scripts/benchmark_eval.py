#!/usr/bin/env python3
"""Full benchmark evaluation — 22 executable scenarios + finale case."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.domain.enums import CaseStage
from app.services.benchmark_runner import BenchmarkRunner
from app.services.case_service import CaseService
from app.services.explainability_integrity_service import ExplainabilityIntegrityService


def main() -> int:
    runner = BenchmarkRunner()
    pack_path = ROOT / "fixtures" / "benchmark" / "executable_pack.json"
    runner.export_fixtures_json(pack_path)

    report = runner.run_all()
    report["finale_case"] = {}

    svc = CaseService()
    case = svc.get_or_create_finale_case()
    case = svc.execute(case.id, CaseStage.FINALE, idempotency_key="benchmark-finale")
    integrity_errors = ExplainabilityIntegrityService().validate(case.snapshot)
    report["finale_case"] = {
        "case_id": case.id,
        "lifecycle": case.lifecycle_state.value,
        "integrity_errors": integrity_errors,
        "pass": not integrity_errors,
    }

    out_dir = ROOT / "artifacts" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    final_path = out_dir / "final_benchmark_report.json"
    latest_path = out_dir / "latest_report.json"
    final_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    latest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Benchmark: {report['passed']}/{report['executed_count']} passed")
    print(f"Report: {final_path}")
    failed = report["failed"] > 0 or not report["finale_case"].get("pass")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
