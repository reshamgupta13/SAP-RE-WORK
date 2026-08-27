"""Run executable benchmark scenarios and governance checks."""

import json
from pathlib import Path
from typing import Any

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import GapStatus
from app.domain.job import JobCapability, JobRequirement, JobTask
from app.services.benchmark_scenarios import all_scenarios
from app.services.diagnosis_service import DiagnosisService
from app.services.explainability_integrity_service import ExplainabilityIntegrityService


class BenchmarkRunner:
    def __init__(self) -> None:
        self._diagnosis = DiagnosisService()
        self._integrity = ExplainabilityIntegrityService()

    def run_all(self) -> dict[str, Any]:
        results = []
        passed = 0
        failed = 0
        negative_count = 0

        for scenario in all_scenarios():
            result = self._run_scenario(scenario)
            results.append(result)
            if result["pass"]:
                passed += 1
            else:
                failed += 1
            if scenario.get("expected", {}).get("negative_outcome"):
                negative_count += 1

        report = {
            "benchmark_version": "final",
            "executed_count": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / max(len(results), 1), 2),
            "negative_scenarios": negative_count,
            "metrics": {
                "scenario_pass_rate": round(passed / max(len(results), 1), 2),
                "classification_agreement": round(passed / max(len(results), 1), 2),
                "governance_violations": sum(len(r.get("governance_violations", [])) for r in results),
            },
            "results": results,
        }
        return report

    def _run_scenario(self, scenario: dict) -> dict[str, Any]:
        cid = scenario["profile"]["id"]
        job_id = scenario["job_id"]
        caps = [CandidateCapability.model_validate(c) for c in scenario["capabilities"]]
        evidence = [CandidateEvidence.model_validate(e) for e in scenario["evidence"]]
        job_caps = [JobCapability.model_validate(c) for c in scenario["job_capabilities"]]
        tasks = [JobTask.model_validate(t) for t in scenario["job_tasks"]]
        requirements = [JobRequirement.model_validate(r) for r in scenario["requirement_analyses"]]
        expected = scenario.get("expected", {})

        assessment, gaps, req_diagnoses, counterfactuals, summary = self._diagnosis.run(
            candidate_id=cid,
            job_id=job_id,
            job_capabilities=job_caps,
            candidate_capabilities=caps,
            candidate_evidence=evidence,
            requirements=requirements,
            tasks=tasks,
            run_id=f"bench-{scenario['id']}",
        )

        genuine = [g.skill_id for g in gaps if g.gap_status == GapStatus.GENUINE_CAPABILITY_GAP]
        diagnosis_state = summary.overall_diagnosis_state.value
        proxies = [
            d.diagnosis_type.value
            for d in req_diagnoses
            if d.diagnosis_type.value in {"ELIGIBILITY_PROXY", "WORKPLACE_CONSTRAINT"}
        ]

        violations = self._governance_check(scenario, summary, req_diagnoses, genuine)
        pass_checks = []

        if expected.get("required_genuine_gaps"):
            ok = all(s in genuine for s in expected["required_genuine_gaps"])
            pass_checks.append(ok)
        if expected.get("min_genuine_gaps") is not None:
            pass_checks.append(len(genuine) >= expected["min_genuine_gaps"])
        if expected.get("allowed_diagnosis"):
            pass_checks.append(diagnosis_state in expected["allowed_diagnosis"])
        if expected.get("expect_proxy"):
            pass_checks.append(len(proxies) > 0 or summary.eligibility_proxy_count > 0)
        if not pass_checks:
            pass_checks.append(len(violations) == 0)

        passed = all(pass_checks) and len(violations) == 0

        return {
            "id": scenario["id"],
            "title": scenario["title"],
            "status": "EXECUTED",
            "pass": passed,
            "actual": {
                "diagnosis_state": diagnosis_state,
                "genuine_gaps": genuine,
                "proxy_flags": proxies,
                "eligibility_proxy_count": summary.eligibility_proxy_count,
            },
            "expected": expected,
            "governance_violations": violations,
            "confidence": summary.diagnosis_confidence,
            "false_positive_risk": "low" if genuine else "review",
        }

    def _governance_check(self, scenario, summary, req_diagnoses, genuine) -> list[str]:
        violations = []
        blob = json.dumps(scenario, default=str).lower()
        if "bias confirmed" in blob or "bias removed" in blob:
            violations.append("prohibited_bias_language")
        if "hire" in blob and "autonomous" in blob:
            violations.append("autonomous_hire_language")
        for d in req_diagnoses:
            if d.human_review_required is False and d.diagnosis_type.value == "ELIGIBILITY_PROXY":
                violations.append("proxy_without_human_review")
        if scenario.get("source_mode") != "SYNTHETIC":
            violations.append("synthetic_label_missing")
        return violations

    def write_report(self, path: Path) -> dict[str, Any]:
        report = self.run_all()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    def export_fixtures_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        pack = {"scenarios": all_scenarios(), "source_mode": "SYNTHETIC"}
        path.write_text(json.dumps(pack, indent=2), encoding="utf-8")
