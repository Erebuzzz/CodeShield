"""
TrustGate v2 — Language-Agnostic Verification Engine

Architecture layers:
  1. Parsing Layer      - tree-sitter based, multi-language
  2. Meta-AST Layer     - unified node representation
  3. Program Graph Layer - CFG, DFG, TFG, Call Graph
  4. Verification DSL   - declarative rules
  5. Execution Engine   - rule matching + incremental verification
"""

from codeshield.trustgate.engine.parser import parse_source, get_supported_languages
from codeshield.trustgate.engine.meta_ast import MetaNode, MetaAST
from codeshield.trustgate.engine.graphs import build_cfg, build_dfg, build_taint_graph
from codeshield.trustgate.engine.rules import Rule, RuleSet, load_builtin_rules
from codeshield.trustgate.engine.executor import verify, VerificationReport

__all__ = [
    "parse_source",
    "get_supported_languages",
    "MetaNode",
    "MetaAST",
    "build_cfg",
    "build_dfg",
    "build_taint_graph",
    "Rule",
    "RuleSet",
    "load_builtin_rules",
    "verify",
    "VerificationReport",
]
