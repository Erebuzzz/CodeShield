"""
CodeShield Metrics - Transparent Statistics Tracking

Provides honest, verifiable metrics for all features:
- TrustGate: Detection rates, fix accuracy, execution stats
- StyleForge: Convention detection accuracy, correction counts
- ContextVault: Storage stats, restore success rates
- LLM: Token usage, cost efficiency, provider performance
"""

import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from collections import defaultdict
from threading import Lock
from contextlib import contextmanager


DB_PATH = Path.home() / ".codeshield" / "metrics.sqlite"

# Thread-safe lock for metrics updates
_metrics_lock = Lock()


@dataclass
class TrustGateMetrics:
    """TrustGate verification metrics"""
    total_verifications: int = 0
    syntax_errors_detected: int = 0
    missing_imports_detected: int = 0
    undefined_names_detected: int = 0
    auto_fixes_applied: int = 0
    sandbox_executions: int = 0
    sandbox_successes: int = 0
    sandbox_failures: int = 0
    total_processing_time_ms: int = 0
    
    @property
    def detection_rate(self) -> float:
        """Percentage of verifications that found issues"""
        if self.total_verifications == 0:
            return 0.0
        issues = self.syntax_errors_detected + self.missing_imports_detected + self.undefined_names_detected
        return min(100.0, (issues / max(1, self.total_verifications)) * 100)
    
    @property
    def fix_success_rate(self) -> float:
        """Percentage of issues that were auto-fixed"""
        issues = self.syntax_errors_detected + self.missing_imports_detected + self.undefined_names_detected
        if issues == 0:
            return 100.0  # No issues = nothing to fix
        return (self.auto_fixes_applied / issues) * 100
    
    @property
    def sandbox_success_rate(self) -> float:
        """Sandbox execution success rate"""
        if self.sandbox_executions == 0:
            return 0.0
        return (self.sandbox_successes / self.sandbox_executions) * 100
    
    @property
    def avg_processing_time_ms(self) -> float:
        """Average processing time per verification"""
        if self.total_verifications == 0:
            return 0.0
        return self.total_processing_time_ms / self.total_verifications
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "detection_rate": round(self.detection_rate, 2),
            "fix_success_rate": round(self.fix_success_rate, 2),
            "sandbox_success_rate": round(self.sandbox_success_rate, 2),
            "avg_processing_time_ms": round(self.avg_processing_time_ms, 2),
        }


@dataclass
class StyleForgeMetrics:
    """StyleForge convention metrics"""
    total_checks: int = 0
    conventions_detected: int = 0
    naming_issues_found: int = 0
    corrections_suggested: int = 0
    corrections_applied: int = 0
    codebases_analyzed: int = 0
    total_processing_time_ms: int = 0
    
    @property
    def detection_accuracy(self) -> float:
        """Ratio of issues found to checks performed"""
        if self.total_checks == 0:
            return 0.0
        return (self.naming_issues_found / self.total_checks) * 100
    
    @property
    def correction_rate(self) -> float:
        """Percentage of suggestions that were applied"""
        if self.corrections_suggested == 0:
            return 0.0
        return (self.corrections_applied / self.corrections_suggested) * 100
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "detection_accuracy": round(self.detection_accuracy, 2),
            "correction_rate": round(self.correction_rate, 2),
        }


@dataclass
class ContextVaultMetrics:
    """ContextVault storage metrics"""
    total_contexts_saved: int = 0
    total_contexts_restored: int = 0
    restore_successes: int = 0
    restore_failures: int = 0
    contexts_deleted: int = 0
    total_files_tracked: int = 0
    total_storage_bytes: int = 0
    
    @property
    def restore_success_rate(self) -> float:
        """Context restore success rate"""
        total_restores = self.restore_successes + self.restore_failures
        if total_restores == 0:
            return 0.0
        return (self.restore_successes / total_restores) * 100
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "restore_success_rate": round(self.restore_success_rate, 2),
            "storage_mb": round(self.total_storage_bytes / (1024 * 1024), 3),
        }


