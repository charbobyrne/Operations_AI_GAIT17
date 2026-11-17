from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.ai.client import OpenAIClient
from app.core.config import Settings
from app.core.models import AIStageResult


class SmallEvidence(BaseModel):
    value: int = 1


class FakeResponses:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_parsed=AIStageResult(stage="test", summary="safe"),
            usage=SimpleNamespace(input_tokens=10, output_tokens=5, total_tokens=15),
        )


class FakeSDK:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def make_client() -> OpenAIClient:
    client = OpenAIClient.__new__(OpenAIClient)
    client.settings = Settings(openai_api_key="test-key")
    client.client = FakeSDK()
    client.usage_records = []
    client.call_count = 0
    return client


def generate_once(client: OpenAIClient) -> AIStageResult:
    return client.generate(
        task="test",
        instructions="Use supplied evidence only.",
        evidence=SmallEvidence(),
        response_type=AIStageResult,
    )


def test_api_call_budget_blocks_fourth_call_before_network() -> None:
    client = make_client()

    for _ in range(3):
        generate_once(client)

    with pytest.raises(RuntimeError, match="call budget exhausted"):
        generate_once(client)

    assert len(client.client.responses.calls) == 3


def test_every_call_has_output_token_cap() -> None:
    client = make_client()

    generate_once(client)

    assert client.client.responses.calls[0]["max_output_tokens"] == 500


def test_oversized_input_is_rejected_before_network() -> None:
    client = make_client()
    client.settings = Settings(openai_api_key="test-key", openai_max_input_characters=1_000)

    class LargeEvidence(BaseModel):
        value: str

    with pytest.raises(ValueError, match="too large"):
        client.generate(
            task="test",
            instructions="Use supplied evidence only.",
            evidence=LargeEvidence(value="x" * 2_000),
            response_type=AIStageResult,
        )

    assert not client.client.responses.calls
