import pandas as pd
import pytest

from app.analysis.statistics import AnalysisError, analyze_duration_column


def test_analysis_excludes_invalid_values() -> None:
    frame = pd.DataFrame({"packing_time": [5, 10, None, -2, "bad", 15]})
    evidence = analyze_duration_column(frame, "packing_time", "minutes")
    assert evidence.row_count_original == 6
    assert evidence.row_count_valid == 3
    assert evidence.exclusions.blank == 1
    assert evidence.exclusions.non_numeric == 1
    assert evidence.exclusions.non_positive == 1
    assert evidence.statistics.mean == pytest.approx(10)


def test_analysis_rejects_column_without_positive_numbers() -> None:
    frame = pd.DataFrame({"packing_time": [None, -1, "bad"]})
    with pytest.raises(AnalysisError, match="no positive numeric values"):
        analyze_duration_column(frame, "packing_time")
