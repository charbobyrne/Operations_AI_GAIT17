from pydantic import BaseModel, Field


class ExclusionSummary(BaseModel):
    blank: int = 0
    non_numeric: int = 0
    non_positive: int = 0

    @property
    def total(self) -> int:
        return self.blank + self.non_numeric + self.non_positive


class DescriptiveStatistics(BaseModel):
    count: int
    mean: float
    median: float
    standard_deviation: float
    minimum: float
    maximum: float


class EvidencePackage(BaseModel):
    column: str
    unit: str
    row_count_original: int
    row_count_valid: int
    exclusions: ExclusionSummary
    statistics: DescriptiveStatistics
    known_facts: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=lambda: ["arrival rate", "number of resources"])


class AIStageResult(BaseModel):
    stage: str
    summary: str
    warnings: list[str] = Field(default_factory=list)
    blocking: bool = False


class AIUsageRecord(BaseModel):
    task: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class PipelineResult(BaseModel):
    evidence: EvidencePackage
    analyst: AIStageResult
    interpreter: AIStageResult
    critic: AIStageResult
    ai_enabled: bool = False
    usage: list[AIUsageRecord] = Field(default_factory=list)
