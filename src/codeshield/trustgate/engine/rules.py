"""
Verification DSL & Rule Engine

Declarative rules that match AST patterns, query program graphs,
and enforce data-flow constraints.  Each rule yields zero or more
*Findings* — typed, located, severity-tagged diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from codeshield.trustgate.engine.meta_ast import MetaAST, MetaNode, NodeKind, TrustLevel
from codeshield.trustgate.engine.graphs import (
    ProgramGraph,
    build_cfg,
    build_dfg,
    build_taint_graph,
    build_call_graph,
)


# ===================================================================
# Severity & Finding
# ===================================================================

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class Finding:
    """A single diagnostic emitted by a rule."""
    rule_id: str
    message: str
    severity: Severity
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0
    fix_hint: Optional[str] = None
    meta_node: Optional[MetaNode] = None

    def to_dict(self) -> dict:
        return {
            "rule": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "fix_hint": self.fix_hint,
        }


# ===================================================================
# Rule & RuleSet
# ===================================================================

@dataclass
class Rule:
    """
    A verification rule.

    * ``id``        – unique slug, e.g. ``"shell_injection"``
    * ``name``      – human-readable label
    * ``severity``  – default severity for findings
    * ``match``     – callable(MetaAST, graphs) → list[Finding]
    * ``languages`` – which languages this rule applies to (empty = all)
    * ``tags``      – classification tags (``"security"``, ``"style"``, …)
    """
    id: str
    name: str
    severity: Severity
    match: Callable[[MetaAST, dict[str, ProgramGraph]], list[Finding]]
    languages: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class RuleSet:
    """An ordered collection of rules."""
    rules: list[Rule] = field(default_factory=list)

    def add(self, rule: Rule) -> None:
        self.rules.append(rule)

    def enabled_rules(self, language: str = "") -> list[Rule]:
        """Return rules applicable to *language* that are enabled."""
        out = []
        for r in self.rules:
            if not r.enabled:
                continue
            if r.languages and language and language not in r.languages:
                continue
            out.append(r)
        return out


# ===================================================================
# Built-in helper matchers
# ===================================================================

def _find_calls_by_name(meta_ast: MetaAST, names: set[str]) -> list[MetaNode]:
    """Find CALL nodes whose function name is in *names*."""
    results = []
    for call in meta_ast.all_calls:
        fname = call.name or ""
        if fname in names:
            results.append(call)
        # Also match dotted suffix  (e.g., "os.system" matches "system")
        short = fname.split(".")[-1] if "." in fname else ""
        if short in names:
            results.append(call)
    return results


def _find_nodes_by_kind(root: MetaNode, kind: NodeKind) -> list[MetaNode]:
    """Recursively find all nodes of a given kind."""
    return root.find_all(kind)


# ===================================================================
# Built-in rules
# ===================================================================

def _rule_shell_injection(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Detect dangerous exec/eval/system calls."""
    dangerous = {"exec", "eval", "compile", "os.system", "os.popen",
                 "subprocess.call", "subprocess.run", "subprocess.Popen",
                 "child_process.exec", "child_process.spawn"}
    findings = []
    for call in _find_calls_by_name(meta_ast, dangerous):
        fname = call.name or "?"
        findings.append(Finding(
            rule_id="shell_injection",
            message=f"Dangerous call to `{fname}` — potential code/command injection",
            severity=Severity.ERROR,
            line=call.line,
            column=call.column,
            fix_hint=f"Avoid `{fname}` or sanitise all inputs before passing them.",
            meta_node=call,
        ))
    return findings


