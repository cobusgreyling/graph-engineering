# Contributing

Thanks for helping keep Graph Engineering small, sharp, and zero-dependency.

## Principles

1. **Zero required runtime dependencies** — stdlib only in `simple_graph_agents/`.
2. **Readable over clever** — the core file should stay easy to finish in one sitting.
3. **No silent behavior changes** — raise `GraphError` instead of overwriting edges.
4. **Tests first for API changes** — `pytest -q` must stay green on 3.9+.

## Setup

```bash
git clone https://github.com/cobusgreyling/graph-engineering.git
cd graph-engineering
python -m pip install -e ".[dev]"
pytest -q
```

## What makes a great PR

- A new **example** that teaches a real agent pattern
- Clearer docs / README / type hints
- Hardening: better errors, validation, edge cases
- Performance only when measured and still readable

## What we will probably decline

- Pulling in LangChain / HTTP / LLM SDKs as required deps
- Full async runtime rewrites (document patterns in examples instead)
- Framework sprawl (plugins, plugin loaders, config DSLs)

Optional extras (like Graphviz) are fine behind `optional-dependencies`.

## Style

- Match existing naming and docstring tone
- Prefer fluent methods that return `self`
- Keep public surface documented in the README API table

## Release checklist (maintainers)

1. Bump version in `pyproject.toml` and `simple_graph_agents/__init__.py`
2. Update `CHANGELOG.md`
3. `pytest -q` + run all examples
4. Tag `vX.Y.Z` and push
