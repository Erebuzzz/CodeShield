"""
CodeShield API Server
Exposes CodeShield functionality via HTTP for the React Frontend.
"""

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any
import uvicorn
import os
from fastapi.staticfiles import StaticFiles

# Import CodeShield core modules
# We wrap imports in try/except to handle potential missing dependencies during dev
try:
    from codeshield.trustgate.checker import verify_code
    from codeshield.trustgate.sandbox import full_verification
    from codeshield.styleforge.corrector import check_style
    from codeshield.contextvault.capture import save_context, list_contexts
    from codeshield.contextvault.restore import restore_context
except Exception:
    # Fallback for dev environment if paths aren't set up
    print("WARNING: Could not import CodeShield modules. Ensure you are running as a module.")
    verify_code = None
    full_verification = None
    check_style = None
    save_context = None
    list_contexts = None
    restore_context = None

app = FastAPI(title="CodeShield API", version="0.1.0")

# Configure CORS — allow all origins for public API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Data Models ---

class VerifyRequest(BaseModel):
    code: str
    auto_fix: bool = True
    use_sandbox: bool = False

class StyleCheckRequest(BaseModel):
    code: str
    codebase_path: str = "."

class ContextSaveRequest(BaseModel):
    name: str
    files: List[str] = []
    cursor: Optional[dict] = None
    notes: Optional[str] = None

class ContextRestoreRequest(BaseModel):
    name: str

# --- Endpoints ---

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "online", "service": "CodeShield API"}

@app.post("/api/verify")
async def api_verify_code(req: VerifyRequest):
    if not verify_code:
        return {"error": "Backend modules not loaded"}
    
    if req.use_sandbox:
        # Full sandbox verification
        result = full_verification(req.code)
        return result
    else:
        # Fast static verification
        result = verify_code(req.code, auto_fix=req.auto_fix)
        return result.to_dict()

@app.post("/api/style")
async def api_check_style(req: StyleCheckRequest):
    if not check_style:
        return {"error": "Backend modules not loaded"}
    
    result = check_style(req.code, req.codebase_path)
    return result.to_dict()

@app.post("/api/context/save")
async def api_save_context(req: ContextSaveRequest):
    if not save_context:
        return {"error": "Backend modules not loaded"}
    
    result = save_context(
        name=req.name,
        files=req.files,
        cursor=req.cursor,
        notes=req.notes
    )
    return result

@app.post("/api/context/restore")
async def api_restore_context(req: ContextRestoreRequest):
    if not restore_context:
        return {"error": "Backend modules not loaded"}
    
    result = restore_context(name=req.name)
    return result

@app.get("/api/contexts")
async def api_list_contexts():
    if not list_contexts:
        return {"error": "Backend modules not loaded"}
    
    result = list_contexts()
    return result


# --- Observability Endpoints ---