def _rule_taint_to_sink(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Flag any taint source → sink path found in the TFG."""
    tfg = graphs.get("tfg")
    if not tfg:
        return []
    findings = []
    for edge in tfg.edges:
        src_node = tfg.nodes.get(edge.src)
        sink_node = tfg.nodes.get(edge.dst)
        if src_node and sink_node:
            findings.append(Finding(
                rule_id="taint_flow",
                message=(
                    f"Untrusted data from `{src_node.label}` (L{src_node.line}) "
                    f"reaches dangerous sink `{sink_node.label}` (L{sink_node.line})"
                ),
                severity=Severity.ERROR,
                line=sink_node.line,
                fix_hint="Sanitise or validate the input before passing to the sink.",
                meta_node=sink_node.meta,
            ))
    return findings


def _rule_unused_import(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Detect imports that are never referenced elsewhere."""
    findings = []
    imports = meta_ast.root.find_all(NodeKind.IMPORT)
    all_vars = {v.name for v in meta_ast.root.find_all(NodeKind.VARIABLE) if v.name}
    all_calls = {c.name.split(".")[0] for c in meta_ast.all_calls if c.name}
    used_names = all_vars | all_calls

    for imp in imports:
        imp_name = imp.name or imp.text.strip()
        # Extract simple module name
        simple = imp_name.split(".")[-1] if "." in imp_name else imp_name
        simple = simple.split(" as ")[-1].strip() if " as " in simple else simple
        if simple and simple not in used_names:
            findings.append(Finding(
                rule_id="unused_import",
                message=f"Import `{imp_name}` is never used",
                severity=Severity.WARNING,
                line=imp.line,
                fix_hint=f"Remove the unused import `{imp_name}`.",
                meta_node=imp,
            ))
    return findings


def _rule_type_mismatch(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Detect obvious type mismatches in binary operations (e.g. str + int)."""
    findings = []
    binops = meta_ast.root.find_all(NodeKind.BINARY_OP)
    for op in binops:
        children = op.children
        if len(children) < 2:
            continue
        left, right = children[0], children[-1]
        left_kind = _infer_literal_type(left)
        right_kind = _infer_literal_type(right)
        if left_kind and right_kind and left_kind != right_kind:
            # Numeric operations between str and int/float
            if {"str"} & {left_kind, right_kind}:
                findings.append(Finding(
                    rule_id="type_mismatch",
                    message=f"Potential type error: mixing `{left_kind}` and `{right_kind}` in arithmetic",
                    severity=Severity.ERROR,
                    line=op.line,
                    fix_hint="Ensure both operands are the same type or use explicit conversion.",
                    meta_node=op,
                ))
    return findings


def _infer_literal_type(node: MetaNode) -> Optional[str]:
    """Heuristic: infer the type of a literal node from its text."""
    if node.kind != NodeKind.LITERAL:
        return None
    text = node.text.strip()
    if not text:
        return None
    if text.startswith(("'", '"', '"""', "'''")):
        return "str"
    if text.startswith(("b'", 'b"')):
        return "bytes"
    if text in ("True", "False", "true", "false"):
        return "bool"
    if text in ("None", "null", "undefined"):
        return "none"
    try:
        int(text)
        return "int"
    except ValueError:
        pass
    try:
        float(text)
        return "float"
    except ValueError:
        pass
    return None


def _rule_bare_except(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Detect bare `except:` or `except Exception:` that swallows everything."""
    findings = []
    try_nodes = meta_ast.root.find_all(NodeKind.TRY_EXCEPT)
    for tn in try_nodes:
        text = tn.text[:200]
        if "except:" in text or "except Exception:" in text:
            findings.append(Finding(
                rule_id="bare_except",
                message="Bare `except` swallows all exceptions — catch specific types",
                severity=Severity.WARNING,
                line=tn.line,
                fix_hint="Replace with `except SpecificError:` to avoid masking bugs.",
                meta_node=tn,
            ))
    return findings


def _rule_hardcoded_secret(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Detect hardcoded passwords, keys, tokens in assignments."""
    SECRET_NAMES = {"password", "passwd", "secret", "api_key", "apikey",
                    "token", "auth_token", "private_key", "secret_key"}
    findings = []
    for assign in meta_ast.root.find_all(NodeKind.ASSIGNMENT):
        if not assign.children:
            continue
        lhs = assign.children[0]
        name = (lhs.name or "").lower()
        if any(s in name for s in SECRET_NAMES):
            # Check if RHS is a literal string
            for child in assign.children[1:]:
                if child.kind == NodeKind.LITERAL and child.text.strip().startswith(("'", '"')):
                    findings.append(Finding(
                        rule_id="hardcoded_secret",
                        message=f"Hardcoded secret in variable `{lhs.name}`",
                        severity=Severity.ERROR,
                        line=assign.line,
                        fix_hint="Use environment variables or a secrets manager instead.",
                        meta_node=assign,
                    ))
                    break
    return findings


def _rule_unreachable_code(meta_ast: MetaAST, graphs: dict[str, ProgramGraph]) -> list[Finding]:
    """Detect statements after return in the same block."""
    findings = []
    for fn in meta_ast.all_functions:
        _check_unreachable_in_block(fn, findings)
    return findings


def _check_unreachable_in_block(node: MetaNode, findings: list[Finding]) -> None:
    """Walk blocks looking for code after return/raise."""
    for child in node.children:
        if child.kind == NodeKind.BLOCK:
            saw_return = False
            for stmt in child.children:
                if saw_return:
                    findings.append(Finding(
                        rule_id="unreachable_code",
                        message="Unreachable code after return/raise statement",
                        severity=Severity.WARNING,
                        line=stmt.line,
                        meta_node=stmt,
                    ))
                if stmt.kind in (NodeKind.RETURN, NodeKind.RAISE):
                    saw_return = True
        _check_unreachable_in_block(child, findings)


# ===================================================================
# Registry
# ===================================================================

_BUILTIN_RULES: list[Rule] = [
    Rule(
        id="shell_injection", name="Shell / Code Injection",
        severity=Severity.ERROR, match=_rule_shell_injection,
        tags=["security"], languages=[],
    ),
    Rule(
        id="taint_flow", name="Taint Source → Sink",
        severity=Severity.ERROR, match=_rule_taint_to_sink,
        tags=["security"], languages=[],
    ),
    Rule(
        id="unused_import", name="Unused Import",
        severity=Severity.WARNING, match=_rule_unused_import,
        tags=["quality"], languages=["python"],
    ),
    Rule(
        id="type_mismatch", name="Type Mismatch in Arithmetic",
        severity=Severity.ERROR, match=_rule_type_mismatch,
        tags=["correctness"], languages=[],
    ),
    Rule(
        id="bare_except", name="Bare Except Clause",
        severity=Severity.WARNING, match=_rule_bare_except,
        tags=["quality"], languages=["python"],
    ),
    Rule(
        id="hardcoded_secret", name="Hardcoded Secret",
        severity=Severity.ERROR, match=_rule_hardcoded_secret,
        tags=["security"], languages=[],
    ),
    Rule(
        id="unreachable_code", name="Unreachable Code",
        severity=Severity.WARNING, match=_rule_unreachable_code,
        tags=["quality"], languages=[],
    ),
]


def load_builtin_rules() -> RuleSet:
    """Return a RuleSet loaded with all built-in rules."""
    rs = RuleSet()
    for r in _BUILTIN_RULES:
        rs.add(r)
    return rs
