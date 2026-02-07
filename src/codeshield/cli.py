"""
CLI entry point for CodeShield

Commands:
  serve           Start MCP server
  verify          Verify a file (v1 legacy)
  style           Check code style
  scan-project    Scan entire project directory
  explain         Explain a verification report
  visualize       Export program graph as JSON
  dashboard       Launch dashboard dev server
  rules           List / manage verification rules
  plugin          Plugin management (list, install)
  audit-deps      Audit dependencies for CVEs
  export-graph    Export program graph for a file
"""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="CodeShield - The Complete AI Coding Safety Net"
    )
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress the metrics banner after commands")
    parser.add_argument("--no-metrics", action="store_true",
                        help="Disable live metrics for this session")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ---- serve ----
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--port", type=int, default=8080, help="Server port")
    serve_parser.add_argument("--host", default="localhost", help="Server host")

    # ---- verify ----
    verify_parser = subparsers.add_parser("verify", help="Verify a file")
    verify_parser.add_argument("file", help="File to verify")
    verify_parser.add_argument("--language", "-l", default=None, help="Language override")
    verify_parser.add_argument("--engine", choices=["v1", "v2", "auto"], default="auto")
    verify_parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")

    # ---- style ----
    style_parser = subparsers.add_parser("style", help="Check code style against codebase")
    style_parser.add_argument("file", help="File to check")
    style_parser.add_argument("--codebase", default=".", help="Codebase path")

    # ---- scan-project ----
    scan_parser = subparsers.add_parser("scan-project", help="Scan entire project directory")
    scan_parser.add_argument("directory", nargs="?", default=".", help="Project root (default: .)")
    scan_parser.add_argument("--extensions", "-e", nargs="+", default=[".py", ".js"],
                             help="File extensions to scan")
    scan_parser.add_argument("--json", action="store_true", dest="as_json")

    # ---- explain ----
    explain_parser = subparsers.add_parser("explain", help="Explain verification findings")
    explain_parser.add_argument("file", help="File to explain")

    # ---- visualize / export-graph ----
    viz_parser = subparsers.add_parser("visualize", help="Export program graph as JSON")
    viz_parser.add_argument("file", help="Source file to analyze")
    viz_parser.add_argument("--graph", "-g", default="cfg",
                            choices=["cfg", "dfg", "tfg", "call_graph"])
    viz_parser.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")

    export_parser = subparsers.add_parser("export-graph", help="Alias for visualize")
    export_parser.add_argument("file", help="Source file to analyze")
    export_parser.add_argument("--graph", "-g", default="cfg",
                               choices=["cfg", "dfg", "tfg", "call_graph"])
    export_parser.add_argument("--output", "-o", default=None)

    # ---- dashboard ----
    dash_parser = subparsers.add_parser("dashboard", help="Launch dashboard dev server")
    dash_parser.add_argument("--port", type=int, default=5173)

    # ---- rules ----
    rules_parser = subparsers.add_parser("rules", help="List / manage verification rules")
    rules_parser.add_argument("action", nargs="?", default="list",
                              choices=["list", "info"])
    rules_parser.add_argument("--id", default=None, help="Rule ID for info")

    # ---- plugin ----
    plugin_parser = subparsers.add_parser("plugin", help="Plugin management")
    plugin_parser.add_argument("action", choices=["list", "install", "info"])
    plugin_parser.add_argument("--name", default=None)

    # ---- audit-deps ----
    audit_parser = subparsers.add_parser("audit-deps", help="Audit dependencies for CVEs")
    audit_parser.add_argument("file", nargs="?", default="requirements.txt",
                              help="Requirements file (default: requirements.txt)")

    args = parser.parse_args()

    # Disable metrics if requested
    if args.no_metrics:
        os.environ["CODESHIELD_METRICS"] = "off"

    if args.command == "serve":
        _cmd_serve(args)
    elif args.command == "verify":
        _cmd_verify(args)
    elif args.command == "style":
        _cmd_style(args)
    elif args.command == "scan-project":
        _cmd_scan_project(args)
    elif args.command == "explain":
        _cmd_explain(args)
    elif args.command in ("visualize", "export-graph"):
        _cmd_visualize(args)
    elif args.command == "dashboard":
        _cmd_dashboard(args)
    elif args.command == "rules":
        _cmd_rules(args)
    elif args.command == "plugin":
        _cmd_plugin(args)
    elif args.command == "audit-deps":
        _cmd_audit_deps(args)
    else:
        parser.print_help()
        sys.exit(1)

    # --- Always print metrics banner (unless --quiet or --no-metrics) ---
    if not getattr(args, "quiet", False) and not getattr(args, "no_metrics", False):
        try:
            from codeshield.utils.live_metrics import live, is_enabled
            if is_enabled() and live.total_runs > 0:
                print(live.banner(), file=sys.stderr)
        except Exception:
            pass