@dataclass
class TokenMetrics:
    """LLM Token Usage Metrics - For Cost Efficiency Tracking"""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Provider-specific tracking
    provider_tokens: Dict[str, dict] = field(default_factory=lambda: defaultdict(lambda: {
        "input": 0, "output": 0, "total": 0, "requests": 0, "cost_usd": 0.0
    }))
    
    # Cost per 1K tokens (estimates)
    COST_PER_1K = {
        "cometapi": {"input": 0.0001, "output": 0.0002},  # Free tier mostly
        "novita": {"input": 0.0005, "output": 0.001},
        "aiml": {"input": 0.001, "output": 0.002},
    }
    
    @property
    def token_efficiency(self) -> float:
        """Output tokens per input token (higher = more efficient responses)"""
        if self.total_input_tokens == 0:
            return 0.0
        return self.total_output_tokens / self.total_input_tokens
    
    @property
    def avg_tokens_per_request(self) -> float:
        """Average tokens used per request"""
        if self.total_requests == 0:
            return 0.0
        return self.total_tokens / self.total_requests
    
    @property
    def estimated_cost_usd(self) -> float:
        """Estimated total cost across all providers"""
        total_cost = 0.0
        for provider, stats in self.provider_tokens.items():
            if isinstance(stats, dict):
                total_cost += stats.get("cost_usd", 0.0)
        return total_cost
    
    @property
    def success_rate(self) -> float:
        """LLM request success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def to_dict(self) -> dict:
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "token_efficiency": round(self.token_efficiency, 3),
            "avg_tokens_per_request": round(self.avg_tokens_per_request, 1),
            "estimated_cost_usd": round(self.estimated_cost_usd, 4),
            "success_rate": round(self.success_rate, 2),
            "by_provider": dict(self.provider_tokens),
        }


class MetricsCollector:
    """
    Centralized metrics collection for all CodeShield features.
    
    Provides:
    - Real-time statistics
    - Persistent storage for historical data
    - Transparent, verifiable metrics
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if MetricsCollector._initialized:
            return
        
        self.trustgate = TrustGateMetrics()
        self.styleforge = StyleForgeMetrics()
        self.contextvault = ContextVaultMetrics()
        self.tokens = TokenMetrics()
        
        self._session_start = datetime.now()
        self._ensure_db()
        self._load_from_db()
        
        MetricsCollector._initialized = True
    
    def _ensure_db(self):
        """Ensure database exists with schema"""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics_snapshot (
                category TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_from_db(self):
        """Load persisted metrics"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            cursor.execute("SELECT category, data FROM metrics_snapshot")
            rows = cursor.fetchall()
            
            for category, data_json in rows:
                data = json.loads(data_json)
                if category == "trustgate":
                    for k, v in data.items():
                        if hasattr(self.trustgate, k) and not k.startswith("_"):
                            setattr(self.trustgate, k, v)
                elif category == "styleforge":
                    for k, v in data.items():
                        if hasattr(self.styleforge, k) and not k.startswith("_"):
                            setattr(self.styleforge, k, v)
                elif category == "contextvault":
                    for k, v in data.items():
                        if hasattr(self.contextvault, k) and not k.startswith("_"):
                            setattr(self.contextvault, k, v)
                elif category == "tokens":
                    for k, v in data.items():
                        if hasattr(self.tokens, k) and not k.startswith("_") and k != "provider_tokens":
                            setattr(self.tokens, k, v)
            
            conn.close()
        except Exception as e:
            print(f"Warning: Could not load metrics: {e}")
    
    def _save_to_db(self):
        """Persist current metrics"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            snapshots = [
                ("trustgate", json.dumps(asdict(self.trustgate))),
                ("styleforge", json.dumps(asdict(self.styleforge))),
                ("contextvault", json.dumps(asdict(self.contextvault))),
                ("tokens", json.dumps({
                    "total_input_tokens": self.tokens.total_input_tokens,
                    "total_output_tokens": self.tokens.total_output_tokens,
                    "total_tokens": self.tokens.total_tokens,
                    "total_requests": self.tokens.total_requests,
                    "successful_requests": self.tokens.successful_requests,
                    "failed_requests": self.tokens.failed_requests,
                })),
            ]
            
            for category, data in snapshots:
                cursor.execute("""
                    INSERT OR REPLACE INTO metrics_snapshot (category, data, updated_at)
                    VALUES (?, ?, ?)
                """, (category, data, now))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")
    
    @contextmanager
    def track_time(self, category: str):
        """Context manager to track processing time"""
        start = time.time()
        yield
        elapsed_ms = int((time.time() - start) * 1000)
        
        with _metrics_lock:
            if category == "trustgate":
                self.trustgate.total_processing_time_ms += elapsed_ms
            elif category == "styleforge":
                self.styleforge.total_processing_time_ms += elapsed_ms
    
    # TrustGate tracking
    def track_verification(self, syntax_error: bool = False, missing_imports: int = 0, 
                          undefined_names: int = 0, auto_fixed: bool = False):
        """Track a TrustGate verification"""
        with _metrics_lock:
            self.trustgate.total_verifications += 1
            if syntax_error:
                self.trustgate.syntax_errors_detected += 1
            self.trustgate.missing_imports_detected += missing_imports
            self.trustgate.undefined_names_detected += undefined_names
            if auto_fixed:
                self.trustgate.auto_fixes_applied += 1
            self._save_to_db()
    
    def track_sandbox(self, success: bool):
        """Track a sandbox execution"""
        with _metrics_lock:
            self.trustgate.sandbox_executions += 1
            if success:
                self.trustgate.sandbox_successes += 1
            else:
                self.trustgate.sandbox_failures += 1
            self._save_to_db()
    
    # StyleForge tracking
    def track_style_check(self, conventions_found: int = 0, issues_found: int = 0,
                         corrections_suggested: int = 0, corrections_applied: int = 0):
        """Track a StyleForge check"""
        with _metrics_lock:
            self.styleforge.total_checks += 1
            self.styleforge.conventions_detected += conventions_found
            self.styleforge.naming_issues_found += issues_found
            self.styleforge.corrections_suggested += corrections_suggested
            self.styleforge.corrections_applied += corrections_applied
            self._save_to_db()
    
    def track_codebase_analyzed(self):
        """Track a codebase analysis"""
        with _metrics_lock:
            self.styleforge.codebases_analyzed += 1
            self._save_to_db()
    
    # ContextVault tracking
    def track_context_save(self, files_count: int = 0):
        """Track a context save"""
        with _metrics_lock:
            self.contextvault.total_contexts_saved += 1
            self.contextvault.total_files_tracked += files_count
            self._save_to_db()
    
    def track_context_restore(self, success: bool):
        """Track a context restore"""
        with _metrics_lock:
            self.contextvault.total_contexts_restored += 1
            if success:
                self.contextvault.restore_successes += 1
            else:
                self.contextvault.restore_failures += 1
            self._save_to_db()
    
    def track_context_delete(self):
        """Track a context deletion"""
        with _metrics_lock:
            self.contextvault.contexts_deleted += 1
            self._save_to_db()
    
    # Token tracking
    def track_tokens(self, provider: str, input_tokens: int, output_tokens: int, 
                    success: bool = True):
        """Track LLM token usage"""
        with _metrics_lock:
            self.tokens.total_input_tokens += input_tokens
            self.tokens.total_output_tokens += output_tokens
            self.tokens.total_tokens += input_tokens + output_tokens
            self.tokens.total_requests += 1
            
            if success:
                self.tokens.successful_requests += 1
            else:
                self.tokens.failed_requests += 1
            
            # Provider-specific tracking
            if provider not in self.tokens.provider_tokens:
                self.tokens.provider_tokens[provider] = {
                    "input": 0, "output": 0, "total": 0, "requests": 0, "cost_usd": 0.0
                }
            
            stats = self.tokens.provider_tokens[provider]
            stats["input"] += input_tokens
            stats["output"] += output_tokens
            stats["total"] += input_tokens + output_tokens
            stats["requests"] += 1
            
            # Estimate cost
            costs = self.tokens.COST_PER_1K.get(provider, {"input": 0.001, "output": 0.002})
            stats["cost_usd"] += (input_tokens / 1000) * costs["input"]
            stats["cost_usd"] += (output_tokens / 1000) * costs["output"]
            
            self._save_to_db()
    
    def get_summary(self) -> dict:
        """Get comprehensive metrics summary"""
        session_duration = (datetime.now() - self._session_start).total_seconds()
        
        return {
            "session": {
                "started_at": self._session_start.isoformat(),
                "duration_seconds": round(session_duration, 2),
                "duration_human": str(timedelta(seconds=int(session_duration))),
            },
            "trustgate": self.trustgate.to_dict(),
            "styleforge": self.styleforge.to_dict(),
            "contextvault": self.contextvault.to_dict(),
            "tokens": self.tokens.to_dict(),
            "totals": {
                "total_operations": (
                    self.trustgate.total_verifications +
                    self.styleforge.total_checks +
                    self.contextvault.total_contexts_saved +
                    self.contextvault.total_contexts_restored +
                    self.tokens.total_requests
                ),
                "total_issues_detected": (
                    self.trustgate.syntax_errors_detected +
                    self.trustgate.missing_imports_detected +
                    self.trustgate.undefined_names_detected +
                    self.styleforge.naming_issues_found
                ),
                "total_auto_fixes": (
                    self.trustgate.auto_fixes_applied +
                    self.styleforge.corrections_applied
                ),
            },
        }
    
    def reset(self):
        """Reset all metrics (for testing)"""
        with _metrics_lock:
            self.trustgate = TrustGateMetrics()
            self.styleforge = StyleForgeMetrics()
            self.contextvault = ContextVaultMetrics()
            self.tokens = TokenMetrics()
            self._session_start = datetime.now()


