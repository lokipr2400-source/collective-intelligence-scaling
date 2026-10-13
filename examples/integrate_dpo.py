#!/usr/bin/env python3
"""
Integration example: Score preference pairs with the Collective Intelligence MCP tools
and optionally use the scores as sample weights in a TRL DPOTrainer.

Requirements:
  pip install trl datasets transformers torch requests

This script can run in two modes:
  1. Offline (uses local metric functions — no server needed)
  2. Live (calls the running MCP server)

Usage:
  python integrate_dpo.py --mode offline
  python integrate_dpo.py --mode live --api-key YOUR_KEY
"""

import argparse
import json
import os
from typing import List, Dict, Any

import requests
from datasets import Dataset

# Local metric fallbacks (same logic as the MCP server)
from metrics.diversity import normalized_diversity
from metrics.info_density import info_density_score


def score_pair_local(tags: List[str], texts: List[str], n_h: int, current_ci: float = 1.0) -> Dict[str, float]:
    """Compute scores using local functions (no server required)."""
    d = normalized_diversity(tags)
    i_d = info_density_score(texts)
    eta = 0.15
    new_ci = current_ci + eta * (n_h * d * i_d)
    return {
        "diversity": round(d, 4),
        "info_density": round(i_d, 4),
        "ci_delta": round(new_ci - current_ci, 4),
        "new_ci": round(new_ci, 4),
    }


def score_pair_live(tags: List[str], texts: List[str], n_h: int, current_ci: float, api_key: str, base_url: str = "http://localhost:8000") -> Dict[str, float]:
    """Call the running MCP server."""
    headers = {"Content-Type": "application/json", "X-API-Key": api_key}

    # Diversity
    r1 = requests.post(f"{base_url}/mcp/tools/compute_diversity", headers=headers, json={"tags": tags})
    r1.raise_for_status()
    d = r1.json().get("diversity", 0.0)

    # Info density
    r2 = requests.post(f"{base_url}/mcp/tools/compute_info_density", headers=headers, json={"texts": texts})
    r2.raise_for_status()
    i_d = r2.json().get("info_density", 0.0)

    # CI update
    r3 = requests.post(
        f"{base_url}/mcp/tools/calculate_ci",
        headers=headers,
        json={"n_h": n_h, "diversity": d, "info_density": i_d, "current_ci": current_ci},
    )
    r3.raise_for_status()
    ci_result = r3.json()

    return {
        "diversity": d,
        "info_density": i_d,
        "ci_delta": ci_result.get("delta", 0.0),
        "new_ci": ci_result.get("new_ci", current_ci),
    }


def prepare_dpo_dataset(pairs: List[Dict[str, Any]], mode: str, api_key: str = None) -> Dataset:
    """
    Score each preference pair and return a Hugging Face Dataset ready for DPOTrainer.
    Expected pair format:
      {
        "prompt": str,
        "chosen": str,
        "rejected": str,
        "tags": List[str],
        "n_h": int
      }
    """
    scored = []
    for p in pairs:
        tags = p.get("tags", ["general"])
        texts = [p.get("chosen", ""), p.get("rejected", "")]
        n_h = p.get("n_h", 1)

        if mode == "live" and api_key:
            scores = score_pair_live(tags, texts, n_h, 1.0, api_key)
        else:
            scores = score_pair_local(tags, texts, n_h)

        # Simple weight: higher diversity and density → higher weight
        # Clip to a reasonable range so it does not dominate the loss
        weight = max(0.2, min(2.0, 0.5 + scores["diversity"] + scores["info_density"]))

        scored.append({
            "prompt": p["prompt"],
            "chosen": p["chosen"],
            "rejected": p["rejected"],
            "diversity": scores["diversity"],
            "info_density": scores["info_density"],
            "ci_delta": scores["ci_delta"],
            "sample_weight": round(weight, 3),
        })

    return Dataset.from_list(scored)


def example_usage():
    """Minimal example that prints scored pairs and shows the DPOTrainer hook."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["offline", "live"], default="offline")
    parser.add_argument("--api-key", default=os.getenv("MCP_API_KEY"))
    args = parser.parse_args()

    # Example synthetic pairs (replace with your real preference data)
    example_pairs = [
        {
            "prompt": "Explain error correction in quantum systems.",
            "chosen": "Quantum error correction uses redundancy and syndrome measurements to detect and correct decoherence without destroying the logical state.",
            "rejected": "Just add more qubits and hope for the best.",
            "tags": ["physics", "quantum", "engineering"],
            "n_h": 5,
        },
        {
            "prompt": "Describe a simple feedback control loop.",
            "chosen": "A feedback loop measures the output, compares it to the setpoint, and adjusts the input to reduce error.",
            "rejected": "Feedback means the system talks to itself.",
            "tags": ["engineering", "control"],
            "n_h": 3,
        },
    ]

    dataset = prepare_dpo_dataset(example_pairs, mode=args.mode, api_key=args.api_key)
    print("Scored dataset:")
    print(dataset.to_pandas()[["prompt", "diversity", "info_density", "sample_weight"]])

    # ------------------------------------------------------------------
    # TRL DPOTrainer integration sketch (uncomment and adapt when ready)
    # ------------------------------------------------------------------
    """
    from trl import DPOTrainer, DPOConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_name = "Qwen/Qwen2.5-0.5B"  # or your base model
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    training_args = DPOConfig(
        output_dir="./dpo_ci_weighted",
        per_device_train_batch_size=2,
        num_train_epochs=1,
        learning_rate=5e-6,
        # If your TRL version supports sample weights, pass them here.
        # Otherwise, filter the dataset or implement a custom collator.
    )

    trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    # Optional: filter low-weight examples before training
    # high_quality = dataset.filter(lambda x: x["sample_weight"] > 0.8)
    # trainer.train_dataset = high_quality

    trainer.train()
    """

    print("\nDPOTrainer sketch is commented out above.")
    print("Uncomment and adapt the model/tokenizer section when you are ready to train.")


if __name__ == "__main__":
    example_usage()
