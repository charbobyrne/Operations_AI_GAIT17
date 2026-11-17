import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from openai import OpenAIError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai.client import OpenAIClient
from app.analysis.statistics import AnalysisError
from app.core.config import get_settings
from app.data.csv_loader import CSVValidationError, candidate_numeric_columns, load_csv
from app.orchestration.pipeline import run_pipeline

SAMPLE_DATA = ROOT / "sample_data" / "call_center_calls.csv"

st.set_page_config(page_title="Operations AI Test Console", page_icon="🧪", layout="wide")
st.markdown(
    """
    <style>
    .block-container {max-width: 1180px; padding-top: 2rem;}
    [data-testid="stMetric"] {background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, .35); padding: 1rem; border-radius: .7rem;}
    .status-card {border: 1px solid rgba(128, 128, 128, .35); border-radius: .8rem; padding: 1rem 1.2rem; background: var(--secondary-background-color);}
    </style>
    """,
    unsafe_allow_html=True,
)

for key, default in {
    "test_open": False,
    "environment_running": False,
    "pipeline_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

settings = get_settings()

with st.sidebar:
    st.title("Operations AI")
    st.caption("Prototype workspace")
    st.button("Dashboard", disabled=True, width="stretch")
    st.button("Simulations", disabled=True, width="stretch")
    st.button("Reports", disabled=True, width="stretch")
    if st.button("Test", type="primary", width="stretch"):
        st.session_state.test_open = True
    st.divider()
    st.caption("Other modules remain locked while the test environment is under development.")

st.title("Test Environment")
st.caption("Run the full data-to-AI pipeline in a controlled workspace.")

if not st.session_state.test_open:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Prototype access")
        st.write(
            "Select **Test** in the sidebar to open the only active module. Dashboard, "
            "Simulations, and Reports are intentionally disabled."
        )
    with right:
        st.markdown(
            '<div class="status-card"><b>Environment</b><br>Not started<br><br>'
            '<b>Available module</b><br>Test only</div>',
            unsafe_allow_html=True,
        )
    st.stop()

st.subheader("1. Start the environment")
ready_items = {
    "Sample data": SAMPLE_DATA.exists(),
    "OpenAI key": bool(settings.openai_api_key),
    "Primary model": bool(settings.openai_model_primary),
}
status_columns = st.columns(len(ready_items))
for status_column, (label, ready) in zip(status_columns, ready_items.items(), strict=True):
    status_column.metric(label, "Ready" if ready else "Missing")

if not st.session_state.environment_running:
    if not all(ready_items.values()):
        st.error("The environment is missing a required item. Check `.env` and the sample data folder.")
        st.button("Start environment", disabled=True, width="stretch")
        st.stop()

    st.info(
        "Starting initializes the same pipeline used by `scripts/run_e2e_demo.py`. "
        "No API credits are used until you run a test."
    )
    if st.button("Start environment", type="primary", width="stretch"):
        OpenAIClient(settings)
        st.session_state.environment_running = True
        st.rerun()
    st.stop()

st.success("Environment running — OpenAI configuration and sample data are ready.")

st.subheader("2. Select test data")
source = st.radio(
    "Data source",
    ["Included call-center sample", "Upload my own CSV"],
    horizontal=True,
)

try:
    if source == "Included call-center sample":
        data = load_csv(SAMPLE_DATA.read_bytes())
        data_label = SAMPLE_DATA.name
    else:
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        if uploaded_file is None:
            st.info("Choose a CSV to continue.")
            st.stop()
        data = load_csv(uploaded_file.getvalue())
        data_label = uploaded_file.name
except CSVValidationError as exc:
    st.error(str(exc))
    st.stop()

candidates = candidate_numeric_columns(data)
if not candidates:
    st.error("No column contains numeric values that can be analyzed.")
    st.stop()

default_column = candidates.index("handle_seconds") if "handle_seconds" in candidates else 0
control_left, control_middle, control_right = st.columns([2, 1, 1])
column = control_left.selectbox("Duration column", candidates, index=default_column)
unit = control_middle.selectbox("Unit", ["seconds", "minutes", "hours"])
mode = control_right.selectbox("Pipeline mode", ["OpenAI", "Offline"])

with st.expander(f"Preview {data_label} — {len(data)} rows", expanded=False):
    st.dataframe(data.head(25), width="stretch")

st.subheader("3. Run and inspect")
st.caption("The OpenAI mode makes three API calls: analyst, interpreter, and critic.")

if st.button("Run test", type="primary", width="stretch"):
    st.session_state.pipeline_result = None
    try:
        with st.spinner("Running validation, statistics, and AI stages..."):
            ai_client = OpenAIClient(settings) if mode == "OpenAI" else None
            st.session_state.pipeline_result = run_pipeline(
                data,
                column,
                unit,
                ai_client=ai_client,
            )
    except (AnalysisError, OpenAIError, RuntimeError, ValueError) as exc:
        st.error(f"Test failed: {exc}")

result = st.session_state.pipeline_result
if result is None:
    st.stop()

evidence = result.evidence
st.success("Test complete. The result below is grounded in the computed evidence package.")
first, second, third, fourth = st.columns(4)
first.metric("Input rows", evidence.row_count_original)
second.metric("Valid rows", evidence.row_count_valid)
third.metric("Excluded", evidence.exclusions.total)
fourth.metric("Mean", f"{evidence.statistics.mean:.2f} {evidence.unit}")

overview_tab, stages_tab, evidence_tab, usage_tab = st.tabs(
    ["Overview", "AI stages", "Evidence", "API usage"]
)
with overview_tab:
    stats = evidence.statistics
    st.dataframe(
        pd.DataFrame(
            {
                "Metric": ["Count", "Mean", "Median", "Std. deviation", "Minimum", "Maximum"],
                "Value": [
                    stats.count,
                    stats.mean,
                    stats.median,
                    stats.standard_deviation,
                    stats.minimum,
                    stats.maximum,
                ],
            }
        ),
        hide_index=True,
        width="stretch",
    )
with stages_tab:
    for stage in (result.analyst, result.interpreter, result.critic):
        with st.container(border=True):
            st.markdown(f"### {stage.stage}")
            st.write(stage.summary)
            if stage.blocking:
                st.error("This stage marked the result as blocking.")
            for warning in stage.warnings:
                st.warning(warning)
with evidence_tab:
    st.json(evidence.model_dump())
with usage_tab:
    if result.usage:
        st.dataframe(
            pd.DataFrame(record.model_dump() for record in result.usage),
            hide_index=True,
            width="stretch",
        )
        st.metric("Total tokens", sum(record.total_tokens for record in result.usage))
    else:
        st.info("Offline mode does not use API tokens.")

report_json = json.dumps(result.model_dump(), indent=2)
st.download_button(
    "Download JSON report",
    data=report_json,
    file_name="operations_ai_test_report.json",
    mime="application/json",
    width="stretch",
)
