"""Text normalization utilities used by the CrisisText notebooks."""

from __future__ import annotations

import re
import unicodedata


MENTION_PATTERN = re.compile(r"@\w+")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HASHTAG_PATTERN = re.compile(r"#(\w+)")
WHITESPACE_PATTERN = re.compile(r"\s+")


def _ensure_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return text


def normalize_basic_text(text: str, lowercase: bool = True) -> str:
    """Normalize Unicode, optionally lowercase, and collapse whitespace."""

    normalized_text = unicodedata.normalize("NFKC", _ensure_text(text))

    if lowercase:
        normalized_text = normalized_text.lower()

    normalized_text = WHITESPACE_PATTERN.sub(" ", normalized_text)
    return normalized_text.strip()


def replace_mentions(text: str, replacement: str = "<user>") -> str:
    """Replace Twitter-style @mentions with a stable placeholder."""

    return MENTION_PATTERN.sub(replacement, _ensure_text(text))


def replace_urls(text: str, replacement: str = "<url>") -> str:
    """Replace URL tokens with a stable placeholder."""

    return URL_PATTERN.sub(replacement, _ensure_text(text))


def normalize_hashtags(text: str) -> str:
    """Remove the leading hash from hashtag tokens while preserving words."""

    return HASHTAG_PATTERN.sub(r"\1", _ensure_text(text))


def preprocess_text(text: str) -> str:
    """Apply the minimal preprocessing workflow used in the experiments."""

    text = normalize_basic_text(text)
    text = replace_urls(text)
    text = replace_mentions(text)
    return normalize_hashtags(text)
