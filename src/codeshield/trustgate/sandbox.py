"""
TrustGate Sandbox - Daytona integration for code execution

Executes verified code in secure sandbox to confirm it actually runs.
"""

from typing import Optional
from dataclasses import dataclass

from codeshield.utils.daytona import get_daytona_client, ExecutionResult


@dataclass
class SandboxVerification:
    """Result of sandbox verification"""
    executed: bool
    runs_successfully: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int = 0
    
    def to_dict(self) -> dict:
        return {
            "executed": self.executed,
            "runs_successfully": self.runs_successfully,
            "output": self.output[:500] if self.output else "",  # Truncate long output
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


def verify_in_sandbox(
    code: str,
    timeout_seconds: int = 10,
) -> SandboxVerification:
    """
    Verify code runs successfully in sandbox.
    
    Args:
        code: Python code to verify
        timeout_seconds: Maximum execution time
    
    Returns:
        SandboxVerification with execution details
    """
    client = get_daytona_client()
    
    # Execute code
    result = client.execute_code(
        code=code,
        language="python",
        timeout_seconds=timeout_seconds,
    )
    
    return SandboxVerification(
        executed=True,
        runs_successfully=result.success,
        output=result.stdout,
        error=result.stderr if not result.success else None,
        execution_time_ms=result.execution_time_ms,
    )


def full_verification(code: str) -> dict:
    """
    Complete verification: syntax + imports + execution.
    
    Returns comprehensive verification report.
    """
    from codeshield.trustgate.checker import verify_code
    
    # Step 1: Static analysis
    static_result = verify_code(code, auto_fix=True)
    
    # Use fixed code if available
    code_to_run = static_result.fixed_code or code
    
    # Step 2: Sandbox execution (only if static checks pass)
    sandbox_result = None
    if static_result.is_valid or static_result.fixed_code:
        sandbox_result = verify_in_sandbox(code_to_run)
    
    # Build comprehensive report
    report = {
        "overall_valid": (
            static_result.is_valid and 
            (sandbox_result is None or sandbox_result.runs_successfully)
        ),
        "static_analysis": static_result.to_dict(),
        "sandbox_execution": sandbox_result.to_dict() if sandbox_result else None,
        "confidence_score": static_result.confidence_score,
        "fixed_code": static_result.fixed_code,
    }
    
    # Adjust confidence based on sandbox result
    if sandbox_result and sandbox_result.runs_successfully:
        report["confidence_score"] = min(1.0, report["confidence_score"] + 0.1)
    elif sandbox_result and not sandbox_result.runs_successfully:
        report["confidence_score"] = max(0.0, report["confidence_score"] - 0.2)
    
    return report
