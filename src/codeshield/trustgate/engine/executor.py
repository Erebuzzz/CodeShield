"""
Execution Engine — Top-level verification orchestrator.

Takes source code → parses → normalises → builds graphs →
runs rule-set → aggregates findings → returns VerificationReport.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional

from codeshield.trustgate.engine.parser import Lang, ParseResult, parse_source, detect_language
from codeshield.trustgate.engine.meta_ast import MetaAST, normalise
from codeshield.trustgate.engine.graphs import (
    ProgramGraph,
    build_cfg,
    build_dfg,
    build_taint_graph,
    build_call_graph,
)
from codeshield.trustgate.engine.rules import (
    Finding,
    RuleSet,
    Severity,
    load_builtin_rules,
)


# ===================================================================
# Verification Report
# ===================================================================

@dataclass
class VerificationReport:
    """Aggregated output of a verification run."""
    is_valid: bool
    confidence_score: float          # 0.0 – 1.0
    findings: list[Finding]         # all diagnostics
    errors: list[Finding]           # severity == ERROR
    warnings: list[Finding]         # severity == WARNING
    language: str
    parse_ok: bool
    elapsed_ms: float
    code_hash: str

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "confidence_score": self.confidence_score,
            "findings": [f.to_dict() for f in self.findings],
            "errors": [f.to_dict() for f in self.errors],
            "warnings": [f.to_dict() for f in self.warnings],
            "language": self.language,
            "parse_ok": self.parse_ok,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "code_hash": self.code_hash,
            "issues": [
                {
                    "severity": f.severity.value,
                    "line": f.line,
                    "message": f.message,
                    "fix_hint": f.fix_hint,
                }
                for f in self.findings
            ],
        }


# ===================================================================
# Simple result cache (hash → report)
# ===================================================================

_cache: dict[str, VerificationReport] = {}
_CACHE_MAX = 512


def _code_hash(code: str, language: str) -> str:
    return hashlib.sha256(f"{language}:{code}".encode()).hexdigest()[:16]


# ===================================================================
# Public API
# ===================================================================

def verify(
    code: str,
    language: str = "python",
    *,
    filename: Optional[str] = None,
    rules: Optional[RuleSet] = None,
    use_cache: bool = True,
) -> VerificationReport:
    """
    Run the full verification pipeline on *code*.

    Parameters
    ----------
    code : str
        Source code to verify.
    language : str
        Language identifier (``"python"``, ``"javascript"``).
        Falls back to ``detect_language(filename)`` if given.
    filename : str, optional
        Original filename for language detection / display.
    rules : RuleSet, optional
        Custom rule-set; defaults to built-in rules.
    use_cache : bool
        Whether to return cached results for identical code+language.

    Returns
    -------
    VerificationReport
    """
    t0 = time.perf_counter()

    # Resolve language
    if filename and language == "python":
        detected = detect_language(filename)
        if detected:
            language = detected.value

    h = _code_hash(code, language)
    if use_cache and h in _cache:
        # Record cache hit in live metrics
        try:
            from codeshield.utils.live_metrics import live
            live.record_verification(engine="v2", language=language, cache_hit=True)
        except Exception:
            pass
        return _cache[h]

    # 1. Parse
    lang_enum = _resolve_lang(language)
    parse_result: Optional[ParseResult] = None
    parse_ok = True
    try:
        parse_result = parse_source(code, lang_enum)
        if parse_result.has_errors:
            parse_ok = False
    except Exception:
        parse_ok = False

    # If parsing fails entirely, return a minimal report with a parse error
    if parse_result is None:
        elapsed = (time.perf_counter() - t0) * 1000
        report = VerificationReport(
            is_valid=False,
            confidence_score=0.0,
            findings=[Finding(
                rule_id="parse_error",
                message=f"Failed to parse {language} code",
                severity=Severity.ERROR,
                line=1,
            )],
            errors=[Finding(
                rule_id="parse_error",
                message=f"Failed to parse {language} code",
                severity=Severity.ERROR,
                line=1,
            )],
            warnings=[],
            language=language,
            parse_ok=False,
            elapsed_ms=elapsed,
            code_hash=h,
        )
        _maybe_cache(h, report)
        return report

    # 2. Normalise → MetaAST
    meta_ast = normalise(parse_result)

    # 3. Build program graphs
    graphs: dict[str, ProgramGraph] = {}
    try:
        graphs["cfg"] = build_cfg(meta_ast)
    except Exception:
        pass
    try:
        graphs["dfg"] = build_dfg(meta_ast)
    except Exception:
        pass
    try:
        graphs["tfg"] = build_taint_graph(meta_ast)
    except Exception:
        pass
    try:
        graphs["call_graph"] = build_call_graph(meta_ast)
    except Exception:
        pass

    # 4. Run rules
    ruleset = rules or load_builtin_rules()
    all_findings: list[Finding] = []

    # Add parse-error finding if syntax tree has errors
    if not parse_ok:
        all_findings.append(Finding(
            rule_id="syntax_error",
            message="Code contains syntax errors",
            severity=Severity.ERROR,
            line=1,
        ))

    for rule in ruleset.enabled_rules(language):
        try:
            findings = rule.match(meta_ast, graphs)
            all_findings.extend(findings)
        except Exception:
            pass  # rule failure should not crash the engine

    # 5. Aggregate
    errors = [f for f in all_findings if f.severity == Severity.ERROR]
    warnings = [f for f in all_findings if f.severity == Severity.WARNING]

    confidence = _compute_confidence(all_findings, parse_ok)
    is_valid = len(errors) == 0 and parse_ok

    elapsed = (time.perf_counter() - t0) * 1000

    report = VerificationReport(
        is_valid=is_valid,
        confidence_score=confidence,
        findings=all_findings,
        errors=errors,
        warnings=warnings,
        language=language,
        parse_ok=parse_ok,
        elapsed_ms=elapsed,
        code_hash=h,
    )

    _maybe_cache(h, report)

    # Auto-record to live metrics (zero-cost if disabled)
    try:
        from codeshield.utils.live_metrics import live
        live.record_verification(
            engine="v2",
            language=language,
            findings=len(all_findings),
            errors=len(errors),
            warnings=len(warnings),
            elapsed_ms=elapsed,
            cache_hit=False,
        )
    except Exception:
        pass

    return report


# ===================================================================

def _resolve_lang(language: str) -> Lang:
    """Map string to Lang enum."""
    mapping = {
        "python": Lang.PYTHON,
        "py": Lang.PYTHON,
        "javascript": Lang.JAVASCRIPT,
        "js": Lang.JAVASCRIPT,
    }
    return mapping.get(language.lower(), Lang.PYTHON)


def _compute_confidence(findings: list[Finding], parse_ok: bool) -> float:
    """
    Heuristic confidence score 0.0–1.0.

    Starts at 1.0 and deducts for each finding based on severity.
    """
    score = 1.0
    if not parse_ok:
        score -= 0.3

    for f in findings:
        if f.severity == Severity.ERROR:
            score -= 0.15
        elif f.severity == Severity.WARNING:
            score -= 0.05
        elif f.severity == Severity.INFO:
            score -= 0.02

    return max(0.0, min(1.0, round(score, 2)))


def _maybe_cache(h: str, report: VerificationReport) -> None:
    """Cache the report, evicting oldest if full."""
    if len(_cache) >= _CACHE_MAX:
        # simple FIFO eviction
        oldest = next(iter(_cache))
        del _cache[oldest]
    _cache[h] = report
