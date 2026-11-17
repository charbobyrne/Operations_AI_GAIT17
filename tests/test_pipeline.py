import pandas as pd
from pydantic import BaseModel

from app.core.models import AIStageResult, AIUsageRecord
from app.orchestration.pipeline import run_pipeline


class FakeAIClient:
    def __init__(self) -> None:
        self.tasks: list[str] = []
        self.usage_records: list[AIUsageRecord] = []

    def generate(
        self,
        *,
        task: str,
        instructions: str,
        evidence: BaseModel,
        response_type: type[AIStageResult],
        critic: bool = False,
    ) -> AIStageResult:
        self.tasks.append(task)
        self.usage_records.append(
            AIUsageRecord(task=task, model="fake-model", input_tokens=10, output_tokens=5, total_tokens=15)
        )
        return response_type(stage="ignored", summary=f"Completed {task}.", blocking=False)


def test_pipeline_returns_three_stages() -> None:
    result = run_pipeline(pd.DataFrame({"duration": [1, 2, 3]}), "duration", "minutes")
    assert result.analyst.stage == "Data analyst"
    assert result.interpreter.stage == "Interpreter"
    assert result.critic.stage == "Critic"
    assert "no bottleneck conclusion" in result.interpreter.summary


def test_pipeline_runs_all_ai_stages_and_records_usage() -> None:
    client = FakeAIClient()
    result = run_pipeline(
        pd.DataFrame({"duration": [1, 2, 3]}),
        "duration",
        "minutes",
        ai_client=client,
    )

    assert client.tasks == ["data_analyst", "interpreter", "critic"]
    assert result.ai_enabled is True
    assert [stage.stage for stage in (result.analyst, result.interpreter, result.critic)] == [
        "Data analyst",
        "Interpreter",
        "Critic",
    ]
    assert sum(record.total_tokens for record in result.usage) == 45
