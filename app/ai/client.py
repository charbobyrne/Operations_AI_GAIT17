from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.core.config import Settings

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class AIClient(Protocol):
    """Provider-neutral contract used by AI stages."""

    def generate(self, *, task: str, evidence: BaseModel, response_type: type[ResponseT]) -> ResponseT: ...


class OpenAIClient:
    """OpenAI adapter placeholder; prompts follow after evaluation cases are defined."""

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        self.settings = settings

    def generate(self, *, task: str, evidence: BaseModel, response_type: type[ResponseT]) -> ResponseT:
        raise NotImplementedError(
            "The adapter is disabled until prompts and evaluation cases are approved."
        )
