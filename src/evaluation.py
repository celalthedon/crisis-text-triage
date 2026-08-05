"""Reusable evaluation helpers for CrisisText experiments and reports."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score

CRITICAL_CLASSES = (
    "missing_or_found_people",
    "requests_or_urgent_needs",
)


def classification_report_dataframe(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Return sklearn's classification report as a DataFrame."""

    return pd.DataFrame(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            output_dict=True,
            zero_division=0,
        )
    ).transpose()


def extract_critical_class_metrics(
    report_df: pd.DataFrame,
    critical_classes: Iterable[str] = CRITICAL_CLASSES,
) -> dict[str, float]:
    """Extract recall and F1 metrics for operationally important classes."""

    metrics: dict[str, float] = {}

    for class_name in critical_classes:
        if class_name in report_df.index:
            metrics[f"{class_name}_recall"] = float(report_df.loc[class_name, "recall"])
            metrics[f"{class_name}_f1"] = float(report_df.loc[class_name, "f1-score"])

    return metrics


def evaluate_predictions(
    experiment_name: str,
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
    critical_classes: Iterable[str] = CRITICAL_CLASSES,
) -> dict[str, Any]:
    """Calculate the standard experiment-selection metrics."""

    report_df = classification_report_dataframe(y_true, y_pred, labels=labels)

    result: dict[str, Any] = {
        "experiment": experiment_name,
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }
    result.update(extract_critical_class_metrics(report_df, critical_classes))
    return result


def build_prediction_analysis_frame(
    texts: Sequence[str],
    y_true: Sequence[str],
    y_pred: Sequence[str],
    probabilities: np.ndarray,
) -> pd.DataFrame:
    """Build a per-message prediction analysis table with confidence fields."""

    if probabilities.ndim != 2 or probabilities.shape[1] < 2:
        raise ValueError("probabilities must be a 2D array with at least two classes")

    sorted_probabilities = np.sort(probabilities, axis=1)
    confidences = sorted_probabilities[:, -1]
    second_best = sorted_probabilities[:, -2]

    analysis_df = pd.DataFrame(
        {
            "text": list(texts),
            "true_label": list(y_true),
            "predicted_label": list(y_pred),
            "confidence": confidences,
            "second_best_probability": second_best,
            "confidence_margin": confidences - second_best,
        }
    )
    analysis_df["is_correct"] = analysis_df["true_label"] == analysis_df["predicted_label"]
    return analysis_df


def summarize_confusion_pairs(
    analysis_df: pd.DataFrame,
    include_margin: bool = True,
) -> pd.DataFrame:
    """Summarize wrong predictions by true/predicted label pair."""

    required_columns = {"true_label", "predicted_label", "confidence", "is_correct"}
    missing_columns = required_columns.difference(analysis_df.columns)
    if missing_columns:
        raise ValueError(f"analysis_df is missing columns: {sorted(missing_columns)}")

    wrong_predictions_df = analysis_df.loc[~analysis_df["is_correct"]].copy()
    aggregations: dict[str, tuple[str, str]] = {
        "error_count": ("true_label", "size"),
        "average_confidence": ("confidence", "mean"),
    }

    if include_margin and "confidence_margin" in wrong_predictions_df.columns:
        aggregations["average_margin"] = ("confidence_margin", "mean")

    return (
        wrong_predictions_df.groupby(["true_label", "predicted_label"])
        .agg(**aggregations)
        .reset_index()
        .sort_values("error_count", ascending=False)
        .reset_index(drop=True)
    )


def summarize_class_errors(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """Return per-class error counts and error rates."""

    if "is_correct" not in analysis_df.columns or "true_label" not in analysis_df.columns:
        raise ValueError("analysis_df must include true_label and is_correct columns")

    summary_df = (
        analysis_df.groupby("true_label")
        .agg(
            total_samples=("is_correct", "size"),
            wrong_predictions=("is_correct", lambda values: int((~values).sum())),
        )
        .reset_index()
    )
    summary_df["error_rate"] = summary_df["wrong_predictions"] / summary_df["total_samples"]
    return summary_df.sort_values("error_rate", ascending=False).reset_index(drop=True)


def validation_summary(
    analysis_df: pd.DataFrame,
    y_true: Sequence[str],
    y_pred: Sequence[str],
) -> dict[str, Any]:
    """Return concise aggregate metrics and prediction counts."""

    is_correct = analysis_df["is_correct"]
    return {
        "total_samples": int(len(analysis_df)),
        "correct_predictions": int(is_correct.sum()),
        "wrong_predictions": int((~is_correct).sum()),
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }
