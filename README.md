# CodeShield 🛡️

> **The Complete AI Coding Safety Net**  
> *AI code that works, matches your style, and remembers where you left off*

## What is CodeShield?

CodeShield is an MCP server that protects you from the "90% correct" AI code trap:

| Problem | CodeShield Solution |
|---------|---------------------|
| Code doesn't compile | **TrustGate** verifies before you see it |
| Wrong variable names | **StyleForge** enforces YOUR conventions |
| Forget where you left off | **ContextVault** saves your mental state |

## Features

### 🔒 TrustGate - Verification Before Acceptance
- Runs AI code in sandbox before you see it
- Catches missing imports, syntax errors, type issues
- Auto-fixes simple problems
- Shows confidence score

### 🎨 StyleForge - Convention Enforcement  
- Learns YOUR codebase patterns
- Corrects `userName` → `user_name` automatically
- Uses existing variables, not new ones
- Prevents "fonts" vs "font" mistakes

### 🧠 ContextVault - Context Memory
- Saves your coding state like a game save
- "You were debugging auth at line 47"
- Restores files, cursor position, mental context

## Quick Start

```bash
# Install
pip install codeshield

# Run MCP server
codeshield serve

# Or use with Claude/Cursor
# Add to your MCP config
```

## Built With

- **LeanMCP** - MCP server framework
- **Daytona** - Sandboxed code execution
- **CometAPI** - Free AI models
- **.cv Domains** - Developer identity

## Built for AI Vibe Coding Hackathon 2026

---

**Stop getting betrayed by 90% correct code.**
