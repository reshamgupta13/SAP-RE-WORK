"""Live SAP provider — not implemented until verified tenant access exists."""

from typing import Any

from app.adapters.sap.provider import SAPProvider
from app.domain.candidate import CandidateCapability
from app.domain.job import JobProfile
from app.domain.pathway import LearningItem, Opportunity
from app.domain.sap import SAPContext


class LiveSAPProvider(SAPProvider):
    """
    Placeholder for BTP Destination / OData integration.
    DO NOT implement fake HTTP calls. Gate on verified credentials.
    """

    def get_context(self) -> SAPContext:
        raise NotImplementedError(
            "Live SAP is not connected. Use SimulatedSAPProvider until tenant is verified."
        )

    def get_candidate_context(self, candidate_id: str) -> dict[str, Any]:
        raise NotImplementedError("Live SAP not connected")

    def get_employee_skills(self, candidate_id: str) -> list[CandidateCapability]:
        raise NotImplementedError("Live SAP not connected")

    def get_role_context(self, job_id: str) -> JobProfile | None:
        raise NotImplementedError("Live SAP not connected")

    def get_learning_items(self) -> list[LearningItem]:
        raise NotImplementedError("Live SAP not connected")

    def get_opportunities(self) -> list[Opportunity]:
        raise NotImplementedError("Live SAP not connected")
