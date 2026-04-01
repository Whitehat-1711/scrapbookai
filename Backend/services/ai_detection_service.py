"""
AI Detection Service
───────────────────
Heuristic-based AI detection that doesn't need a third-party API.
Scores on: burstiness, perplexity proxy, phrase patterns, sentence variance.

Scale: ai_probability (0-100), naturalness_score (0-100, higher = more human).
"""

import re
import math
import statistics

# Handle imports with fallback for different module contexts
try:
    from backend.utils.seo_utils import strip_markdown, count_sentences
except ImportError:
    from ..utils.seo_utils import strip_markdown, count_sentences

from nltk.tokenize import sent_tokenize, word_tokenize

# Patterns commonly found in AI-generated text
AI_PATTERNS = [
    r"\bin conclusion\b",
    r"\bto summarize\b",
    r"\bit is worth noting\b",
    r"\bit is important to note\b",
    r"\bin today's (digital|fast-paced|modern) world\b",
    r"\bwithout further ado\b",
    r"\bembark on (a|this) journey\b",
    r"\bdelve into\b",
    r"\bin the realm of\b",
    r"\btapestry of\b",
    r"\bunleash the power\b",
    r"\bnavigate the (complex|ever-changing)\b",
    r"\bpivotal role\b",
    r"\blandscape of\b",
    r"\bsynergy\b",
    r"\bseamlessly\b",
    r"\brobust\b",
    r"\bunderscores\b",
    r"\bfostering\b",
    r"\bharness\b",
]


def _sentence_lengths(text: str) -> list[int]:
    sentences = sent_tokenize(strip_markdown(text))
    return [len(s.split()) for s in sentences if s.strip()]


def _burstiness_score(sentence_lengths: list[int]) -> float:
    """
    Burstiness: measure of variance in sentence lengths.
    AI text tends to be uniformly medium-length → low burstiness.
    Human text varies wildly → high burstiness.
    Returns 0-100 (higher = more human-like / bursty).
    """
    if len(sentence_lengths) < 3:
        return 50.0
    mean = statistics.mean(sentence_lengths)
    if mean == 0:
        return 50.0
    std = statistics.stdev(sentence_lengths)
    cv = (std / mean) * 100  # coefficient of variation
    # Map CV: 0-15 = robot, 15-35 = borderline, 35+ = human
    return round(min(cv * 2.5, 100.0), 1)


def _perplexity_indicator(text: str) -> str:
    """
    Rough perplexity proxy: very predictable n-gram transitions = AI.
    We measure bigram repetition rate.
    """
    tokens = word_tokenize(strip_markdown(text).lower())
    bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    if not bigrams:
        return "medium"
    unique_ratio = len(set(bigrams)) / len(bigrams)
    if unique_ratio >= 0.85:
        return "high"    # lots of unique bigrams → human
    elif unique_ratio >= 0.70:
        return "medium"
    else:
        return "low"     # repetitive bigrams → AI


def _ai_pattern_flags(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for pattern in AI_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            found.append(f"AI phrase detected: '{match.group()}'")
    return found


def _paragraph_uniformity_penalty(text: str) -> float:
    """
    AI often writes uniform paragraph lengths.
    Returns 0-20 penalty score (higher = more uniform = more AI-like).
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) < 3:
        return 0.0
    lengths = [len(p.split()) for p in paragraphs]
    if statistics.mean(lengths) == 0:
        return 0.0
    cv = statistics.stdev(lengths) / statistics.mean(lengths)
    # Low cv → uniform → AI penalty
    if cv < 0.2:
        return 20.0
    elif cv < 0.4:
        return 10.0
    return 0.0


def analyze_ai_probability(content: str) -> dict:
    """
    Main function. Returns dict matching AIDetectionResponse schema.
    """
    plain = strip_markdown(content)
    sentence_lengths = _sentence_lengths(plain)

    burstiness = _burstiness_score(sentence_lengths)
    perplexity = _perplexity_indicator(plain)
    flags = _ai_pattern_flags(plain)
    uniformity_penalty = _paragraph_uniformity_penalty(content)

    # Build raw score (0-100 AI probability)
    ai_score = 0.0

    # Burstiness contribution (max 35 pts)
    # Low burstiness → high AI probability
    ai_score += max(0, (100 - burstiness) * 0.35)

    # Perplexity contribution (max 25 pts)
    perplexity_penalty = {"low": 25, "medium": 12, "high": 0}[perplexity]
    ai_score += perplexity_penalty

    # AI phrase flags (max 30 pts, 5 per flag)
    ai_score += min(len(flags) * 5, 30)

    # Uniformity penalty (max 20 pts, already 0-20)
    ai_score += uniformity_penalty * 0.5

    ai_score = round(min(ai_score, 100.0), 1)
    naturalness = round(100.0 - ai_score, 1)

    if ai_score >= 70:
        verdict = "likely_ai"
    elif ai_score >= 45:
        verdict = "borderline"
    else:
        verdict = "likely_human"

    return {
        "ai_probability_percent": ai_score,
        "naturalness_score": naturalness,
        "burstiness_score": burstiness,
        "perplexity_indicator": perplexity,
        "flags": flags,
        "verdict": verdict,
    }
