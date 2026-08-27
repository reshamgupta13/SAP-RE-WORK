"""LangGraph orchestration state."""

from operator import add
from typing import Annotated, Any, TypedDict


class ReworkGraphState(TypedDict, total=False):
    run_id: str
    status: str
    engine_mode: str
    candidate_id: str
    job_id: str
    candidate: dict[str, Any]
    job: dict[str, Any]
    sap_context: dict[str, Any]
    candidate_evidence: list[dict[str, Any]]
    candidate_capabilities: list[dict[str, Any]]
    job_tasks: list[dict[str, Any]]
    job_capabilities: list[dict[str, Any]]
    role_outcomes: list[dict[str, Any]]
    requirement_analyses: list[dict[str, Any]]
    capability_assessments: list[dict[str, Any]]
    capability_gaps: list[dict[str, Any]]
    requirement_diagnoses: list[dict[str, Any]]
    counterfactuals: list[dict[str, Any]]
    diagnosis_summary: dict[str, Any] | None
    run_mode: str
    learning_path: dict[str, Any] | None
    proof_assessment: dict[str, Any] | None
    proof_submission: dict[str, Any] | None
    proof_result: dict[str, Any] | None
    proof_evidence: dict[str, Any] | None
    capability_update_events: list[dict[str, Any]]
    updated_candidate_capabilities: list[dict[str, Any]]
    reassessment_summary: dict[str, Any] | None
    audit_events: Annotated[list[dict[str, Any]], add]
    errors: Annotated[list[str], add]
