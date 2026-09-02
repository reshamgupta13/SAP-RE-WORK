"""Learning resource provider abstraction."""

from abc import ABC, abstractmethod

from app.domain.learning import LearningResource


class LearningResourceProvider(ABC):
    @abstractmethod
    def get_catalog_label(self) -> str:
        ...

    @abstractmethod
    def list_resources(self) -> list[LearningResource]:
        ...

    @abstractmethod
    def search(
        self,
        capability: str,
        *,
        step_type: str | None = None,
        limit: int = 4,
    ) -> list[LearningResource]:
        ...

    @abstractmethod
    def get_by_ids(self, resource_ids: list[str]) -> list[LearningResource]:
        ...

    def get_source_type(self) -> str:
        return "prototype_catalog"


class FutureSAPLearningResourceProvider(LearningResourceProvider):
    """Extension point for future SAP Learning Hub integration — not implemented."""

    def get_catalog_label(self) -> str:
        return "SAP Learning Hub (not connected)"

    def list_resources(self) -> list[LearningResource]:
        raise NotImplementedError("SAP Learning Hub integration is not yet available.")

    def search(
        self,
        capability: str,
        *,
        step_type: str | None = None,
        limit: int = 4,
    ) -> list[LearningResource]:
        raise NotImplementedError("SAP Learning Hub integration is not yet available.")

    def get_by_ids(self, resource_ids: list[str]) -> list[LearningResource]:
        raise NotImplementedError("SAP Learning Hub integration is not yet available.")
