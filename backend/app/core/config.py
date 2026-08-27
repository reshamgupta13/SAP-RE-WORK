"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RE:WORK API"
    debug: bool = False
    demo_mode: bool = True
    database_url: str = "postgresql+psycopg://rework:rework@localhost:5432/rework"
    fixtures_dir: str = "../fixtures"


@lru_cache
def get_settings() -> Settings:
    return Settings()
