
from pathlib import Path
from typing import Any

import joblib
import numpy as np

try:
    from .paths import FINAL_MODEL_PATH
except ImportError:  # pragma: no cover - supports `python src/inference.py`
    from paths import FINAL_MODEL_PATH


DEFAULT_MODEL_PATH = FINAL_MODEL_PATH


CLASS_DISPLAY_NAMES = {
    "caution_and_advice": "Caution and Advice",
    "displaced_people_and_evacuations": "Displaced People and Evacuations",
    "infrastructure_and_utility_damage": "Infrastructure and Utility Damage",
    "injured_or_dead_people": "Injured or Dead People",
    "missing_or_found_people": "Missing or Found People",
    "not_humanitarian": "Not Humanitarian",
    "other_relevant_information": "Other Relevant Information",
    "requests_or_urgent_needs": "Requests or Urgent Needs",
    "rescue_volunteering_or_donation_effort": "Rescue, Volunteering or Donation Effort",
    "sympathy_and_support": "Sympathy and Support"
}


def load_model(model_path: str | Path | None = None):
    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    return joblib.load(path)


def predict_message(
    text: str,
    model,
    top_n: int = 8
) -> dict[str, Any]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        raise ValueError("text cannot be empty")

    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    vectorizer = model.named_steps["vectorizer"]
    classifier = model.named_steps["classifier"]

    class_names = classifier.classes_
    feature_names = vectorizer.get_feature_names_out()

    probabilities = model.predict_proba([text])[0]
    predicted_class_index = int(np.argmax(probabilities))
    predicted_class = str(class_names[predicted_class_index])
    confidence = float(probabilities[predicted_class_index])

    sorted_class_indices = np.argsort(probabilities)[::-1]

    class_probabilities = [
        {
            "class_name": str(class_names[index]),
            "display_name": CLASS_DISPLAY_NAMES.get(
                str(class_names[index]),
                str(class_names[index])
            ),
            "probability": float(probabilities[index])
        }
        for index in sorted_class_indices
    ]

    text_vector = vectorizer.transform([text])
    active_indices = text_vector.indices
    active_values = text_vector.data

    class_weights = classifier.coef_[predicted_class_index]

    contributions = (
        active_values
        * class_weights[active_indices]
    )

    contribution_records = [
        {
            "feature": str(feature_names[feature_index]),
            "tfidf_value": float(tfidf_value),
            "class_weight": float(class_weights[feature_index]),
            "contribution": float(contribution)
        }
        for feature_index, tfidf_value, contribution in zip(
            active_indices,
            active_values,
            contributions
        )
    ]

    supporting_features = sorted(
        [
            record
            for record in contribution_records
            if record["contribution"] > 0
        ],
        key=lambda record: record["contribution"],
        reverse=True
    )[:top_n]

    opposing_features = sorted(
        [
            record
            for record in contribution_records
            if record["contribution"] < 0
        ],
        key=lambda record: record["contribution"]
    )[:top_n]

    return {
        "text": text,
        "predicted_class": predicted_class,
        "display_name": CLASS_DISPLAY_NAMES.get(
            predicted_class,
            predicted_class
        ),
        "confidence": confidence,
        "class_probabilities": class_probabilities,
        "supporting_features": supporting_features,
        "opposing_features": opposing_features
    }


if __name__ == "__main__":
    model = load_model()

    sample_text = (
        "Families urgently need clean water, food and medical supplies."
    )

    result = predict_message(
        text=sample_text,
        model=model,
        top_n=5
    )

    print("Prediction:", result["display_name"])
    print("Confidence:", f'{result["confidence"]:.2%}')

    print("\nSupporting features:")
    for feature in result["supporting_features"]:
        print(
            feature["feature"],
            round(feature["contribution"], 4)
        )
