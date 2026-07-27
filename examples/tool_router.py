#!/usr/bin/env python3
"""
Tool-router pattern: plan → route to a tool → observe → decide again.

Shows how conditional edges replace hard-coded if/else trees when an
agent picks among tools (search, calc, finish) based on state.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simple_graph_agents import END, Graph


def plan(state: dict) -> dict:
    """Decide what the agent still needs. Stub — swap for an LLM planner."""
    goal = state.get("goal", "answer a question")
    scratch = state.setdefault("scratch", [])
    if "searched" not in scratch:
        state["intent"] = "search"
        state["query"] = goal
    elif "calculated" not in scratch:
        state["intent"] = "calc"
        state["expr"] = "6 * 7"
    else:
        state["intent"] = "finish"
    print(f"[plan] intent={state['intent']}")
    return state


def search_tool(state: dict) -> dict:
    q = state.get("query", "")
    hit = f"search({q!r}) → 'People reduce this to a short product.'"
    state.setdefault("facts", []).append(hit)
    state.setdefault("scratch", []).append("searched")
    print(f"[search] {hit}")
    return state


def calc_tool(state: dict) -> dict:
    expr = state.get("expr", "0")
    # Stub calculator — swap for a real tool / sandbox in production
    table = {"6 * 7": 42, "6*7": 42}
    value = table.get(expr.strip(), "unknown")
    fact = f"calc({expr}) = {value}"
    state.setdefault("facts", []).append(fact)
    state.setdefault("scratch", []).append("calculated")
    print(f"[calc] {fact}")
    return state


def finish(state: dict) -> dict:
    facts = state.get("facts") or []
    state["answer"] = facts[-1] if facts else "no answer"
    print(f"[finish] answer={state['answer']!r}")
    return state


def route_intent(state: dict) -> str:
    return state.get("intent", "finish")


def build_graph() -> Graph:
    g = (
        Graph(name="tool_router")
        .node("plan", plan)
        .node("search", search_tool)
        .node("calc", calc_tool)
        .node("finish", finish)
        .entry("plan")
        .branch(
            "plan",
            route_intent,
            path_map={
                "search": "search",
                "calc": "calc",
                "finish": "finish",
            },
        )
        .edge("search", "plan")
        .edge("calc", "plan")
        .edge("finish", END)
    )
    return g.validate()


def main() -> None:
    g = build_graph()
    print(g.render_ascii())
    print("=== Mermaid ===")
    print(g.render_mermaid())

    result = g.run({"goal": "what is 6 times 7?"}, verbose=True, timed=True, max_steps=20)
    print("\ntrail:", result.trail())
    print("answer:", result.state.get("answer"))
    print(f"steps={result.steps} duration_ms={result.duration_ms:.2f}")


if __name__ == "__main__":
    main()
