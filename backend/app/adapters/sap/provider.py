"""SAP provider abstraction — intelligence layer depends on this interface only."""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.candidate import CandidateCapability
from app.domain.job import JobProfile
from app.domain.pathway import LearningItem, Opportunity
from app.domain.sap import SAPContext


class SAPProvider(ABC):
    """Interface for SAP SuccessFactors-compatible workforce data access."""

    @abstractmethod
    def get_context(self) -> SAPContext:
        """Return integration context with explicit source_mode."""

    @abstractmethod
    def get_candidate_context(self, candidate_id: str) -> dict[str, Any]:
        """Workforce / employee context for a candidate."""

    @abstractmethod
    def get_employee_skills(self, candidate_id: str) -> list[CandidateCapability]:
        """Skills from Growth Portfolio or equivalent."""

    @abstractmethod
    def get_role_context(self, job_id: str) -> JobProfile | None:
        """Role / requisition structured context if available."""

    @abstractmethod
    def get_learning_items(self) -> list[LearningItem]:
        """Learning catalog items."""

    @abstractmethod
    def get_opportunities(self) -> list[Opportunity]:
        """Opportunity marketplace or requisition-backed opportunities."""

    def record_development_progress(self, candidate_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Write-back placeholder — human-approved only in production."""
        raise NotImplementedError("record_development_progress requires live SAP and human approval")

    def record_human_decision(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Write-back placeholder — human-approved only in production."""
        raise NotImplementedError("record_human_decision requires live SAP and human approval")
