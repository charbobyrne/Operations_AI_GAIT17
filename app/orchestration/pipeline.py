import pandas as pd

from app.ai.stages import run_placeholder_stages
from app.analysis.statistics import analyze_duration_column
from app.core.models import PipelineResult


def run_pipeline(frame: pd.DataFrame, column: str, unit: str) -> PipelineResult:
    evidence = analyze_duration_column(frame, column, unit)
    analyst, interpreter, critic = run_placeholder_stages(evidence)
    return PipelineResult(evidence=evidence, analyst=analyst, interpreter=interpreter, critic=critic)
