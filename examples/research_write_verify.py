#!/usr/bin/env python3
"""
Minimal agent loop: research → write → verify, with test feedback.

If verification fails, the graph routes back to `write` with feedback
in the shared state until checks pass (or max_steps is hit).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as `python examples/research_write_verify.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simple_graph_agents import END, Graph


# ---------------------------------------------------------------------------
# Nodes — plain functions (state dict in, state dict out)
# ---------------------------------------------------------------------------

def research(state: dict) -> dict:
    """Gather notes for the topic. (Stub — swap for a real LLM/tool call.)"""
    topic = state.get("topic", "something")
    notes = [
        f"{topic} is a pattern for composing multi-step agent workflows.",
        "Each step is a pure-ish function over a shared state dictionary.",
        "Conditional edges let you retry on failed verification.",
        "Mermaid export makes the control flow inspectable.",
    ]
    state["notes"] = notes
    state["research_done"] = True
    print(f"[research] collected {len(notes)} notes on {topic!r}")
    return state


def write(state: dict) -> dict:
    """Draft a short summary from notes + any prior feedback."""
    notes = state.get("notes") or []
    feedback = state.get("feedback") or []
    attempt = state.get("attempt", 0) + 1
    state["attempt"] = attempt

    body = " ".join(notes)
    draft = f"# Summary (attempt {attempt})\n\n{body}\n"
    if feedback:
        # Incorporate the latest feedback naively so the next verify can pass
        draft += "\n## Revisions\n"
        for item in feedback:
            draft += f"- Addressed: {item}\n"
        # Ensure required keywords appear after first failure
        draft += "\nVerified against tests with explicit test feedback loop.\n"

    state["draft"] = draft
    print(f"[write] attempt={attempt}, draft_len={len(draft)}")
    return state


def verify(state: dict) -> dict:
    """
    Lightweight 'tests' on the draft.

    Checks:
      1. Draft exists and is non-trivial
      2. Mentions 'state' (from research notes)
      3. On retry, must acknowledge feedback / tests
    """
    draft = state.get("draft") or ""
    attempt = state.get("attempt", 0)
    failures = []

    if len(draft) < 40:
        failures.append("draft too short")
    if "state" not in draft.lower():
        failures.append("missing concept: shared state")
    # Force at least one revision cycle so the loop is visible
    if attempt < 2:
        failures.append("needs a second pass with test feedback")
    if attempt >= 2 and "test feedback" not in draft.lower() and "tests" not in draft.lower():
        failures.append("revisions must reference tests/feedback")

    state["passed"] = len(failures) == 0
    state["feedback"] = failures
    if failures:
        print(f"[verify] FAIL: {failures}")
    else:
        print("[verify] PASS")
    return state


def route_after_verify(state: dict) -> str:
    """Router: pass → END, fail → write again."""
    return "pass" if state.get("passed") else "retry"


# ---------------------------------------------------------------------------
# Build graph
# ---------------------------------------------------------------------------

def build_graph() -> Graph:
    g = Graph(name="research_write_verify")
    g.add_node("research", research)
    g.add_node("write", write)
    g.add_node("verify", verify)

    g.set_entry("research")
    g.add_edge("research", "write")
    g.add_edge("write", "verify")
    g.add_conditional_edges(
        "verify",
        route_after_verify,
        path_map={"pass": END, "retry": "write"},
    )
    return g


def main() -> None:
    g = build_graph()

    print("=== Mermaid ===")
    mermaid = g.render_mermaid()
    print(mermaid)
    out = Path(__file__).resolve().parents[1] / "demo" / "graph.mmd"
    out.write_text(mermaid, encoding="utf-8")
    print(f"(also wrote {out})\n")

    print("=== Run ===")
    result = g.run(
        {"topic": "simple graph agents"},
        verbose=True,
        max_steps=20,
    )

    print("\n=== Trail ===")
    print(" -> ".join(result.history))

    print("\n=== Final draft ===")
    print(result.state.get("draft", ""))
    print(
        f"passed={result.state.get('passed')} "
        f"attempts={result.state.get('attempt')} "
        f"steps={result.steps}"
    )


if __name__ == "__main__":
    main()
