# Model Artifact

The repository commits only the deployable final model:

- `models/final_e11_train_plus_validation.joblib`

Historical experiment binaries are preserved locally but ignored by Git.

## Configuration

- Vectorizer: `TfidfVectorizer`
- Features: word unigrams and bigrams
- `min_df`: 2
- `sublinear_tf`: true
- `lowercase`: true
- Classifier: `LogisticRegression`
- `C`: 2.0
- `class_weight`: `balanced`
- `solver`: `liblinear`
- `max_iter`: 1000
- `random_state`: 42

## Training Scope

The final model is retrained on the combined train and validation splits after validation-driven selection:

- Train samples: 53,531
- Validation samples: 7,793
- Combined samples: 61,324

The held-out test set is evaluated once after final selection.

## Verified Test Metrics

- Accuracy: 0.7515
- Macro-F1: 0.7282
- Weighted-F1: 0.7501
- Missing/found people recall: 0.7361
- Requests/urgent needs recall: 0.6257

## Loading Example

```python
from src.inference import load_model, predict_message

model = load_model()
result = predict_message(
    "Families urgently need clean water, food and medical supplies.",
    model=model,
)
print(result["display_name"], result["confidence"])
```

## Compatibility Warning

The model is a scikit-learn/joblib serialized Python object. Load it only in trusted environments and prefer the dependency versions in `requirements.txt`, especially scikit-learn, to avoid serialization compatibility issues.

## Limitations

The model is trained on English crisis-related social-media text from historical disaster events. It may underperform on new events, non-English messages, sarcasm, duplicate reports, ambiguous labels, or messages requiring real-world context. It is decision support, not emergency dispatch.
