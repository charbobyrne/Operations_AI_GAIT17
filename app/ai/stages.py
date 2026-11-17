from pydantic import BaseModel

from app.ai.client import AIClient
from app.core.models import AIStageResult, EvidencePackage


class InterpretationContext(BaseModel):
    evidence: EvidencePackage
    analyst: AIStageResult


class CritiqueContext(BaseModel):
    evidence: EvidencePackage
    analyst: AIStageResult
    interpreter: AIStageResult


COMMON_RULES = """
Use only the supplied JSON evidence. Never invent statistics, arrivals, staffing, capacity,
bottlenecks, causal explanations, or business context. State missing inputs plainly. Keep the
summary under 140 words. Warnings should be short and actionable. Set blocking true only when
the proposed interpretation is unsafe or materially unsupported.
""".strip()


def run_ai_stages(evidence: EvidencePackage, client: AIClient) -> tuple[AIStageResult, ...]:
    analyst = client.generate(
        task="data_analyst",
        instructions=(
            "You are the data analyst stage. Describe data quality, exclusions, and what the "
            "computed statistics establish. Do not diagnose a bottleneck. " + COMMON_RULES
        ),
        evidence=evidence,
        response_type=AIStageResult,
    )
    analyst = analyst.model_copy(update={"stage": "Data analyst"})
    interpreter = client.generate(
        task="interpreter",
        instructions=(
            "You are the operations interpreter stage. Explain the computed evidence in plain "
            "language and identify what additional data is required for operational conclusions. "
            + COMMON_RULES
        ),
        evidence=InterpretationContext(evidence=evidence, analyst=analyst),
        response_type=AIStageResult,
    )
    interpreter = interpreter.model_copy(update={"stage": "Interpreter"})
    critic = client.generate(
        task="critic",
        instructions=(
            "You are the final grounding critic. Check every claim in the analyst and interpreter "
            "against the evidence. Identify unsupported claims and set blocking true if any must "
            "be removed before display. " + COMMON_RULES
        ),
        evidence=CritiqueContext(evidence=evidence, analyst=analyst, interpreter=interpreter),
        response_type=AIStageResult,
        critic=True,
    )
    critic = critic.model_copy(update={"stage": "Critic"})
    return analyst, interpreter, critic


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
