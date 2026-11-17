import pandas as pd

from app.ai.client import AIClient
from app.ai.stages import run_ai_stages, run_placeholder_stages
from app.analysis.statistics import analyze_duration_column
from app.core.models import PipelineResult


def run_pipeline(
    frame: pd.DataFrame,
    column: str,
    unit: str,
    ai_client: AIClient | None = None,
) -> PipelineResult:
    evidence = analyze_duration_column(frame, column, unit)
    if ai_client is None:
        analyst, interpreter, critic = run_placeholder_stages(evidence)
        usage = []
    else:
        analyst, interpreter, critic = run_ai_stages(evidence, ai_client)
        usage = ai_client.usage_records
    return PipelineResult(
        evidence=evidence,
        analyst=analyst,
        interpreter=interpreter,
        critic=critic,
        ai_enabled=ai_client is not None,
        usage=usage,
    )
