"""Unit tests for simple_graph_agents."""

from __future__ import annotations

import doctest

import pytest

from simple_graph_agents import END, Graph, GraphError, RunResult, StepRecord, __version__
from simple_graph_agents import graph as graph_mod


def _linear() -> Graph:
    g = Graph(name="linear")
    g.add_node("a", lambda s: {**s, "x": 1})
    g.add_node("b", lambda s: {**s, "y": 2})
    g.set_entry("a")
    g.add_edge("a", "b")
    g.add_edge("b", END)
    return g


# ---------------------------------------------------------------------------
# Definition
# ---------------------------------------------------------------------------


def test_version():
    assert __version__ == "0.2.0"


def test_add_node_rejects_end_and_duplicates():
    g = Graph()
    with pytest.raises(GraphError, match="Invalid node name"):
        g.add_node(END, lambda s: s)
    with pytest.raises(GraphError, match="Invalid node name"):
        g.add_node("", lambda s: s)
    g.add_node("a", lambda s: s)
    with pytest.raises(GraphError, match="already exists"):
        g.add_node("a", lambda s: s)
    with pytest.raises(GraphError, match="must be callable"):
        g.add_node("b", "not-callable")  # type: ignore[arg-type]


def test_duplicate_fixed_edge_raises():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_node("b", lambda s: s)
    g.add_edge("a", "b")
    with pytest.raises(GraphError, match="already has a fixed edge"):
        g.add_edge("a", END)


def test_fixed_then_conditional_raises():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_edge("a", END)
    with pytest.raises(GraphError, match="already has a fixed edge"):
        g.add_conditional_edges("a", lambda s: END)


def test_conditional_then_fixed_raises():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_conditional_edges("a", lambda s: END)
    with pytest.raises(GraphError, match="already has conditional edges"):
        g.add_edge("a", END)


def test_duplicate_conditional_raises():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_conditional_edges("a", lambda s: END)
    with pytest.raises(GraphError, match="already has conditional edges"):
        g.add_conditional_edges("a", lambda s: END)


def test_unknown_target_and_entry():
    g = Graph()
    g.add_node("a", lambda s: s)
    with pytest.raises(GraphError, match="Unknown target"):
        g.add_edge("a", "missing")
    with pytest.raises(GraphError, match="Unknown entry"):
        g.set_entry("missing")
    with pytest.raises(GraphError, match="Unknown source"):
        g.add_edge("missing", END)
    with pytest.raises(GraphError, match="path_map target"):
        g.add_conditional_edges(
            "a",
            lambda s: "x",
            path_map={"x": "nope"},
        )


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


def test_run_linear_returns_run_result():
    g = _linear()
    result = g.run({})
    assert isinstance(result, RunResult)
    assert result.state == {"x": 1, "y": 2}
    assert result.history == ["a", "b", END]
    assert result.steps == 2
    assert g.history == result.history


def test_run_result_unpacking():
    g = _linear()
    state, history = g.run({})
    assert state["x"] == 1
    assert history[-1] == END


def test_run_requires_entry():
    g = Graph()
    g.add_node("a", lambda s: s)
    with pytest.raises(GraphError, match="Entry node not set"):
        g.run({})


def test_node_must_return_dict():
    g = Graph()
    g.add_node("a", lambda s: None)  # type: ignore[return-value, arg-type]
    g.set_entry("a")
    with pytest.raises(GraphError, match="returned None"):
        g.run({})

    g2 = Graph()
    g2.add_node("a", lambda s: "nope")  # type: ignore[return-value, arg-type]
    g2.set_entry("a")
    with pytest.raises(GraphError, match="must return a dict"):
        g2.run({})


def test_max_steps_cycle():
    g = Graph()
    g.add_node("loop", lambda s: {**s, "n": s.get("n", 0) + 1})
    g.set_entry("loop")
    g.add_edge("loop", "loop")
    with pytest.raises(GraphError, match="max_steps"):
        g.run({}, max_steps=5)


