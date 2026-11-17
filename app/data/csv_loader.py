from io import BytesIO

import pandas as pd


class CSVValidationError(ValueError):
    """Raised when an uploaded file cannot be used by the analysis pipeline."""


def load_csv(contents: bytes) -> pd.DataFrame:
    if not contents:
        raise CSVValidationError("The uploaded CSV is empty.")
    try:
        frame = pd.read_csv(BytesIO(contents))
    except Exception as exc:
        raise CSVValidationError("The file could not be parsed as a CSV.") from exc
    if frame.empty:
        raise CSVValidationError("The CSV has no data rows.")
    if frame.columns.empty:
        raise CSVValidationError("The CSV has no columns.")
    return frame


def candidate_numeric_columns(frame: pd.DataFrame) -> list[str]:
    candidates: list[str] = []
    for column in frame.columns:
        converted = pd.to_numeric(frame[column], errors="coerce")
        if converted.notna().any():
            candidates.append(str(column))
    return candidates
