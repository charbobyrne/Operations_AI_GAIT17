import pandas as pd

from app.orchestration.pipeline import run_pipeline


def test_pipeline_returns_three_stages() -> None:
    result = run_pipeline(pd.DataFrame({"duration": [1, 2, 3]}), "duration", "minutes")
    assert result.analyst.stage == "Data analyst"
    assert result.interpreter.stage == "Interpreter"
    assert result.critic.stage == "Critic"
    assert "no bottleneck conclusion" in result.interpreter.summary