def test_conditional_path_map_and_router_key_error():
    g = Graph()
    g.add_node("a", lambda s: {**s, "ok": True})
    g.set_entry("a")
    g.add_conditional_edges(
        "a",
        lambda s: "pass" if s.get("ok") else "retry",
        path_map={"pass": END, "retry": "a"},
    )
    result = g.run({})
    assert result.history == ["a", END]

    g2 = Graph()
    g2.add_node("a", lambda s: s)
    g2.set_entry("a")
    g2.add_conditional_edges(
        "a",
        lambda s: "unknown",
        path_map={"pass": END},
    )
    with pytest.raises(GraphError, match="not in path_map"):
        g2.run({})


def test_router_without_path_map_returns_node_name():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_node("b", lambda s: {**s, "done": True})
    g.set_entry("a")
    g.add_conditional_edges("a", lambda s: "b")
    g.add_edge("b", END)
    assert g.run({}).state["done"] is True


def test_router_must_return_str():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.set_entry("a")
    g.add_conditional_edges("a", lambda s: 1)  # type: ignore[return-value, arg-type]
    with pytest.raises(GraphError, match="must return str"):
        g.run({})


def test_implicit_end_when_no_outgoing_edge():
    g = Graph()
    g.add_node("solo", lambda s: {**s, "v": 1})
    g.set_entry("solo")
    result = g.run({})
    assert result.state == {"v": 1}
    assert result.history == ["solo", END]


def test_on_step_hook():
    seen = []

    def hook(name, state, step):
        seen.append((name, dict(state), step))

    g = _linear()
    g.run({"seed": 0}, on_step=hook)
    assert [s[0] for s in seen] == ["a", "b"]
    assert seen[0][1]["x"] == 1
    assert seen[0][2] == 0
    assert seen[1][2] == 1


def test_verbose_uses_print(capsys):
    g = _linear()
    g.run({}, verbose=True)
    out = capsys.readouterr().out
    assert "→ a" in out
    assert "→ b" in out
    assert "→ END" in out


def test_shallow_copy_input_state():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.set_entry("a")
    original = {"nested": [1], "k": 0}
    result = g.run(original)
    # top-level key on returned state does not mutate caller's top-level if node
    # replaces dict — but our node returns same object after shallow copy
    assert result.state is not original
    result.state["nested"].append(2)
    # nested list is shared (documented shallow copy)
    assert original["nested"] == [1, 2]


def test_mutate_in_place_and_return_new_dict():
    def mut(s):
        s["a"] = 1
        return s

    def fresh(s):
        return {**s, "b": 2}

    g = Graph()
    g.add_node("mut", mut)
    g.add_node("fresh", fresh)
    g.set_entry("mut")
    g.add_edge("mut", "fresh")
    g.add_edge("fresh", END)
    assert g.run({}).state == {"a": 1, "b": 2}


def test_retry_loop():
    def bump(s):
        s["n"] = s.get("n", 0) + 1
        return s

    def route(s):
        return "loop" if s["n"] < 3 else "done"

    g = Graph()
    g.add_node("bump", bump)
    g.set_entry("bump")
    g.add_conditional_edges(
        "bump",
        route,
        path_map={"loop": "bump", "done": END},
    )
    result = g.run({})
    assert result.state["n"] == 3
    assert result.steps == 3
    assert result.history.count("bump") == 3


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------


def test_render_mermaid_contains_edges_and_entry():
    g = Graph()
    g.add_node("research", lambda s: s)
    g.add_node("write", lambda s: s)
    g.add_node("verify", lambda s: s)
    g.set_entry("research")
    g.add_edge("research", "write")
    g.add_edge("write", "verify")
    g.add_conditional_edges(
        "verify",
        lambda s: "pass",
        path_map={"pass": END, "retry": "write"},
    )
    src = g.render_mermaid()
    assert "flowchart TD" in src
    assert "research --> write" in src
    assert "verify -->|pass| END" in src
    assert "verify -->|retry| write" in src
    assert "start((start)) --> research" in src


