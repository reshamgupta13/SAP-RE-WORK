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
    persistence_mode: str = "memory"  # memory | postgres
    sap_mode: str = "SIMULATED"  # SIMULATED | LIVE
    sap_api_url: str | None = None
    sap_client_id: str | None = None
    sap_client_secret: str | None = None
    sap_company_id: str | None = None
    database_url: str = "postgresql+psycopg://rework:rework@localhost:5432/rework"
    fixtures_dir: str = "../fixtures"
    llm_provider: str = "gemini"
    llm_api_key: str | None = None
    llm_model: str = "gemini-2.0-flash"
    llm_timeout_seconds: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
