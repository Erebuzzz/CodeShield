# CodeShield

> **An intelligent security layer for AI-generated code.** CodeShield validates, formats, and secures code before it enters your production environment, acting as a firewall for your development workflow.

[![PyPI](https://img.shields.io/pypi/v/codeshield-ai?color=blue)](https://pypi.org/project/codeshield-ai/)
[![npm](https://img.shields.io/npm/v/codeshield-mcp?color=red)](https://www.npmjs.com/package/codeshield-mcp)
[![Demo](https://img.shields.io/badge/Demo-Live-emerald)](https://codeshield-five.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Built for AI Vibe Coding Hackathon 2026** — *Stop getting betrayed by 90% correct code.*

---

## 📦 Installation

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

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

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

---

## 🚀 Quick Start

### Python Usage

```python
from codeshield import verify_code, check_style, full_verify

# Quick syntax & import verification
result = verify_code("print(x)", auto_fix=True)
print(f"Valid: {result.is_valid}")
print(f"Issues: {result.issues}")

# Style checking against your codebase
style = check_style("def MyFunc(): pass", "./src")
print(style.conventions_detected)

# Full sandbox verification (with Daytona if available)
result = full_verify("x = 1 + 2\nprint(x)")
print(result['overall_valid'])
```

### MCP Tools (Claude/Cursor)

Once configured, you can use these tools in Claude:

- **verify_code** - Fast static analysis
- **full_verify** - Static + sandbox execution  
- **check_style** - Convention enforcement
- **save_context** - Save coding state
- **restore_context** - Restore with AI briefing

---

## 🎯 What CodeShield Does

CodeShield intercepts AI-generated code and ensures it's:
- **Safe** — No malicious imports, infinite loops, or dangerous operations
- **Correct** — Syntax validated, missing imports detected and auto-fixed
- **Consistent** — Matches your codebase's naming conventions
- **Efficient** — Optimized token usage with caching and local processing

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CodeShield                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐    │
│  │  TrustGate   │   │  StyleForge  │   │   ContextVault   │    │
│  │  (Security)  │   │   (Style)    │   │    (Memory)      │    │
│  └──────┬───────┘   └──────┬───────┘   └────────┬─────────┘    │
│         │                  │                     │               │
│         └──────────────────┼─────────────────────┘               │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │   LLM Client    │                           │
│                   │  (Multi-Provider)│                          │
│                   └────────┬────────┘                           │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                 │
│         │                  │                  │                 │
│    ┌────▼────┐       ┌─────▼─────┐     ┌─────▼─────┐          │
│    │CometAPI │       │ Novita.ai │     │ AIML API  │          │
│    │(Primary)│       │(Secondary)│     │(Fallback) │          │
│    └─────────┘       └───────────┘     └───────────┘          │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Token Optimizer │ Metrics Collector │ LeanMCP │ Daytona       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Core Features

### 🛡️ TrustGate — Security Verification

Validates generated code in an isolated sandbox environment:

| Feature | Description |
|---------|-------------|
| **Syntax Validation** | AST parsing to catch syntax errors before execution |
| **Import Detection** | Identifies missing imports with auto-fix capability |
| **Undefined Names** | Detects potentially undefined variables |
| **Sandbox Execution** | Runs code in Daytona's isolated environment |
| **Confidence Scoring** | 0-100% confidence score based on issue severity |
| **Auto-Fix** | Automatically adds missing imports |

```python
from codeshield.trustgate.checker import verify_code

code = """
def fetch_data(url):
    return requests.get(url).json()
"""

result = verify_code(code, auto_fix=True)
print(f"Valid: {result.is_valid}")           # False (missing import)
print(f"Confidence: {result.confidence_score:.0%}")  # 80%
print(result.fixed_code)                     # Includes 'import requests'
```

**Detection Capabilities:**
- ❌ Missing standard library imports (os, json, re, etc.)
- ❌ Missing third-party imports (requests, numpy, pandas, etc.)
- ❌ Syntax errors (missing colons, unmatched brackets)
- ❌ Indentation errors
- ❌ Undefined variable usage

---

### 🎨 StyleForge — Convention Enforcement

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

**Supported Conventions:**
- `snake_case` — Python standard (PEP 8)
- `camelCase` — JavaScript/Java style
- `PascalCase` — Class names
- `SCREAMING_SNAKE_CASE` — Constants

---

### 💾 ContextVault — State Persistence

Saves your development state like a game save file:

| Feature | Description |
|---------|-------------|
| **State Capture** | Saves open files, cursor position, notes |
| **SQLite Storage** | Persistent local database |
| **Instant Restore** | One-click context restoration |
| **AI Briefing** | LLM-generated summary when restoring |

```python
from codeshield.contextvault.capture import save_context, list_contexts
from codeshield.contextvault.restore import restore_context

# Save current state
save_context(
    name="auth-refactor",
    files=["src/auth.py", "tests/test_auth.py"],
    cursor={"file": "src/auth.py", "line": 42, "column": 10},
    notes="Fixing token expiration logic"
)

# List all contexts
contexts = list_contexts()

# Restore with AI briefing
result = restore_context("auth-refactor")
print(result["briefing"])  # "You were working on auth token logic..."
```

---

### ⚡ Token Efficiency — Up to 90% Savings

Advanced optimization system to minimize LLM token usage:

| Optimization | Savings | How It Works |
|-------------|---------|--------------|
| **Local Processing** | 100% | Fix common imports without LLM calls |
| **Prompt Compression** | 40-60% | Shorter prompts, same results |
| **Dynamic max_tokens** | 50-75% | Adaptive limits based on task |
| **Model Tiering** | 30-50% | Cheap models for simple tasks |
| **Response Caching** | 100% | SQLite cache for repeated requests |

```python
from codeshield.utils.token_optimizer import LocalProcessor, get_token_optimizer

# Local fix (0 tokens!)
code = "x = json.loads(data)"
issues = ["Missing import: json"]

if LocalProcessor.can_fix_locally(code, issues):
    fixed = LocalProcessor.fix_locally(code, issues)
    # Result: "import json\nx = json.loads(data)"
    # Tokens used: 0

# Check efficiency stats
optimizer = get_token_optimizer()
stats = optimizer.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']}%")
print(f"Tokens saved: {stats['tokens_saved_by_cache']}")
```

**Supported Local Fixes (35+ imports):**
`json`, `os`, `sys`, `re`, `math`, `random`, `datetime`, `time`, `pathlib`, `typing`, `dataclasses`, `collections`, `itertools`, `functools`, `requests`, `httpx`, `asyncio`, `logging`, `subprocess`, `tempfile`, `shutil`, `glob`, `csv`, `sqlite3`, `hashlib`, `base64`, `copy`, `io`, `threading`, `uuid`, `enum`, `abc`, `contextlib`, `pydantic`, `fastapi`, `flask`, `numpy`, `pandas`, `pytest`

---

### 📊 Metrics & Observability

Real-time, transparent statistics tracking:

```python
from codeshield.utils.metrics import get_metrics

metrics = get_metrics()
summary = metrics.get_summary()

# TrustGate metrics
print(f"Detection rate: {summary['trustgate']['detection_rate']}%")
print(f"Fix success rate: {summary['trustgate']['fix_success_rate']}%")
print(f"Sandbox success rate: {summary['trustgate']['sandbox_success_rate']}%")

# Token metrics
print(f"Token efficiency: {summary['tokens']['token_efficiency']}")
print(f"Estimated cost: ${summary['tokens']['estimated_cost_usd']}")
```

**Tracked Metrics:**
- TrustGate: verifications, detections, fixes, sandbox results
- StyleForge: checks, conventions detected, corrections
- ContextVault: saves, restores, success rates
- Tokens: input/output, efficiency ratio, cost estimates

---

## 🔌 Integrations

CodeShield requires these services for full functionality:

| Service | Purpose | Environment Variable |
|---------|---------|---------------------|
| **[CometAPI](https://apidoc.cometapi.com/)** | Primary LLM (100+ models) | `COMETAPI_KEY` |
| **[Novita.ai](https://novita.ai/docs)** | Secondary LLM (cost-effective) | `NOVITA_API_KEY` |
| **[AIML API](https://aimlapi.com/)** | Fallback LLM | `AIML_API_KEY` |
| **[Daytona](https://daytona.io/docs)** | Sandbox execution | `DAYTONA_API_KEY`, `DAYTONA_API_URL` |
| **[LeanMCP](https://docs.leanmcp.com/)** | MCP deployment & observability | See [LeanMCP Deployment](#-leanmcp-deployment) |

---

## 🌐 LeanMCP Deployment

CodeShield can be deployed to [LeanMCP Platform](https://ship.leanmcp.com) for production-grade MCP infrastructure with built-in observability.

### Quick Deploy

```bash
# Install LeanMCP CLI
npm install -g @leanmcp/cli

# Login to LeanMCP
leanmcp login

# Deploy CodeShield MCP Server
cd leanmcp
npm install
leanmcp deploy .
```

Your MCP server will be live at `https://codeshield.leanmcp.link/mcp`

### What You Get

| Feature | Description |
|---------|-------------|
| **Edge Deployment** | Auto-scaling across 30+ global regions |
| **Built-in Monitoring** | Tool analytics, latency metrics, error tracking |
| **Zero DevOps** | No infrastructure to manage |
| **MCP Protocol** | Full support for Claude, Cursor, Windsurf, etc. |

### Architecture

```
MCP Clients → LeanMCP Platform → CodeShield TypeScript MCP → Python Backend
              (Edge Deployment)   (leanmcp/ folder)          (api_server.py)
```

### Connect Your MCP Client

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "codeshield": {
      "url": "https://codeshield.leanmcp.link/mcp"
    }
  }
}
```

See [leanmcp/README.md](leanmcp/README.md) for full deployment documentation

---

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install codeshield-ai
```

### From Source

```bash
# Clone repository
git clone https://github.com/Erebuzzz/CodeShield.git
cd CodeShield

# Install in development mode
pip install -e .
```

### MCP Server Setup

```bash
# Install the MCP server globally
npm install -g codeshield-mcp

# Or use npx (no install needed)
npx codeshield-mcp
```

### Prerequisites
- Python 3.10+
- Node.js 18+ (for MCP server)

### Environment Variables

```bash
# .env
COMETAPI_KEY=sk-your-cometapi-key
NOVITA_API_KEY=sk_your-novita-key
AIML_API_KEY=your-aiml-key
DAYTONA_API_KEY=dtn_your-daytona-key
DAYTONA_API_URL=https://app.daytona.io/api
LEANMCP_KEY=leanmcp_your-key
```

---

## 📖 Usage

### Python API

```python
# Security verification
from codeshield.trustgate.checker import verify_code
result = verify_code("print('hello')", auto_fix=True)

# Full sandbox verification
from codeshield.trustgate.sandbox import full_verification
result = full_verification("print('hello')")

# Style checking
from codeshield.styleforge.corrector import check_style
result = check_style("def MyFunc(): pass", "./src")

# Context management
from codeshield.contextvault.capture import save_context
save_context(name="my-task", files=["main.py"])
```

### REST API

```bash
# Start server
python -m uvicorn codeshield.api_server:app --reload

# Verify code
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "print(x)", "auto_fix": true}'

# Check style
curl -X POST http://localhost:8000/api/style \
  -H "Content-Type: application/json" \
  -d '{"code": "def MyFunc(): pass", "codebase_path": "."}'

# Get metrics
curl http://localhost:8000/api/metrics

# Get token efficiency
curl http://localhost:8000/api/tokens/efficiency
```

### MCP Server (Claude/Cursor)

**Option 1: npm package (Recommended)**

Add to your MCP settings (`claude_desktop_config.json`):

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

**Option 2: Local Python server**

Add to your MCP settings:

```json
{
  "mcpServers": {
    "codeshield": {
      "command": "python",
      "args": ["-m", "codeshield.mcp.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `verify_code` | Fast static analysis |
| `full_verify` | Static + sandbox execution |
| `check_style` | Convention enforcement |
| `save_context` | Save coding state |
| `restore_context` | Restore with AI briefing |
| `list_contexts` | List saved contexts |
| `mcp_health` | Server health check |
| `test_llm_connection` | Test LLM providers |

---

## 🧪 Testing

```bash
# Run all tests (70 tests)
pytest tests/ -v

# Run specific test suites
pytest tests/test_trustgate.py -v
pytest tests/test_styleforge.py -v
pytest tests/test_comprehensive.py -v

# Quick demo
python test_quick.py

# Token efficiency demo
python demo_token_efficiency.py
```

---

## 📁 Project Structure

```
CodeShield/
├── src/codeshield/
│   ├── trustgate/          # Security verification
│   │   ├── checker.py      # Syntax, import, undefined detection
│   │   └── sandbox.py      # Daytona sandbox integration
│   ├── styleforge/         # Style enforcement
│   │   └── corrector.py    # Convention detection & correction
│   ├── contextvault/       # State persistence
│   │   ├── capture.py      # Save context
│   │   └── restore.py      # Restore with briefing
│   ├── mcp/                # MCP server (Python)
│   │   └── server.py       # FastMCP implementation
│   ├── utils/
│   │   ├── llm.py          # Multi-provider LLM client
│   │   ├── metrics.py      # Statistics tracking
│   │   ├── token_optimizer.py  # Token efficiency
│   │   ├── daytona.py      # Sandbox client
│   │   └── leanmcp.py      # Observability client
│   ├── api_server.py       # FastAPI HTTP server
│   └── cli.py              # Command-line interface
├── leanmcp/                # LeanMCP TypeScript MCP Server
│   ├── main.ts             # Entry point
│   ├── leanmcp.config.js   # Deployment config
│   └── mcp/                # MCP services
│       ├── verification/   # TrustGate tools
│       ├── styleforge/     # Style tools
│       ├── contextvault/   # Context tools
│       └── health/         # Health & metrics
├── frontend/               # React/TypeScript UI
├── tests/                  # Comprehensive test suite
└── examples/               # Sample code
```

---

## 🔧 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Server health check |
| `POST` | `/api/verify` | Verify code |
| `POST` | `/api/style` | Check style conventions |
| `POST` | `/api/context/save` | Save context |
| `POST` | `/api/context/restore` | Restore context |
| `GET` | `/api/contexts` | List contexts |

### Observability Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics` | Full metrics summary |
| `GET` | `/api/metrics/trustgate` | TrustGate stats |
| `GET` | `/api/metrics/styleforge` | StyleForge stats |
| `GET` | `/api/metrics/tokens` | Token usage |
| `GET` | `/api/tokens/efficiency` | Optimization stats |
| `GET` | `/api/providers/status` | LLM provider status |
| `GET` | `/api/providers/test` | Test LLM connectivity |
| `GET` | `/api/integrations/status` | All integrations status |

---

## 🤝 Built With

| Sponsor | Integration |
|---------|-------------|
| **[Daytona](https://daytona.io)** | Sandboxed code execution |
| **[LeanMCP](https://leanmcp.com)** | MCP observability platform |
| **[CometAPI](https://cometapi.com)** | Unified AI gateway |
| **[Novita.ai](https://novita.ai)** | Cost-effective inference |

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙋 Support

- 📖 [Documentation](https://codeshield-five.vercel.app/)
- 🐛 [Issue Tracker](https://github.com/Erebuzzz/CodeShield/issues)
- 💬 [Discussions](https://github.com/Erebuzzz/CodeShield/discussions)

---

**CodeShield** — *Because AI-generated code should be verified, not trusted.*
