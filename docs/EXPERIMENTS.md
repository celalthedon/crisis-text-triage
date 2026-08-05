# Experiments

Validation Macro-F1 was the primary model-selection metric because the dataset is imbalanced and minority operational classes are important.

| Experiment | Accuracy | Macro-F1 | Weighted-F1 |
| --- | ---: | ---: | ---: |
| E16 raw max_df=0.95 TF-IDF LR balanced C2 | 0.7467 | 0.7252 | 0.7460 |
| E11 raw text TF-IDF LR balanced C2 | 0.7467 | 0.7252 | 0.7460 |
| E10 TF-IDF unigram/bigram LR balanced C2 | 0.7463 | 0.7247 | 0.7456 |
| E15 raw no sublinear TF-IDF LR balanced C2 | 0.7458 | 0.7245 | 0.7450 |
| E13 raw min_df=5 TF-IDF LR balanced C2 | 0.7458 | 0.7234 | 0.7457 |
| E12 raw stopwords TF-IDF LR balanced C2 | 0.7425 | 0.7207 | 0.7414 |
| E6 TF-IDF unigram/bigram LR balanced | 0.7396 | 0.7195 | 0.7386 |
| E14 raw min_df=1 TF-IDF LR balanced C2 | 0.7426 | 0.7192 | 0.7392 |
| E5 TF-IDF unigram LR balanced | 0.7395 | 0.7163 | 0.7393 |
| E7 TF-IDF unigram/bigram LinearSVC balanced | 0.7368 | 0.7111 | 0.7337 |
| E8 char 3-5gram LinearSVC balanced | 0.7364 | 0.7093 | 0.7349 |
| E9 word+char TF-IDF LinearSVC balanced | 0.7364 | 0.7093 | 0.7349 |
| E4 TF-IDF unigram LR | 0.7436 | 0.7034 | 0.7388 |
| E1 count unigram NB | 0.6811 | 0.6148 | 0.6692 |
| E2 count unigram/bigram NB | 0.6895 | 0.5983 | 0.6764 |
| E3 TF-IDF unigram NB | 0.6139 | 0.4614 | 0.5831 |
| E0 dummy most frequent | 0.2782 | 0.0435 | 0.1211 |

## Selection Notes

E11 was selected because raw text with vectorizer-level lowercasing slightly improved validation Macro-F1 over the tuned minimal-preprocessing model while preserving critical recalls. E16 matched E11 because `max_df=0.95` removed no features and changed no validation predictions, so E11 remains the simpler configuration.

## Ablation Conclusions

- Raw text marginally outperformed minimal preprocessing.
- Stopword removal reduced Macro-F1 and urgent-needs recall.
- `min_df=1` slightly improved urgent recall but reduced Macro-F1.
- `min_df=5` reduced Macro-F1 without improving critical recalls.
- `sublinear_tf=True` provided a small improvement.
- `max_df=0.95` had no practical effect on this vocabulary.

## Test Policy

The held-out test set is evaluated only in `notebooks/03_evaluation_explainability.ipynb`, after validation selection and final train+validation retraining are complete.
