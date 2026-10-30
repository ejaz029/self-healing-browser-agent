
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Configuration
# --------------------------------------------------

REPORTS_DIR = Path(__file__).parent / "reports"

STRATEGY_LABELS = {
    "original_selector": "Original Selector",
    "inspect_and_match_button": "Text-Based Recovery",
}

SCENARIO_LABELS = {
    "normal_execution": "Normal Execution",
    "selector_recovery": "Selector Recovery",
    "missing_element": "Missing Element",
    "ambiguous_target": "Ambiguous Target",
    "verification_failure": "Verification Failure",
    "recovery_execution_failure": "Recovery Execution Failure",
}


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Self-Healing Browser Agent",
    page_icon="🔥",
    layout="wide",
)

st.title("Self-Healing Browser Agent")
st.caption("Browser execution reliability and recovery analytics")


# --------------------------------------------------
# Load Execution Reports
# --------------------------------------------------

def load_reports():
    reports = []

    if not REPORTS_DIR.exists():
        return reports

    for file_path in sorted(REPORTS_DIR.glob("execution_*.json")):
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            events = data.get("events", [])

            if not events:
                continue

            last_event = events[-1]

            reports.append({
                "report": file_path.name,
                "timestamp": last_event.get("timestamp"),
                "events": data.get("total_events", len(events)),
                "outcome": data.get(
                    "workflow_outcome", "unknown"
                ).title(),
                "scenario": SCENARIO_LABELS.get(
                    data.get("scenario", "unknown"),
                    data.get("scenario", "unknown"),
                ),
                "strategy": STRATEGY_LABELS.get(
                    last_event.get("strategy"),
                    last_event.get("strategy", "Unknown"),
                ),
                "result": last_event.get("result"),
                "verification": last_event.get("verification"),
            })

        except (OSError, json.JSONDecodeError):
            continue

    return reports


reports = load_reports()

if not reports:
    st.info("No execution reports found. Run the recovery tests first.")
    st.stop()

df = pd.DataFrame(reports)


# --------------------------------------------------
# Summary Metrics
# --------------------------------------------------

total = len(df)
successful = (df["outcome"] == "Success").sum()
failed = (df["outcome"] == "Failed").sum()
unknown = total - successful - failed

classified = successful + failed

success_rate = (
    (successful / classified) * 100
    if classified > 0 else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Executions", total)
col2.metric("Successful", int(successful))
col3.metric("Failed", int(failed))
col4.metric("Success Rate", f"{success_rate:.1f}%")
col5 = st.columns(1)[0]
col5.metric("Classified Executions", classified)

if unknown:
    st.caption(f"{unknown} reports have an unknown outcome.")

st.divider()


# --------------------------------------------------
# Execution Outcomes
# --------------------------------------------------

st.subheader("Execution Outcomes")

outcome_counts = df["outcome"].value_counts()
st.bar_chart(outcome_counts)


# --------------------------------------------------
# Recovery Strategy Usage
# --------------------------------------------------

st.subheader("Recovery Strategy Usage")

strategy_counts = df["strategy"].value_counts()
st.bar_chart(strategy_counts)


# --------------------------------------------------
# Workflow Scenario Breakdown
# --------------------------------------------------

st.subheader("Workflow Scenario Breakdown")

scenario_counts = df["scenario"].value_counts()
st.bar_chart(scenario_counts)


# --------------------------------------------------
# Execution History
# --------------------------------------------------

st.subheader("Execution History")

st.dataframe(
    df.sort_values("timestamp", ascending=False),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Refresh
# --------------------------------------------------

if st.button("Refresh Reports"):
    st.rerun()
