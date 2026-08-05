from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from src.inference import CLASS_DISPLAY_NAMES, load_model, predict_message
from src.paths import FINAL_TEST_METRICS_PATH


EXAMPLE_MESSAGES = {
    "Urgent needs": "Families urgently need clean water, food and medical supplies.",
    "Missing person": (
        "A 14-year-old child is still missing after the floods. "
        "Please contact local authorities with any information."
    ),
    "Infrastructure damage": (
        "The earthquake destroyed several buildings and caused widespread power outages."
    ),
    "Donation effort": (
        "Volunteers are collecting food, clothing and donations for families affected by the hurricane."
    ),
    "Sympathy and support": (
        "Our thoughts and prayers are with everyone affected by this terrible disaster."
    ),
    "Custom message": "",
}


@st.cache_resource(show_spinner=False)
def get_model():
    return load_model()


@st.cache_data(show_spinner=False)
def load_final_metrics() -> dict[str, Any]:
    if not FINAL_TEST_METRICS_PATH.exists():
        return {}
    return json.loads(FINAL_TEST_METRICS_PATH.read_text(encoding="utf-8"))


def percent(value: float | None) -> str:
    if value is None:
        return "Unavailable"
    return f"{value * 100:.2f}%"


def build_probability_dataframe(result: dict[str, Any]) -> pd.DataFrame:
    probability_df = pd.DataFrame(result["class_probabilities"])
    probability_df["probability_percent"] = probability_df["probability"] * 100
    return probability_df[["class_name", "display_name", "probability", "probability_percent"]]


def build_feature_dataframe(features: list[dict[str, Any]]) -> pd.DataFrame:
    columns = ["feature", "tfidf_value", "class_weight", "contribution"]
    if not features:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(features)[columns]


def render_feature_table(title: str, features: list[dict[str, Any]], empty_message: str) -> None:
    st.subheader(title)
    feature_df = build_feature_dataframe(features)

    if feature_df.empty:
        st.info(empty_message)
        return

    st.dataframe(
        feature_df.rename(
            columns={
                "feature": "Feature",
                "tfidf_value": "TF-IDF",
                "class_weight": "Class weight",
                "contribution": "Contribution",
            }
        ).round(4),
        use_container_width=True,
        hide_index=True,
    )


st.set_page_config(
    page_title="CrisisText",
    page_icon="!",
    layout="wide",
    initial_sidebar_state="expanded",
)

metrics = load_final_metrics()

with st.sidebar:
    st.header("CrisisText")
    st.write("Explainable humanitarian crisis message triage across ten operational categories.")

    st.metric("Final Test Accuracy", percent(metrics.get("accuracy")))
    st.metric("Final Test Macro-F1", percent(metrics.get("macro_f1")))
    st.metric("Missing-Person Recall", percent(metrics.get("missing_recall")))
    st.metric("Urgent-Needs Recall", percent(metrics.get("urgent_recall")))

    st.divider()
    st.caption("TF-IDF word unigrams/bigrams with class-balanced Logistic Regression.")
    st.warning(
        "Decision-support prototype only. This is not emergency dispatch and should not replace human review."
    )


st.title("CrisisText")
st.caption("Explainable humanitarian crisis message triage")

input_column, control_column = st.columns([3, 1])

with control_column:
    selected_example = st.selectbox(
        "Example message",
        options=list(EXAMPLE_MESSAGES.keys()),
        index=0,
    )
    top_n = st.slider(
        "Explanation features",
        min_value=3,
        max_value=15,
        value=8,
    )

with input_column:
    message = st.text_area(
        "Crisis message",
        value=EXAMPLE_MESSAGES[selected_example],
        height=170,
        placeholder="Enter a crisis-related message, social-media post or humanitarian update.",
    )

analyze_button = st.button("Analyze Message", type="primary")

if analyze_button:
    if not message.strip():
        st.error("Enter a message before running the analysis.")
        st.stop()

    try:
        with st.spinner("Loading model and analyzing message..."):
            result = predict_message(message, model=get_model(), top_n=top_n)
    except Exception as exc:
        st.error("The model could not complete the analysis.")
        st.exception(exc)
        st.stop()

    probability_df = build_probability_dataframe(result)
    second_best = probability_df.iloc[1]
    margin = probability_df.iloc[0]["probability"] - probability_df.iloc[1]["probability"]

    st.success("Analysis completed.")

    prediction_column, confidence_column, second_column, margin_column = st.columns(4)
    prediction_column.metric("Predicted Category", result["display_name"])
    confidence_column.metric("Confidence", percent(result["confidence"]))
    second_column.metric("Second-Best Category", second_best["display_name"])
    margin_column.metric("Top-Two Margin", percent(float(margin)))

    st.subheader("Class Probabilities")
    chart_df = probability_df.set_index("display_name")[["probability_percent"]]
    st.bar_chart(chart_df, horizontal=True)
    st.dataframe(
        probability_df[["display_name", "probability_percent"]]
        .rename(columns={"display_name": "Category", "probability_percent": "Probability (%)"})
        .round(2),
        use_container_width=True,
        hide_index=True,
    )

    support_column, oppose_column = st.columns(2)
    with support_column:
        render_feature_table(
            "Supporting Features",
            result["supporting_features"],
            "No positive feature contributions were found for this prediction.",
        )
    with oppose_column:
        render_feature_table(
            "Opposing Features",
            result["opposing_features"],
            "No opposing feature contributions were found for this prediction.",
        )

    st.caption(
        "Feature contribution equals a message TF-IDF value multiplied by the selected class coefficient. "
        "It explains the linear score and is not itself a probability."
    )

    with st.expander("Raw Prediction Output"):
        st.json(
            {
                "predicted_class": result["predicted_class"],
                "display_name": result["display_name"],
                "confidence": result["confidence"],
                "class_probabilities": result["class_probabilities"],
                "class_display_names": CLASS_DISPLAY_NAMES,
            }
        )
