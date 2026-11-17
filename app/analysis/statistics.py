import math

import pandas as pd

from app.core.models import DescriptiveStatistics, EvidencePackage, ExclusionSummary


class AnalysisError(ValueError):
    """Raised when a selected column cannot produce reliable statistics."""


def analyze_duration_column(frame: pd.DataFrame, column: str, unit: str = "minutes") -> EvidencePackage:
    if column not in frame.columns:
        raise AnalysisError(f"Column '{column}' was not found.")

    source = frame[column]
    numeric = pd.to_numeric(source, errors="coerce")
    blank_mask = source.isna() | source.astype(str).str.strip().eq("")
    non_numeric_mask = numeric.isna() & ~blank_mask
    non_positive_mask = numeric.notna() & numeric.le(0)
    valid = numeric[numeric.gt(0)].astype(float)

    if valid.empty:
        raise AnalysisError("The selected column has no positive numeric values.")

    standard_deviation = float(valid.std(ddof=1)) if len(valid) > 1 else 0.0
    values = {
        "mean": float(valid.mean()),
        "median": float(valid.median()),
        "standard_deviation": standard_deviation,
        "minimum": float(valid.min()),
        "maximum": float(valid.max()),
    }
    if not all(math.isfinite(value) for value in values.values()):
        raise AnalysisError("The selected column produced non-finite statistics.")

    exclusions = ExclusionSummary(
        blank=int(blank_mask.sum()),
        non_numeric=int(non_numeric_mask.sum()),
        non_positive=int(non_positive_mask.sum()),
    )
    return EvidencePackage(
        column=column,
        unit=unit,
        row_count_original=len(frame),
        row_count_valid=len(valid),
        exclusions=exclusions,
        statistics=DescriptiveStatistics(count=len(valid), **values),
        known_facts=[
            f"{len(valid)} positive numeric observations were analyzed.",
            f"{exclusions.total} observations were excluded by validation rules.",
        ],
    )
