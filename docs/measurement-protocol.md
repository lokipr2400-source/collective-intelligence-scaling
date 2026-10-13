# Measurement Protocol

## Diversity (D)
Shannon entropy over a fixed set of categorical tags:
- expertise domain
- years of experience (binned)
- geographic region

Implementation: `metrics/diversity.py`

## Information Density (I_d)
Two supported definitions (both available as MCP tools):
1. Average pairwise embedding cosine distance from a reference corpus.
2. Unique n-gram ratio (default n=3).

Implementation: `metrics/info_density.py`

## Calibration
See `examples/calibration_table.md` for expected ranges under homogeneous, mixed, and high-novelty conditions.
