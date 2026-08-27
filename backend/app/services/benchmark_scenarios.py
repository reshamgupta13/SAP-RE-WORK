"""Executable benchmark scenario definitions — 22 scenarios."""

from datetime import date

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    GapStatus,
    RecencyStatus,
    SourceMode,
    VerificationStatus,
)
from app.domain.enums import RequirementClass, ReviewTag
from tests.diagnosis_fixtures import (
    make_capability,
    make_evidence,
    make_job_capability,
    make_requirement,
    make_task,
)

_JOB_ID = "data-analyst-junior"
_CID = "bench-candidate"


def _profile(id_suffix: str, location: str = "Bangalore", work_modes: list[str] | None = None):
    return {
        "id": f"bench-{id_suffix}",
        "display_name": f"Bench Candidate {id_suffix}",
        "location": location,
        "work_modes": work_modes or ["hybrid", "remote"],
        "languages": ["en"],
        "source": "REWORK",
        "source_mode": "SYNTHETIC",
        "is_demo_persona": False,
        "created_at": "2026-08-28T00:00:00",
    }


def _pack(id: str, title: str, caps, evidence, expected: dict) -> dict:
    return {
        "id": id,
        "title": title,
        "candidate_id": expected.get("candidate_id", _CID),
        "job_id": _JOB_ID,
        "profile": expected.get("profile") or _profile(id.lower()),
        "evidence": [e.model_dump(mode="json") for e in evidence],
        "capabilities": [c.model_dump(mode="json") for c in caps],
        "expected": expected,
        "source_mode": "SYNTHETIC",
    }


# Shared job decomposition slice (from data analyst fixture)
def base_job_slice() -> dict:
    return {
        "job_capabilities": [
            make_job_capability("sql", "SQL", 0.55, _JOB_ID).model_dump(mode="json"),
            make_job_capability("excel", "Excel", 0.55, _JOB_ID).model_dump(mode="json"),
            make_job_capability("power_bi", "Power BI", 0.6, _JOB_ID).model_dump(mode="json"),
            make_job_capability("communication", "Communication", 0.5, _JOB_ID).model_dump(mode="json"),
            make_job_capability("data_analysis", "Data Analysis", 0.55, _JOB_ID).model_dump(mode="json"),
        ],
        "job_tasks": [
            make_task("task-sql", "SQL extracts", ["sql", "data_analysis"], _JOB_ID).model_dump(mode="json"),
            make_task("task-dash", "Dashboards", ["power_bi", "reporting"], _JOB_ID).model_dump(mode="json"),
        ],
        "requirement_analyses": [
            make_requirement(
                "req-exp",
                "3 years continuous experience",
                RequirementClass.EXPERIENCE_REQUIREMENT,
                _JOB_ID,
                ReviewTag.POTENTIAL_PROXY,
            ).model_dump(mode="json"),
            make_requirement(
                "req-loc",
                "Bangalore onsite 5 days",
                RequirementClass.WORKPLACE_CONDITION,
                _JOB_ID,
                ReviewTag.POTENTIAL_PROXY,
            ).model_dump(mode="json"),
        ],
    }


