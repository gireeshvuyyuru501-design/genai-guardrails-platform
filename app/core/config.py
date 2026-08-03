from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GenAI Guardrails Platform"
    environment: str = "development"
    llm_provider: str = "mock"
    llm_model: str = "mock-safe-assistant"
    audit_file: str = "data/guardrail_events.jsonl"
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
