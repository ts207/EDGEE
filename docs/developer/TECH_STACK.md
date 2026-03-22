# Tech Stack

## Language and Runtime

- **Python 3.11+** — Required. The codebase uses Python 3.11 features. `pyproject.toml` sets `requires-python = ">=3.11"`.

---

## Core Dependencies

Pinned versions are in `pyproject.toml`.

| Package | Version | Purpose |
|---|---|---|
| `numpy` | 1.26.0 | Numerical computation |
| `numba` | 0.59.1 | JIT-compiled hot paths |
| `pandas` | 2.2.2 | DataFrame operations and pipeline data flow |
| `pyarrow` | 17.0.0 | Parquet I/O for lake and artifact layers |
| `PyYAML` | 6.0.1 | Spec and config loading |
| `pandera` | 0.19.3 | DataFrame schema validation |
| `scikit-learn` | 1.5.0 | ML utilities (clustering, preprocessing) |
| `scipy` | 1.13.1 | Statistical functions |
| `statsmodels` | 0.14.2 | Regression and time-series tools |
| `pydantic` | 2.8.0 | Data model validation |
| `networkx` | latest | DAG and stage dependency graph |
| `requests` | 2.32.4 | HTTP (data ingestion) |
| `aiohttp` | 3.9.5 | Async HTTP (live ingest) |
| `websockets` | latest | Live data streams |

---

## Optional Dependencies

### Nautilus Trader Runtime

Required for live execution and the Nautilus backtester:

```bash
pip install -e ".[nautilus]"
```

### Dev Tools

```bash
pip install -e ".[dev]"
```

Includes `pyright==1.1.350` for type checking.

---

## Tooling

| Tool | Version | Use |
|---|---|---|
| `ruff` | via `pyproject.toml` | Linting and formatting |
| `pytest` | latest | Test framework |
| `make` | system | Build commands (`make test`, `make lint`, etc.) |

Ruff configuration:
- Line length: `100`
- Target version: `py311`
- Enabled rules: `E`, `F`, `I`, `W`, `E9`, `F63`, `F7`, `F82`
- Excluded: `data/`, `.venv/`, `MEMORY/`, `.agents/`

---

## Architectural Decisions

**Explicit Mode Boundaries**
Promotion logic distinguishes between `research` and `deploy-ready` modes using explicit helpers instead of inline checks. Strict-mode failures are captured in a separate `deploy_only_reject_reason` field to prevent them from being lost in the general `reject_reason`.

**Auditable Results**
Promotion output explicitly records the normalized run mode and whether deploy-only gates were active.

**Explicit Scoring Composition**
Promotion scores are computed from a named vector of components, making the formula auditable and versioned. Every component is recorded in the output to enable detailed debugging of candidate rankings.

**Parquet-First Storage**
All pipeline outputs (cleaned bars, feature tables, event outputs, research artifacts) use Parquet via PyArrow. Do not introduce new ad-hoc CSV or JSON outputs for large data artifacts.

**YAML Specs as DSL**
The `spec/` tree defines events, features, states, strategies, and search configurations as YAML. Load specs via `project.spec_registry` — never parse them ad-hoc outside the registry surface.
