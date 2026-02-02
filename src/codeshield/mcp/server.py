"""
MCP Server - Proper FastMCP implementation with LeanMCP Observability

Uses the official MCP Python SDK (FastMCP) to expose CodeShield tools
as a proper MCP server that integrates with Claude, Cursor, etc.

Integrations:
- FastMCP: MCP protocol implementation
- LeanMCP: Observability, metrics, and analytics tracking
- CometAPI/Novita/AIML: LLM providers for code fixes
"""

from typing import Optional, Any
import json
import time

# Try to import FastMCP, fallback to simple HTTP if not available
try:
    from mcp.server.fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False
    FastMCP = None


def create_mcp_server():
    """Create and configure the CodeShield MCP server with LeanMCP observability"""
    
    if not HAS_FASTMCP:
        raise ImportError(
            "MCP SDK not installed. Run: pip install mcp"
        )
    
    # Initialize LeanMCP tracking
    from codeshield.utils.leanmcp import get_leanmcp_client
    leanmcp = get_leanmcp_client()
    
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
        start_time = time.time()
        try:
            from codeshield.trustgate.checker import verify_code as _verify
            
            result = _verify(code, auto_fix=auto_fix)
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("verify_code", duration_ms=duration_ms, success=True)
            return result.to_dict()
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("verify_code", duration_ms=duration_ms, success=False, error_message=str(e))
            raise
    
    # ============================================
    # TOOL: full_verify (with sandbox execution)
    # ============================================
    @mcp.tool()
    def full_verify(code: str) -> dict:
        """
        Complete verification: syntax + imports + sandbox execution.
        Runs code in secure sandbox (Daytona) to confirm it actually works.
        
        Args:
            code: Python code to verify
        
        Returns:
            Comprehensive verification report including execution results
        """
        start_time = time.time()
        try:
            from codeshield.trustgate.sandbox import full_verification
            
            result = full_verification(code)
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("full_verify", duration_ms=duration_ms, success=True)
            return result
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("full_verify", duration_ms=duration_ms, success=False, error_message=str(e))
            raise
    
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
        start_time = time.time()
        try:
            from codeshield.styleforge.corrector import check_style as _check
            
            result = _check(code, codebase_path)
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("check_style", duration_ms=duration_ms, success=True)
            return result.to_dict()
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("check_style", duration_ms=duration_ms, success=False, error_message=str(e))
            raise
    
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
    
    # ============================================
    # TOOL: mcp_health (Observability)
    # ============================================
    @mcp.tool()
    def mcp_health() -> dict:
        """
        Check MCP server health and connectivity status.
        Returns status of all integrated services and providers.
        
        Use this to verify:
        - MCP server is running correctly
        - LLM providers are configured (CometAPI, Novita, AIML)
        - All CodeShield modules are loaded
        
        Returns:
            Health status with provider configurations and stats
        """
        from codeshield.utils.llm import get_llm_client, get_provider_stats
        
        # Check LLM providers
        llm = get_llm_client()
        provider_status = llm.get_status()
        provider_stats = get_provider_stats()
        
        # Check module availability
        modules_status = {}
        try:
            from codeshield.trustgate import checker
            modules_status["trustgate"] = "loaded"
        except ImportError:
            modules_status["trustgate"] = "not_available"
        
        try:
            from codeshield.styleforge import corrector
            modules_status["styleforge"] = "loaded"
        except ImportError:
            modules_status["styleforge"] = "not_available"
        
        try:
            from codeshield.contextvault import capture
            modules_status["contextvault"] = "loaded"
        except ImportError:
            modules_status["contextvault"] = "not_available"
        
        # Get LeanMCP metrics
        leanmcp_status = leanmcp.get_status()
        leanmcp_metrics = leanmcp.get_metrics()
        
        # Check Daytona configuration
        import os
        daytona_configured = bool(os.getenv("DAYTONA_API_KEY"))
        
        return {
            "status": "healthy",
            "mcp_server": "CodeShield",
            "version": "1.0.0",
            "integrations": {
                "leanmcp": leanmcp_status,
                "daytona": {
                    "configured": daytona_configured,
                    "api_url": os.getenv("DAYTONA_API_URL", "https://app.daytona.io/api")
                }
            },
            "llm_providers": provider_status,
            "llm_stats": provider_stats,
            "mcp_metrics": leanmcp_metrics,
            "modules": modules_status,
            "message": "MCP server is running with LeanMCP observability."
        }
    
    # ============================================
    # TOOL: test_llm_connection
    # ============================================
    @mcp.tool()
    def test_llm_connection(provider: str = None) -> dict:
        """
        Test LLM provider connectivity with a simple request.
        
        Args:
            provider: Optional specific provider to test (cometapi, novita, aiml)
                     If not specified, tests the first available provider.
        
        Returns:
            Connection test result with provider used and response time
        """
        import time
        from codeshield.utils.llm import get_llm_client
        
        llm = get_llm_client()
        if provider:
            llm.preferred_provider = provider
        
        start_time = time.time()
        response = llm.chat(
            prompt="Reply with exactly: 'CodeShield MCP connected'",
            max_tokens=20
        )
        elapsed = time.time() - start_time
        
        if response:
            return {
                "success": True,
                "provider": response.provider,
                "model": response.model,
                "response": response.content,
                "response_time_ms": round(elapsed * 1000),
                "tokens_used": response.tokens_used
            }
        else:
            return {
                "success": False,
                "error": "No LLM provider available or all providers failed",
                "hint": "Check that at least one of COMETAPI_KEY, NOVITA_API_KEY, or AIML_API_KEY is set"
            }
    
    return mcp


def run_mcp_server():
    """Run the MCP server using stdio transport"""
    mcp = create_mcp_server()
    mcp.run()


# For direct execution
if __name__ == "__main__":
    run_mcp_server()
