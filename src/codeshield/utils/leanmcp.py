"""
LeanMCP Integration - MCP Server Observability & Analytics

LeanMCP provides production-grade MCP infrastructure.
This module integrates CodeShield with LeanMCP's observability platform
to track MCP tool usage, performance metrics, and health status.

Docs: https://docs.leanmcp.com/
"""

import os
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MCPEvent:
    """Represents an MCP tool invocation event for analytics"""
    tool_name: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LeanMCPClient:
    """
    LeanMCP observability client for tracking MCP server metrics.
    
    Features:
    - Tool invocation tracking
    - Performance metrics
    - Health reporting
    - Usage analytics
    """
    
    def __init__(self):
        self.api_key = os.getenv("LEANMCP_KEY")
        self.api_url = os.getenv("LEANMCP_API_URL", "https://api.leanmcp.com")
        self.enabled = bool(self.api_key)
        self._client = httpx.Client(timeout=10.0) if self.enabled else None
        self._events_buffer: list[MCPEvent] = []
        self._buffer_size = 10  # Flush after 10 events
        
        # Local metrics tracking (always available)
        self._metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tools": {},
            "start_time": datetime.utcnow().isoformat(),
        }
    
    def is_configured(self) -> bool:
        """Check if LeanMCP is properly configured"""
        return self.enabled and self.api_key is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get LeanMCP integration status"""
        return {
            "configured": self.is_configured(),
            "api_url": self.api_url,
            "events_buffered": len(self._events_buffer),
            "local_metrics": self._metrics,
        }
    
    def track_tool_call(
        self,
        tool_name: str,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track an MCP tool invocation for analytics.
        
        Args:
            tool_name: Name of the MCP tool (e.g., "verify_code", "check_style")
            duration_ms: Execution time in milliseconds
            success: Whether the call succeeded
            error_message: Error message if failed
            metadata: Additional context
        """
        # Update local metrics
        self._metrics["total_calls"] += 1
        if success:
            self._metrics["successful_calls"] += 1
        else:
            self._metrics["failed_calls"] += 1
        
        if tool_name not in self._metrics["tools"]:
            self._metrics["tools"][tool_name] = {"calls": 0, "errors": 0, "total_duration_ms": 0}
        
        self._metrics["tools"][tool_name]["calls"] += 1
        if not success:
            self._metrics["tools"][tool_name]["errors"] += 1
        if duration_ms:
            self._metrics["tools"][tool_name]["total_duration_ms"] += duration_ms
        
        # Create event for LeanMCP
        event = MCPEvent(
            tool_name=tool_name,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        self._events_buffer.append(event)
        
        # Auto-flush if buffer is full
        if len(self._events_buffer) >= self._buffer_size:
            self.flush_events()
    
    def flush_events(self) -> bool:
        """
        Send buffered events to LeanMCP platform.
        Returns True if successful or LeanMCP not configured.
        """
        if not self._events_buffer:
            return True
        
        if not self.is_configured() or self._client is None:
            # Clear buffer if not configured (events are still tracked locally)
            self._events_buffer.clear()
            return True
        
        try:
            events_data = [
                {
                    "tool_name": e.tool_name,
                    "timestamp": e.timestamp,
                    "duration_ms": e.duration_ms,
                    "success": e.success,
                    "error_message": e.error_message,
                    "metadata": e.metadata,
                }
                for e in self._events_buffer
            ]
            
            response = self._client.post(
                f"{self.api_url}/v1/events",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "server_name": "CodeShield",
                    "events": events_data,
                }
            )
            
            if response.status_code == 200:
                self._events_buffer.clear()
                return True
            else:
                print(f"LeanMCP event flush failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"LeanMCP error: {e}")
            return False
    
    def report_health(self) -> Dict[str, Any]:
        """
        Report server health to LeanMCP and return health status.
        """
        health_data = {
            "server_name": "CodeShield",
            "status": "healthy",
            "version": "1.0.0",
            "metrics": self._metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if self.is_configured() and self._client is not None:
            try:
                self._client.post(
                    f"{self.api_url}/v1/health",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=health_data
                )
            except Exception as e:
                print(f"LeanMCP health report error: {e}")
        
        return health_data
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        metrics = self._metrics.copy()
        
        # Calculate averages
        for tool_name, tool_data in metrics["tools"].items():
            if tool_data["calls"] > 0 and tool_data["total_duration_ms"] > 0:
                tool_data["avg_duration_ms"] = tool_data["total_duration_ms"] / tool_data["calls"]
        
        return metrics


# Singleton instance
_leanmcp_client: Optional[LeanMCPClient] = None


def get_leanmcp_client() -> LeanMCPClient:
    """Get or create LeanMCP client singleton"""
    global _leanmcp_client
    if _leanmcp_client is None:
        _leanmcp_client = LeanMCPClient()
    return _leanmcp_client


def track_mcp_call(tool_name: str):
    """
    Decorator to automatically track MCP tool calls with LeanMCP.
    
    Usage:
        @track_mcp_call("verify_code")
        def verify_code(code: str) -> dict:
            ...
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client = get_leanmcp_client()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                client.track_tool_call(
                    tool_name=tool_name,
                    duration_ms=duration_ms,
                    success=True
                )
                return result
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                client.track_tool_call(
                    tool_name=tool_name,
                    duration_ms=duration_ms,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator
