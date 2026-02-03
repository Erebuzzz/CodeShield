# CodeShield MCP Server

MCP (Model Context Protocol) server for CodeShield - The Complete AI Coding Safety Net.

## Installation

```bash
npm install -g codeshield-mcp
```

Or run directly with npx:

```bash
npx codeshield-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/.config/claude/claude_desktop_config.json` on Mac/Linux or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

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

## Available Tools

### `verify_code`
Verify code for syntax errors, security issues, and best practices.

### `full_verify`
Full verification with sandbox execution in an isolated environment.

### `check_style`
Check code style against codebase conventions.

### `save_context`
Save current coding context for later restoration.

### `restore_context`
Restore a previously saved coding context.

### `list_contexts`
List all saved coding contexts.

## Environment Variables

- `CODESHIELD_API_URL` - Override the backend API URL (default: https://codeshield-production.up.railway.app)

## License

MIT
