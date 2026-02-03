# CodeShield

**Stop getting betrayed by 90% correct code.**

[![PyPI](https://img.shields.io/pypi/v/codeshield-ai?color=blue)](https://pypi.org/project/codeshield-ai/)
[![npm](https://img.shields.io/npm/v/codeshield-mcp?color=red)](https://www.npmjs.com/package/codeshield-mcp)
[![Demo](https://img.shields.io/badge/Demo-Live-emerald)](https://codeshield-five.vercel.app/)

---

## Inspiration

We asked real developers one brutal question: *"What do you honestly hate about coding with AI?"*

The responses hit hard:

> "It f***ing forgets even the variables which was used in the past and creates another variable!"

> "AI writes code to burn tokens. Humans write for efficiency."

> "Yesterday I saw it made classes as 'fonts' instead of 'font'. The guy who PR'd it got roasted in public."

> "Poor mapping. Poor interpretation. It just CAN'T SAY NO to anything!"

> "More output. Least money burnt. And for god's sake... STOP WITH THE NEON TEMPLATES!"

The pattern was clear: **90% of AI-generated code works perfectly. The other 10% ruins your entire day.**

Missing imports that break at runtime. Style chaos that makes PRs unreadable. Context that vanishes when you step away. And tokens burning on problems that don't need AI at all.

We're two students who got tired of this. So we built CodeShield.

---

## What it does

CodeShield is a **token-efficient verification layer** that sits between AI and your codebase. It catches the 10% before it betrays you.

**Three core modules:**

### 🛡️ TrustGate — Security Verification
- Detects missing imports using AST parsing
- Fixes 35+ common packages **locally** (zero tokens!)
- Confidence scoring to tell you how "sus" the code is
- Optional sandbox execution via Daytona for untrusted code

### 🎨 StyleForge — Convention Enforcement  
- Scans YOUR codebase to learn YOUR conventions
- Detects snake_case, camelCase, PascalCase patterns
- Converts AI's style chaos to match your project
- Typo detection using Levenshtein distance (catches `usre` → `user`)

### 💾 ContextVault — State Persistence
- Save your coding session like a video game checkpoint
- Stores files, cursor position, open tabs, notes
- AI-generated briefings when you restore
- Never lose context after lunch again

### ⚡ Token Efficiency — 90% Savings
We obsessed over not wasting money:

| Optimization | Savings |
|-------------|---------|
| Local Processing | 100% (no API call) |
| Response Caching | 100% (duplicate requests) |
| Prompt Compression | 40-60% |
| Dynamic `max_tokens` | 50-75% |
| Model Tiering | 30-50% |

Missing `import json`? That's not a 500-token problem. That's a string concatenation we handle locally.

---

## How we built it

### Backend (Python)
- **FastAPI** for the REST API server (hosted on Railway)
- **MCP SDK** for Model Context Protocol integration
- **AST module** for parsing Python code and detecting imports
- **SQLite** for metrics, caching, and context persistence
- **httpx** for async HTTP to LLM providers

### Frontend (React + TypeScript)
- **Vite** for blazing fast builds
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Monaco-inspired** code editor component

### Integrations (All 5 Required — Server-Side)
All API keys are stored on our backend. **Clients need zero configuration.**

- **CometAPI** — Primary LLM access (100+ models, one API)
- **Novita.ai** — Secondary provider with automatic failover
- **AIML API** — Tertiary fallback (belt AND suspenders)
- **Daytona** — Sandbox execution for untrusted code
- **LeanMCP** — MCP deployment platform with observability

### MCP Server
Available as npm package (`npx codeshield-mcp`) — connects to our hosted backend:
- `verify_code` — Quick validation
- `full_verify` — With sandbox execution (Daytona)
- `check_style` — Convention analysis
- `save_context` / `restore_context` / `list_contexts`

**No API keys required for clients.** Just install and use.

### Token Optimization Pipeline
```
Request → LocalProcessor → Cache Check → Prompt Compression → Model Selection → Response
            ↓                  ↓
      (fixes imports)    (returns cached)
       zero tokens        zero tokens
```

---

## Challenges we ran into

### AST Complexity
Python's AST module is powerful but unforgiving. Handling edge cases like:
- Conditional imports (`if TYPE_CHECKING:`)
- Dynamic imports (`importlib.import_module()`)
- Star imports (`from module import *`)
- Relative vs absolute imports

We ended up building a comprehensive import map for 35+ packages with all their common attributes.

### Style Detection Accuracy
Detecting naming conventions sounds simple until you realize:
- Mixed conventions in real codebases
- Framework-specific patterns (Django's `get_queryset` vs standard `get_query_set`)
- Abbreviations and acronyms (is `getHTTPResponse` correct?)

We settled on majority-voting: scan the codebase, count patterns, enforce the dominant style.

### Context Window Optimization
How much context is "enough"? Too little and the AI hallucinates. Too much and you burn tokens.

We built dynamic `max_tokens` calculation based on task complexity:
- Simple import fix: 100 tokens max
- Style correction: 200 tokens max  
- Complex refactor: Let the model decide

### Making Caching Actually Work
Cache invalidation is one of the two hard problems in computer science. We hash:
- The code content
- The operation type
- The style context

Same request twice? Instant response, zero cost.

### MCP Protocol Learning Curve
MCP is powerful but documentation was sparse when we started. We had to:
- Read the FastMCP source code
- Experiment with tool schemas
- Debug weird serialization issues
- Figure out proper error handling

LeanMCP's observability saved us here—we could actually see what was happening.

---

## Accomplishments that we're proud of

- **Published to PyPI & npm** — `pip install codeshield-ai` / `npx codeshield-mcp`
- **70 unit tests, all passing** — We tested our own code. Revolutionary.
- **35+ imports handled locally** — The greatest hits of Python packages
- **90% token savings measured** — Not a marketing number, actual benchmarks
- **6 MCP tools** — Full integration with Claude and Cursor
- **3 LLM providers with failover** — Primary goes down? We keep working.
- **Sub-100ms local fixes** — Instant feedback for common issues
- **Real user research** — We didn't guess the problems, we asked
- **Working live demo** — codeshield-five.vercel.app (it actually works!)

---

## What we learned

### Token cost is a product constraint, not an optimization
Every API call costs money. When you're a student, that matters. We learned to ask "does this NEED AI?" before every feature.

### The biggest UX win is reducing loops
Developers don't want more buttons. They want fewer steps. One verification that catches everything beats three separate tools.

### Code intelligence is 90% edge cases
The happy path is easy. Real codebases have weird imports, inconsistent styles, and legacy patterns. Handling those gracefully is the real work.

### Smart defaults make demos magical
When the live demo "just works," it's because we obsessed over sensible defaults. No configuration needed for common cases.

### MCP is the future of AI tooling
Direct integration with Claude/Cursor through MCP feels like magic. The AI can verify its own code before giving it to you. Meta, but powerful.

---

## What's next for CodeShield

- **Language expansion** — JavaScript/TypeScript support (AST parsing with tree-sitter)
- **IDE extensions** — VS Code extension for inline verification
- **Team features** — Shared style configurations across projects
- **Smarter caching** — Semantic similarity for near-duplicate requests
- **Custom import maps** — Let users define their own package patterns
- **CI/CD integration** — Verify AI-generated PRs automatically
- **Fine-tuned models** — Train on common fix patterns for even faster local processing

---

## Installation

### MCP Server (for Claude/Cursor)
**Zero configuration required** — just install and use:

```bash
npx codeshield-mcp
```

Claude Desktop config (`claude_desktop_config.json`):
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

That's it. No API keys needed. The MCP server connects to our hosted backend which handles all the integrations (Daytona, LLM providers, etc.).

### Python Library
```bash
pip install codeshield-ai
```

```python
from codeshield import verify_code, check_style

result = verify_code("print(x)", auto_fix=True)
print(result.is_valid)
```

---

## Built With

- Python
- FastAPI
- MCP SDK
- React
- TypeScript
- Vite
- Tailwind CSS
- SQLite
- CometAPI
- Novita.ai
- AIML API
- Daytona
- LeanMCP
- Railway (hosting)

---

## Links

- **Live Demo:** [codeshield-five.vercel.app](https://codeshield-five.vercel.app)
- **GitHub:** [github.com/Erebuzzz/CodeShield](https://github.com/Erebuzzz/CodeShield)
- **PyPI:** [pypi.org/project/codeshield-ai](https://pypi.org/project/codeshield-ai/)
- **npm:** [npmjs.com/package/codeshield-mcp](https://www.npmjs.com/package/codeshield-mcp)

---

*CodeShield: Verify, don't trust.*
