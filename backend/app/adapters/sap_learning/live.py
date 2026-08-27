"""Live SAP Learning provider stub — not connected."""

from typing import Any

from app.adapters.sap_learning.base import SAPLearningProvider
from app.domain.enums import SourceMode
from app.domain.pathway import LearningItem


class LiveSAPLearningProvider(SAPLearningProvider):
    """Placeholder for live SAP Learning integration."""

    def get_source_mode(self) -> str:
        return SourceMode.LIVE.value

    def search_learning_items(
        self,
        capability: str,
        proficiency_gap: float,
        role_context: dict[str, Any] | None = None,
    ) -> list[LearningItem]:
        raise NotImplementedError("Live SAP Learning is not connected")
