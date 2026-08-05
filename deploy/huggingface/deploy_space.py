"""Deploy CrisisText to a Docker-based Hugging Face Space."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPLOY_DIR = PROJECT_ROOT / "deploy" / "huggingface"
TARGET_SPACE = "celalibr/crisis-text-triage"
FALLBACK_SPACE = "celalibr/crisis-text-triage-demo"


def copy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing deployment file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing deployment directory: {source}")
    shutil.copytree(source, destination)


def create_or_reuse_space(api: HfApi, repo_id: str) -> str:
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True,
        )
        return repo_id
    except HfHubHTTPError as exc:
        if repo_id == TARGET_SPACE and exc.response is not None and exc.response.status_code in {403, 409}:
            print(f"Could not create or reuse {TARGET_SPACE}; trying {FALLBACK_SPACE}.")
            return create_or_reuse_space(api, FALLBACK_SPACE)
        raise


def stage_space_files(staging_dir: Path) -> None:
    copy_file(PROJECT_ROOT / "app.py", staging_dir / "app.py")
    copy_file(PROJECT_ROOT / "requirements.txt", staging_dir / "requirements.txt")
    copy_file(DEPLOY_DIR / "Dockerfile", staging_dir / "Dockerfile")
    copy_file(DEPLOY_DIR / "README.md", staging_dir / "README.md")
    copy_file(PROJECT_ROOT / ".streamlit" / "config.toml", staging_dir / ".streamlit" / "config.toml")

    copy_tree(PROJECT_ROOT / "src", staging_dir / "src")
    copy_tree(PROJECT_ROOT / "assets", staging_dir / "assets")

    copy_file(
        PROJECT_ROOT / "models" / "final_e11_train_plus_validation.joblib",
        staging_dir / "models" / "final_e11_train_plus_validation.joblib",
    )
    copy_file(
        PROJECT_ROOT / "reports" / "final_test_metrics.json",
        staging_dir / "reports" / "final_test_metrics.json",
    )


def deploy() -> str:
    api = HfApi()
    whoami = api.whoami()
    username = whoami.get("name") or whoami.get("fullname") or "authenticated user"
    print(f"Authenticated to Hugging Face as {username}.")

    repo_id = create_or_reuse_space(api, TARGET_SPACE)
    print(f"Deploying to {repo_id}.")

    with tempfile.TemporaryDirectory(prefix="crisistext-space-") as temporary_dir:
        staging_dir = Path(temporary_dir)
        stage_space_files(staging_dir)
        api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=str(staging_dir),
            commit_message="Deploy CrisisText Docker Space",
        )

    space_url = f"https://huggingface.co/spaces/{repo_id}"
    print(f"Space URL: {space_url}")
    return space_url


def main() -> int:
    try:
        deploy()
    except Exception as exc:
        print(f"Deployment failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
