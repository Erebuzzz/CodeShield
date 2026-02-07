"""
CodeShield SDK — Programmatic Python API

Provides a clean, importable interface for:
  - verify()           — verify code with the v2 engine
  - verify_file()      — verify a file on disk
  - scan_project()     — scan a whole directory
  - export_graph()     — get CFG/DFG/TFG/call-graph as dicts
  - list_rules()       — query the rule registry
  - audit_deps()       — audit a requirements file
  - get_dashboard()    — get dashboard state
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def verify(code: str, language: str = "python", **kwargs) -> dict:
    """Verify source code. Returns a dict with is_valid, confidence_score, findings."""
    from codeshield.trustgate.engine.executor import verify as _verify
    report = _verify(code, language=language, **kwargs)
    return report.to_dict()


def verify_file(path: str | Path, language: str | None = None) -> dict:
    """Verify a file on disk."""
    from codeshield.trustgate.engine.executor import verify as _verify
    from codeshield.trustgate.engine.parser import detect_language

    p = Path(path)
    code = p.read_text(encoding="utf-8")
    if language is None:
        lang_enum = detect_language(p.name)
        language = lang_enum.value if lang_enum else "python"
    return _verify(code, language=language, filename=p.name).to_dict()


def scan_project(
    directory: str | Path = ".",
    extensions: list[str] | None = None,
) -> dict:
    """Recursively scan a project. Returns {files: [...], total_findings: int}."""
    from codeshield.trustgate.engine.executor import verify as _verify
    from codeshield.trustgate.engine.parser import detect_language

    root = Path(directory)
    exts = extensions or [".py", ".js"]
    results = []
    total = 0
    for ext in exts:
        for fpath in root.rglob(f"*{ext}"):
            if any(part.startswith(".") for part in fpath.parts):
                continue
            if "node_modules" in fpath.parts or "__pycache__" in fpath.parts:
                continue
            try:
                code = fpath.read_text(encoding="utf-8", errors="replace")
                lang_enum = detect_language(fpath.name)
                lang = lang_enum.value if lang_enum else "python"
                r = _verify(code, language=lang, filename=fpath.name)
                results.append({"file": str(fpath.relative_to(root)), **r.to_dict()})
                total += len(r.findings)
            except Exception as e:
                results.append({"file": str(fpath.relative_to(root)), "error": str(e)})
    return {"files": results, "total_findings": total}


def export_graph(
    code: str,
    language: str = "python",
    graph_type: str = "cfg",
) -> dict:
    """Export a program graph as a JSON-serializable dict."""
    from codeshield.trustgate.engine.parser import parse_source
    from codeshield.trustgate.engine.meta_ast import normalise
    from codeshield.trustgate.engine.graphs import (
        build_cfg, build_dfg, build_taint_graph, build_call_graph,
    )

    pr = parse_source(code, language)
    meta = normalise(pr)
    builders = {
        "cfg": build_cfg, "dfg": build_dfg,
        "tfg": build_taint_graph, "call_graph": build_call_graph,
    }
    builder = builders.get(graph_type)
    if not builder:
        raise ValueError(f"Unknown graph type: {graph_type}. Use: {list(builders.keys())}")
    graph = builder(meta)
    return {
        "graph_type": graph_type,
        "nodes": [{"id": n.id, "label": n.label, "line": n.line} for n in graph.nodes.values()],
        "edges": [{"src": e.src, "dst": e.dst, "label": e.label} for e in graph.edges],
        "entry": graph.entry,
        "exit": graph.exit,
    }


def list_rules() -> list[dict]:
    """Return all verification rules (built-in + plugins)."""
    from codeshield.plugins import get_registry
    rs = get_registry().get_all_rules()
    return [
        {"id": r.id, "name": r.name, "severity": r.severity.value,
         "tags": r.tags, "languages": r.languages or ["all"]}
        for r in rs.rules
    ]


def audit_deps(requirements_path: str | Path) -> dict:
    """Audit a requirements.txt for known CVEs."""
    import re
    p = Path(requirements_path)
    text = p.read_text(encoding="utf-8")
    insecure_db = {
        "pyyaml": "CVE-2020-14343", "requests": "CVE-2018-18074",
        "flask": "Multiple CVEs", "django": "EOL security",
        "jinja2": "CVE-2020-28493", "urllib3": "CVE-2021-33503",
        "pillow": "Buffer overflow CVEs", "cryptography": "CVE-2020-36242",
        "paramiko": "CVE-2022-24302", "setuptools": "CVE-2022-40897",
    }
    packages = []
    flagged = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z0-9_.-]+)", line)
        if match:
            name = match.group(1).lower()
            packages.append(name)
            if name in insecure_db:
                flagged.append({"package": name, "advisory": insecure_db[name]})
    return {"total": len(packages), "flagged": len(flagged), "advisories": flagged}


def get_dashboard() -> dict:
    """Get dashboard state for programmatic access."""
    from codeshield.plugins import get_registry
    from codeshield.contextvault.capture import list_contexts
    registry = get_registry()
    rs = registry.get_all_rules()
    return {
        "rules_loaded": len(rs.rules),
        "plugins": registry.list_plugins(),
        "recent_contexts": list_contexts()[:10],
        "supported_languages": ["python", "javascript"],
    }
