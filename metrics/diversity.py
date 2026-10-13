import math
from collections import Counter

def shannon_entropy(tags: list) -> float:
    """Shannon entropy over categorical tags. Returns value in [0, log2(|unique|)]."""
    if not tags:
        return 0.0
    counts = Counter(tags)
    total = len(tags)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return entropy

def normalized_diversity(tags: list) -> float:
    """Normalized diversity in [0, 1]."""
    if len(set(tags)) <= 1:
        return 0.0
    max_ent = math.log2(len(set(tags)))
    return shannon_entropy(tags) / max_ent if max_ent > 0 else 0.0