def test_render_mermaid_without_path_map_shows_router_note():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.set_entry("a")
    g.add_conditional_edges("a", lambda s: END)
    src = g.render_mermaid()
    assert "router" in src
    assert "-.->" in src


def test_render_writes_file(tmp_path):
    g = _linear()
    path = tmp_path / "g.mmd"
    out = g.render(str(path))
    assert path.read_text(encoding="utf-8") == out


def test_render_graphviz_dot():
    g = _linear()
    dot = g.render_graphviz()
    assert "digraph" in dot
    assert '"a" -> "b"' in dot
    assert "END" in dot


def test_mermaid_id_sanitization():
    assert graph_mod._mermaid_id(END) == "END"
    assert graph_mod._mermaid_id("foo-bar") == "foo_bar"
    assert graph_mod._mermaid_id("9x") == "n_9x"


def test_nodes_and_repr():
    g = _linear()
    assert list(g.nodes()) == ["a", "b"]
    assert "linear" in repr(g)
    assert "entry='a'" in repr(g)


def test_entry_alias():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.entry("a")
    assert g.run({}).history == ["a", END]


def test_fluent_aliases_and_chain():
    g = (
        Graph("fluent")
        .node("a", lambda s: {**s, "x": 1})
        .node("b", lambda s: {**s, "y": 2})
        .entry("a")
        .chain("a", "b")
    )
    result = g.run({})
    assert result.state == {"x": 1, "y": 2}
    assert result.history == ["a", "b", END]


def test_chain_without_end():
    g = Graph()
    g.node("a", lambda s: s).node("b", lambda s: {**s, "ok": True}).entry("a")
    g.chain("a", "b", end=False)
    # b has no edge → implicit END
    assert g.run({}).state["ok"] is True


def test_branch_alias():
    g = (
        Graph()
        .node("a", lambda s: {**s, "n": 1})
        .entry("a")
        .branch("a", lambda s: "done", path_map={"done": END})
    )
    assert g.run({}).history == ["a", END]


def test_validate_unreachable():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_node("orphan", lambda s: s)
    g.set_entry("a")
    g.add_edge("a", END)
    with pytest.raises(GraphError, match="Unreachable"):
        g.validate()


def test_validate_ok_and_run_flag():
    g = _linear()
    assert g.validate() is g
    result = g.run({}, validate=True)
    assert result.steps == 2


def test_render_ascii():
    g = Graph(name="demo")
    g.add_node("research", lambda s: s)
    g.add_node("write", lambda s: s)
    g.set_entry("research")
    g.add_edge("research", "write")
    g.add_conditional_edges(
        "write",
        lambda s: "ok",
        path_map={"ok": END, "retry": "write"},
    )
    ascii_out = g.render_ascii()
    assert "Graph: demo" in ascii_out
    assert "entry: research" in ascii_out
    assert "research --> write" in ascii_out
    assert "write -[ok]-> END" in ascii_out


def test_timed_run_and_trail():
    g = _linear()
    result = g.run({}, timed=True)
    assert result.duration_ms is not None
    assert result.duration_ms >= 0
    assert len(result.trace) == 2
    assert all(isinstance(t, StepRecord) for t in result.trace)
    assert result.trace[0].name == "a"
    assert result.trace[0].duration_ms is not None
    assert result.trail() == f"a -> b -> {END}"


def test_edges_listing():
    g = Graph()
    g.add_node("a", lambda s: s)
    g.add_node("b", lambda s: s)
    g.set_entry("a")
    g.add_edge("a", "b")
    g.add_conditional_edges("b", lambda s: "x", path_map={"x": END})
    edges = g.edges()
    assert ("a", "b", None) in edges
    assert ("b", END, "x") in edges


def test_backward_compatible_simple_graph_import():
    from simple_graph import END as E2
    from simple_graph import Graph as G2

    assert E2 is END
    g = G2()
    g.add_node("a", lambda s: s)
    g.set_entry("a")
    assert g.run({}).state == {}


def test_doctest_module():
    failures, attempted = doctest.testmod(graph_mod)
    assert attempted > 0
    assert failures == 0
