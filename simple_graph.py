"""
simple-graph-agents — zero-dependency graph runtime for agent loops.

Nodes are plain callables: (state: dict) -> dict
Edges are fixed or conditional (router returns next node name).
END is a reserved terminal node.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Union

State = Dict[str, Any]
NodeFn = Callable[[State], State]
RouterFn = Callable[[State], str]

# Reserved terminal sentinel
END = "__end__"


class GraphError(Exception):
    """Raised for graph definition or runtime errors."""


class Graph:
    """
    Minimal directed graph of state-transforming nodes.

    Example
    -------
    >>> g = Graph()
    >>> g.add_node("a", lambda s: {**s, "x": 1})
    >>> g.add_node("b", lambda s: {**s, "y": 2})
    >>> g.add_edge("a", "b")
    >>> g.add_edge("b", END)
    >>> g.set_entry("a")
    >>> g.run({})
    {'x': 1, 'y': 2}
    """

    def __init__(self, name: str = "agent_graph") -> None:
        self.name = name
        self._nodes: Dict[str, NodeFn] = {}
        self._edges: Dict[str, str] = {}
        self._conditional: Dict[str, RouterFn] = {}
        # Optional map of router return value -> node name (for Mermaid labels)
        self._path_maps: Dict[str, Mapping[str, str]] = {}
        self._entry: Optional[str] = None
        self._history: List[str] = []

    # ------------------------------------------------------------------
    # Definition API
    # ------------------------------------------------------------------

    def add_node(self, name: str, fn: NodeFn) -> "Graph":
        """Register a node. `fn` receives and returns a shared state dict."""
        if not name or name == END:
            raise GraphError(f"Invalid node name: {name!r}")
        if name in self._nodes:
            raise GraphError(f"Node already exists: {name!r}")
        if not callable(fn):
            raise GraphError(f"Node {name!r} must be callable")
        self._nodes[name] = fn
        return self

    def add_edge(self, source: str, target: str) -> "Graph":
        """Unconditional edge from `source` to `target` (or END)."""
        self._assert_source(source)
        if target != END and target not in self._nodes:
            raise GraphError(f"Unknown target node: {target!r}")
        if source in self._conditional:
            raise GraphError(f"Node {source!r} already has conditional edges")
        self._edges[source] = target
        return self

    def add_conditional_edges(
        self,
        source: str,
        router: RouterFn,
        path_map: Optional[Mapping[str, str]] = None,
    ) -> "Graph":
        """
        Conditional edges from `source`.

        `router(state)` must return a node name (or END), or a key that
        `path_map` maps to a node name.
        """
        self._assert_source(source)
        if source in self._edges:
            raise GraphError(f"Node {source!r} already has a fixed edge")
        if not callable(router):
            raise GraphError("router must be callable")
        self._conditional[source] = router
        if path_map is not None:
            for key, target in path_map.items():
                if target != END and target not in self._nodes:
                    raise GraphError(
                        f"path_map target for {key!r} is unknown: {target!r}"
                    )
            self._path_maps[source] = dict(path_map)
        return self

    def set_entry(self, name: str) -> "Graph":
        """Set the node where `run` begins."""
        if name not in self._nodes:
            raise GraphError(f"Unknown entry node: {name!r}")
        self._entry = name
        return self

    # Fluent aliases
    def entry(self, name: str) -> "Graph":
        return self.set_entry(name)

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    def run(
        self,
        state: Optional[State] = None,
        *,
        max_steps: int = 50,
        verbose: bool = False,
    ) -> State:
        """
        Execute the graph starting at the entry node.

        Mutates and returns the same state dict (nodes may return a new dict
        or mutate in place; both are supported).
        """
        if self._entry is None:
            raise GraphError("Entry node not set; call set_entry() first")
        if not self._nodes:
            raise GraphError("Graph has no nodes")

        current: State = dict(state or {})
        node_name: str = self._entry
        self._history = []
        steps = 0

        while node_name != END:
            if steps >= max_steps:
                raise GraphError(
                    f"Exceeded max_steps={max_steps}; possible cycle. "
                    f"Trail: {' -> '.join(self._history)}"
                )
            if node_name not in self._nodes:
                raise GraphError(f"Unknown node at runtime: {node_name!r}")

            self._history.append(node_name)
            if verbose:
                print(f"[{steps}] → {node_name}")

            fn = self._nodes[node_name]
            result = fn(current)
            if result is None:
                raise GraphError(
                    f"Node {node_name!r} returned None; must return a state dict"
                )
            if not isinstance(result, dict):
                raise GraphError(
                    f"Node {node_name!r} must return a dict, got {type(result).__name__}"
                )
            current = result
            node_name = self._next(node_name, current)
            steps += 1

        self._history.append(END)
        if verbose:
            print(f"[{steps}] → END")
        return current

    def _next(self, source: str, state: State) -> str:
        if source in self._conditional:
            router = self._conditional[source]
            key = router(state)
            if not isinstance(key, str):
                raise GraphError(
                    f"Router for {source!r} must return str, got {type(key).__name__}"
                )
            path_map = self._path_maps.get(source)
            if path_map is not None:
                if key not in path_map:
                    raise GraphError(
                        f"Router for {source!r} returned {key!r}, "
                        f"not in path_map keys {list(path_map)}"
                    )
                return path_map[key]
            return key

        if source in self._edges:
            return self._edges[source]

        # Implicit end if no outgoing edge
        return END

    @property
    def history(self) -> List[str]:
        """Node visit order from the last `run` (includes END)."""
        return list(self._history)

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def render_mermaid(self, *, direction: str = "TD") -> str:
        """
        Return Mermaid flowchart syntax for this graph.

        Paste into https://mermaid.live or any Mermaid-capable viewer.
        """
        if direction not in {"TD", "TB", "LR", "RL", "BT"}:
            direction = "TD"

        lines: List[str] = [f"flowchart {direction}"]
        # Node declarations
        for name in self._nodes:
            safe = _mermaid_id(name)
            label = name.replace('"', "'")
            lines.append(f'    {safe}["{label}"]')
        lines.append(f'    {_mermaid_id(END)}((END))')

        # Fixed edges
        for src, tgt in self._edges.items():
            lines.append(f"    {_mermaid_id(src)} --> {_mermaid_id(tgt)}")

        # Conditional edges
        for src, router in self._conditional.items():
            path_map = self._path_maps.get(src)
            if path_map:
                for label, tgt in path_map.items():
                    lab = str(label).replace('"', "'")
                    lines.append(
                        f"    {_mermaid_id(src)} -->|{lab}| {_mermaid_id(tgt)}"
                    )
            else:
                # Unknown branches: show dashed edge to a diamond note
                note = _mermaid_id(f"{src}__router")
                lines.append(f'    {note}{{"router"}}')
                lines.append(f"    {_mermaid_id(src)} -.-> {note}")

        # Entry marker
        if self._entry:
            lines.append(f"    start((start)) --> {_mermaid_id(self._entry)}")

        return "\n".join(lines) + "\n"

    def render(self, path: Optional[str] = None) -> str:
        """
        Alias for render_mermaid. If `path` is given, write the .mmd file.
        Returns the Mermaid source string.
        """
        src = self.render_mermaid()
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)
        return src

    def render_graphviz(self, path: Optional[str] = None, format: str = "png") -> str:
        """
        Optional Graphviz DOT export. Requires the `graphviz` package only if
        you want to render to an image; DOT text itself needs no deps.

        Returns DOT source. If `path` is set and graphviz is installed, also
        writes `path` with the given format (e.g. png, svg).
        """
        lines = [f'digraph "{self.name}" {{', "  rankdir=TB;"]
        for name in self._nodes:
            lines.append(f'  "{name}" [shape=box];')
        lines.append(f'  "{END}" [shape=doublecircle, label="END"];')
        for src, tgt in self._edges.items():
            lines.append(f'  "{src}" -> "{tgt}";')
        for src in self._conditional:
            path_map = self._path_maps.get(src)
            if path_map:
                for label, tgt in path_map.items():
                    lines.append(f'  "{src}" -> "{tgt}" [label="{label}"];')
            else:
                lines.append(f'  "{src}" -> "{END}" [style=dashed, label="router"];')
        if self._entry:
            lines.append('  "__start__" [shape=circle, label="start"];')
            lines.append(f'  "__start__" -> "{self._entry}";')
        lines.append("}")
        dot = "\n".join(lines) + "\n"

        if path:
            try:
                import graphviz  # type: ignore
            except ImportError as e:
                raise GraphError(
                    "graphviz package not installed. "
                    "pip install graphviz  (and system graphviz binaries)"
                ) from e
            g = graphviz.Source(dot)
            # path may include extension; graphviz appends format
            out = path.rsplit(".", 1)[0] if "." in path.split("/")[-1] else path
            g.render(out, format=format, cleanup=True)

        return dot

    def _assert_source(self, source: str) -> None:
        if source not in self._nodes:
            raise GraphError(f"Unknown source node: {source!r}")

    def nodes(self) -> Sequence[str]:
        return list(self._nodes)

    def __repr__(self) -> str:
        return (
            f"Graph(name={self.name!r}, nodes={list(self._nodes)}, "
            f"entry={self._entry!r})"
        )


def _mermaid_id(name: str) -> str:
    """Sanitize a node name into a Mermaid-safe identifier."""
    if name == END:
        return "END"
    out = []
    for ch in name:
        if ch.isalnum() or ch == "_":
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out) or "node"
    if s[0].isdigit():
        s = "n_" + s
    return s


# Convenience re-export for `from simple_graph import Graph, END`
__all__ = ["Graph", "END", "GraphError", "State", "NodeFn", "RouterFn"]
