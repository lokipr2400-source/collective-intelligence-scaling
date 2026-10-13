import re
from collections import Counter

def unique_ngram_ratio(text: str, n: int = 3) -> float:
    """Simple unique n-gram ratio as information density proxy."""
    words = re.findall(r'\w+', text.lower())
    if len(words) < n:
        return 0.0
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
    if not ngrams:
        return 0.0
    return len(set(ngrams)) / len(ngrams)

def info_density_score(texts: list[str]) -> float:
    """Average unique n-gram ratio across a list of texts."""
    if not texts:
        return 0.0
    return sum(unique_ngram_ratio(t) for t in texts) / len(texts)
