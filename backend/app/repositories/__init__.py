"""Repository factory — InMemory default; Postgres when configured."""

from app.core.config import get_settings
from app.repositories.case_repository import CaseRepository
from app.repositories.in_memory_case_repository import InMemoryCaseRepository, in_memory_case_repository


def get_case_repository() -> CaseRepository:
    settings = get_settings()
    if settings.persistence_mode == "postgres" and not settings.demo_mode:
        try:
            from app.repositories.postgres_case_repository import PostgresCaseRepository

            return PostgresCaseRepository()
        except Exception:
            return in_memory_case_repository
    return in_memory_case_repository
