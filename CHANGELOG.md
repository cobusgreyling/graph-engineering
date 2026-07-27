# Changelog

## 0.2.0

### Added

- Fluent aliases: `node`, `edge`, `branch`, `entry`
- `Graph.chain(*names)` for linear wiring
- `Graph.validate()` + `run(..., validate=True)` reachability checks
- `Graph.render_ascii()` terminal sketches
- `Graph.edges()` structured edge listing
- `RunResult.trace` / `StepRecord` and `run(..., timed=True)`
- `RunResult.trail()` human-readable history
- Examples: `minimal.py`, `tool_router.py`, `multi_agent_handoff.py`
- `py.typed` marker
- GitHub Pages deploy for the Mermaid demo
- CONTRIBUTING, LAUNCH, CHANGELOG

### Fixed

- `pyproject.toml` URLs now point at `graph-engineering` (not the old name)

## 0.1.0

- Initial installable package
- `Graph`, `END`, `RunResult`, Mermaid + Graphviz export
- Research → write → verify example
- Tests + CI on Python 3.9–3.13
