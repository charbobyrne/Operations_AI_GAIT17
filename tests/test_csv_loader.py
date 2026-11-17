from app.data.csv_loader import candidate_numeric_columns, load_csv


def test_load_csv_and_find_candidate_columns() -> None:
    frame = load_csv(b"name,duration\na,2\nb,3\n")
    assert list(frame.columns) == ["name", "duration"]
    assert candidate_numeric_columns(frame) == ["duration"]
