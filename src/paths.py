"""Project-relative paths used by notebooks, scripts, and the app."""

from __future__ import annotations

from pathlib import Path


def discover_project_root(start: str | Path | None = None) -> Path:
    """Return the nearest parent directory that looks like the project root."""

    current = Path(start or __file__).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / "app.py").exists() and (candidate / "src").is_dir():
            return candidate
        if (candidate / ".git").is_dir() and (candidate / "src").is_dir():
            return candidate

    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = discover_project_root()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
ASSETS_DIR = PROJECT_ROOT / "assets"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

FINAL_MODEL_PATH = MODELS_DIR / "final_e11_train_plus_validation.joblib"
FINAL_SELECTION_PATH = CHECKPOINTS_DIR / "final_model_selection.json"
FINAL_TEST_METRICS_PATH = REPORTS_DIR / "final_test_metrics.json"
