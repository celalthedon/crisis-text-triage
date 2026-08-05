"""Validate release-critical CrisisText project invariants."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

IN_PROGRESS_REQUIRED_FILES = [
    ".dockerignore",
    ".gitattributes",
    ".gitignore",
    ".streamlit/config.toml",
    "README.md",
    "app.py",
    "assets/final_test_confusion_matrix_normalized.png",
    "checkpoints/final_model_selection.json",
    "data/README.md",
    "docs/ETHICS_AND_LIMITATIONS.md",
    "docs/EXPERIMENTS.md",
    "docs/MODEL_CARD.md",
    "models/README.md",
    "models/final_e11_train_plus_validation.joblib",
    "notebooks/01_data_setup.ipynb",
    "notebooks/02_model_training.ipynb",
    "notebooks/03_evaluation_explainability.ipynb",
    "notebooks/archive/01_data_setup_original.ipynb",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "scripts/smoke_test_inference.py",
    "scripts/validate_project.py",
    "src/__init__.py",
    "src/evaluation.py",
    "src/inference.py",
    "src/paths.py",
    "src/preprocessing.py",
    "tests/test_inference.py",
    "tests/test_project_structure.py",
]

RELEASE_REQUIRED_FILES = [
    *IN_PROGRESS_REQUIRED_FILES,
    ".github/workflows/ci.yml",
    "CHANGELOG.md",
    "CITATION.cff",
    "LICENSE",
    "deploy/huggingface/Dockerfile",
    "deploy/huggingface/README.md",
    "deploy/huggingface/deploy_space.py",
]

SAFE_LARGE_FILES = {
    "models/final_e11_train_plus_validation.joblib",
    "assets/final_test_confusion_matrix_normalized.png",
    "reports/final_test_confusion_matrix_normalized.png",
}

SENSITIVE_TRACKED_PATTERNS = [
    "data/raw/",
    "data/processed/",
    "reports/final_test_predictions.csv",
    "reports/validation_prediction_analysis.csv",
    "reports/validation_wrong_predictions.csv",
    "reports/manual_error_audit.csv",
    "models/best_tfidf_lr_balanced_c2.joblib",
    "models/dummy_model.joblib",
    "models/e10_tfidf_bigram_lr_balanced_c2.joblib",
    "models/nb_bigram_pipeline.joblib",
    "models/nb_pipeline.joblib",
    "models/selected_validation_model_e11.joblib",
    "models/tfidf_bigram_lr_balanced_pipeline.joblib",
    "models/tfidf_lr_balanced_c1.joblib",
    "models/tfidf_lr_balanced_pipeline.joblib",
    "models/tfidf_lr_pipeline.joblib",
    "models/tfidf_nb_pipeline.joblib",
]

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]"),
]


def fail(message: str) -> None:
    raise AssertionError(message)


def git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def required_files() -> list[str]:
    if (PROJECT_ROOT / "TASK_STATE.md").exists():
        return IN_PROGRESS_REQUIRED_FILES
    return RELEASE_REQUIRED_FILES


def check_expected_files() -> None:
    missing = [path for path in required_files() if not (PROJECT_ROOT / path).exists()]
    if missing:
        fail(f"Missing expected files: {missing}")


def check_model_loadability() -> None:
    model_path = PROJECT_ROOT / "models/final_e11_train_plus_validation.joblib"
    model = joblib.load(model_path)
    if "vectorizer" not in model.named_steps or "classifier" not in model.named_steps:
        fail("Final model does not have vectorizer/classifier steps")


def check_json_validity() -> None:
    for path in [
        PROJECT_ROOT / "reports/final_test_metrics.json",
        PROJECT_ROOT / "checkpoints/final_model_selection.json",
    ]:
        json.loads(path.read_text(encoding="utf-8"))


def check_csv_readability() -> None:
    csv_paths = [
        "reports/final_test_classification_report.csv",
        "reports/final_test_confusion_matrix.csv",
        "reports/final_test_confusion_matrix_normalized.csv",
        "reports/final_test_confusion_pairs.csv",
        "reports/validation_results.csv",
        "reports/c_tuning_results.csv",
        "reports/top_features_all_classes.csv",
        "reports/manual_error_audit_summary.csv",
    ]
    for relative_path in csv_paths:
        frame = pd.read_csv(PROJECT_ROOT / relative_path)
        if frame.empty:
            fail(f"CSV is empty: {relative_path}")


def check_app_syntax() -> None:
    ast.parse((PROJECT_ROOT / "app.py").read_text(encoding="utf-8"))


def check_no_colab_paths(tracked_files: list[str]) -> None:
    forbidden = ["/content/drive", "/content/", "google.colab", "drive.mount"]
    text_suffixes = {".py", ".md", ".toml", ".yml", ".yaml", ".txt", ".cff", ".json", ".csv", ".ipynb"}

    for relative_path in tracked_files:
        if relative_path in {"TASK_STATE.md", "scripts/validate_project.py"}:
            continue
        if relative_path.startswith("notebooks/archive/"):
            continue
        path = PROJECT_ROOT / relative_path
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = [pattern for pattern in forbidden if pattern in text]
        if matches:
            fail(f"Forbidden Colab/Drive pattern in {relative_path}: {matches}")


def check_no_token_patterns(tracked_files: list[str]) -> None:
    text_suffixes = {".py", ".md", ".toml", ".yml", ".yaml", ".txt", ".cff", ".json", ".csv", ".ipynb"}

    for relative_path in tracked_files:
        path = PROJECT_ROOT / relative_path
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"Possible secret pattern found in {relative_path}")


def check_sensitive_files_not_tracked(tracked_files: list[str]) -> None:
    for tracked_file in tracked_files:
        for sensitive_pattern in SENSITIVE_TRACKED_PATTERNS:
            if tracked_file.startswith(sensitive_pattern):
                fail(f"Sensitive or redundant file is tracked: {tracked_file}")


def check_no_oversized_unexpected_files(tracked_files: list[str]) -> None:
    for relative_path in tracked_files:
        path = PROJECT_ROOT / relative_path
        if not path.exists() or relative_path in SAFE_LARGE_FILES:
            continue
        if path.stat().st_size > 5_000_000:
            fail(f"Unexpected tracked file over 5 MB: {relative_path}")


def check_no_oversized_unexpected_staged_files() -> None:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for relative_path in result.stdout.splitlines():
        normalized = relative_path.strip().replace("\\", "/")
        path = PROJECT_ROOT / normalized
        if not path.exists() or normalized in SAFE_LARGE_FILES:
            continue
        if path.stat().st_size > 5_000_000:
            fail(f"Unexpected staged file over 5 MB: {normalized}")


def main() -> int:
    tracked_files = git_ls_files()
    checks = [
        check_expected_files,
        check_model_loadability,
        check_json_validity,
        check_csv_readability,
        check_app_syntax,
        lambda: check_no_colab_paths(tracked_files),
        lambda: check_no_token_patterns(tracked_files),
        lambda: check_sensitive_files_not_tracked(tracked_files),
        lambda: check_no_oversized_unexpected_files(tracked_files),
        check_no_oversized_unexpected_staged_files,
    ]

    for check in checks:
        check()

    print("Project validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Project validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
