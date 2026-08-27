"""LLM structured generation abstraction."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from app.domain.enums import EngineMode

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
  @property
  @abstractmethod
  def engine_mode(self) -> EngineMode:
    """Engine mode used by this provider."""

  @abstractmethod
  def generate_structured(
    self,
    prompt: str,
    schema: type[T],
    context: dict[str, Any] | None = None,
  ) -> T:
    """Generate and validate structured output against schema."""
