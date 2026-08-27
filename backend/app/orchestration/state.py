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
    audit_events: Annotated[list[dict[str, Any]], add]
    errors: Annotated[list[str], add]
