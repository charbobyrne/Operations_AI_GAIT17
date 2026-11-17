import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis.statistics import AnalysisError
from app.data.csv_loader import CSVValidationError, candidate_numeric_columns, load_csv
from app.orchestration.pipeline import run_pipeline

st.set_page_config(page_title="Operations AI", page_icon="📊", layout="wide")
st.title("Operations AI")
st.caption("Grounded process-data analysis with human review at every consequential step.")

with st.sidebar:
    st.header("Analysis setup")
    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])
    unit = st.selectbox("Duration unit", ["seconds", "minutes", "hours"], index=1)
    st.info("Your API key stays in your local `.env` file and is never uploaded here.")

if uploaded_file is None:
    st.subheader("Start with one process-time column")
    st.write(
        "Upload a CSV to review its rows, select a duration column, confirm exclusions, "
        "and generate a grounded evidence package."
    )
    st.stop()

try:
    data = load_csv(uploaded_file.getvalue())
except CSVValidationError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("1. Review uploaded data")
st.dataframe(data.head(25), use_container_width=True)
st.caption(f"Showing up to 25 of {len(data)} rows.")

candidates = candidate_numeric_columns(data)
if not candidates:
    st.error("No column contains numeric values that can be analyzed.")
    st.stop()

column = st.selectbox("Select the process-time column", candidates)
st.subheader("2. Validate and analyze")
st.write("Blank, non-numeric, zero, and negative values will be excluded from calculations.")

if st.button("Run analysis", type="primary"):
    try:
        result = run_pipeline(data, column, unit)
    except AnalysisError as exc:
        st.error(str(exc))
        st.stop()

    evidence = result.evidence
    first, second, third = st.columns(3)
    first.metric("Valid rows", evidence.row_count_valid)
    second.metric("Excluded rows", evidence.exclusions.total)
    third.metric("Mean duration", f"{evidence.statistics.mean:.2f} {unit}")

    stats = evidence.statistics
    st.dataframe(
        pd.DataFrame(
            {
                "Metric": ["Count", "Mean", "Median", "Std. deviation", "Minimum", "Maximum"],
                "Value": [stats.count, stats.mean, stats.median, stats.standard_deviation, stats.minimum, stats.maximum],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("3. Evidence-grounded pipeline")
    for stage in (result.analyst, result.interpreter, result.critic):
        with st.container(border=True):
            st.markdown(f"**{stage.stage}**")
            st.write(stage.summary)
            for warning in stage.warnings:
                st.warning(warning)

    with st.expander("View evidence package"):
        st.json(evidence.model_dump())
