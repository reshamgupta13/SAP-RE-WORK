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
    environment: str = "development"  # development | production
    debug: bool = False
    demo_mode: bool = True
    persistence_mode: str = "memory"  # memory | postgres
    sap_mode: str = "SIMULATED"  # SIMULATED | LIVE
    sap_api_url: str | None = None
    sap_client_id: str | None = None
    sap_client_secret: str | None = None
    sap_company_id: str | None = None
    # OData transport (configure when official URL is provided)
    sap_odata_base_url: str | None = None
    sap_odata_service: str | None = None
    sap_odata_metadata_url: str | None = None
    sap_timeout_seconds: float = 15.0
    sap_auth_mode: str = "NONE"  # NONE | BASIC | OAUTH2
    sap_username: str | None = None
    sap_password: str | None = None
    # Seven-table OData entity sets — fill after $metadata inspection
    sap_entity_user: str | None = None
    sap_entity_skill: str | None = None
    sap_entity_person_skill: str | None = None
    sap_entity_job: str | None = None
    sap_entity_job_skill: str | None = None
    sap_entity_organization: str | None = None
    sap_entity_hr: str | None = None
    # Legacy aliases
    sap_entity_person: str | None = None
    sap_entity_position: str | None = None
    sap_entity_qualification: str | None = None
    sap_entity_application: str | None = None
    sap_entity_learning: str | None = None
    sap_entity_opportunity: str | None = None
    sap_prototype_fallback: bool = True
    database_url: str = "postgresql+psycopg://rework:rework@localhost:5432/rework"
    fixtures_dir: str = "../fixtures"
    llm_provider: str = "groq"  # groq | gemini
    llm_api_key: str | None = None
    llm_model: str = "openai/gpt-oss-120b"
    llm_timeout_seconds: float = 30.0
    cors_origins: str | None = None  # comma-separated, e.g. https://rework.vercel.app


@lru_cache
def get_settings() -> Settings:
    return Settings()
