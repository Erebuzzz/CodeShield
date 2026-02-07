"""
Program Graph Layer — CFG, DFG, Taint Flow Graph, Call Graph

Builds language-agnostic graphs from the MetaAST so that
verification rules can perform path-sensitive queries
(reachability, taint propagation, data-flow constraints).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from codeshield.trustgate.engine.meta_ast import MetaAST, MetaNode, NodeKind, TrustLevel


# ===================================================================
# Shared graph primitives
# ===================================================================

@dataclass
class GraphNode:
    """A node in any program graph."""
    id: int
    label: str
    meta: Optional[MetaNode] = None
    line: int = 0

    def __hash__(self) -> int:
        return self.id


@dataclass
class GraphEdge:
    """Directed edge between two GraphNodes."""
    src: int
    dst: int
    label: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class ProgramGraph:
    """Generic directed graph."""
    kind: str  # "cfg", "dfg", "tfg", "call_graph"
    nodes: dict[int, GraphNode] = field(default_factory=dict)
    edges: list[GraphEdge] = field(default_factory=list)
    entry: Optional[int] = None
    exit: Optional[int] = None

    _next_id: int = field(default=0, repr=False)

    def add_node(self, label: str, meta: Optional[MetaNode] = None, line: int = 0) -> GraphNode:
        nid = self._next_id
        self._next_id += 1
        node = GraphNode(id=nid, label=label, meta=meta, line=line)
        self.nodes[nid] = node
        return node

    def add_edge(self, src: int, dst: int, label: str = "", **extra: object) -> GraphEdge:
        edge = GraphEdge(src=src, dst=dst, label=label, extra=dict(extra))
        self.edges.append(edge)
        return edge

    def successors(self, nid: int) -> list[int]:
        return [e.dst for e in self.edges if e.src == nid]

    def predecessors(self, nid: int) -> list[int]:
        return [e.src for e in self.edges if e.dst == nid]

    def reachable_from(self, start: int) -> set[int]:
        """BFS reachability from *start*."""
        visited: set[int] = set()
        queue = [start]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            queue.extend(self.successors(current))
        return visited


# ===================================================================
# Control Flow Graph (CFG)
# ===================================================================

def build_cfg(meta_ast: MetaAST) -> ProgramGraph:
    """
    Build an intra-procedural CFG from a MetaAST.

    Each statement-level MetaNode becomes a CFG node.
    Conditional / loop structures produce branch edges.
    """
    cfg = ProgramGraph(kind="cfg")
    entry = cfg.add_node("ENTRY", line=0)
    cfg.entry = entry.id

    _cfg_visit(meta_ast.root, cfg, prev_ids=[entry.id])

    # Add single EXIT node
    exit_node = cfg.add_node("EXIT", line=0)
    cfg.exit = exit_node.id
    # Connect all leaf nodes → EXIT
    all_targets = {e.dst for e in cfg.edges}
    all_sources = {e.src for e in cfg.edges}
    leaf_ids = all_sources - all_targets
    if not leaf_ids:
        leaf_ids = {entry.id}
    for lid in leaf_ids:
        cfg.add_edge(lid, exit_node.id)

    return cfg


_STATEMENT_KINDS = {
    NodeKind.ASSIGNMENT, NodeKind.CALL, NodeKind.RETURN,
    NodeKind.IMPORT, NodeKind.RAISE,
}


def _cfg_visit(
    node: MetaNode,
    cfg: ProgramGraph,
    prev_ids: list[int],
) -> list[int]:
    """Recursive CFG builder. Returns list of 'current' node ids after visiting."""
    if node.kind in _STATEMENT_KINDS:
        n = cfg.add_node(
            label=f"{node.kind.value}: {node.name or node.text[:40]}",
            meta=node,
            line=node.line,
        )
        for pid in prev_ids:
            cfg.add_edge(pid, n.id)
        return [n.id]

    if node.kind == NodeKind.CONDITIONAL:
        cond = cfg.add_node(label="IF", meta=node, line=node.line)
        for pid in prev_ids:
            cfg.add_edge(pid, cond.id)

        # True branch = first child block, False branch = else / next
        branch_exits: list[int] = []
        for i, child in enumerate(node.children):
            if child.kind == NodeKind.BLOCK:
                exits = _cfg_visit_block(child, cfg, [cond.id])
                branch_exits.extend(exits)
        # If no else, the condition itself can fall through
        if len([c for c in node.children if c.kind == NodeKind.BLOCK]) < 2:
            branch_exits.append(cond.id)
        return branch_exits

    if node.kind == NodeKind.LOOP:
        loop_header = cfg.add_node(label="LOOP", meta=node, line=node.line)
        for pid in prev_ids:
            cfg.add_edge(pid, loop_header.id)

        # Body
        body_exits: list[int] = [loop_header.id]
        for child in node.children:
            if child.kind == NodeKind.BLOCK:
                body_exits = _cfg_visit_block(child, cfg, body_exits)
        # Back-edge
        for be in body_exits:
            cfg.add_edge(be, loop_header.id, label="back")
        return [loop_header.id]  # loop can also exit

    if node.kind == NodeKind.FUNCTION:
        fn = cfg.add_node(
            label=f"FUNC: {node.name or '?'}",
            meta=node,
            line=node.line,
        )
        for pid in prev_ids:
            cfg.add_edge(pid, fn.id)
        # Visit body
        body_exits_fn: list[int] = [fn.id]
        for child in node.children:
            if child.kind == NodeKind.BLOCK:
                body_exits_fn = _cfg_visit_block(child, cfg, body_exits_fn)
        return body_exits_fn

    # Default: recurse through children sequentially
    current = prev_ids
    for child in node.children:
        current = _cfg_visit(child, cfg, current)
    return current


def _cfg_visit_block(block: MetaNode, cfg: ProgramGraph, prev_ids: list[int]) -> list[int]:
    """Visit children of a BLOCK node sequentially."""
    current = prev_ids
    for child in block.children:
        current = _cfg_visit(child, cfg, current)
    return current


# ===================================================================
# Data Flow Graph (DFG)
# ===================================================================

@dataclass
class DFGFact:
    """A single data-flow fact: variable defined/used at a location."""
    variable: str
    kind: str  # "def" or "use"
    line: int
    node_id: int


def build_dfg(meta_ast: MetaAST) -> ProgramGraph:
    """
    Build a def-use data flow graph.

    Nodes = variable definitions and uses.
    Edges = def → use for the same variable name.
    """
    dfg = ProgramGraph(kind="dfg")
    facts: list[DFGFact] = []

    _dfg_collect(meta_ast.root, dfg, facts)

    # Connect defs → uses
    defs: dict[str, list[DFGFact]] = {}
    for f in facts:
        if f.kind == "def":
            defs.setdefault(f.variable, []).append(f)

    for f in facts:
        if f.kind == "use" and f.variable in defs:
            for d in defs[f.variable]:
                if d.line <= f.line:
                    dfg.add_edge(d.node_id, f.node_id, label=f.variable)

    return dfg


def _dfg_collect(node: MetaNode, dfg: ProgramGraph, facts: list[DFGFact]) -> None:
    """Collect def/use facts from MetaAST."""
    if node.kind == NodeKind.ASSIGNMENT:
        # Left side = def, right side = uses
        if node.children:
            lhs = node.children[0] if node.children else None
            if lhs and lhs.kind == NodeKind.VARIABLE and lhs.name:
                n = dfg.add_node(label=f"def:{lhs.name}", meta=node, line=node.line)
                facts.append(DFGFact(variable=lhs.name, kind="def", line=node.line, node_id=n.id))
            # RHS uses
            for child in node.children[1:]:
                _dfg_collect_uses(child, dfg, facts)

    elif node.kind == NodeKind.VARIABLE and node.name:
        n = dfg.add_node(label=f"use:{node.name}", meta=node, line=node.line)
        facts.append(DFGFact(variable=node.name, kind="use", line=node.line, node_id=n.id))

    elif node.kind == NodeKind.FUNCTION:
        # Parameters are defs
        for child in node.children:
            if child.kind == NodeKind.PARAMETER:
                for param in child.children:
                    if param.kind == NodeKind.VARIABLE and param.name:
                        n = dfg.add_node(label=f"param:{param.name}", meta=param, line=param.line)
                        facts.append(DFGFact(variable=param.name, kind="def", line=param.line, node_id=n.id))

    for child in node.children:
        _dfg_collect(child, dfg, facts)


def _dfg_collect_uses(node: MetaNode, dfg: ProgramGraph, facts: list[DFGFact]) -> None:
    """Collect 'use' facts from an expression subtree."""
    if node.kind == NodeKind.VARIABLE and node.name:
        n = dfg.add_node(label=f"use:{node.name}", meta=node, line=node.line)
        facts.append(DFGFact(variable=node.name, kind="use", line=node.line, node_id=n.id))
    for child in node.children:
        _dfg_collect_uses(child, dfg, facts)


# ===================================================================
# Taint Flow Graph (TFG)
# ===================================================================

# Sources of untrusted data (function names)
_TAINT_SOURCES: set[str] = {
    "input", "raw_input",                          # Python
    "os.environ", "os.getenv", "sys.argv",          # Python env
    "request.args", "request.form", "request.json",  # Flask/Django
    "prompt",                                        # JS
    "readline",                                      # Node
    "req.body", "req.query", "req.params",           # Express
}

# Dangerous sinks
_TAINT_SINKS: set[str] = {
    "exec", "eval", "compile", "__import__",   # Python
    "os.system", "os.popen", "subprocess.call", "subprocess.run", "subprocess.Popen",
    "open",                                     # File access
    "cursor.execute", "db.execute",             # SQL
    "eval",                                     # JS
    "child_process.exec", "child_process.spawn",
    "innerHTML",
}


def build_taint_graph(meta_ast: MetaAST) -> ProgramGraph:
    """
    Build a taint-flow graph.

    Marks CALL nodes as sources/sinks based on known function names,
    then connects them through the data flow.
    """
    tfg = ProgramGraph(kind="tfg")

    sources: list[GraphNode] = []
    sinks: list[GraphNode] = []

    for call in meta_ast.all_calls:
        fname = call.name or ""
        if fname in _TAINT_SOURCES or any(fname.endswith(f".{s.split('.')[-1]}") for s in _TAINT_SOURCES if "." in s):
            n = tfg.add_node(label=f"SOURCE: {fname}", meta=call, line=call.line)
            sources.append(n)
        if fname in _TAINT_SINKS or any(fname.endswith(f".{s.split('.')[-1]}") for s in _TAINT_SINKS if "." in s):
            n = tfg.add_node(label=f"SINK: {fname}", meta=call, line=call.line)
            sinks.append(n)

    # Heuristic: if tainted data flows to a sink within the same scope → edge
    for src in sources:
        for sink in sinks:
            if src.meta and sink.meta and src.line <= sink.line:
                if src.meta.scope == sink.meta.scope:
                    tfg.add_edge(src.id, sink.id, label="taint_flow")

    return tfg


# ===================================================================
# Call Graph
# ===================================================================

def build_call_graph(meta_ast: MetaAST) -> ProgramGraph:
    """
    Build an inter-procedural call graph.

    Nodes = functions.  Edges = function A calls function B.
    """
    cg = ProgramGraph(kind="call_graph")

    # Collect all function definitions
    func_nodes: dict[str, GraphNode] = {}
    for fn in meta_ast.all_functions:
        if fn.name:
            gn = cg.add_node(label=fn.name, meta=fn, line=fn.line)
            func_nodes[fn.name] = gn

    # Collect calls and link to function nodes
    for fn in meta_ast.all_functions:
        if not fn.name or fn.name not in func_nodes:
            continue
        caller = func_nodes[fn.name]
        for call in fn.calls:
            callee_name = call.name or ""
            # Strip attribute prefix for simple matching
            simple_name = callee_name.split(".")[-1] if "." in callee_name else callee_name
            if simple_name in func_nodes:
                cg.add_edge(caller.id, func_nodes[simple_name].id, label="calls")

    return cg
