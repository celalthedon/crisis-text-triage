# Data

This project uses the Hugging Face dataset `QCRI/HumAID-all`, a Twitter crisis-informatics dataset curated by Qatar Computing Research Institute / HumAID researchers.

Expected split sizes used by this repository:

| Split | Rows |
| --- | ---: |
| Train | 53,531 |
| Validation | 7,793 |
| Test | 15,160 |

## Regenerating Local Data

Run `notebooks/01_data_setup.ipynb` from a local Python environment with the project dependencies installed. The notebook downloads `QCRI/HumAID-all`, audits the splits, applies the minimal preprocessing function used in ablation experiments, and can optionally write local parquet files under:

- `data/raw/`
- `data/processed/`

Those parquet files are intentionally ignored by Git.

## Why Data Is Not Committed

The repository does not publish raw tweet text or processed per-message copies. This keeps the public project lightweight and avoids redistributing dataset text outside the upstream dataset terms. Aggregate reports, metrics, confusion matrices, and feature tables are committed separately when they do not expose unnecessary full message text.

## Upstream License and Attribution

The Hugging Face dataset page for `QCRI/HumAID-all` lists the dataset license metadata as `cc-by-nc-sa-4.0`. The dataset card also includes upstream licensing and citation information. Always consult the official dataset card before redistributing or using the data beyond local reproduction.

Citation from the official dataset card:

```bibtex
@inproceedings{humaid2020,
  Author = {Firoj Alam, Umair Qazi, Muhammad Imran, Ferda Ofli},
  booktitle = {Proceedings of the Fifteenth International AAAI Conference on Web and Social Media},
  series = {ICWSM~'21},
  Keywords = {Social Media, Crisis Computing, Tweet Text Classification, Disaster Response},
  Title = {HumAID: Human-Annotated Disaster Incidents Data from Twitter},
  Year = {2021},
  publisher = {AAAI},
  address = {Online}
}
```
