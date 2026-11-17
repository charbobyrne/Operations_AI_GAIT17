from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or a local .env file."""

    openai_api_key: str = ""
    openai_model_primary: str = "gpt-4.1-mini"
    openai_model_critic: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = Field(default=30, gt=0, le=60)
    openai_max_calls_per_run: int = Field(default=3, ge=1, le=3)
    openai_max_output_tokens: int = Field(default=500, ge=100, le=1000)
    openai_max_input_characters: int = Field(default=20_000, ge=1_000, le=50_000)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
