# Graph Engineering

<p align="center">
  <img src="ge1.jpg" alt="Graph Engineering" width="100%" />
</p>

[![CI](https://github.com/cobusgreyling/graph-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/cobusgreyling/graph-engineering/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Zero-dependency Python graph runtime for small agent loops.

Nodes are **plain functions** that take and return a shared `dict` state. Wire them with fixed edges or **conditional edges** (a router function returns the next node name). Call `render_mermaid()` for instant control-flow diagrams.

```
research ──► write ──► verify ──► END
                ▲         │
                └─ retry ─┘
```

## Why

Most agent frameworks bury the control plane under adapters, schemas, and vendor SDKs. This repo is intentionally tiny:

- small installable package ([`simple_graph_agents/`](simple_graph_agents/))
- no required third-party packages
- Mermaid out of the box (optional Graphviz if you want images)
- a research → write → verify example with test feedback
- `RunResult` + `on_step` hooks for inspectable runs

**Use this** for teaching, demos, and tiny scripts where you want readable control flow.  
**Use LangGraph (or similar)** when you need durable checkpoints, streaming platforms, or multi-actor orchestration.

## Install

```bash
# from GitHub
pip install "git+https://github.com/cobusgreyling/graph-engineering.git"

# or clone and install editable
git clone https://github.com/cobusgreyling/graph-engineering.git
cd graph-engineering
pip install -e ".[dev]"
```

Nothing is required at runtime beyond the standard library.

```bash
python examples/research_write_verify.py
```

Optional image export:

```bash
pip install "simple-graph-agents[graphviz]"   # also need system graphviz binaries
# or: pip install graphviz
```

## Quick start

```python
from simple_graph_agents import Graph, END

def research(state):
    state["notes"] = ["fact A", "fact B"]
    return state

def write(state):
    state["draft"] = " ".join(state.get("notes", []))
    return state

def verify(state):
    state["passed"] = len(state.get("draft", "")) > 10
    return state

def route(state):
    return "pass" if state.get("passed") else "retry"

g = Graph()
g.add_node("research", research)
g.add_node("write", write)
g.add_node("verify", verify)
g.set_entry("research")
g.add_edge("research", "write")
g.add_edge("write", "verify")
g.add_conditional_edges(
    "verify",
    route,
    path_map={"pass": END, "retry": "write"},
)

result = g.run({"topic": "agents"})
print(result.state["draft"])
print(result.history)   # node trail including END
print(result.steps)
print(g.render_mermaid())
```

Clone-and-run without install still works via the root shim:

```python
from simple_graph import Graph, END  # re-exports simple_graph_agents
```

## API

| Method / type | Purpose |
|---------------|---------|
| `add_node(name, fn)` | Register `fn(state: dict) -> dict` |
| `add_edge(src, tgt)` | Fixed edge; `tgt` may be `END` (no silent overwrite) |
| `add_conditional_edges(src, router, path_map=None)` | `router(state) -> str` next node (or key into `path_map`) |
| `set_entry(name)` / `entry(name)` | Where `run` starts |
| `run(state, max_steps=50, verbose=False, on_step=None)` | Execute until `END`; returns `RunResult` |
| `RunResult.state` / `.history` / `.steps` | Final state, node trail, step count |
| `on_step(name, state, step)` | Optional hook after each node |
| `render_mermaid()` / `render(path=None)` | Mermaid flowchart string |
| `render_graphviz(path=None, format="png")` | DOT (+ optional render via `graphviz` package) |
| `history` | Node trail from last run (includes `END`) |
| `GraphError` | Definition and runtime errors |

`END` is the reserved terminal sentinel (`"__end__"`).

### State notes

- Input state is **shallow-copied**; nested lists/dicts are shared with the caller.
- Nodes may mutate and return the same object, or return a new dict.
- A node with no outgoing edge **implicitly ends** (routes to `END`).

## Mermaid visualization

Any graph prints paste-ready Mermaid:

```python
print(g.render_mermaid())
# or
g.render("graph.mmd")
```

Paste into:

- [mermaid.live](https://mermaid.live)
- GitHub / GitLab markdown fenced as ` ```mermaid `
- the local demo under [`demo/`](demo/)

Example output from the research/write/verify loop:

```mermaid
flowchart TD
    start((start)) --> research
    research["research"]
    write["write"]
    verify["verify"]
    END((END))
    research --> write
    write --> verify
    verify -->|pass| END
    verify -->|retry| write
```

## Example: research → write → verify

```bash
python examples/research_write_verify.py
```

What it shows:

1. **research** — fills `state["notes"]`
2. **write** — builds `state["draft"]`, using `state["feedback"]` on retries
3. **verify** — runs lightweight checks; first pass intentionally fails so you see the loop
4. **router** — `"retry"` → `write`, `"pass"` → `END`

Also writes [`demo/graph.mmd`](demo/graph.mmd) for the web viewer.

## Web demo (vanilla JS)

Static page; Mermaid is loaded from a CDN. No build step.

```bash
# generate demo/graph.mmd
python examples/research_write_verify.py

# serve the folder
python -m http.server 8765 --directory demo
# open http://localhost:8765
```

Edit the source pane and hit **Render**, or paste output from `render_mermaid()`.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

CI runs pytest on Python 3.9–3.13 and executes the example script.

## Design notes

- **State is a dict.** Nodes may mutate and return the same object, or return a new dict.
- **No async / streaming.** Add it in the node body if you need it.
- **No LLM client.** Swap stubs in the example for your provider of choice.
- **Cycles are allowed** (retry loops). Guard with `max_steps`.
- **Routers return strings.** Prefer `path_map` so Mermaid edge labels stay stable.
- **Duplicate edges raise.** Fixed and conditional edges cannot be redefined on the same source.

## Layout

```
simple-graph-agents/
├── simple_graph_agents/         # installable package
│   ├── __init__.py
│   └── graph.py                 # Graph, END, RunResult, Mermaid / DOT
├── simple_graph.py              # clone-and-run shim
├── examples/
│   └── research_write_verify.py # research → write → verify loop
├── demo/
│   ├── index.html               # vanilla JS Mermaid viewer
│   └── graph.mmd                # generated by the example
├── tests/
│   └── test_graph.py
├── pyproject.toml
└── README.md
```

## License

MIT — use it, fork it, keep it small.
