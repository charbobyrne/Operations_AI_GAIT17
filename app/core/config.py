from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or a local .env file."""

    openai_api_key: str = ""
    openai_model_primary: str = "gpt-4.1-mini"
    openai_model_critic: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
