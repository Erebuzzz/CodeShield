# CodeShield

> **An intelligent security layer for AI-generated code.** CodeShield validates, formats, and secures code before it enters your production environment — powered by a tree-sitter-based multi-language engine, deterministic program-graph analysis, and a local-first architecture that minimises LLM costs.

[![PyPI](https://img.shields.io/pypi/v/codeshield-ai?color=blue)](https://pypi.org/project/codeshield-ai/)
[![npm](https://img.shields.io/npm/v/codeshield-mcp?color=red)](https://www.npmjs.com/package/codeshield-mcp)
[![Demo](https://img.shields.io/badge/Demo-Live-emerald)](https://codeshield-five.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-54%20passed-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Built for AI Vibe Coding Hackathon 2026** — *Stop getting betrayed by 90% correct code.*

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [What CodeShield Does](#what-codeshield-does)
- [Architecture](#architecture)
- [TrustGate v2 Engine](#trustgate-v2--multi-language-verification-engine)
- [StyleForge](#styleforge--convention-enforcement)
- [ContextVault](#contextvault--state-persistence)
- [Plugin System](#plugin-system)
- [SDK](#sdk--programmatic-api)
- [Live Metrics](#live-metrics--always-on-telemetry)
- [Token Efficiency](#token-efficiency--up-to-95-savings)
- [MCP Server](#mcp-server-18-tools)
- [CLI](#cli-commands)
- [REST API](#rest-api-endpoints)
- [Provider Stack](#provider-stack)
- [Dashboard](#dashboard)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Changelog](#changelog)

---

## Installation

### Python Package (pip)

```bash
pip install codeshield-ai
```

### MCP Server (npm/npx)

```bash
# Install globally
npm install -g codeshield-mcp

# Or run directly with npx
npx codeshield-mcp
```

### From Source

```bash
git clone https://github.com/Erebuzzz/CodeShield.git
cd CodeShield
pip install -e ".[dev]"
```

### Prerequisites
- Python 3.10+
- Node.js 18+ (for MCP server)

### Environment Variables

```bash
# .env
COMETAPI_KEY=sk-your-cometapi-key          # Primary LLM (critical tasks only)
NOVITA_API_KEY=sk_your-novita-key           # Secondary LLM
AIML_API_KEY=your-aiml-key                  # Free-tier embeddings & completions
OPENROUTER_API_KEY=your-openrouter-key      # Free power models
DAYTONA_API_KEY=dtn_your-daytona-key        # Sandbox execution
DAYTONA_API_URL=https://app.daytona.io/api
LEANMCP_KEY=leanmcp_your-key               # MCP observability
```

---

## Quick Start

### Python SDK (Recommended)

```python
from codeshield.sdk import verify, verify_file, scan_project, export_graph

# Verify a code string (v2 engine — tree-sitter powered)
result = verify("import os\nos.system(input())", language="python")
print(result["is_valid"])        # False
print(result["findings"])        # [shell_injection, taint_flow, ...]
print(result["confidence_score"])  # 0.4

# Verify a file on disk (auto-detects language)
result = verify_file("src/auth.py")

# Scan an entire project
report = scan_project("./src", extensions=[".py", ".js"])
print(f"{report['total_findings']} issues across {len(report['files'])} files")

# Export program graphs as JSON
cfg = export_graph("def f(x): return x + 1", graph_type="cfg")
dfg = export_graph("x = input(); eval(x)", graph_type="tfg")
```

### Legacy v1 API (AST-based)

```python
from codeshield import verify_code, check_style, full_verify

result = verify_code("print(x)", auto_fix=True)
print(f"Valid: {result.is_valid}")

style = check_style("def MyFunc(): pass", "./src")
print(style.conventions_detected)

result = full_verify("x = 1 + 2\nprint(x)")
print(result['overall_valid'])
```

### CLI

```bash
# Verify a single file
codeshield verify app.py --engine v2 --json

# Scan a whole project
codeshield scan-project ./src --extensions .py .js

# Export a control-flow graph
codeshield export-graph handler.py --graph cfg --output cfg.json

# Audit dependencies for CVEs
codeshield audit-deps requirements.txt

# List all verification rules
codeshield rules list
```

### MCP Tools (Claude/Cursor)

Once configured, **18 tools** are available:

```
verify_code · full_verify · check_style · save_context · restore_context
list_contexts · mcp_health · test_llm_connection · multi_language_verify
batch_verification · project_graph_export · dependency_audit
security_baseline_scan · policy_enforcement_check · rule_registry_access
dashboard_sync · language_plugin_install
```

---

## What CodeShield Does

CodeShield intercepts AI-generated code and ensures it's:

- **Safe** — Shell injection, taint flows, hardcoded secrets, eval attacks detected deterministically
- **Correct** — Syntax validated, missing imports detected and auto-fixed
- **Consistent** — Matches your codebase's naming conventions
- **Multi-Language** — Python and JavaScript via tree-sitter; plugin system for more
- **Efficient** — 70-95% token savings with local-first architecture
- **Observable** — Full metrics, dashboards, and provider cost tracking

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            CodeShield                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │              TrustGate v2 — Verification Engine                    │  │
│  │  tree-sitter → MetaAST → Program Graphs → Rule DSL → Executor    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐            │
│  │  TrustGate   │   │  StyleForge  │   │   ContextVault   │            │
│  │  v1 (Legacy) │   │   (Style)    │   │ (Memory+Autosave)│            │
│  └──────┬───────┘   └──────┬───────┘   └────────┬─────────┘            │
│         │                  │                     │                       │
│  ┌──────┴──────────────────┴─────────────────────┴──────────────────┐   │
│  │                      Plugin Registry                              │   │
│  │  Language · Rule · Analysis · Dashboard · Policy plugins          │   │
│  └──────────────────────────┬────────────────────────────────────────┘   │
│                             │                                            │
│         ┌───────────────────┼───────────────────────┐                   │
│         │                   │                       │                   │
│    ┌────▼─────┐     ┌──────▼──────┐         ┌──────▼──────┐           │
│    │   SDK    │     │  REST API   │         │ MCP Server  │           │
│    │ (import) │     │  (FastAPI)  │         │ (18 tools)  │           │
│    └──────────┘     └─────────────┘         └─────────────┘           │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  Provider Stack (cheapest-first routing):                                │
│  OpenRouter Free → AIML Free → Novita → CometAPI (critical only)        │
├──────────────────────────────────────────────────────────────────────────┤
│  Token Optimizer │ Metrics │ LeanMCP │ Daytona Sandbox │ Auto-Save      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Unified Processing Pipeline

Every code verification flows through the same 6-layer pipeline — no duplicated analysis:

| Layer | Component | Purpose |
|-------|-----------|---------|
| 1 | **tree-sitter Parser** | Multi-language concrete syntax tree |
| 2 | **MetaAST Normalizer** | Unified `MetaNode` representation (18 kinds) |
| 3 | **Program Graphs** | CFG, DFG, Taint Flow Graph, Call Graph |
| 4 | **Rule DSL** | 7 built-in rules, declarative matching |
| 5 | **Execution Engine** | Rule execution with SHA-256 caching |
| 6 | **Metrics Collector** | Latency, findings, provider costs |

---

## TrustGate v2 — Multi-Language Verification Engine

The v2 engine replaces Python `ast` with a tree-sitter-powered pipeline that works across languages.

### Supported Languages

| Language | Parser | Status |
|----------|--------|--------|
| Python | tree-sitter-python | Full support |
| JavaScript | tree-sitter-javascript | Full support |
| TypeScript | Plugin-ready | Planned |
| Rust | Plugin-ready | Planned |
| Go | Plugin-ready | Planned |

### Detection Rules (Built-in)

| Rule ID | Severity | Languages | What It Catches |
|---------|----------|-----------|-----------------|
| `shell_injection` | Critical | Python, JS | `eval()`, `exec()`, `os.system()`, `subprocess` with user input |
| `taint_flow` | Critical | Python, JS | Data flowing from `input()`/`stdin` to dangerous sinks |
| `hardcoded_secret` | Error | Python, JS | Passwords, API keys, tokens in source code |
| `type_mismatch` | Warning | Python | `str + int`, incompatible binary operations |
| `unused_import` | Warning | Python | Imported modules never referenced |
| `bare_except` | Warning | Python | `except:` without specific exception type |
| `unreachable_code` | Info | Python, JS | Code after `return`/`break` in CFG |

### Program Graphs

```python
from codeshield.sdk import export_graph

# Control Flow Graph
cfg = export_graph("if x > 0:\n  print(x)\nelse:\n  print(-x)", graph_type="cfg")

# Data Flow Graph (definitions & uses)
dfg = export_graph("x = 1\ny = x + 2", graph_type="dfg")

# Taint Flow Graph (sources → sinks)
tfg = export_graph("data = input()\neval(data)", graph_type="tfg")

# Call Graph
cg = export_graph("def a(): b()\ndef b(): c()\ndef c(): pass", graph_type="call_graph")
```

Each graph returns `{ nodes: [...], edges: [...], entry, exit }` — ready for visualization or further analysis.

### Engine Usage

```python
# Low-level engine access
from codeshield.trustgate.engine import verify, parse_source, build_cfg

# Full verification report
report = verify("import os\nos.system(input())", language="python")
print(report.is_valid)         # False
print(report.confidence_score) # 0.3
for f in report.findings:
    print(f"{f.severity}: {f.rule_id} at line {f.line} — {f.message}")

# Parse + build graph manually
tree = parse_source("x = 1; y = x + 2", "python")
from codeshield.trustgate.engine.meta_ast import normalise
meta = normalise(tree)
cfg = build_cfg(meta)
```

---

## StyleForge — Convention Enforcement

Analyzes your codebase to detect and enforce naming conventions:

| Feature | Description |
|---------|-------------|
| **Pattern Detection** | Automatically detects snake_case, camelCase, PascalCase |
| **Codebase Analysis** | Scans up to 50 files to determine dominant style |
| **Auto-Correction** | Converts names to match project conventions |
| **Typo Detection** | Finds similar existing names that might be typos |

```python
from codeshield.styleforge.corrector import check_style

code = """
def GetUserData(userName):
    totalValue = calculateTotal(userName)
    return totalValue
"""

result = check_style(code, codebase_path="./src")
print(result.conventions_detected)  # {'functions': 'snake_case', ...}
print(result.corrected_code)        # Uses snake_case throughout
```

**Supported Conventions:** `snake_case` · `camelCase` · `PascalCase` · `SCREAMING_SNAKE_CASE`

---

## ContextVault — State Persistence

Saves your development state like a game save file, with crash-safe auto-save:

| Feature | Description |
|---------|-------------|
| **State Capture** | Saves open files, cursor position, notes |
| **SQLite Storage** | Persistent local database |
| **Instant Restore** | One-click context restoration |
| **AI Briefing** | LLM-generated summary when restoring |
| **Auto-Save Failsafe** | `atexit` + signal hooks + background daemon |
| **Crash Recovery** | Periodic snapshots every 5 min (configurable) |

```python
from codeshield.contextvault.capture import save_context, list_contexts
from codeshield.contextvault.restore import restore_context

# Save state
save_context(
    name="auth-refactor",
    files=["src/auth.py", "tests/test_auth.py"],
    cursor={"file": "src/auth.py", "line": 42, "column": 10},
    notes="Fixing token expiration logic"
)

# Restore with AI briefing
result = restore_context("auth-refactor")
print(result["briefing"])  # "You were working on auth token logic..."

# Auto-save runs automatically — no setup needed
# Manual trigger available via API:
# POST /api/autosave/trigger
# GET  /api/autosave/latest
```

**Auto-Save Configuration (env vars):**
- `CODESHIELD_AUTOSAVE_INTERVAL` — Interval in seconds (default: 300)
- `CODESHIELD_MAX_AUTOSAVES` — Keep N most recent (default: 5)

---

## Plugin System

Extensible architecture supporting 5 plugin types:

| Type | Purpose | Example |
|------|---------|---------|
| **Language** | Add new language support | TypeScript parser + rules |
| **Rule** | Custom verification rules | Company-specific security policies |
| **Analysis** | Custom analysis passes | Complexity metrics, dead code |
| **Dashboard** | Dashboard widgets | Custom charts, status panels |
| **Policy** | Organizational policies | "No eval in production" |

### Registering a Plugin

```python
from codeshield.plugins import get_registry, RulePlugin, PluginType

# Register a custom rule plugin
registry = get_registry()
registry.register(RulePlugin(
    name="no-console-log",
    version="1.0.0",
    description="Disallow console.log in production code",
    plugin_type=PluginType.RULE,
    rules=[...],  # list of Rule objects
))

# Discover plugins from entry points & ~/.codeshield/plugins/
registry.discover_entrypoints()     # codeshield.plugins entry point group
registry.discover_directory()       # ~/.codeshield/plugins/
```

### Hook System

Plugins can register hooks that fire during the verification pipeline:

```python
from codeshield.plugins import HookEvent

# Available hooks:
# ON_PARSE, ON_NORMALIZE, ON_GRAPH_BUILD, ON_RULE_EXECUTE, ON_VIOLATION
```

---

## SDK — Programmatic API

The `codeshield.sdk` module provides a clean, high-level Python API:

```python
from codeshield.sdk import (
    verify,          # Verify code string
    verify_file,     # Verify a file on disk
    scan_project,    # Scan entire directory
    export_graph,    # Export CFG/DFG/TFG/call graph
    list_rules,      # Query rule registry
    audit_deps,      # Audit requirements.txt for CVEs
    get_dashboard,   # Get dashboard state
)

# Audit dependencies
report = audit_deps("requirements.txt")
print(f"{report['flagged']} packages with known CVEs out of {report['total']}")
for advisory in report["advisories"]:
    print(f"   {advisory['package']}: {advisory['advisory']}")

# List all rules (built-in + plugins)
for rule in list_rules():
    print(f"  [{rule['severity']}] {rule['id']} — {rule['name']}")
```

---

## Live Metrics — Always-On Telemetry

Metrics are **always on by default** — every verification, token call, and style check is tracked in real-time with zero performance overhead. No setup needed.

### How It Works

| Feature | Detail |
|---------|--------|
| **Hot path** | GIL-safe integer increments — no I/O, no locks, no DB writes |
| **Cold path** | Batched SQLite flush every 20 ops or 30 seconds (background thread) |
| **API responses** | Every JSON response includes a `_metrics` key automatically |
| **CLI** | Metrics banner printed after every command |
| **Overhead** | Near-zero — ~0.001ms per `record_verification()` call |

### API Response Example

Every API response automatically includes:

```json
{
  "is_valid": true,
  "confidence_score": 1.0,
  "_metrics": {
    "verifications": 42,
    "by_engine": { "v1": 5, "v2": 37 },
    "by_language": { "python": 30, "javascript": 12 },
    "findings": 18,
    "cache_hits": 15,
    "timing": { "avg_ms": 1.2, "fastest_ms": 0.3, "slowest_ms": 4.1 },
    "tokens": { "total": 1200, "saved": 48000, "savings_pct": 97.6, "cost_usd": 0.0012 },
    "uptime_s": 3600.0
  }
}
```

### CLI Banner

After every CLI command:

```
  [PASS] handler.py
  Language: python
  Confidence: 100%

[metrics] runs=42 | findings=18 | cache=15 | tokens=1200 | saved=98% | cost=$0.0012
```

### Turning It Off

```bash
# Environment variable
export CODESHIELD_METRICS=off

# CLI flag (per-command)
codeshield --quiet verify app.py        # suppress banner only
codeshield --no-metrics verify app.py    # disable tracking entirely
```

```python
# Python
from codeshield.utils.live_metrics import set_enabled
set_enabled(False)
```

```bash
# REST API toggle
curl -X POST http://localhost:8000/api/live-metrics/toggle \
  -H "Content-Type: application/json" -d '{"enabled": false}'
```

### Configuration (Environment Variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `CODESHIELD_METRICS` | `on` | Set to `off`/`0`/`false` to disable |
| `CODESHIELD_METRICS_FLUSH` | `30` | Seconds between SQLite flushes |
| `CODESHIELD_METRICS_FLUSH_OPS` | `20` | Operations between flushes |

### Dedicated Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/live-metrics` | Full metrics snapshot |
| `POST` | `/api/live-metrics/toggle` | Enable/disable (`{"enabled": false}`) |
| `POST` | `/api/live-metrics/reset` | Reset all counters |

---

## Token Efficiency — Up to 95% Savings

Local-first architecture minimizes LLM calls:

| Optimization | Savings | How It Works |
|-------------|---------|--------------|
| **v2 Engine (no LLM)** | 100% | All verification is deterministic — zero tokens |
| **Local Processing** | 100% | Fix common imports without LLM calls |
| **Prompt Compression** | 40-60% | Shorter prompts, same results |
| **Dynamic max_tokens** | 50-75% | Adaptive limits based on task |
| **Model Tiering** | 30-50% | Free/cheap models for simple tasks |
| **Response Caching** | 100% | SQLite cache + SHA-256 engine cache |
| **AST Diff Compression** | 60-80% | Only send changed graph nodes |

```python
from codeshield.utils.token_optimizer import LocalProcessor, get_token_optimizer

# Local fix (0 tokens!)
code = "x = json.loads(data)"
issues = ["Missing import: json"]
if LocalProcessor.can_fix_locally(code, issues):
    fixed = LocalProcessor.fix_locally(code, issues)

# Check efficiency stats
optimizer = get_token_optimizer()
stats = optimizer.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']}%")
print(f"Tokens saved: {stats['tokens_saved_by_cache']}")
```

---

## MCP Server (18 Tools)

### Configuration

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "codeshield": {
      "command": "npx",
      "args": ["codeshield-mcp"]
    }
  }
}
```

**Local Python MCP:**

```json
{
  "mcpServers": {
    "codeshield": {
      "command": "python",
      "args": ["-m", "codeshield.mcp.server"],
      "env": { "PYTHONPATH": "${workspaceFolder}/src" }
    }
  }
}
```

**LeanMCP (Production):**

```json
{
  "mcpServers": {
    "codeshield": {
      "url": "https://codeshield.leanmcp.link/mcp"
    }
  }
}
```

### Available Tools

| Tool | Category | Description |
|------|----------|-------------|
| `verify_code` | Core | Fast static analysis (v1) |
| `full_verify` | Core | Static + sandbox execution |
| `multi_language_verify` | Core | v2 engine verification (Python/JS) |
| `batch_verification` | Core | Verify multiple files at once |
| `check_style` | Style | Convention enforcement |
| `save_context` | Context | Save coding state |
| `restore_context` | Context | Restore with AI briefing |
| `list_contexts` | Context | List saved contexts |
| `project_graph_export` | Analysis | Export CFG/DFG/TFG/call graph |
| `dependency_audit` | Security | Audit requirements for CVEs |
| `security_baseline_scan` | Security | Security-focused code scan |
| `policy_enforcement_check` | Security | Check against org policy |
| `rule_registry_access` | Rules | List all verification rules |
| `dashboard_sync` | Dashboard | Sync dashboard state via MCP |
| `language_plugin_install` | Plugins | Install language support |
| `mcp_health` | Health | Server health check |
| `test_llm_connection` | Health | Test LLM provider connectivity |

---

## CLI Commands

```
codeshield <command> [options]
```

| Command | Description | Example |
|---------|-------------|---------|
| `serve` | Start MCP server | `codeshield serve --port 8080` |
| `verify` | Verify a file | `codeshield verify app.py --engine v2 --json` |

**Global flags:** `--quiet` (suppress metrics banner) · `--no-metrics` (disable tracking)
| `style` | Check code style | `codeshield style main.py --codebase ./src` |
| `scan-project` | Scan entire directory | `codeshield scan-project ./src -e .py .js` |
| `explain` | Explain verification findings | `codeshield explain handler.py` |
| `visualize` | Export program graph | `codeshield visualize app.py --graph cfg` |
| `export-graph` | Alias for visualize | `codeshield export-graph app.py -g dfg -o out.json` |
| `dashboard` | Launch dashboard dev server | `codeshield dashboard --port 5173` |
| `rules` | List/inspect rules | `codeshield rules list` |
| `plugin` | Plugin management | `codeshield plugin list` |
| `audit-deps` | Audit deps for CVEs | `codeshield audit-deps requirements.txt` |

---

## REST API Endpoints

### Core

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Server health check |
| `POST` | `/api/verify` | Verify code (v1/v2 auto-routing) |
| `POST` | `/api/verify/batch` | Batch verify multiple files |
| `POST` | `/api/style` | Check style conventions |

### Program Graphs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/graph/export` | Export CFG/DFG/TFG/call graph |

### Security

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/security/baseline` | Security baseline scan |

### Context

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/context/save` | Save context |
| `POST` | `/api/context/restore` | Restore context |
| `GET` | `/api/contexts` | List contexts |
| `GET` | `/api/autosave/latest` | Get latest auto-save |
| `POST` | `/api/autosave/trigger` | Trigger manual auto-save |

### Live Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/live-metrics` | Always-on metrics snapshot |
| `POST` | `/api/live-metrics/toggle` | Enable/disable metrics |
| `POST` | `/api/live-metrics/reset` | Reset all counters |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/state` | Full dashboard state |
| `GET` | `/api/dashboard/rules` | List all verification rules |
| `GET` | `/api/dashboard/plugins` | List installed plugins |

### Observability

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics` | Full metrics summary |
| `GET` | `/api/metrics/trustgate` | TrustGate stats |
| `GET` | `/api/metrics/styleforge` | StyleForge stats |
| `GET` | `/api/metrics/tokens` | Token usage |
| `GET` | `/api/tokens/efficiency` | Optimization stats |
| `POST` | `/api/tokens/budget` | Set token budget |
| `GET` | `/api/providers/status` | LLM provider status |
| `GET` | `/api/providers/test` | Test LLM connectivity |
| `GET` | `/api/integrations/status` | All integrations status |

---

## Provider Stack

CodeShield uses **cheapest-first routing** to stay within credit limits:

| Priority | Provider | Purpose | Cost |
|----------|----------|---------|------|
| 1 | **OpenRouter Free** | Explanations, summaries, rewrites | Free |
| 2 | **AIML Free** | Embeddings, cheap completions | Free |
| 3 | **Novita.ai** | Secondary LLM (cost-effective) | Low |
| 4 | **CometAPI** | Critical security tasks only | Credits |

**Free OpenRouter Models Used:**
- `arcee-ai/trinity-large-preview:free` — TrustGate explanations
- `google/gemini-2.0-flash-free` — StyleForge large rewrites
- `qwen/qwen2.5-coder:free` — Context restore summaries
- `deepseek/deepseek-r1:free` — Complex reasoning tasks

**Key Principle:** The v2 engine is **fully deterministic** — verification, graph generation, and rule matching use **zero tokens**. LLMs are only called for explanations, summaries, and AI briefings.

| Service | Credits | Strategy |
|---------|---------|----------|
| LeanMCP | 99 | MCP deployment |
| CometAPI | 3 | Critical tasks only |
| Daytona | 99 | Sandbox execution (static-first) |
| AIML | Free tier | Embeddings & completions |
| OpenRouter | Free models | Explanations & summaries |

---

## Dashboard

CodeShield includes backend endpoints for a full-featured dashboard:

**Planned frontend features:**
- Local repo scan results
- Program graph visualizer (CFG, DFG, TFG)
- Violations panel with severity filtering
- Rule editor / browser
- ContextVault snapshot browser
- Token efficiency charts
- Provider cost breakdown
- Sandbox execution viewer

**Current backend support:**
- `GET /api/dashboard/state` — Full state (rules, plugins, contexts, languages)
- `GET /api/dashboard/rules` — All rules with severity and tags
- `GET /api/dashboard/plugins` — Installed plugins
- `GET /api/metrics` — Live metrics (TrustGate, StyleForge, tokens, costs)

**Tech stack:** React · Tailwind · D3/vis.js (frontend) · SQLite · LeanMCP metrics (backend)

---

## Testing

```bash
# Run v2 engine tests (54 tests across 10 suites)
pytest tests/test_engine_multilang.py -v

# Run legacy test suites
pytest tests/test_trustgate.py -v
pytest tests/test_styleforge.py -v
pytest tests/test_comprehensive.py -v

# Run all tests
pytest tests/ -v

# Quick demo
python test_quick.py

# Token efficiency demo
python demo_token_efficiency.py
```

### Test Coverage (v2 Engine — 54 tests)

| Suite | Tests | Covers |
|-------|-------|--------|
| `TestPythonPass` | 8 | Clean Python: functions, classes, async, decorators |
| `TestPythonFail` | 10 | Shell injection, taint flow, hardcoded secrets, type mismatch |
| `TestJavaScriptPass` | 6 | Functions, arrows, classes, async/await, destructuring |
| `TestJavaScriptFail` | 3 | eval injection, syntax errors, hardcoded tokens |
| `TestParser` | 7 | Parse, detect language, error nodes |
| `TestMetaAST` | 3 | Function/call extraction, node kind mapping |
| `TestGraphs` | 5 | CFG entry/exit, DFG defs/uses, taint graph, call graph |
| `TestRules` | 3 | Built-in rules loaded, IDs, language filtering |
| `TestExecutor` | 4 | Report structure, caching, language detection |
| `TestEdgeCases` | 5 | Long code, unicode, mixed indent, deep nesting |

---

## Project Structure

```
CodeShield/
├── src/codeshield/
│   ├── __init__.py             # Package exports (v1 API)
│   ├── sdk.py                  # SDK — Programmatic Python API (v2)
│   ├── api_server.py           # FastAPI REST server (27 endpoints)
│   ├── cli.py                  # CLI (11 commands)
│   ├── trustgate/
│   │   ├── checker.py          # v1 — AST-based syntax/import checker
│   │   ├── sandbox.py          # Daytona sandbox integration
│   │   └── engine/             # v2 — tree-sitter verification engine
│   │       ├── parser.py       #   Multi-language tree-sitter parsing
│   │       ├── meta_ast.py     #   Unified MetaNode representation
│   │       ├── graphs.py       #   CFG, DFG, TFG, Call Graph builders
│   │       ├── rules.py        #   7 built-in rules + DSL
│   │       └── executor.py     #   Orchestrator with caching
│   ├── styleforge/
│   │   └── corrector.py        # Convention detection & correction
│   ├── contextvault/
│   │   ├── capture.py          # Save context snapshots
│   │   ├── restore.py          # Restore with AI briefing
│   │   └── autosave.py         # Crash-safe auto-save daemon
│   ├── plugins/
│   │   └── __init__.py         # Plugin registry (5 types, hooks)
│   │   └── __init__.py         # Plugin registry (5 types, hooks)
│   ├── mcp/
│   │   └── server.py           # FastMCP server (18 tools)
│   └── utils/
│       ├── llm.py              # Multi-provider LLM client
│       ├── metrics.py          # Statistics & observability (heavy, SQLite)
│       ├── live_metrics.py     # Always-on telemetry (zero-overhead)
│       ├── token_optimizer.py  # Token efficiency engine
│       ├── daytona.py          # Sandbox client
│       └── leanmcp.py          # LeanMCP observability
├── leanmcp/                    # LeanMCP TypeScript MCP Server
├── frontend/                   # React/TypeScript UI (Vercel)
├── tests/
│   ├── test_engine_multilang.py  # 54 v2 engine tests
│   ├── test_trustgate.py         # v1 TrustGate tests
│   ├── test_styleforge.py        # StyleForge tests
│   └── test_comprehensive.py     # Integration tests
├── npm/                        # npm package for MCP
├── pyproject.toml              # Python project config
├── Dockerfile                  # Container deployment
└── railway.toml                # Railway deployment config
```

---

## LeanMCP Deployment

CodeShield can be deployed to [LeanMCP Platform](https://ship.leanmcp.com) for production-grade MCP infrastructure:

```bash
# Deploy
cd leanmcp && npm install && leanmcp deploy .
```

Your MCP server will be live at `https://codeshield.leanmcp.link/mcp`

| Feature | Description |
|---------|-------------|
| **Edge Deployment** | Auto-scaling across 30+ global regions |
| **Built-in Monitoring** | Tool analytics, latency metrics, error tracking |
| **Zero DevOps** | No infrastructure to manage |
| **MCP Protocol** | Full support for Claude, Cursor, Windsurf |

---

## Roadmap

Based on the [CodeShield Master Plan](docs/DEVPOST_SUBMISSION.md):

- [x] TrustGate v2 engine (tree-sitter, MetaAST, program graphs)
- [x] 7 built-in detection rules (shell injection, taint flow, secrets, etc.)
- [x] Python + JavaScript support
- [x] Plugin architecture (5 types)
- [x] SDK with 7 public functions
- [x] 18 MCP tools
- [x] 11 CLI commands
- [x] Always-on live metrics (zero-overhead, auto-attach to responses)
- [x] 30 REST API endpoints
- [x] Auto-save crash recovery
- [x] 54 engine tests passing
- [ ] TypeScript language plugin
- [ ] Rust & Go language plugins
- [ ] Embedding-based ContextVault
- [ ] OpenRouter free model routing integration
- [ ] Dashboard frontend (graph visualizer, violations panel)
- [ ] Rule marketplace
- [ ] Policy manager
- [ ] Offline mode

---

## Built With

| Sponsor | Integration |
|---------|-------------|
| **[Daytona](https://daytona.io)** | Sandboxed code execution |
| **[LeanMCP](https://leanmcp.com)** | MCP observability platform |
| **[CometAPI](https://cometapi.com)** | Unified AI gateway |
| **[Novita.ai](https://novita.ai)** | Cost-effective inference |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Support

- [Documentation](https://codeshield-five.vercel.app/)
- [Issue Tracker](https://github.com/Erebuzzz/CodeShield/issues)
- [Discussions](https://github.com/Erebuzzz/CodeShield/discussions)

---

## Changelog

| Date | Version | Changes |
|------|---------|--------|
| 2026-02-07 | 0.5.0 | Always-on live metrics (zero-overhead telemetry, `_metrics` in every API response, CLI banner, toggle support); 3 new endpoints (`/api/live-metrics`, `/api/live-metrics/toggle`, `/api/live-metrics/reset`); `--quiet` and `--no-metrics` CLI flags |
| 2026-02-06 | 0.4.0 | Full README rewrite; SDK module (7 public functions); JS `hardcoded_secret` detection fix; 54 engine tests passing |
| 2026-02-05 | 0.3.0 | Platform expansion: plugin architecture (5 types), MCP server (18 tools), CLI (11 commands), auto-save crash recovery, dashboard backend, 27+ REST endpoints |
| 2026-02-04 | 0.2.0 | TrustGate v2 engine: tree-sitter parser, MetaAST normalizer, program graphs (CFG/DFG/TFG/call graph), 7 built-in rules, executor with SHA-256 caching; Python + JavaScript support |
| 2026-02-03 | 0.1.0 | Initial release: TrustGate v1 (AST-based), StyleForge, ContextVault, token optimizer, MCP server (6 tools), FastAPI backend, React frontend |

---

**CodeShield** — *Because AI-generated code should be verified, not trusted.*
