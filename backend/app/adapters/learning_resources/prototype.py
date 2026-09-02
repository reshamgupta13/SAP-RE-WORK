"""Prototype learning resource catalog provider."""

import json

from pydantic import TypeAdapter

from app.adapters.learning_resources.base import LearningResourceProvider
from app.core.config import get_settings
from app.core.paths import resolve_fixtures_dir
from app.domain.learning import LearningResource

_TYPE_MAP = {
    "concept": "concept",
    "hands_on": "hands_on",
    "practice": "practice",
    "assessment": "assessment",
    "documentation": "documentation",
}


class PrototypeLearningResourceProvider(LearningResourceProvider):
    def __init__(self) -> None:
        settings = get_settings()
        catalog_path = resolve_fixtures_dir(settings.fixtures_dir) / "learning" / "prototype_catalog.json"
        with catalog_path.open(encoding="utf-8") as f:
            data = json.load(f)
        self._label = data.get("catalog_label", "RE:WORK Prototype Learning Catalog")
        self._resources = TypeAdapter(list[LearningResource]).validate_python(
            data.get("resources", [])
        )

    def get_catalog_label(self) -> str:
        return self._label

    def list_resources(self) -> list[LearningResource]:
        return list(self._resources)

    def search(
        self,
        capability: str,
        *,
        step_type: str | None = None,
        limit: int = 4,
    ) -> list[LearningResource]:
        cap = capability.lower().replace(" ", "_")
        matched = [
            r
            for r in self._resources
            if r.capability == cap
            or cap in r.capability
            or cap.replace("skill", "") in r.capability.replace("skill", "")
        ]
        if step_type:
            normalized = _TYPE_MAP.get(step_type, step_type)
            typed = [r for r in matched if r.type == normalized]
            if typed:
                matched = typed
        return matched[:limit]

    def get_by_ids(self, resource_ids: list[str]) -> list[LearningResource]:
        by_id = {r.id: r for r in self._resources}
        return [by_id[rid] for rid in resource_ids if rid in by_id]


def get_learning_resource_provider() -> LearningResourceProvider:
    return PrototypeLearningResourceProvider()
