# Tech Stack

## Language and runtime

- Python 3.11+

## Core dependencies

Pinned in `pyproject.toml`:

- `numpy==1.26.0`
- `numba==0.59.1`
- `pandas==2.2.2`
- `pyarrow==17.0.0`
- `requests==2.32.4`
- `PyYAML==6.0.1`
- `pandera==0.19.3`
- `scikit-learn==1.5.0`
- `scipy==1.13.1`
- `statsmodels==0.14.2`
- `pydantic==2.8.0`
- `aiohttp==3.9.5`
- `websockets`
- `networkx`

## Optional dependencies

- `nautilus-trader` via `.[nautilus]`
- `pyright==1.1.350` via `.[dev]`

## Tooling

Common developer tooling is driven by `make`, pytest, Ruff, and the repo scripts under `project/scripts/`.

Useful checks:

```bash
make test
make lint
make format-check
python3 -m project.scripts.build_system_map --check
python3 -m project.scripts.ontology_consistency_audit
```

## Architectural decisions this stack supports

- Pandas and PyArrow for artifact handling
- Scikit-learn for MI scan and related statistical workflows
- Statsmodels and SciPy for hypothesis evaluation
- Pydantic and Pandera for schema and validation layers
- Nautilus Trader for live execution integration