# ===================================================================
# Command implementations
# ===================================================================

def _cmd_serve(args):
    from codeshield.mcp.server import run_mcp_server
    run_mcp_server()


def _cmd_verify(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    code = path.read_text(encoding="utf-8")
    language = args.language

    if language is None:
        from codeshield.trustgate.engine.parser import detect_language
        lang_enum = detect_language(path.name)
        language = lang_enum.value if lang_enum else "python"

    if args.engine in ("v2", "auto"):
        try:
            from codeshield.trustgate.engine.executor import verify as engine_verify
            result = engine_verify(code, language=language, filename=path.name)
            if args.as_json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                _print_report(result, path.name)
            return
        except Exception:
            if args.engine == "v2":
                raise
            # fall through to v1

    from codeshield.trustgate.checker import verify_code
    result = verify_code(code)
    if args.as_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\n  File: {path.name}")
        print(f"  Valid: {result.is_valid}")
        print(f"  Confidence: {result.confidence_score:.0%}")
        for issue in result.issues:
            line_part = f"L{issue.line} " if issue.line else ""
            print(f"    [{issue.severity}] {line_part}{issue.message}")


def _cmd_style(args):
    from codeshield.styleforge.corrector import check_style
    result = check_style(args.file, args.codebase)
    print(result)


def _cmd_scan_project(args):
    from codeshield.trustgate.engine.executor import verify as engine_verify
    from codeshield.trustgate.engine.parser import detect_language

    root = Path(args.directory)
    if not root.is_dir():
        print(f"Error: not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    results = []
    total_findings = 0
    for ext in args.extensions:
        for fpath in root.rglob(f"*{ext}"):
            if any(part.startswith(".") for part in fpath.parts):
                continue
            if "node_modules" in fpath.parts or "__pycache__" in fpath.parts:
                continue
            try:
                code = fpath.read_text(encoding="utf-8", errors="replace")
                lang_enum = detect_language(fpath.name)
                lang = lang_enum.value if lang_enum else "python"
                r = engine_verify(code, language=lang, filename=fpath.name)
                results.append({"file": str(fpath.relative_to(root)), **r.to_dict()})
                total_findings += len(r.findings)
            except Exception as e:
                results.append({"file": str(fpath.relative_to(root)), "error": str(e)})

    if args.as_json:
        print(json.dumps({"files": results, "total_findings": total_findings}, indent=2))
    else:
        print(f"\n  CodeShield Project Scan: {root.resolve()}")
        print(f"  Files scanned: {len(results)}")
        print(f"  Total findings: {total_findings}\n")
        for r in results:
            status = "PASS" if r.get("is_valid", False) else "FAIL"
            n = len(r.get("findings", []))
            print(f"    [{status}] {r['file']}  ({n} findings)")
            for f in r.get("findings", [])[:3]:
                print(f"           [{f['severity']}] L{f.get('line', '?')}: {f['message']}")


def _cmd_explain(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    from codeshield.trustgate.engine.executor import verify as engine_verify
    from codeshield.trustgate.engine.parser import detect_language

    code = path.read_text(encoding="utf-8")
    lang_enum = detect_language(path.name)
    lang = lang_enum.value if lang_enum else "python"
    r = engine_verify(code, language=lang, filename=path.name)

    print(f"\n  Explanation for: {path.name}")
    print(f"  Language: {r.language}")
    print(f"  Valid: {r.is_valid}  |  Confidence: {r.confidence_score:.0%}")
    print(f"  Parse OK: {r.parse_ok}  |  Elapsed: {r.elapsed_ms:.1f}ms\n")
    if not r.findings:
        print("  No issues found. Code looks clean!\n")
    for f in r.findings:
        print(f"  [{f.severity.value.upper()}] Line {f.line}: {f.message}")
        if f.fix_hint:
            print(f"    Fix: {f.fix_hint}")
        print()


def _cmd_visualize(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    from codeshield.trustgate.engine.parser import parse_source, detect_language
    from codeshield.trustgate.engine.meta_ast import normalise
    from codeshield.trustgate.engine.graphs import (
        build_cfg, build_dfg, build_taint_graph, build_call_graph,
    )

    code = path.read_text(encoding="utf-8")
    lang_enum = detect_language(path.name)
    lang = lang_enum.value if lang_enum else "python"

    pr = parse_source(code, lang)
    meta = normalise(pr)
    builders = {"cfg": build_cfg, "dfg": build_dfg, "tfg": build_taint_graph, "call_graph": build_call_graph}
    graph = builders[args.graph](meta)

    data = {
        "graph_type": args.graph,
        "file": str(path),
        "language": lang,
        "nodes": [{"id": n.id, "label": n.label, "line": n.line} for n in graph.nodes.values()],
        "edges": [{"src": e.src, "dst": e.dst, "label": e.label} for e in graph.edges],
        "entry": graph.entry,
        "exit": graph.exit,
    }

    output = json.dumps(data, indent=2)
    if args.output:
        Path(args.output).write_text(output)
        print(f"Graph exported to {args.output}")
    else:
        print(output)


def _cmd_dashboard(args):
    import subprocess
    frontend = Path("frontend")
    if not frontend.exists():
        print("Error: frontend/ directory not found", file=sys.stderr)
        sys.exit(1)
    print(f"Starting dashboard on http://localhost:{args.port}")
    subprocess.run(["npm", "run", "dev", "--", "--port", str(args.port)], cwd="frontend")


def _cmd_rules(args):
    from codeshield.trustgate.engine.rules import load_builtin_rules
    rs = load_builtin_rules()
    if args.action == "list":
        print(f"\n  Verification Rules ({len(rs.rules)} loaded)\n")
        for r in rs.rules:
            langs = ", ".join(r.languages) if r.languages else "all"
            tags = ", ".join(r.tags) if r.tags else "-"
            print(f"    {r.id:<22} {r.severity.value:<8} langs={langs:<16} tags={tags}")
    elif args.action == "info" and args.id:
        rule = next((r for r in rs.rules if r.id == args.id), None)
        if rule:
            print(f"\n  Rule: {rule.id}")
            print(f"  Name: {rule.name}")
            print(f"  Severity: {rule.severity.value}")
            print(f"  Languages: {rule.languages or 'all'}")
            print(f"  Tags: {rule.tags}")
            print(f"  Enabled: {rule.enabled}\n")
        else:
            print(f"Rule '{args.id}' not found.")


def _cmd_plugin(args):
    from codeshield.plugins import get_registry
    registry = get_registry()

    if args.action == "list":
        plugins = registry.list_plugins()
        if not plugins:
            print("\n  No plugins installed.\n")
            print("  Place plugins in ~/.codeshield/plugins/ or install via entry-points.\n")
        else:
            print(f"\n  Installed Plugins ({len(plugins)})\n")
            for p in plugins:
                print(f"    {p['name']:<24} v{p['version']:<8} type={p['type']}")
    elif args.action == "install":
        print("  Plugin install via CLI is not yet available.")
        print("  Place your plugin folder with plugin.json in ~/.codeshield/plugins/\n")


def _cmd_audit_deps(args):
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")

    # Reuse the MCP dependency_audit logic inline
    import re
    insecure_db = {
        "pyyaml": ("< 5.4", "CVE-2020-14343 — arbitrary code execution via yaml.load"),
        "requests": ("< 2.20", "CVE-2018-18074 — session cookie leak"),
        "flask": ("< 1.0", "Multiple known vulnerabilities"),
        "django": ("< 3.2", "Security support ended"),
        "jinja2": ("< 2.11.3", "CVE-2020-28493 — ReDOS"),
        "urllib3": ("< 1.26.5", "CVE-2021-33503 — ReDOS"),
        "pillow": ("< 9.0", "Multiple buffer overflow CVEs"),
        "cryptography": ("< 3.3", "CVE-2020-36242 — integer overflow"),
        "paramiko": ("< 2.10", "CVE-2022-24302 — race condition"),
        "setuptools": ("< 65.5.1", "CVE-2022-40897 — ReDOS"),
    }

    lines = text.strip().splitlines()
    packages = []
    flagged = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z0-9_.-]+)", line)
        if match:
            name = match.group(1).lower()
            packages.append(name)
            if name in insecure_db:
                ver_req, reason = insecure_db[name]
                flagged.append((name, ver_req, reason))

    print(f"\n  Dependency Audit: {path.name}")
    print(f"  Packages found: {len(packages)}\n")
    if flagged:
        for name, ver_req, reason in flagged:
            print(f"    [WARN] {name} — {reason}")
            print(f"           Ensure version is NOT {ver_req}\n")
    else:
        print("  All packages look clean.\n")


# ===================================================================
# Helpers
# ===================================================================

def _print_report(report, filename: str):
    status = "PASS" if report.is_valid else "FAIL"
    print(f"\n  [{status}] {filename}")
    print(f"  Language: {report.language}")
    print(f"  Confidence: {report.confidence_score:.0%}")
    print(f"  Elapsed: {report.elapsed_ms:.1f}ms")
    if report.findings:
        print(f"  Findings ({len(report.findings)}):")
        for f in report.findings:
            print(f"    [{f.severity.value}] L{f.line}: {f.message}")
    else:
        print("  No issues found.")
    print()


if __name__ == "__main__":
    main()
