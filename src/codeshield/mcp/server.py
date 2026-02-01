"""
MCP Server - Main CodeShield MCP server

Exposes tools:
- verify_code: Verify code and return issues
- fix_code: Auto-fix code issues
- check_style: Check code against codebase conventions
- save_context: Save current coding context
- restore_context: Restore saved context
"""

import json
from typing import Any
from dataclasses import dataclass, asdict

# MCP protocol implementation
# Using a simple HTTP-based approach that works with LeanMCP


@dataclass
class MCPTool:
    """Definition of an MCP tool"""
    name: str
    description: str
    parameters: dict


@dataclass
class MCPResponse:
    """Response from an MCP tool"""
    success: bool
    result: Any
    error: Optional[str] = None


# Tool definitions
TOOLS = [
    MCPTool(
        name="verify_code",
        description="Verify Python code for syntax errors, missing imports, and other issues. Returns verification report with confidence score.",
        parameters={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to verify"
                },
                "auto_fix": {
                    "type": "boolean",
                    "description": "Whether to automatically fix issues",
                    "default": True
                }
            },
            "required": ["code"]
        }
    ),
    MCPTool(
        name="check_style",
        description="Check code against codebase conventions. Detects naming mismatches and suggests corrections.",
        parameters={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to check"
                },
                "codebase_path": {
                    "type": "string",
                    "description": "Path to codebase for convention extraction"
                }
            },
            "required": ["code"]
        }
    ),
    MCPTool(
        name="save_context",
        description="Save current coding context for later restoration.",
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name for this context snapshot"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of open file paths"
                },
                "cursor": {
                    "type": "object",
                    "description": "Current cursor position {file, line, column}"
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes about current work"
                }
            },
            "required": ["name"]
        }
    ),
    MCPTool(
        name="restore_context",
        description="Restore a previously saved coding context. Returns AI briefing of where you left off.",
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of context to restore"
                }
            },
            "required": ["name"]
        }
    ),
]


class CodeShieldMCPServer:
    """Main MCP server implementation"""
    
    def __init__(self):
        self.tools = {tool.name: tool for tool in TOOLS}
    
    def get_tools(self) -> list[dict]:
        """Get list of available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters
            }
            for tool in TOOLS
        ]
    
    def call_tool(self, name: str, arguments: dict) -> MCPResponse:
        """Call a tool by name with arguments"""
        if name not in self.tools:
            return MCPResponse(
                success=False,
                result=None,
                error=f"Unknown tool: {name}"
            )
        
        try:
            if name == "verify_code":
                return self._verify_code(arguments)
            elif name == "check_style":
                return self._check_style(arguments)
            elif name == "save_context":
                return self._save_context(arguments)
            elif name == "restore_context":
                return self._restore_context(arguments)
            else:
                return MCPResponse(
                    success=False,
                    result=None,
                    error=f"Tool not implemented: {name}"
                )
        except Exception as e:
            return MCPResponse(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _verify_code(self, args: dict) -> MCPResponse:
        """Verify code implementation"""
        from codeshield.trustgate.checker import verify_code
        
        code = args.get("code", "")
        auto_fix = args.get("auto_fix", True)
        
        result = verify_code(code, auto_fix=auto_fix)
        
        return MCPResponse(
            success=True,
            result=result.to_dict()
        )
    
    def _check_style(self, args: dict) -> MCPResponse:
        """Check style implementation"""
        from codeshield.styleforge.corrector import check_style
        
        code = args.get("code", "")
        codebase_path = args.get("codebase_path", ".")
        
        result = check_style(code, codebase_path)
        
        return MCPResponse(
            success=True,
            result=result
        )
    
    def _save_context(self, args: dict) -> MCPResponse:
        """Save context implementation"""
        from codeshield.contextvault.capture import save_context
        
        result = save_context(
            name=args.get("name", "default"),
            files=args.get("files", []),
            cursor=args.get("cursor"),
            notes=args.get("notes")
        )
        
        return MCPResponse(
            success=True,
            result=result
        )
    
    def _restore_context(self, args: dict) -> MCPResponse:
        """Restore context implementation"""
        from codeshield.contextvault.restore import restore_context
        
        result = restore_context(name=args.get("name", "default"))
        
        return MCPResponse(
            success=True,
            result=result
        )


# Server runner
def run_server(host: str = "localhost", port: int = 8080):
    """Run the MCP server"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    server = CodeShieldMCPServer()
    
    class MCPHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data)
            
            if self.path == "/tools":
                response = server.get_tools()
            elif self.path == "/call":
                tool_name = request.get("name")
                arguments = request.get("arguments", {})
                result = server.call_tool(tool_name, arguments)
                response = asdict(result)
            else:
                response = {"error": "Unknown endpoint"}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            elif self.path == "/tools":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(server.get_tools()).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    print(f"🛡️ CodeShield MCP Server starting on http://{host}:{port}")
    httpd = HTTPServer((host, port), MCPHandler)
    httpd.serve_forever()


# Add missing import
from typing import Optional
