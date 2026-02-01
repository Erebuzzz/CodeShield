# CodeShield

An intelligent security layer for AI-generated code. CodeShield validates, formats, and secures code before it enters your production environment, acting as a firewall for your development workflow.

[View Demo](https://codeshield-five.vercel.app/)

## Capabilities

### TrustGate
Validates generated code in an isolated sandbox environment. It detects potential security vulnerabilities, resource exhaustion, and malicious patterns through static analysis and runtime execution.

### StyleForge
Analyzes your existing codebase to detect and enforce naming conventions. It automatically adapts new code to match your project's snake_case, camelCase, or PascalCase patterns.

### ContextVault
Persists your development state including open files, cursor positions, and notes. Allows for instant context restoration when switching between tasks.

## Installation

```bash
pip install -e .
```

## Python API Usage

### Security Verification
```python
from codeshield.trustgate.checker import verify_code

code = """
def fetch_data(url):
    return requests.get(url) 
"""

# Detects missing imports and potential errors
result = verify_code(code, auto_fix=True)
print(result.fixed_code)
```

### Style Enforcement
```python
from codeshield.styleforge.corrector import check_style

# Enforces project-specific conventions
result = check_style(
    code="def GetUserData(): pass", 
    codebase_path="./src"
)
# Output: def get_user_data(): pass
```

### Context Management
```python
from codeshield.contextvault.capture import save_context

save_context(
    name="auth-refactor",
    files=["src/auth.py", "tests/test_auth.py"],
    notes="fixing token expiration logic"
)
```

## Model Context Protocol (MCP)

CodeShield exposes its functionality to AI assistants via MCP. Add the following configuration to your MCP settings file:

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

## Development

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Run tests: `pytest`
4. Start frontend: `cd frontend && npm run dev`

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
