"""Configured LLM provider (Gemini-compatible REST API)."""

import json
import logging
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.adapters.llm.base import LLMProvider
from app.core.config import get_settings
from app.domain.enums import EngineMode

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ConfiguredLLMProvider(LLMProvider):
    """Calls configured LLM API with JSON schema validation on response."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        provider_name: str = "gemini",
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_seconds
        self._provider_name = provider_name

    @property
    def engine_mode(self) -> EngineMode:
        return EngineMode.LLM

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        context: dict[str, Any] | None = None,
    ) -> T:
        ctx = context or {}
        system = ctx.get(
            "system_instruction",
            "Return only valid JSON matching the requested schema. No markdown.",
        )
        schema_json = json.dumps(schema.model_json_schema())
        full_prompt = (
            f"{system}\n\n"
            f"JSON Schema:\n{schema_json}\n\n"
            f"Task:\n{prompt}\n\n"
            "Respond with a single JSON object only."
        )

        if self._provider_name == "gemini":
            raw_text = self._call_gemini(full_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self._provider_name}")

        parsed = self._extract_json(raw_text)
        return schema.model_validate(parsed)

    def _call_gemini(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
        }
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=body)
            response.raise_for_status()
            data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected Gemini response shape: {data}") from exc

    def _extract_json(self, text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(text)


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_api_key:
        return ConfiguredLLMProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            provider_name=settings.llm_provider,
        )
    from app.adapters.llm.fallback import DeterministicFallbackProvider

    return DeterministicFallbackProvider()
