# Collective Intelligence Scaling

Experimental toolkit for measuring and amplifying collective intelligence signals that can generate higher-quality preference data for frontier models.

## Scope
This repository implements a measurable collective-intelligence scoring layer and agent tooling. Geometric and narrative framing used during development is documented separately in `docs/lattice-context.md` and is not required to run or evaluate the code.

## How to Verify
```bash
python -c "from metrics.diversity import normalized_diversity; print(normalized_diversity(['physics','biology','physics']))"
# Expected: ~0.918 (normalized Shannon entropy)
```

## Status & Validation
All equations and scaling laws in this repository are **proposed models / engineering heuristics**. They have not been validated by published empirical trials. A model is considered provisionally useful if it shows correlation ≥ 0.7 with human preference agreement across ≥ 50 independent trials under the measurement protocol defined in `docs/measurement-protocol.md`.

## Core Scaling Law
\[ CI_{n+1} = CI_n + 0.15 \times (N_h \times D \times I_d) \]

- \(\eta = 0.15\) (conservative safety factor)
- \(N_h\): active collaborators
- \(D\): diversity (Shannon entropy over categorical tags)
- \(I_d\): information density (unique n-gram ratio)

## MCP Tools
| Tool | Description | Required Fields |
|------|-------------|-----------------|
| `calculate_ci` | Compute next CI score | `n_h`, `diversity`, `info_density`, `current_ci` |
| `compute_diversity` | Normalized Shannon entropy | `tags` (list of strings) |
| `compute_info_density` | Average unique n-gram ratio | `texts` (list of strings) |
| `relay_equation` | Basic relay update | `c_n`, `r_n`, `s_n` |

## Quickstart (Local)
```bash
# Install dependencies
pip install fastapi uvicorn[standard] fastmcp pydantic

# Run unit tests
PYTHONPATH=. python -m unittest tests/test_metrics.py -v

# Start the server
export MCP_API_KEY="test-key"
cd mcp_server
PYTHONPATH=.. python mcp_server.py
```

## Human Data Protocol
All current examples and the synthetic dataset are non-human. See `docs/human-data-protocol.md` for consent requirements before any real participant data is collected.

## Limitations and Open Questions
- Proxies for diversity and density are operational definitions, not unique ground truth.
- No live human trials have been run.
- Security configuration (mTLS, key rotation) is documented but must be operationalized by the deployer.

## Call for Data
We welcome contributions of synthetic or consented preference pairs. Required fields: `n_h`, categorical tags for diversity, response texts, and outcome label. See `docs/measurement-protocol.md` for schema. Submit via issue or pull request.

## Related Work
Grounded in collective intelligence research (MIT CCI, COHUMAIN framework) and standard information-theoretic metrics.
