from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_project_structure_exists():
    expected_paths = [
        "app.py",
        "requirements.txt",
        "src/__init__.py",
        "src/evaluation.py",
        "src/inference.py",
        "src/paths.py",
        "src/preprocessing.py",
        "models/final_e11_train_plus_validation.joblib",
        "checkpoints/final_model_selection.json",
        "reports/final_test_metrics.json",
        "notebooks/archive/01_data_setup_original.ipynb",
        "notebooks/01_data_setup.ipynb",
        "notebooks/02_model_training.ipynb",
        "notebooks/03_evaluation_explainability.ipynb",
    ]

    missing_paths = [
        relative_path
        for relative_path in expected_paths
        if not (PROJECT_ROOT / relative_path).exists()
    ]

    assert missing_paths == []
