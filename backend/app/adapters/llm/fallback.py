"""Deterministic structured generation for demo reliability."""

import json
from typing import Any, TypeVar

from pydantic import BaseModel

from app.adapters.llm.base import LLMProvider
from app.domain.enums import EngineMode

T = TypeVar("T", bound=BaseModel)


class DeterministicFallbackProvider(LLMProvider):
    """Fixture-aware fallback — not a general NLP engine."""

    @property
    def engine_mode(self) -> EngineMode:
        return EngineMode.DEMO_FALLBACK

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        context: dict[str, Any] | None = None,
    ) -> T:
        ctx = context or {}
        payload = ctx.get("fallback_payload")
        if payload is None:
            raise ValueError("DeterministicFallbackProvider requires fallback_payload in context")
        if isinstance(payload, dict):
            return schema.model_validate(payload)
        if isinstance(payload, str):
            return schema.model_validate(json.loads(payload))
        raise ValueError("fallback_payload must be dict or JSON string")
