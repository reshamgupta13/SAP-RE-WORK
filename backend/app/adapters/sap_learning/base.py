"""SAP Learning provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.pathway import LearningItem


class SAPLearningProvider(ABC):
    """Interface for SAP Learning catalog search — pathway engine uses this only."""

    @abstractmethod
    def search_learning_items(
        self,
        capability: str,
        proficiency_gap: float,
        role_context: dict[str, Any] | None = None,
    ) -> list[LearningItem]:
        """Return learning items aligned to a capability gap."""

    @abstractmethod
    def get_source_mode(self) -> str:
        """Return explicit source mode for provenance."""
