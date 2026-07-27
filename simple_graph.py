"""
Backward-compatible entry point for clone-and-run usage::

    from simple_graph import Graph, END

Prefer the installable package when possible::

    from simple_graph_agents import Graph, END
"""

from simple_graph_agents import (
    END,
    Graph,
    GraphError,
    NodeFn,
    RouterFn,
    RunResult,
    State,
    StepHook,
    StepRecord,
    __version__,
)

__all__ = [
    "Graph",
    "END",
    "GraphError",
    "RunResult",
    "StepRecord",
    "State",
    "NodeFn",
    "RouterFn",
    "StepHook",
    "__version__",
]
