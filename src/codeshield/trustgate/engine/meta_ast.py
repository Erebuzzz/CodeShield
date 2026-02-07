"""
Meta-AST Normalisation Layer

Converts language-specific tree-sitter nodes into a unified MetaNode
representation that downstream layers (graphs, rules) can consume
without caring about the source language.

Normalised node types:
    FUNCTION, CALL, ASSIGNMENT, LOOP, CONDITIONAL, IMPORT, RETURN,
    CLASS, VARIABLE, LITERAL, BINARY_OP, BLOCK, PARAMETER, MODULE

Semantic annotations attached to each node:
    scope, trust_level, async_boundary, eval_order, exception_points
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

from tree_sitter import Node as TSNode

from codeshield.trustgate.engine.parser import ParseResult, Lang


# ---------------------------------------------------------------------------
# Normalised node types
# ---------------------------------------------------------------------------

class NodeKind(str, Enum):
    MODULE = "MODULE"
    FUNCTION = "FUNCTION"
    CLASS = "CLASS"
    CALL = "CALL"
    ASSIGNMENT = "ASSIGNMENT"
    LOOP = "LOOP"
    CONDITIONAL = "CONDITIONAL"
    IMPORT = "IMPORT"
    RETURN = "RETURN"
    VARIABLE = "VARIABLE"
    LITERAL = "LITERAL"
    BINARY_OP = "BINARY_OP"
    PARAMETER = "PARAMETER"
    BLOCK = "BLOCK"
    ATTRIBUTE = "ATTRIBUTE"
    TRY_EXCEPT = "TRY_EXCEPT"
    RAISE = "RAISE"
    UNKNOWN = "UNKNOWN"


class TrustLevel(str, Enum):
    """How much we trust the data flowing through this node."""
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    SANITIZED = "sanitized"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# MetaNode — unified AST node
# ---------------------------------------------------------------------------

@dataclass
class MetaNode:
    """Language-agnostic AST node."""
    kind: NodeKind
    name: Optional[str] = None
    text: str = ""
    line: int = 0
    end_line: int = 0
    column: int = 0
    children: list[MetaNode] = field(default_factory=list)

    # Semantic annotations
    scope: Optional[str] = None
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    is_async: bool = False
    exception_point: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    # Back-reference to original tree-sitter node (not serialised)
    _ts_node: Optional[Any] = field(default=None, repr=False)

    def find_all(self, kind: NodeKind) -> list[MetaNode]:
        """Recursively collect all descendants of a given kind."""
        result: list[MetaNode] = []
        if self.kind == kind:
            result.append(self)
        for child in self.children:
            result.extend(child.find_all(kind))
        return result

    def find_first(self, kind: NodeKind) -> Optional[MetaNode]:
        """Return first descendant of a given kind (DFS)."""
        if self.kind == kind:
            return self
        for child in self.children:
            found = child.find_first(kind)
            if found is not None:
                return found
        return None

    @property
    def calls(self) -> list[MetaNode]:
        return self.find_all(NodeKind.CALL)

    @property
    def functions(self) -> list[MetaNode]:
        return self.find_all(NodeKind.FUNCTION)

    @property
    def imports(self) -> list[MetaNode]:
        return self.find_all(NodeKind.IMPORT)


# ---------------------------------------------------------------------------
# MetaAST — root container
# ---------------------------------------------------------------------------

@dataclass
class MetaAST:
    """Top-level container for a normalised AST."""
    root: MetaNode
    language: str
    has_errors: bool
    source: str

    @property
    def all_calls(self) -> list[MetaNode]:
        return self.root.find_all(NodeKind.CALL)

    @property
    def all_functions(self) -> list[MetaNode]:
        return self.root.find_all(NodeKind.FUNCTION)

    @property
    def all_imports(self) -> list[MetaNode]:
        return self.root.find_all(NodeKind.IMPORT)


# ---------------------------------------------------------------------------
# Language-specific normalizers
# ---------------------------------------------------------------------------

# Node-type mappings: tree-sitter type → NodeKind
_PYTHON_MAP: dict[str, NodeKind] = {
    "module": NodeKind.MODULE,
    "function_definition": NodeKind.FUNCTION,
    "async_function_definition": NodeKind.FUNCTION,
    "class_definition": NodeKind.CLASS,
    "call": NodeKind.CALL,
    "assignment": NodeKind.ASSIGNMENT,
    "augmented_assignment": NodeKind.ASSIGNMENT,
    "for_statement": NodeKind.LOOP,
    "while_statement": NodeKind.LOOP,
    "if_statement": NodeKind.CONDITIONAL,
    "elif_clause": NodeKind.CONDITIONAL,
    "else_clause": NodeKind.CONDITIONAL,
    "import_statement": NodeKind.IMPORT,
    "import_from_statement": NodeKind.IMPORT,
    "return_statement": NodeKind.RETURN,
    "identifier": NodeKind.VARIABLE,
    "string": NodeKind.LITERAL,
    "integer": NodeKind.LITERAL,
    "float": NodeKind.LITERAL,
    "true": NodeKind.LITERAL,
    "false": NodeKind.LITERAL,
    "none": NodeKind.LITERAL,
    "binary_operator": NodeKind.BINARY_OP,
    "comparison_operator": NodeKind.BINARY_OP,
    "boolean_operator": NodeKind.BINARY_OP,
    "parameters": NodeKind.PARAMETER,
    "block": NodeKind.BLOCK,
    "attribute": NodeKind.ATTRIBUTE,
    "try_statement": NodeKind.TRY_EXCEPT,
    "raise_statement": NodeKind.RAISE,
}

_JAVASCRIPT_MAP: dict[str, NodeKind] = {
    "program": NodeKind.MODULE,
    "function_declaration": NodeKind.FUNCTION,
    "arrow_function": NodeKind.FUNCTION,
    "method_definition": NodeKind.FUNCTION,
    "class_declaration": NodeKind.CLASS,
    "call_expression": NodeKind.CALL,
    "assignment_expression": NodeKind.ASSIGNMENT,
    "variable_declaration": NodeKind.ASSIGNMENT,
    "lexical_declaration": NodeKind.ASSIGNMENT,
    "variable_declarator": NodeKind.ASSIGNMENT,
    "augmented_assignment_expression": NodeKind.ASSIGNMENT,
    "for_statement": NodeKind.LOOP,
    "for_in_statement": NodeKind.LOOP,
    "while_statement": NodeKind.LOOP,
    "do_statement": NodeKind.LOOP,
    "if_statement": NodeKind.CONDITIONAL,
    "else_clause": NodeKind.CONDITIONAL,
    "import_statement": NodeKind.IMPORT,
    "return_statement": NodeKind.RETURN,
    "identifier": NodeKind.VARIABLE,
    "string": NodeKind.LITERAL,
    "template_string": NodeKind.LITERAL,
    "number": NodeKind.LITERAL,
    "true": NodeKind.LITERAL,
    "false": NodeKind.LITERAL,
    "null": NodeKind.LITERAL,
    "undefined": NodeKind.LITERAL,
    "binary_expression": NodeKind.BINARY_OP,
    "formal_parameters": NodeKind.PARAMETER,
    "statement_block": NodeKind.BLOCK,
    "member_expression": NodeKind.ATTRIBUTE,
    "try_statement": NodeKind.TRY_EXCEPT,
    "throw_statement": NodeKind.RAISE,
}

_LANG_MAPS: dict[Lang, dict[str, NodeKind]] = {
    Lang.PYTHON: _PYTHON_MAP,
    Lang.JAVASCRIPT: _JAVASCRIPT_MAP,
}


# ---------------------------------------------------------------------------
# Normalisation functions
# ---------------------------------------------------------------------------

def _extract_name(ts_node: TSNode, source: bytes, language: Lang) -> Optional[str]:
    """Try to extract a human-readable name from a tree-sitter node."""
    if language == Lang.PYTHON:
        # function_definition → child "name"
        if ts_node.type in ("function_definition", "async_function_definition", "class_definition"):
            for child in ts_node.children:
                if child.type == "identifier":
                    return source[child.start_byte:child.end_byte].decode("utf-8", errors="replace")
        # call → child "function"  (identifier or attribute)
        if ts_node.type == "call":
            func_node = ts_node.child_by_field_name("function")
            if func_node:
                return source[func_node.start_byte:func_node.end_byte].decode("utf-8", errors="replace")
        # import
        if ts_node.type in ("import_statement", "import_from_statement"):
            return source[ts_node.start_byte:ts_node.end_byte].decode("utf-8", errors="replace").strip()

    elif language == Lang.JAVASCRIPT:
        if ts_node.type in ("function_declaration", "class_declaration"):
            name_node = ts_node.child_by_field_name("name")
            if name_node:
                return source[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
        if ts_node.type == "call_expression":
            func_node = ts_node.child_by_field_name("function")
            if func_node:
                return source[func_node.start_byte:func_node.end_byte].decode("utf-8", errors="replace")

    # Fallback for identifiers / literals
    if ts_node.type in ("identifier", "string", "integer", "float", "number"):
        return source[ts_node.start_byte:ts_node.end_byte].decode("utf-8", errors="replace")

    return None


def _normalise_node(
    ts_node: TSNode,
    source: bytes,
    language: Lang,
    scope: str = "<module>",
) -> MetaNode:
    """Convert a single tree-sitter node into a MetaNode, recursively."""
    lang_map = _LANG_MAPS.get(language, {})
    kind = lang_map.get(ts_node.type, NodeKind.UNKNOWN)

    text = source[ts_node.start_byte:ts_node.end_byte].decode("utf-8", errors="replace")
    name = _extract_name(ts_node, source, language)

    is_async = ts_node.type.startswith("async_") or ts_node.type.startswith("await")
    exception_point = ts_node.type in ("try_statement", "raise_statement", "throw_statement")

    # Determine scope for children
    child_scope = scope
    if kind == NodeKind.FUNCTION and name:
        child_scope = f"{scope}.{name}"
    elif kind == NodeKind.CLASS and name:
        child_scope = f"{scope}.{name}"

    children: list[MetaNode] = []
    for child in ts_node.children:
        # Skip purely structural nodes
        if child.type in ("(", ")", "{", "}", "[", "]", ",", ":", ";", "comment"):
            continue
        children.append(_normalise_node(child, source, language, child_scope))

    return MetaNode(
        kind=kind,
        name=name,
        text=text if len(text) <= 200 else text[:200] + "…",
        line=ts_node.start_point[0] + 1,
        end_line=ts_node.end_point[0] + 1,
        column=ts_node.start_point[1],
        children=children,
        scope=scope,
        is_async=is_async,
        exception_point=exception_point,
        _ts_node=ts_node,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalise(parse_result: ParseResult) -> MetaAST:
    """
    Convert a ParseResult (tree-sitter tree) into a language-agnostic MetaAST.
    """
    root = _normalise_node(
        parse_result.root,
        parse_result.source,
        parse_result.language,
    )
    return MetaAST(
        root=root,
        language=parse_result.language.value,
        has_errors=parse_result.has_errors,
        source=parse_result.source.decode("utf-8", errors="replace"),
    )
