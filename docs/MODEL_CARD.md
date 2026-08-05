# CrisisText Model Card

## Model Details

- Model name: CrisisText final E11 train+validation classifier
- File: `models/final_e11_train_plus_validation.joblib`
- Task: multiclass humanitarian crisis-message classification
- Dataset: `QCRI/HumAID-all`
- Input: raw English tweet/message text
- Output: one of ten operational crisis categories plus class probabilities and coefficient-based explanations

## Intended Use

Use this model as decision support for portfolio demonstrations, crisis-informatics experimentation, and human-in-the-loop triage prototypes. It is not emergency dispatch and should not be used as the sole basis for operational decisions.

## Training Data

The final model is trained on the combined train and validation splits:

- Train: 53,531 messages
- Validation: 7,793 messages
- Combined final training set: 61,324 messages

The test split contains 15,160 messages and was evaluated once after final selection.

## Model Configuration

- `TfidfVectorizer`
- Word ngrams: `(1, 2)`
- `min_df=2`
- `sublinear_tf=True`
- `lowercase=True`
- `stop_words=None`
- `LogisticRegression`
- `C=2.0`
- `class_weight="balanced"`
- `solver="liblinear"`
- `max_iter=1000`
- `random_state=42`

## Metrics

| Metric | Test value |
| --- | ---: |
| Accuracy | 0.7515 |
| Macro-F1 | 0.7282 |
| Weighted-F1 | 0.7501 |
| Missing/found people recall | 0.7361 |
| Requests/urgent needs recall | 0.6257 |

## Explainability

For each prediction, the app reports features whose `TF-IDF value x class coefficient` most support or oppose the selected class. These contributions explain the linear model score and are not probabilities.

## Limitations

- English-only social-media style text.
- Historical disaster-event vocabulary can create event-specific shortcuts.
- Broad labels, especially `other_relevant_information`, introduce ambiguity.
- Label noise exists and manual audit found likely mislabeled examples.
- Confidence is not certainty and does not encode downstream operational priority.

## Safety

Keep a human reviewer in the loop. Do not use the model to dispatch emergency services, allocate scarce resources automatically, or suppress messages without review.
