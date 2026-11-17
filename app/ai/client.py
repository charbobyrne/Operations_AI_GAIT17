from typing import Protocol, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import Settings
from app.core.models import AIUsageRecord

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class AIClient(Protocol):
    """Provider-neutral contract used by AI stages."""

    usage_records: list[AIUsageRecord]

    def generate(
        self,
        *,
        task: str,
        instructions: str,
        evidence: BaseModel,
        response_type: type[ResponseT],
        critic: bool = False,
    ) -> ResponseT: ...


class OpenAIClient:
    """OpenAI Responses API adapter with Pydantic structured outputs."""

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=0,
        )
        self.usage_records: list[AIUsageRecord] = []
        self.call_count = 0

    def generate(
        self,
        *,
        task: str,
        instructions: str,
        evidence: BaseModel,
        response_type: type[ResponseT],
        critic: bool = False,
    ) -> ResponseT:
        if self.call_count >= self.settings.openai_max_calls_per_run:
            raise RuntimeError(
                f"API call budget exhausted: this run allows at most "
                f"{self.settings.openai_max_calls_per_run} calls."
            )

        payload = evidence.model_dump_json(indent=2)
        if len(payload) > self.settings.openai_max_input_characters:
            raise ValueError(
                "Evidence payload is too large for the configured API safety limit "
                f"({len(payload)} > {self.settings.openai_max_input_characters} characters)."
            )

        model = self.settings.openai_model_critic if critic else self.settings.openai_model_primary
        self.call_count += 1
        response = self.client.responses.parse(
            model=model,
            instructions=instructions,
            input=payload,
            text_format=response_type,
            max_output_tokens=self.settings.openai_max_output_tokens,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError(f"OpenAI returned no structured result for the {task} stage.")

        usage = response.usage
        self.usage_records.append(
            AIUsageRecord(
                task=task,
                model=model,
                input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
                output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
                total_tokens=getattr(usage, "total_tokens", 0) if usage else 0,
            )
        )
        return parsed
