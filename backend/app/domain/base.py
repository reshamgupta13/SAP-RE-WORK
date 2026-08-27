"""Shared base models and mixins."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class TimestampedModel(DomainModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None


class IdentifiedModel(TimestampedModel):
    id: Annotated[str, Field(min_length=1, max_length=128)]
