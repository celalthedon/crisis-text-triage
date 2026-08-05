from __future__ import annotations

import math

import pytest

from src.inference import DEFAULT_MODEL_PATH, load_model, predict_message


@pytest.fixture(scope="session")
def model():
    return load_model()


def test_final_model_file_can_be_loaded(model):
    assert DEFAULT_MODEL_PATH.exists()
    assert model.named_steps["vectorizer"]
    assert model.named_steps["classifier"]


def test_empty_input_raises_value_error(model):
    with pytest.raises(ValueError):
        predict_message("   ", model)


def test_non_string_input_raises_type_error(model):
    with pytest.raises(TypeError):
        predict_message(123, model)  # type: ignore[arg-type]


def test_normal_message_returns_required_keys(model):
    result = predict_message(
        "Families urgently need clean water, food and medical supplies.",
        model,
        top_n=5,
    )

    assert {
        "text",
        "predicted_class",
        "display_name",
        "confidence",
        "class_probabilities",
        "supporting_features",
        "opposing_features",
    }.issubset(result)


def test_class_probabilities_are_sorted_and_sum_to_one(model):
    result = predict_message(
        "Families urgently need clean water, food and medical supplies.",
        model,
        top_n=5,
    )
    probabilities = [item["probability"] for item in result["class_probabilities"]]

    assert probabilities == sorted(probabilities, reverse=True)
    assert math.isclose(sum(probabilities), 1.0, rel_tol=1e-6, abs_tol=1e-6)


def test_confidence_lies_between_zero_and_one(model):
    result = predict_message(
        "Families urgently need clean water, food and medical supplies.",
        model,
        top_n=5,
    )

    assert 0.0 <= result["confidence"] <= 1.0


def test_supporting_feature_records_have_expected_fields(model):
    result = predict_message(
        "Families urgently need clean water, food and medical supplies.",
        model,
        top_n=5,
    )

    assert result["supporting_features"]
    for record in result["supporting_features"]:
        assert {"feature", "tfidf_value", "class_weight", "contribution"}.issubset(record)


@pytest.mark.parametrize(
    ("message", "expected_class"),
    [
        (
            "Families urgently need clean water, food and medical supplies.",
            "requests_or_urgent_needs",
        ),
        (
            "A 14-year-old child is still missing after the floods.",
            "missing_or_found_people",
        ),
        (
            "Volunteers are collecting food and donations for affected families.",
            "rescue_volunteering_or_donation_effort",
        ),
    ],
)
def test_prediction_works_for_representative_examples(model, message, expected_class):
    result = predict_message(message, model, top_n=5)
    assert result["predicted_class"] == expected_class
