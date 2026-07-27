#!/usr/bin/env python3
"""Smallest possible graph — three lines of wiring, one coffee to understand."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simple_graph_agents import END, Graph

g = (
    Graph("hello")
    .node("greet", lambda s: {**s, "msg": f"hello, {s.get('name', 'world')}"})
    .node("shout", lambda s: {**s, "msg": s["msg"].upper()})
    .entry("greet")
    .chain("greet", "shout")
)

result = g.run({"name": "graph engineering"}, timed=True)
print(result.state["msg"])
print(result.trail())
print(g.render_ascii())
print(g.render_mermaid())
