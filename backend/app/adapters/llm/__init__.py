"""LLM provider factory."""

from app.adapters.llm.base import LLMProvider
from app.adapters.llm.configured import get_llm_provider as _get_provider

__all__ = ["get_llm_provider", "LLMProvider"]


def get_llm_provider() -> LLMProvider:
    return _get_provider()
