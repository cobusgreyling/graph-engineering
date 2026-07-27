#!/usr/bin/env python3
"""
Multi-agent handoff: researcher → writer → critic → (revise | ship).

Each "agent" is a node. The critic routes back to the writer with notes,
or ends when quality is good enough. Same runtime — no framework ceremony.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simple_graph_agents import END, Graph


def researcher(state: dict) -> dict:
    topic = state.get("topic", "graph agents")
    state["brief"] = (
        f"Topic: {topic}. "
        "Key points: plain functions, shared dict state, conditional edges, Mermaid."
    )
    print(f"[researcher] brief ready ({len(state['brief'])} chars)")
    return state


def writer(state: dict) -> dict:
    attempt = state.get("attempt", 0) + 1
    state["attempt"] = attempt
    notes = state.get("critic_notes") or []
    draft = f"## {state.get('topic', 'Untitled')} (v{attempt})\n\n{state.get('brief', '')}\n"
    if notes:
        draft += "\n### Addressing feedback\n"
        for n in notes:
            draft += f"- {n}\n"
        draft += "\nClarity improved; control flow made explicit.\n"
    state["draft"] = draft
    print(f"[writer] attempt={attempt} len={len(draft)}")
    return state


def critic(state: dict) -> dict:
    draft = state.get("draft") or ""
    attempt = state.get("attempt", 0)
    notes = []
    if attempt < 2:
        notes.append("Add a section addressing reviewer feedback")
    if "control flow" not in draft.lower() and attempt >= 2:
        notes.append("Mention control flow explicitly")
    if len(draft) < 80:
        notes.append("Draft too short")
    state["critic_notes"] = notes
    state["ship"] = len(notes) == 0
    print(f"[critic] ship={state['ship']} notes={notes}")
    return state


def route_critic(state: dict) -> str:
    return "ship" if state.get("ship") else "revise"


def build_graph() -> Graph:
    return (
        Graph(name="multi_agent_handoff")
        .node("researcher", researcher)
        .node("writer", writer)
        .node("critic", critic)
        .entry("researcher")
        .edge("researcher", "writer")
        .edge("writer", "critic")
        .branch(
            "critic",
            route_critic,
            path_map={"ship": END, "revise": "writer"},
        )
        .validate()
    )


def main() -> None:
    g = build_graph()
    print(g.render_ascii())
    result = g.run({"topic": "Graph Engineering"}, verbose=True, timed=True)
    print("\n=== Final draft ===")
    print(result.state.get("draft"))
    print("trail:", result.trail())
    print(f"steps={result.steps} ms={result.duration_ms:.2f}")


if __name__ == "__main__":
    main()
