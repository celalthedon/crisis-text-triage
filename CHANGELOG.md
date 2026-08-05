# Changelog

All notable changes to CrisisText are documented here.

## [1.0.0] - 2026-08-05

### Added

- Reproducible local project structure for CrisisText.
- Archived original 324-cell research notebook with source cells preserved.
- Clean notebooks for data setup, model training, evaluation, explainability, and one-time test reporting.
- Reusable `src` modules for paths, preprocessing, evaluation helpers, and inference.
- Streamlit app for crisis-message triage with class probabilities and local explanations.
- Final deployable E11 train+validation model artifact.
- Safe aggregate reports, final metrics, confusion matrices, tuning results, and top-feature tables.
- Tests, smoke-test script, validation script, Ruff configuration, and GitHub Actions CI.
- Docker-based Hugging Face Space deployment package.
- Model card, experiment notes, ethics and limitations, citation metadata, and MIT code license.

### Notes

- Raw and processed dataset parquet files are intentionally excluded from Git.
- Per-message prediction exports and detailed manual-audit files are intentionally excluded from Git.
- The MIT license applies to original project code only. The dataset and dependencies remain governed by upstream terms.
