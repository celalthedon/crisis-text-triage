# Ethics and Limitations

## Human Review

CrisisText is a decision-support prototype. It should help reviewers scan and prioritize information, not replace human judgment, emergency dispatch, or local operational procedures.

## Dataset Bias

The dataset consists of English Twitter messages from historical disaster events. Performance can shift on new platforms, new events, non-English messages, local dialects, or messages with context that is not visible in the text.

## Label Ambiguity

Some categories overlap in real crisis communication. Donation offers can look like urgent needs, casualty reports can overlap with missing-person messages, and `other_relevant_information` is intentionally broad. These boundaries are not purely technical.

## Label Noise

Manual audit found ambiguous and likely mislabeled examples. A high-confidence model error may indicate model weakness, but it may also indicate an ambiguous or noisy source label.

## Explanation Limits

TF-IDF coefficient contributions are transparent but limited. They explain a linear score for one class, not causality, truth, urgency, or operational value. A feature can also be event-specific rather than generally meaningful.

## Deployment Limits

The Streamlit app is a public demo surface. It should not collect sensitive personal data, protected health information, exact rescue coordinates, or emergency reports that require immediate official response.

## Recommended Use

- Keep humans in the loop.
- Monitor predictions on new events.
- Review low-confidence and high-impact messages manually.
- Treat confidence as model uncertainty, not certainty.
- Revalidate before operational or policy use.