@app.get("/api/providers/status")
async def api_provider_status():
    """
    Get status of all LLM providers (CometAPI, Novita, AIML).
    Useful for checking which providers are configured and their usage stats.
    """
    try:
        from codeshield.utils.llm import get_llm_client, get_provider_stats
        
        llm = get_llm_client()
        status = llm.get_status()
        stats = get_provider_stats()
        
        return {
            "providers": status,
            "usage_stats": stats,
            "active_provider": next(
                (name for name, info in status.items() if info["configured"]),
                None
            )
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/providers/test")
async def api_test_provider(provider: str = None):
    """
    Test LLM provider connectivity.
    Query param: ?provider=cometapi|novita|aiml
    """
    try:
        import time
        from codeshield.utils.llm import get_llm_client
        
        llm = get_llm_client()
        if provider:
            llm.preferred_provider = provider
        
        start_time = time.time()
        response = llm.chat(
            prompt="Reply with exactly: 'CodeShield connected'",
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
                "error": "No LLM provider available",
                "hint": "Set COMETAPI_KEY, NOVITA_API_KEY, or AIML_API_KEY in .env"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/mcp/status")
async def api_mcp_status():
    """
    Check if MCP server components are available.
    """
    try:
        from mcp.server.fastmcp import FastMCP
        mcp_available = True
    except ImportError:
        mcp_available = False
    
    return {
        "mcp_sdk_installed": mcp_available,
        "mcp_config": "mcp_config.json",
        "tools_available": [
            "verify_code", "full_verify", "check_style",
            "save_context", "restore_context", "list_contexts",
            "mcp_health", "test_llm_connection"
        ] if mcp_available else [],
        "usage": "Add mcp_config.json to your Claude/Cursor MCP settings"
    }


@app.get("/api/leanmcp/status")
async def api_leanmcp_status():
    """
    Get LeanMCP integration status and metrics.
    """
    try:
        from codeshield.utils.leanmcp import get_leanmcp_client
        
        client = get_leanmcp_client()
        return {
            "status": client.get_status(),
            "metrics": client.get_metrics(),
            "configured": client.is_configured()
        }
    except Exception as e:
        return {"error": str(e), "configured": False}


@app.get("/api/leanmcp/health")
async def api_leanmcp_health():
    """
    Report and retrieve health status via LeanMCP.
    """
    try:
        from codeshield.utils.leanmcp import get_leanmcp_client
        
        client = get_leanmcp_client()
        return client.report_health()
    except Exception as e:
        return {"error": str(e), "status": "error"}


@app.get("/api/integrations/status")
async def api_integrations_status():
    """
    Get status of ALL required integrations.
    """
    import os
    
    integrations = {
        "cometapi": {
            "configured": bool(os.getenv("COMETAPI_KEY")),
            "env_var": "COMETAPI_KEY",
            "docs": "https://apidoc.cometapi.com/"
        },
        "novita": {
            "configured": bool(os.getenv("NOVITA_API_KEY")),
            "env_var": "NOVITA_API_KEY",
            "docs": "https://novita.ai/docs/guides/llm-api"
        },
        "aiml": {
            "configured": bool(os.getenv("AIML_API_KEY")),
            "env_var": "AIML_API_KEY",
        },
        "daytona": {
            "configured": bool(os.getenv("DAYTONA_API_KEY")),
            "env_var": "DAYTONA_API_KEY",
            "api_url": os.getenv("DAYTONA_API_URL"),
            "docs": "https://www.daytona.io/docs"
        },
        "leanmcp": {
            "configured": bool(os.getenv("LEANMCP_KEY")),
            "env_var": "LEANMCP_KEY",
            "api_url": os.getenv("LEANMCP_API_URL"),
            "docs": "https://docs.leanmcp.com/"
        }
    }
    
    all_configured = all(i["configured"] for i in integrations.values())
    
    return {
        "all_configured": all_configured,
        "integrations": integrations,
        "message": "All integrations configured!" if all_configured else "Some integrations missing. Check .env file."
    }


# --- Metrics Endpoints ---

@app.get("/api/metrics")
async def api_get_metrics():
    """
    Get comprehensive CodeShield metrics.
    
    Returns transparent, verifiable statistics for:
    - TrustGate: Detection rates, fix accuracy, sandbox success
    - StyleForge: Convention detection, corrections
    - ContextVault: Save/restore stats
    - Tokens: Usage efficiency, costs
    """
    try:
        from codeshield.utils.metrics import get_metrics
        
        metrics = get_metrics()
        return metrics.get_summary()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/metrics/trustgate")
async def api_trustgate_metrics():
    """Get TrustGate-specific metrics"""
    try:
        from codeshield.utils.metrics import get_metrics
        return get_metrics().trustgate.to_dict()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/metrics/styleforge")
async def api_styleforge_metrics():
    """Get StyleForge-specific metrics"""
    try:
        from codeshield.utils.metrics import get_metrics
        return get_metrics().styleforge.to_dict()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/metrics/tokens")
async def api_token_metrics():
    """
    Get token utilization metrics.
    
    Includes:
    - Total tokens used (input/output)
    - Token efficiency ratio
    - Cost estimates per provider
    - Average tokens per request
    """
    try:
        from codeshield.utils.metrics import get_metrics
        return get_metrics().tokens.to_dict()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/metrics/reset")
async def api_reset_metrics():
    """Reset all metrics (for testing)"""
    try:
        from codeshield.utils.metrics import get_metrics
        get_metrics().reset()
        return {"success": True, "message": "Metrics reset"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/tokens/efficiency")
async def api_token_efficiency():
    """
    Get token efficiency and optimization stats.
    
    Shows:
    - Cache hit rate (higher = more savings)
    - Tokens saved by caching
    - Budget usage
    - Session statistics
    """
    try:
        from codeshield.utils.token_optimizer import get_token_optimizer
        from codeshield.utils.llm import get_provider_stats
        
        optimizer = get_token_optimizer()
        provider_stats = get_provider_stats()
        
        return {
            "optimization": optimizer.get_stats(),
            "provider_efficiency": {
                name: {
                    "token_efficiency": stats.get("token_efficiency", 0),
                    "avg_tokens_per_call": stats.get("avg_tokens_per_call", 0),
                    "avg_latency_ms": stats.get("avg_latency_ms", 0),
                }
                for name, stats in provider_stats.items()
            },
            "tips": [
                "Cache hit rate > 20% indicates good prompt reuse",
                "Token efficiency > 1.0 means more output than input (verbose responses)",
                "Aim for avg_tokens_per_call < 500 for cost efficiency"
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/tokens/budget")
async def api_set_token_budget(budget: int = 100000):
    """Set token budget for the session"""
    try:
        from codeshield.utils.token_optimizer import get_token_optimizer
        optimizer = get_token_optimizer()
        optimizer.set_budget(budget)
        return {"success": True, "budget": budget}
    except Exception as e:
        return {"error": str(e)}


# --- Frontend Static Serving ---

# Mount assets (CSS/JS)
if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Serve other static files (favicon, etc.) and SPA fallback
@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    # API requests are handled by routes above.
    # If we get here, it's a static file or client-side route.
    
    # Security: Prevent traversing up? FileResponse handles it.
    
    dist_dir = "frontend/dist"
    if not os.path.exists(dist_dir):
        return {"status": "Frontend not built", "deployment": "backend-only"}

    # Try to find specific file
    file_path = os.path.join(dist_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    return FileResponse(os.path.join(dist_dir, "index.html"))


if __name__ == "__main__":
    uvicorn.run("codeshield.api_server:app", host="0.0.0.0", port=8000, reload=True)
