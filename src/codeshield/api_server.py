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

# TrustGate v2 engine (tree-sitter based, multi-language)
try:
    from codeshield.trustgate.engine.executor import verify as engine_verify
    _engine_available = True
except Exception:
    engine_verify = None
    _engine_available = False

app = FastAPI(title="CodeShield API", version="0.1.0")

# --- Always-on live metrics ---
try:
    from codeshield.utils.live_metrics import live as _live_metrics
    _live_metrics.start_flush_timer()
    _live_metrics_available = True
except Exception:
    _live_metrics = None
    _live_metrics_available = False

# --- Auto-save failsafe ---
try:
    from codeshield.contextvault.autosave import enable_autosave
    enable_autosave()
except Exception:
    pass

# Configure CORS — allow all origins for public API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# --- Metrics middleware — attaches _metrics to every JSON response ---

from starlette.middleware.base import BaseHTTPMiddleware
import json as _json


class _MetricsBannerMiddleware(BaseHTTPMiddleware):
    """Injects a `_metrics` key into every JSON response body.

    Overhead: one dict copy + json encode.  Skipped for non-JSON or
    when metrics are disabled via CODESHIELD_METRICS=off.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if not _live_metrics_available or not _live_metrics:
            return response

        from codeshield.utils.live_metrics import is_enabled
        if not is_enabled():
            return response

        # Only inject into JSON responses
        ct = response.headers.get("content-type", "")
        if "application/json" not in ct:
            return response

        # Read body, inject _metrics, return new response
        body_parts = []
        async for chunk in response.body_iterator:
            body_parts.append(chunk if isinstance(chunk, bytes) else chunk.encode())
        body = b"".join(body_parts)

        try:
            data = _json.loads(body)
            if isinstance(data, dict):
                data["_metrics"] = _live_metrics.summary()
                body = _json.dumps(data).encode()
        except Exception:
            pass  # non-JSON or malformed — pass through

        return JSONResponse(
            content=_json.loads(body),
            status_code=response.status_code,
            headers=dict(response.headers),
        )


app.add_middleware(_MetricsBannerMiddleware)


# --- Data Models ---

class VerifyRequest(BaseModel):
    code: str
    auto_fix: bool = True
    use_sandbox: bool = False
    language: str = "python"
    engine: str = "auto"  # "auto", "v1", "v2"

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
    # Route to v2 engine when appropriate
    use_v2 = (
        req.engine == "v2"
        or (req.engine == "auto" and _engine_available and req.language != "python")
    )

    if use_v2 and _engine_available:
        report = engine_verify(req.code, language=req.language)
        return report.to_dict()

    if req.use_sandbox:
        if not full_verification:
            return {"error": "Backend modules not loaded"}
        result = full_verification(req.code)
        return result

    if not verify_code:
        # Fall back to v2 engine if legacy checker unavailable
        if _engine_available:
            report = engine_verify(req.code, language=req.language)
            return report.to_dict()
        return {"error": "Backend modules not loaded"}

    # Legacy v1 checker (Python only)
    result = verify_code(req.code, auto_fix=req.auto_fix)
    v1_dict = result.to_dict()

    # Enrich with v2 findings if engine is available
    if _engine_available and req.engine != "v1":
        try:
            v2_report = engine_verify(req.code, language=req.language)
            # Merge unique v2 findings that v1 missed
            v1_lines = {(i.get("line"), i.get("message")) for i in v1_dict.get("issues", [])}
            for f in v2_report.to_dict().get("issues", []):
                if (f.get("line"), f.get("message")) not in v1_lines:
                    v1_dict.setdefault("issues", []).append(f)
            # Use the lower confidence
            v1_dict["confidence_score"] = min(
                v1_dict.get("confidence_score", 1.0),
                v2_report.confidence_score,
            )
            v1_dict["is_valid"] = v1_dict["is_valid"] and v2_report.is_valid
        except Exception:
            pass  # v2 enrichment is best-effort

    return v1_dict

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


# --- Dashboard & Graph Endpoints ---

class BatchVerifyRequest(BaseModel):
    files: List[dict]  # [{code, language, filename}, ...]

class GraphExportRequest(BaseModel):
    code: str
    language: str = "python"
    graph_type: str = "cfg"  # cfg, dfg, tfg, call_graph


@app.post("/api/verify/batch")
async def api_batch_verify(req: BatchVerifyRequest):
    """Verify multiple code snippets in a single request."""
    if not _engine_available:
        return {"error": "v2 engine not available"}
    results = []
    total_findings = 0
    for item in req.files:
        r = engine_verify(
            item.get("code", ""),
            language=item.get("language", "python"),
            filename=item.get("filename"),
        )
        results.append({"filename": item.get("filename", "unnamed"), **r.to_dict()})
        total_findings += len(r.findings)
    return {
        "results": results,
        "total_files": len(req.files),
        "total_findings": total_findings,
        "all_valid": all(r.get("is_valid", False) for r in results),
    }


@app.post("/api/graph/export")
async def api_export_graph(req: GraphExportRequest):
    """Export a program graph (CFG, DFG, TFG, call_graph) as JSON."""
    try:
        from codeshield.trustgate.engine.parser import parse_source
        from codeshield.trustgate.engine.meta_ast import normalise
        from codeshield.trustgate.engine.graphs import (
            build_cfg, build_dfg, build_taint_graph, build_call_graph,
        )
        pr = parse_source(req.code, req.language)
        meta = normalise(pr)
        builders = {
            "cfg": build_cfg, "dfg": build_dfg,
            "tfg": build_taint_graph, "call_graph": build_call_graph,
        }
        builder = builders.get(req.graph_type)
        if not builder:
            return {"error": f"Unknown graph type. Use: {list(builders.keys())}"}
        graph = builder(meta)
        return {
            "graph_type": req.graph_type,
            "language": req.language,
            "nodes": [{"id": n.id, "label": n.label, "line": n.line} for n in graph.nodes.values()],
            "edges": [{"src": e.src, "dst": e.dst, "label": e.label} for e in graph.edges],
            "entry": graph.entry,
            "exit": graph.exit,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/dashboard/state")
async def api_dashboard_state():
    """Return full dashboard state for frontend sync."""
    try:
        from codeshield.plugins import get_registry
        from codeshield.contextvault.capture import list_contexts
        from codeshield.trustgate.engine.rules import load_builtin_rules

        registry = get_registry()
        rs = registry.get_all_rules()
        contexts = list_contexts()

        return {
            "engine_status": "online",
            "v2_engine": _engine_available,
            "supported_languages": ["python", "javascript"],
            "rules_loaded": len(rs.rules),
            "rules": [
                {"id": r.id, "name": r.name, "severity": r.severity.value,
                 "tags": r.tags, "languages": r.languages or ["all"], "enabled": r.enabled}
                for r in rs.rules
            ],
            "plugins": registry.list_plugins(),
            "recent_contexts": contexts[:10],
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/dashboard/rules")
async def api_dashboard_rules():
    """List all verification rules (built-in + plugins)."""
    try:
        from codeshield.plugins import get_registry
        registry = get_registry()
        rs = registry.get_all_rules()
        return {
            "total": len(rs.rules),
            "rules": [
                {"id": r.id, "name": r.name, "severity": r.severity.value,
                 "tags": r.tags, "languages": r.languages or ["all"], "enabled": r.enabled}
                for r in rs.rules
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/dashboard/plugins")
async def api_dashboard_plugins():
    """List installed plugins."""
    try:
        from codeshield.plugins import get_registry
        return {"plugins": get_registry().list_plugins()}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/security/baseline")
async def api_security_baseline(req: VerifyRequest):
    """Run security-focused baseline scan."""
    if not _engine_available:
        return {"error": "v2 engine not available"}
    r = engine_verify(req.code, language=req.language)
    security_findings = [
        f.to_dict() for f in r.findings
        if f.rule_id in ("shell_injection", "taint_flow", "hardcoded_secret")
    ]
    return {
        "scan_type": "security_baseline",
        "language": req.language,
        "issues_found": len(security_findings),
        "findings": security_findings,
        "passed": len(security_findings) == 0,
        "confidence": r.confidence_score,
    }


@app.get("/api/autosave/latest")
async def api_autosave_latest():
    """Get the most recent auto-saved context."""
    try:
        from codeshield.contextvault.autosave import get_latest_autosave
        ctx = get_latest_autosave()
        if ctx:
            return {"found": True, "context": ctx}
        return {"found": False, "message": "No auto-save found"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/autosave/trigger")
async def api_autosave_trigger():
    """Manually trigger an auto-save."""
    try:
        from codeshield.contextvault.autosave import perform_autosave
        result = perform_autosave(reason="manual_trigger")
        if result:
            return result
        return {"message": "Nothing to auto-save (no tracked state)"}
    except Exception as e:
        return {"error": str(e)}


# --- Live Metrics endpoints ---

@app.get("/api/live-metrics")
async def api_live_metrics():
    """Get current live metrics snapshot (always-on telemetry)."""
    if _live_metrics_available and _live_metrics:
        return _live_metrics.summary()
    return {"metrics": "unavailable"}


@app.post("/api/live-metrics/toggle")
async def api_live_metrics_toggle(enabled: bool = Body(..., embed=True)):
    """Enable or disable live metrics. Set enabled=false to turn off."""
    if _live_metrics_available:
        from codeshield.utils.live_metrics import set_enabled
        set_enabled(enabled)
        return {"metrics_enabled": enabled}
    return {"error": "Live metrics module unavailable"}


@app.post("/api/live-metrics/reset")
async def api_live_metrics_reset():
    """Reset all live metrics counters."""
    if _live_metrics_available and _live_metrics:
        _live_metrics.reset()
        return {"message": "Live metrics reset"}
    return {"error": "Live metrics module unavailable"}


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
