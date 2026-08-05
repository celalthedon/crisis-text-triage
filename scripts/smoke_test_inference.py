"""Smoke-test the deployable CrisisText inference path."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference import load_model, predict_message


SAMPLES = [
    (
        "urgent",
        "Families urgently need clean water, food and medical supplies.",
        "requests_or_urgent_needs",
    ),
    (
        "missing",
        "A 14-year-old child is still missing after the floods.",
        "missing_or_found_people",
    ),
    (
        "donation",
        "Volunteers are collecting food and donations for affected families.",
        "rescue_volunteering_or_donation_effort",
    ),
]


def main() -> int:
    model = load_model()

    for name, message, expected_class in SAMPLES:
        result = predict_message(message, model=model, top_n=5)
        predicted_class = result["predicted_class"]
        confidence = result["confidence"]
        print(f"{name}: {predicted_class} ({confidence:.3f})")

        if predicted_class != expected_class:
            print(
                f"Expected {expected_class} for {name}, got {predicted_class}",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