def all_scenarios() -> list[dict]:
    scenarios = []

    # B01 Strong match
    ev = [make_evidence("ev-b01-sql", title="SQL projects", confidence=0.9)]
    caps = [
        make_capability("sql", "SQL", 0.85, ["ev-b01-sql"]),
        make_capability("excel", "Excel", 0.8, ["ev-b01-sql"]),
        make_capability("power_bi", "Power BI", 0.75, ["ev-b01-sql"]),
        make_capability("communication", "Communication", 0.7, ["ev-b01-sql"]),
        make_capability("data_analysis", "Data Analysis", 0.8, ["ev-b01-sql"]),
    ]
    scenarios.append(
        _pack("B01", "Strong match", caps, ev, {
            "allowed_diagnosis": ["STRONG_MATCH", "MATCH_WITH_GAPS", "POTENTIALLY_VIABLE"],
            "min_genuine_gaps": 0,
            "negative_outcome": False,
        })
    )

    # B02 True capability gap — no SQL
    ev = [make_evidence("ev-b02-excel", title="Excel only")]
    caps = [
        make_capability("excel", "Excel", 0.7, ["ev-b02-excel"]),
        make_capability("communication", "Communication", 0.65, ["ev-b02-excel"]),
    ]
    scenarios.append(
        _pack("B02", "True capability gap", caps, ev, {
            "allowed_diagnosis": ["INSUFFICIENT_EVIDENCE", "NOT_CURRENTLY_READY", "MATCH_WITH_GAPS"],
            "negative_outcome": True,
        })
    )

    # B03 Career returner — power bi gap + proxy
    ev = [
        make_evidence("ev-b03-mis", title="MIS project", occurred_on=date(2023, 2, 1)),
        make_evidence("ev-b03-self", title="Self Power BI", evidence_type=EvidenceType.SELF_REPORTED,
                      verification=VerificationStatus.SELF_REPORTED, confidence=0.35),
    ]
    caps = [
        make_capability("sql", "SQL", 0.62, ["ev-b03-mis"]),
        make_capability("excel", "Excel", 0.7, ["ev-b03-mis"]),
        make_capability("power_bi", "Power BI", 0.22, ["ev-b03-self"],
                        verification=CapabilityVerificationStatus.SELF_REPORTED),
        make_capability("communication", "Communication", 0.68, ["ev-b03-mis"]),
        make_capability("data_analysis", "Data Analysis", 0.55, ["ev-b03-mis"]),
    ]
    scenarios.append(
        _pack("B03", "Career returner", caps, ev, {
            "required_genuine_gaps": ["power_bi"],
            "expect_proxy": True,
            "negative_outcome": False,
        })
    )

    # B04 Credential proxy — strong skills, degree gap narrative
    ev = [make_evidence("ev-b04-git", title="Git portfolio", confidence=0.92)]
    caps = [
        make_capability("sql", "SQL", 0.8, ["ev-b04-git"]),
        make_capability("data_analysis", "Data Analysis", 0.78, ["ev-b04-git"]),
        make_capability("power_bi", "Power BI", 0.72, ["ev-b04-git"]),
    ]
    scenarios.append(
        _pack("B04", "Credential proxy candidate", caps, ev, {
            "expect_proxy": True,
            "min_genuine_gaps": 0,
            "negative_outcome": False,
        })
    )

    # B05 Experience proxy — 18 months intense SQL
    ev = [make_evidence("ev-b05-sql", title="18mo SQL contract", occurred_on=date(2024, 6, 1))]
    caps = [
        make_capability("sql", "SQL", 0.78, ["ev-b05-sql"]),
        make_capability("excel", "Excel", 0.7, ["ev-b05-sql"]),
        make_capability("power_bi", "Power BI", 0.55, ["ev-b05-sql"]),
    ]
    scenarios.append(
        _pack("B05", "Experience proxy candidate", caps, ev, {"expect_proxy": True}))

    # B06 Workplace constraint — remote only candidate vs onsite job
    ev = [make_evidence("ev-b06", title="Remote analytics")]
    caps = [
        make_capability("sql", "SQL", 0.7, ["ev-b06"]),
        make_capability("data_analysis", "Data Analysis", 0.72, ["ev-b06"]),
    ]
    scenarios.append(
        _pack("B06", "Workplace constraint", caps, ev, {
            "profile": _profile("b06", location="Lucknow", work_modes=["remote"]),
            "expect_workplace_constraint": True,
        })
    )

    # B07 Insufficient evidence — self-reported only
    ev = [
        make_evidence("ev-b07", title="Self claim", evidence_type=EvidenceType.SELF_REPORTED,
                      verification=VerificationStatus.SELF_REPORTED, confidence=0.3),
    ]
    caps = [
        make_capability("sql", "SQL", 0.5, ["ev-b07"],
                        verification=CapabilityVerificationStatus.SELF_REPORTED),
    ]
    scenarios.append(
        _pack("B07", "Insufficient evidence", caps, ev, {
            "allowed_diagnosis": ["INSUFFICIENT_EVIDENCE", "REQUIRES_HUMAN_REVIEW", "MATCH_WITH_GAPS"],
            "negative_outcome": True,
        })
    )

    # B08 Transferable capability — BPM to analyst
    ev = [make_evidence("ev-b08", title="BPM reporting")]
    caps = [
        make_capability("excel", "Excel", 0.82, ["ev-b08"]),
        make_capability("sql", "SQL", 0.58, ["ev-b08"]),
        make_capability("data_analysis", "Data Analysis", 0.6, ["ev-b08"]),
    ]
    scenarios.append(_pack("B08", "Transferable capability", caps, ev, {}))

    # B09 Adjacent capability — Excel god, no SQL
    ev = [make_evidence("ev-b09", title="Excel expert")]
    caps = [
        make_capability("excel", "Excel", 0.95, ["ev-b09"]),
        make_capability("communication", "Communication", 0.7, ["ev-b09"]),
    ]
    scenarios.append(
        _pack("B09", "Adjacent capability", caps, ev, {
            "allowed_diagnosis": ["INSUFFICIENT_EVIDENCE", "NOT_CURRENTLY_READY", "MATCH_WITH_GAPS"],
            "negative_outcome": True,
        })
    )

    # B10 Stale evidence
    ev = [make_evidence("ev-b10", title="Old SQL work", occurred_on=date(2018, 1, 1))]
    caps = [
        make_capability("sql", "SQL", 0.75, ["ev-b10"], recency=RecencyStatus.STALE),
        make_capability("power_bi", "Power BI", 0.3, ["ev-b10"]),
    ]
    scenarios.append(_pack("B10", "Stale evidence", caps, ev, {"expect_stale": True}))

    # B11 Employer not ready — diagnosis only; flagged in metadata
    scenarios.append(
        _pack("B11", "Employer not ready", caps=[
            make_capability("sql", "SQL", 0.7, ["ev-b11"]),
        ], evidence=[make_evidence("ev-b11")], expected={
            "employer_not_ready": True,
            "note": "Employer readiness evaluated at opportunity stage",
        })
    )

    # B12 Two-sided gap — candidate + employer metadata
    scenarios.append(
        _pack("B12", "Two-sided gap", caps=[
            make_capability("power_bi", "Power BI", 0.25, ["ev-b12"]),
            make_capability("sql", "SQL", 0.6, ["ev-b12"]),
        ], evidence=[make_evidence("ev-b12")], expected={
            "required_genuine_gaps": ["power_bi"],
            "two_sided": True,
        })
    )

    # B13 Multiple viable — strong generalist
    ev = [make_evidence("ev-b13", confidence=0.88)]
    caps = [
        make_capability("sql", "SQL", 0.8, ["ev-b13"]),
        make_capability("excel", "Excel", 0.78, ["ev-b13"]),
        make_capability("power_bi", "Power BI", 0.72, ["ev-b13"]),
        make_capability("data_analysis", "Data Analysis", 0.75, ["ev-b13"]),
    ]
    scenarios.append(_pack("B13", "Multiple viable opportunities", caps, ev, {"min_genuine_gaps": 0}))

    # B14 No viable — missing core skills
    caps = [make_capability("communication", "Communication", 0.5, ["ev-b14"])]
    scenarios.append(
        _pack("B14", "No viable opportunities", caps, [make_evidence("ev-b14")], {
            "allowed_diagnosis": ["NOT_CURRENTLY_READY", "INSUFFICIENT_EVIDENCE", "REQUIRES_HUMAN_REVIEW"],
            "negative_outcome": True,
        })
    )

    # B15 Conflicting evidence
    ev = [
        make_evidence("ev-b15a", title="Strong SQL", confidence=0.9),
        make_evidence("ev-b15b", title="Weak SQL claim", evidence_type=EvidenceType.SELF_REPORTED,
                      verification=VerificationStatus.SELF_REPORTED, confidence=0.2),
    ]
    caps = [make_capability("sql", "SQL", 0.65, ["ev-b15a", "ev-b15b"])]
    scenarios.append(_pack("B15", "Conflicting candidate evidence", caps, ev, {}))

    # B16 Conflicting job requirements — handled via job slice
    scenarios.append(
        _pack("B16", "Conflicting job requirements", caps=[
            make_capability("sql", "SQL", 0.7, ["ev-b16"]),
        ], evidence=[make_evidence("ev-b16")], expected={"note": "Job conflict in requirements"})
    )

    # B17 Necessary credential — statutory license missing
    caps = [make_capability("sql", "SQL", 0.4, ["ev-b17"])]
    scenarios.append(
        _pack("B17", "Necessary credential", caps, [make_evidence("ev-b17")], {
            "allowed_diagnosis": ["NOT_CURRENTLY_READY", "REQUIRES_HUMAN_REVIEW", "MATCH_WITH_GAPS"],
            "negative_outcome": True,
        })
    )

    # B18 Accessibility compatible — remote/hybrid
    scenarios.append(
        _pack("B18", "Accessibility compatible role", caps=[
            make_capability("sql", "SQL", 0.7, ["ev-b18"]),
        ], evidence=[make_evidence("ev-b18")], expected={
            "profile": _profile("b18", work_modes=["remote", "hybrid"]),
        })
    )

    # B19 Accessibility incompatible — onsite only mismatch
    scenarios.append(
        _pack("B19", "Accessibility incompatible role", caps=[
            make_capability("sql", "SQL", 0.7, ["ev-b19"]),
        ], evidence=[make_evidence("ev-b19")], expected={
            "profile": _profile("b19", work_modes=["remote"]),
            "expect_workplace_constraint": True,
        })
    )

    # B20 Displaced worker — voice ops, no data evidence
    scenarios.append(
        _pack("B20", "Displaced worker", caps=[
            make_capability("communication", "Communication", 0.75, ["ev-b20"]),
        ], evidence=[make_evidence("ev-b20", title="Call center ops")], expected={
            "allowed_diagnosis": ["INSUFFICIENT_EVIDENCE", "NOT_CURRENTLY_READY", "REQUIRES_HUMAN_REVIEW"],
            "negative_outcome": True,
        })
    )

    # B21 Tier-2/3 — institution proxy
    scenarios.append(
        _pack("B21", "Tier-2/3 candidate", caps=[
            make_capability("sql", "SQL", 0.68, ["ev-b21"]),
            make_capability("excel", "Excel", 0.7, ["ev-b21"]),
        ], evidence=[make_evidence("ev-b21", title="Regional college degree")], expected={
            "expect_proxy": True,
            "profile": _profile("b21", location="Lucknow"),
        })
    )

    # B22 Reskilling — accountant to analyst
    scenarios.append(
        _pack("B22", "Reskilling candidate", caps=[
            make_capability("excel", "Excel", 0.85, ["ev-b22"]),
            make_capability("communication", "Communication", 0.7, ["ev-b22"]),
        ], evidence=[make_evidence("ev-b22", title="Accounting background")], expected={
            "allowed_diagnosis": ["INSUFFICIENT_EVIDENCE", "NOT_CURRENTLY_READY", "MATCH_WITH_GAPS"],
            "negative_outcome": True,
        })
    )

    job_slice = base_job_slice()
    for s in scenarios:
        s.update(job_slice)
    return scenarios

