"""
MCP Server - Proper FastMCP implementation

Uses the official MCP Python SDK (FastMCP) to expose CodeShield tools
as a proper MCP server that integrates with Claude, Cursor, etc.
"""

from typing import Optional, Any
import json

# Try to import FastMCP, fallback to simple HTTP if not available
try:
    from mcp.server.fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False
    FastMCP = None


def create_mcp_server():
    """Create and configure the CodeShield MCP server"""
    
    if not HAS_FASTMCP:
        raise ImportError(
            "MCP SDK not installed. Run: pip install mcp"
        )
    
    # Create FastMCP server
    mcp = FastMCP("CodeShield")
    
    # ============================================
    # TOOL: verify_code
    # ============================================
    @mcp.tool()
    def verify_code(code: str, auto_fix: bool = True) -> dict:
        """
        Verify Python code for syntax errors, missing imports, and other issues.
        Returns verification report with confidence score and optional auto-fixes.
        
        Args:
            code: Python code to verify
            auto_fix: Whether to automatically fix issues (default: True)
        
        Returns:
            Verification report with issues, fixes, and confidence score
        """
        from codeshield.trustgate.checker import verify_code as _verify
        
        result = _verify(code, auto_fix=auto_fix)
        return result.to_dict()
    
    # ============================================
    # TOOL: full_verify (with sandbox execution)
    # ============================================
    @mcp.tool()
    def full_verify(code: str) -> dict:
        """
        Complete verification: syntax + imports + sandbox execution.
        Runs code in secure sandbox to confirm it actually works.
        
        Args:
            code: Python code to verify
        
        Returns:
            Comprehensive verification report including execution results
        """
        from codeshield.trustgate.sandbox import full_verification
        
        return full_verification(code)
    
    # ============================================
    # TOOL: check_style
    # ============================================
    @mcp.tool()
    def check_style(code: str, codebase_path: str = ".") -> dict:
        """
        Check code against codebase conventions.
        Detects naming mismatches and suggests corrections.
        
        Args:
            code: Code to check
            codebase_path: Path to codebase for convention extraction
        
        Returns:
            Style check results with issues and corrections
        """
        from codeshield.styleforge.corrector import check_style as _check
        
        result = _check(code, codebase_path)
        return result.to_dict()
    
    # ============================================
    # TOOL: save_context
    # ============================================
    @mcp.tool()
    def save_context(
        name: str,
        files: list[str] = None,
        cursor: dict = None,
        notes: str = None,
    ) -> dict:
        """
        Save current coding context for later restoration.
        Like a game save file for your coding session.
        
        Args:
            name: Unique name for this context snapshot
            files: List of open file paths
            cursor: Current cursor position {file, line, column}
            notes: Optional notes about current work
        
        Returns:
            Confirmation of saved context
        """
        from codeshield.contextvault.capture import save_context as _save
        
        return _save(
            name=name,
            files=files or [],
            cursor=cursor,
            notes=notes,
        )
    
    # ============================================
    # TOOL: restore_context
    # ============================================
    @mcp.tool()
    def restore_context(name: str) -> dict:
        """
        Restore a previously saved coding context.
        Returns AI briefing of where you left off.
        
        Args:
            name: Name of context to restore
        
        Returns:
            Context info with AI briefing
        """
        from codeshield.contextvault.restore import restore_context as _restore
        
        return _restore(name=name)
    
    # ============================================
    # TOOL: list_contexts
    # ============================================
    @mcp.tool()
    def list_contexts() -> list[dict]:
        """
        List all saved coding contexts.
        
        Returns:
            List of saved contexts with names and timestamps
        """
        from codeshield.contextvault.capture import list_contexts as _list
        
        return _list()
    
    return mcp


def run_mcp_server():
    """Run the MCP server using stdio transport"""
    mcp = create_mcp_server()
    mcp.run()


# For direct execution
if __name__ == "__main__":
    run_mcp_server()
