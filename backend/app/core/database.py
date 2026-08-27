"""PostgreSQL connection configuration for future persistence layers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def get_engine():
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    """Dependency for FastAPI routes when DB is required."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
