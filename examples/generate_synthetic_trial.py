import json
import random
from metrics.diversity import normalized_diversity
from metrics.info_density import info_density_score

def generate_synthetic_trial(n_pairs: int = 100, seed: int = 42) -> list:
    random.seed(seed)
    domains = ["physics", "biology", "engineering", "philosophy", "policy"]
    regions = ["NA", "EU", "APAC", "LATAM"]
    experience = ["0-2", "3-5", "6-10", "10+"]
    
    pairs = []
    for i in range(n_pairs):
        n_h = random.randint(4, 20)
        tags = [random.choice(domains), random.choice(regions), random.choice(experience)] * (n_h // 3 + 1)
        tags = tags[:n_h]
        d = normalized_diversity(tags)
        
        resp_a = " ".join(["quantum error correction in biological systems"] * random.randint(5, 15))
        resp_b = " ".join(["classical control theory applied to feedback loops"] * random.randint(5, 15))
        i_d = info_density_score([resp_a, resp_b])
        
        pairs.append({
            "pair_id": i,
            "n_h": n_h,
            "diversity": round(d, 4),
            "info_density": round(i_d, 4),
            "response_a": resp_a,
            "response_b": resp_b,
            "synthetic": True
        })
    return pairs

if __name__ == "__main__":
    data = generate_synthetic_trial()
    with open("examples/synthetic_trial_100.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} synthetic pairs")