# Singleton instance
def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return MetricsCollector()


# Convenience decorators for automatic tracking
def track_trustgate_verification(func):
    """Decorator to track TrustGate verifications"""
    def wrapper(*args, **kwargs):
        metrics = get_metrics()
        with metrics.track_time("trustgate"):
            result = func(*args, **kwargs)
        
        # Extract metrics from result if it has the right attributes
        if hasattr(result, 'issues'):
            syntax_error = any(i.severity == "error" and "Syntax" in i.message for i in result.issues)
            missing_imports = sum(1 for i in result.issues if "Missing import" in i.message)
            undefined = sum(1 for i in result.issues if "undefined" in i.message.lower())
            auto_fixed = result.fixed_code is not None
            
            metrics.track_verification(
                syntax_error=syntax_error,
                missing_imports=missing_imports,
                undefined_names=undefined,
                auto_fixed=auto_fixed
            )
        
        return result
    return wrapper


def track_styleforge_check(func):
    """Decorator to track StyleForge checks"""
    def wrapper(*args, **kwargs):
        metrics = get_metrics()
        with metrics.track_time("styleforge"):
            result = func(*args, **kwargs)
        
        if hasattr(result, 'issues'):
            metrics.track_style_check(
                conventions_found=len(result.conventions_detected) if hasattr(result, 'conventions_detected') else 0,
                issues_found=len(result.issues),
                corrections_suggested=len(result.issues),
                corrections_applied=1 if result.corrected_code else 0
            )
        
        return result
    return wrapper
