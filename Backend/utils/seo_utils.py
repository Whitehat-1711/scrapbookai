"""
Pure-function SEO helpers — no LLM calls here, all deterministic.
"""

import re
import math
from collections import Counter
import textstat
import nltk

# Download required NLTK data (run once)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

STOP_WORDS = set(stopwords.words("english"))


# ── Text Cleaning ─────────────────────────────────────────────────────────────

def strip_markdown(text: str) -> str:
    """Remove markdown syntax, return plain text."""
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def count_words(text: str) -> int:
    return len(text.split())


def count_sentences(text: str) -> int:
    return len(sent_tokenize(text))


# ── Keyword Density ───────────────────────────────────────────────────────────

def compute_keyword_density(text: str, keyword: str) -> float:
    """Return keyword density as a percentage."""
    plain = strip_markdown(text).lower()
    words = plain.split()
    kw_lower = keyword.lower()
    kw_words = kw_lower.split()
    kw_len = len(kw_words)

    if kw_len == 1:
        count = words.count(kw_lower)
    else:
        # Multi-word phrase matching
        phrase = " ".join(kw_words)
        count = plain.count(phrase)

    total_words = len(words)
    if total_words == 0:
        return 0.0
    return round((count / total_words) * 100, 2)


def keyword_in_first_n_words(text: str, keyword: str, n: int = 100) -> bool:
    plain = strip_markdown(text).lower()
    first_n = " ".join(plain.split()[:n])
    return keyword.lower() in first_n


def keyword_in_title(title: str, keyword: str) -> bool:
    return keyword.lower() in title.lower()


# ── Readability ───────────────────────────────────────────────────────────────

def get_readability_score(text: str) -> tuple[float, str]:
    """
    Returns (flesch_score 0-100, grade_level_label).
    Higher Flesch = easier to read.
    """
    plain = strip_markdown(text)
    score = textstat.flesch_reading_ease(plain)
    score = max(0.0, min(100.0, score))

    if score >= 80:
        grade = "Very Easy (Grade 5)"
    elif score >= 70:
        grade = "Easy (Grade 6)"
    elif score >= 60:
        grade = "Standard (Grade 7-8)"
    elif score >= 50:
        grade = "Fairly Difficult (Grade 10-12)"
    elif score >= 30:
        grade = "Difficult (College)"
    else:
        grade = "Very Difficult (Professional)"

    return round(score, 1), grade


# ── Heading Analysis ──────────────────────────────────────────────────────────

def count_headings(text: str) -> int:
    return len(re.findall(r"^#{1,6}\s+.+", text, re.MULTILINE))


def extract_headings(text: str) -> list[str]:
    return re.findall(r"^#{1,6}\s+(.+)", text, re.MULTILINE)


# ── LSI / Semantic Keywords ───────────────────────────────────────────────────

def extract_lsi_keywords(text: str, primary_keyword: str, top_n: int = 10) -> list[str]:
    """
    Extract top co-occurring non-stopword terms (LSI proxy).
    """
    plain = strip_markdown(text).lower()
    tokens = word_tokenize(plain)
    tokens = [t for t in tokens if t.isalpha() and t not in STOP_WORDS and len(t) > 3]

    # Remove primary keyword words from pool
    kw_words = set(primary_keyword.lower().split())
    tokens = [t for t in tokens if t not in kw_words]

    freq = Counter(tokens)
    return [word for word, _ in freq.most_common(top_n)]


# ── Internal Link Count ───────────────────────────────────────────────────────

def count_internal_links(text: str) -> int:
    """Count markdown links in the blog content."""
    return len(re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", text))


# ── SEO Score Calculator ──────────────────────────────────────────────────────

def compute_seo_score(
    word_count: int,
    keyword_density: float,
    readability_score: float,
    heading_count: int,
    has_keyword_in_title: bool,
    has_keyword_in_first_100: bool,
    internal_link_count: int,
    lsi_count: int,
) -> float:
    """
    Weighted SEO score out of 100.
    """
    score = 0.0

    # Word count (20 pts)
    if word_count >= 2500:
        score += 20
    elif word_count >= 1500:
        score += 14
    elif word_count >= 800:
        score += 8

    # Keyword density (20 pts)
    if 0.5 <= keyword_density <= 2.5:
        score += 20
    elif 0.3 <= keyword_density < 0.5 or 2.5 < keyword_density <= 3.5:
        score += 10

    # Readability (15 pts)
    if readability_score >= 60:
        score += 15
    elif readability_score >= 50:
        score += 10
    elif readability_score >= 40:
        score += 5

    # Headings (10 pts)
    if heading_count >= 5:
        score += 10
    elif heading_count >= 3:
        score += 6
    elif heading_count >= 1:
        score += 3

    # Keyword in title (15 pts)
    score += 15 if has_keyword_in_title else 0

    # Keyword in first 100 words (10 pts)
    score += 10 if has_keyword_in_first_100 else 0

    # Internal links (5 pts)
    if internal_link_count >= 3:
        score += 5
    elif internal_link_count >= 1:
        score += 2

    # LSI keywords (5 pts)
    if lsi_count >= 8:
        score += 5
    elif lsi_count >= 4:
        score += 3

    return round(min(score, 100.0), 1)


# ── Traffic Potential Estimator ───────────────────────────────────────────────

def estimate_traffic_potential(seo_score: float, keyword_difficulty: str = "medium") -> str:
    """
    Rough monthly traffic estimate based on SEO score and keyword difficulty.
    Returns a descriptive range string.
    """
    difficulty_multiplier = {"low": 1.5, "medium": 1.0, "high": 0.5}.get(keyword_difficulty, 1.0)
    base = seo_score * difficulty_multiplier

    if base >= 90:
        return "5,000 – 20,000 visits/month"
    elif base >= 75:
        return "1,500 – 5,000 visits/month"
    elif base >= 60:
        return "500 – 1,500 visits/month"
    elif base >= 45:
        return "100 – 500 visits/month"
    else:
        return "< 100 visits/month"
