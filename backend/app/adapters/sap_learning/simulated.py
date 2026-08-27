"""Simulated SAP Learning catalog provider."""

from typing import Any

from app.adapters.sap_learning.base import SAPLearningProvider
from app.domain.enums import SourceMode
from app.domain.pathway import LearningItem
from app.services.fixture_service import FixtureService


class SimulatedSAPLearningProvider(SAPLearningProvider):
    """Fixture-backed learning catalog. source_mode=SIMULATED for SAP-tagged items."""

    def __init__(self, fixture_service: FixtureService | None = None) -> None:
        self._fixtures = fixture_service or FixtureService()

    def get_source_mode(self) -> str:
        return SourceMode.SIMULATED.value

    def search_learning_items(
        self,
        capability: str,
        proficiency_gap: float,
        role_context: dict[str, Any] | None = None,
    ) -> list[LearningItem]:
        catalog = self._fixtures.get_sap_learning_items()
        matched = [
            item
            for item in catalog
            if item.capability == capability
            or capability in item.skill_alignment
            or capability.replace("_", " ") in item.title.lower()
        ]
        if not matched:
            matched = [
                item
                for item in catalog
                if capability.replace("_", "") in item.id.replace("-", "")
            ]

        if proficiency_gap >= 0.3:
            matched = sorted(matched, key=lambda i: i.difficulty)
        else:
            matched = sorted(matched, key=lambda i: i.hours)

        return matched[:4]
