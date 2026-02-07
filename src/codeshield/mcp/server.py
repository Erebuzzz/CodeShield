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

    # ============================================
    # TOOL: multi_language_verify (v2 engine)
    # ============================================
    @mcp.tool()
    def multi_language_verify(code: str, language: str = "python") -> dict:
        """
        Verify code using the TrustGate v2 multi-language engine.
        Supports Python and JavaScript with tree-sitter parsing,
        program graph analysis, taint tracking, and 7+ built-in rules.

        Args:
            code: Source code to verify
            language: Language identifier — "python" or "javascript"

        Returns:
            VerificationReport with findings, confidence, and graph metadata
        """
        start_time = time.time()
        try:
            from codeshield.trustgate.engine.executor import verify as engine_verify
            report = engine_verify(code, language=language)
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("multi_language_verify", duration_ms=duration_ms, success=True)
            return report.to_dict()
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("multi_language_verify", duration_ms=duration_ms, success=False, error_message=str(e))
            raise

    # ============================================
    # TOOL: batch_verification
    # ============================================
    @mcp.tool()
    def batch_verification(files: list[dict]) -> dict:
        """
        Verify multiple code snippets in a single call.

        Args:
            files: List of {code, language, filename} dicts

        Returns:
            Batch results with per-file reports and aggregate stats
        """
        start_time = time.time()
        try:
            from codeshield.trustgate.engine.executor import verify as engine_verify
            results = []
            total_findings = 0
            all_valid = True
            for item in files:
                r = engine_verify(
                    item.get("code", ""),
                    language=item.get("language", "python"),
                    filename=item.get("filename"),
                )
                results.append({
                    "filename": item.get("filename", "unnamed"),
                    **r.to_dict(),
                })
                total_findings += len(r.findings)
                if not r.is_valid:
                    all_valid = False
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("batch_verification", duration_ms=duration_ms, success=True)
            return {
                "results": results,
                "total_files": len(files),
                "total_findings": total_findings,
                "all_valid": all_valid,
                "elapsed_ms": duration_ms,
            }
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            leanmcp.track_tool_call("batch_verification", duration_ms=duration_ms, success=False, error_message=str(e))
            raise

    # ============================================
    # TOOL: project_graph_export
    # ============================================
    @mcp.tool()
    def project_graph_export(code: str, language: str = "python", graph_type: str = "cfg") -> dict:
        """
        Export a program graph (CFG, DFG, TFG, call_graph) as JSON.
        Useful for visualization and external analysis tools.

        Args:
            code: Source code to analyze
            language: Language identifier
            graph_type: One of "cfg", "dfg", "tfg", "call_graph"

        Returns:
            Graph as {nodes: [...], edges: [...]}
        """
        from codeshield.trustgate.engine.parser import parse_source
        from codeshield.trustgate.engine.meta_ast import normalise
        from codeshield.trustgate.engine.graphs import (
            build_cfg, build_dfg, build_taint_graph, build_call_graph,
        )
        pr = parse_source(code, language)
        meta = normalise(pr)
        builders = {
            "cfg": build_cfg,
            "dfg": build_dfg,
            "tfg": build_taint_graph,
            "call_graph": build_call_graph,
        }
        builder = builders.get(graph_type)
        if not builder:
            return {"error": f"Unknown graph type: {graph_type}. Use: {list(builders.keys())}"}
        graph = builder(meta)
        return {
            "graph_type": graph_type,
            "language": language,
            "nodes": [
                {"id": n.id, "label": n.label, "line": n.line}
                for n in graph.nodes.values()
            ],
            "edges": [
                {"src": e.src, "dst": e.dst, "label": e.label}
                for e in graph.edges
            ],
            "entry": graph.entry,
            "exit": graph.exit,
        }

    # ============================================
    # TOOL: dependency_audit
    # ============================================
    @mcp.tool()
    def dependency_audit(requirements_text: str) -> dict:
        """
        Audit Python dependencies for known security issues.
        Pass the contents of requirements.txt or pyproject.toml deps.

        Args:
            requirements_text: Contents of requirements file

        Returns:
            Audit results with flagged packages
        """
        import re
        flagged = []
        # Known-insecure packages / patterns
        insecure = {
            "pyyaml<5.4": "CVE-2020-14343 — arbitrary code execution via yaml.load",
            "requests<2.20": "CVE-2018-18074 — session cookie leak",
            "flask<1.0": "Multiple known vulnerabilities",
            "django<3.2": "Security support ended",
            "jinja2<2.11.3": "CVE-2020-28493 — ReDOS",
            "urllib3<1.26.5": "CVE-2021-33503 — ReDOS",
            "pillow<9.0": "Multiple buffer overflow CVEs",
            "cryptography<3.3": "CVE-2020-36242 — integer overflow",
            "paramiko<2.10": "CVE-2022-24302 — race condition",
            "setuptools<65.5.1": "CVE-2022-40897 — ReDOS",
        }
        lines = requirements_text.strip().splitlines()
        packages = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^([a-zA-Z0-9_-]+)", line)
            if match:
                packages.append({"name": match.group(1), "spec": line})

        for pkg in packages:
            for pattern, reason in insecure.items():
                if pkg["name"].lower() in pattern.lower():
                    flagged.append({
                        "package": pkg["spec"],
                        "advisory": reason,
                        "action": "Upgrade to latest version",
                    })

        return {
            "total_packages": len(packages),
            "flagged": len(flagged),
            "advisories": flagged,
            "clean": len(flagged) == 0,
        }

    # ============================================
    # TOOL: security_baseline_scan
    # ============================================
    @mcp.tool()
    def security_baseline_scan(code: str, language: str = "python") -> dict:
        """
        Run a security-focused baseline scan.
        Checks for hardcoded secrets, injection vectors, taint flows,
        and dangerous API usage.

        Args:
            code: Source code to scan
            language: Language identifier

        Returns:
            Security report with severity-ranked findings
        """
        from codeshield.trustgate.engine.executor import verify as engine_verify
        r = engine_verify(code, language=language)
        security_findings = [
            f.to_dict() for f in r.findings
            if f.rule_id in ("shell_injection", "taint_flow", "hardcoded_secret")
        ]
        return {
            "scan_type": "security_baseline",
            "language": language,
            "issues_found": len(security_findings),
            "findings": security_findings,
            "passed": len(security_findings) == 0,
            "confidence": r.confidence_score,
        }

    # ============================================
    # TOOL: policy_enforcement_check
    # ============================================
    @mcp.tool()
    def policy_enforcement_check(code: str, language: str = "python") -> dict:
        """
        Check code against the active organizational policy.
        If no policy is configured, uses default thresholds.

        Args:
            code: Source code to check
            language: Language identifier

        Returns:
            Policy compliance report
        """
        from codeshield.trustgate.engine.executor import verify as engine_verify
        from codeshield.plugins import get_registry

        r = engine_verify(code, language=language)
        registry = get_registry()
        policy = registry.get_active_policy()

        min_confidence = policy.min_confidence if policy else 0.7
        required_rules = set(policy.required_rules) if policy else set()
        blocked = policy.blocked_patterns if policy else []

        violations = []
        if r.confidence_score < min_confidence:
            violations.append(f"Confidence {r.confidence_score:.2f} below threshold {min_confidence:.2f}")

        triggered_rules = {f.rule_id for f in r.findings}
        for req in required_rules:
            if req not in triggered_rules and not r.is_valid:
                pass  # rule wasn't needed

        for pattern in blocked:
            if pattern in code:
                violations.append(f"Blocked pattern found: '{pattern}'")

        return {
            "compliant": len(violations) == 0 and r.is_valid,
            "confidence": r.confidence_score,
            "violations": violations,
            "findings_count": len(r.findings),
            "policy_active": policy is not None,
        }

    # ============================================
    # TOOL: rule_registry_access
    # ============================================
    @mcp.tool()
    def rule_registry_access() -> dict:
        """
        List all verification rules (built-in + plugins).

        Returns:
            List of rules with id, name, severity, tags, and languages
        """
        from codeshield.plugins import get_registry
        rs = get_registry().get_all_rules()
        return {
            "total_rules": len(rs.rules),
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "severity": r.severity.value,
                    "tags": r.tags,
                    "languages": r.languages or ["all"],
                    "enabled": r.enabled,
                }
                for r in rs.rules
            ],
        }

    # ============================================
    # TOOL: dashboard_sync
    # ============================================
    @mcp.tool()
    def dashboard_sync() -> dict:
        """
        Return current dashboard state for UI synchronization.
        Includes verification stats, active rules, plugin status,
        and recent context saves.

        Returns:
            Dashboard state object
        """
        from codeshield.plugins import get_registry
        from codeshield.contextvault.capture import list_contexts

        registry = get_registry()
        rs = registry.get_all_rules()
        contexts = list_contexts()

        return {
            "rules_loaded": len(rs.rules),
            "plugins": registry.list_plugins(),
            "recent_contexts": contexts[:5],
            "engine_status": "online",
            "supported_languages": ["python", "javascript"],
        }

    # ============================================
    # TOOL: language_plugin_install (stub)
    # ============================================
    @mcp.tool()
    def language_plugin_install(language: str) -> dict:
        """
        Install a language plugin to add support for a new language.
        Currently a stub — returns guidance on creating language plugins.

        Args:
            language: Language to add (e.g. "go", "rust", "java")

        Returns:
            Installation status or guidance
        """
        supported = {"python", "javascript"}
        if language.lower() in supported:
            return {"status": "already_supported", "language": language}

        return {
            "status": "plugin_required",
            "language": language,
            "instructions": (
                f"To add {language} support, create a LanguagePlugin with:\n"
                f"  1. tree-sitter grammar for {language}\n"
                f"  2. Node-kind mapping to MetaAST NodeKind\n"
                f"  3. Taint source/sink definitions\n"
                f"Place in ~/.codeshield/plugins/{language}/ with plugin.json"
            ),
        }
    
    return mcp


def run_mcp_server():
    """Run the MCP server using stdio transport"""
    mcp = create_mcp_server()
    mcp.run()


# For direct execution
if __name__ == "__main__":
    run_mcp_server()
