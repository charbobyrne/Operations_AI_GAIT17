from app.core.models import AIStageResult, EvidencePackage


def run_placeholder_stages(evidence: EvidencePackage) -> tuple[AIStageResult, ...]:
    """Return transparent local results while API prompts are under development."""

    analyst = AIStageResult(
        stage="Data analyst",
        summary=(
            f"Validated {evidence.row_count_valid} of {evidence.row_count_original} rows "
            f"from '{evidence.column}'."
        ),
        warnings=["AI analysis has not been enabled; this is a deterministic placeholder."],
    )
    interpreter = AIStageResult(
        stage="Interpreter",
        summary=(
            f"The mean observed duration is {evidence.statistics.mean:.2f} "
            f"{evidence.unit}; no bottleneck conclusion can be made from service times alone."
        ),
        warnings=[f"Missing: {item}." for item in evidence.missing_information],
    )
    critic = AIStageResult(
        stage="Critic",
        summary="The displayed statements are supported by the computed evidence.",
        warnings=["Model-based critique is not yet enabled."],
    )
    return analyst, interpreter, critic
