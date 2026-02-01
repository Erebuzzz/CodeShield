# CodeShield 🛡️

> **The Complete AI Coding Safety Net**  
> *AI code that works, matches your style, and remembers where you left off*

[![Hackathon](https://img.shields.io/badge/AI%20Vibe-Hackathon%202026-purple)](https://devpost.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io)

## The Problem

AI coding assistants give you **90% correct code** that wastes your time:

- ❌ Missing imports (`requests`, `json` not imported)
- ❌ Wrong variable names (`userName` instead of `user_name`)  
- ❌ Forgets your codebase conventions
- ❌ Syntax errors that look right
- ❌ You lose context when switching tasks

## The Solution: 3 Pillars

| Pillar | What It Does |
|--------|--------------|
| 🔒 **TrustGate** | Verifies code before you see it |
| 🎨 **StyleForge** | Enforces YOUR naming conventions |
| 🧠 **ContextVault** | Saves/restores your coding context |

## Quick Start

```bash
# Install
pip install -e .

# Verify some code
python -c "
from codeshield.trustgate.checker import verify_code
result = verify_code('''
def fetch():
    return requests.get(url)
''')
print(f'Valid: {result.is_valid}')
print(f'Issues: {[i.message for i in result.issues]}')
print(f'Fixed: {result.fixed_code}')
"
```

## Features

### 🔒 TrustGate

```python
from codeshield.trustgate.checker import verify_code
from codeshield.trustgate.sandbox import full_verification

# Quick check (static analysis)
result = verify_code(code, auto_fix=True)

# Full check (static + sandbox execution)
report = full_verification(code)
print(f"Confidence: {report['confidence_score']:.0%}")
```

**What it catches:**
- Missing imports → Auto-adds them
- Syntax errors → Reports exact line
- Runtime errors → Catches in sandbox

### 🎨 StyleForge

```python
from codeshield.styleforge.corrector import check_style

# Check code against your codebase conventions
result = check_style(code, codebase_path="./src")

# Fixes: userName → user_name
# Fixes: getUserData → get_user_data
```

### 🧠 ContextVault

```python
from codeshield.contextvault.capture import save_context
from codeshield.contextvault.restore import restore_context

# Save where you are
save_context(
    name="debugging-auth",
    files=["src/auth.py", "src/users.py"],
    notes="Working on login flow"
)

# Later, restore with AI briefing
result = restore_context("debugging-auth")
print(result["briefing"])  # "You were working on login flow..."
```

## MCP Integration

CodeShield works as an MCP server with Claude, Cursor, etc:

```json
{
  "mcpServers": {
    "codeshield": {
      "command": "python",
      "args": ["-m", "codeshield.mcp.server"]
    }
  }
}
```

**Available Tools:**
- `verify_code` - Check code for issues
- `full_verify` - Check + sandbox execution
- `check_style` - Enforce conventions
- `save_context` - Save coding state
- `restore_context` - Restore with briefing
- `list_contexts` - List saved contexts

## Built With

| Sponsor | Integration |
|---------|-------------|
| **Daytona** | Sandboxed code execution |
| **LeanMCP** | MCP server framework |
| **CometAPI** | Free AI models |
| **.cv Domains** | Developer identity |

## Demo

```bash
# Run the quick test
python test_quick.py

# Run sandbox test  
python test_sandbox.py
```

---

**Built for AI Vibe Coding Hackathon 2026**

*Stop getting betrayed by 90% correct code.*
