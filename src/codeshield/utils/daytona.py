"""
Daytona SDK Wrapper - Sandboxed code execution

Uses Daytona's secure sandbox environment to:
- Execute untrusted/AI-generated code safely
- Verify code actually runs without side effects
- Capture execution results and errors
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of code execution in sandbox"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
        }


class DaytonaClient:
    """Client for Daytona sandbox execution"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DAYTONA_API_KEY")
        self.api_url = api_url or os.getenv("DAYTONA_API_URL", "https://app.daytona.io/api")
        self._client = None
        self._sandbox = None
    
    def _ensure_sdk(self):
        """Ensure Daytona SDK is available"""
        try:
            # Official SDK import (pip install daytona)
            from daytona import Daytona, DaytonaConfig
            return Daytona, DaytonaConfig
        except ImportError:
            try:
                # Alternative import (pip install daytona-sdk)
                from daytona_sdk import Daytona, DaytonaConfig
                return Daytona, DaytonaConfig
            except ImportError:
                return None, None
    
    def is_available(self) -> bool:
        """Check if Daytona is available and configured"""
        Daytona, _ = self._ensure_sdk()
        return Daytona is not None and self.api_key is not None
    
    def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout_seconds: int = 30,
    ) -> ExecutionResult:
        """
        Execute code in Daytona sandbox.
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, etc.)
            timeout_seconds: Maximum execution time
        
        Returns:
            ExecutionResult with stdout, stderr, and status
        """
        Daytona, SandboxConfig = self._ensure_sdk()
        
        if Daytona is None:
            # Fallback to local execution with safety measures
            return self._local_execute(code, language, timeout_seconds)
        
        if not self.api_key:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error="DAYTONA_API_KEY not configured",
            )
        
        try:
            # Get SDK classes
            Daytona, DaytonaConfig = self._ensure_sdk()
            
            if Daytona is None:
                return self._local_execute(code, language, timeout_seconds)
            
            # Initialize Daytona client with config (official SDK pattern)
            config = DaytonaConfig(api_key=self.api_key)
            daytona = Daytona(config)
            
            # Create sandbox
            sandbox = daytona.create()
            
            try:
                # Execute code in sandbox
                response = sandbox.process.code_run(code)
                
                return ExecutionResult(
                    success=response.exit_code == 0,
                    stdout=response.result or "",
                    stderr="",
                    exit_code=response.exit_code,
                    execution_time_ms=0,
                )
            finally:
                # Clean up sandbox
                daytona.delete(sandbox)
                
        except Exception as e:
            # Fall back to local execution if Daytona fails
            print(f"Daytona error: {e}, falling back to local execution")
            return self._local_execute(code, language, timeout_seconds)
    
    def _local_execute(
        self,
        code: str,
        language: str,
        timeout_seconds: int,
    ) -> ExecutionResult:
        """
        Fallback local execution with safety measures.
        
        WARNING: This is less safe than Daytona. Use only for demo/testing.
        """
        import subprocess
        import tempfile
        import time
        
        if language != "python":
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error=f"Local execution only supports Python, got: {language}",
            )
        
        # Write code to temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            start_time = time.time()
            
            # Execute with timeout
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time_ms=execution_time,
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error=f"Execution timed out after {timeout_seconds}s",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                error=f"Local execution failed: {e}",
            )
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def verify_code_runs(self, code: str) -> tuple[bool, str]:
        """
        Quick verification that code runs without error.
        
        Returns:
            Tuple of (success, message)
        """
        result = self.execute_code(code, timeout_seconds=10)
        
        if result.success:
            return True, "Code executed successfully"
        else:
            error_msg = result.stderr or result.error or "Unknown error"
            return False, f"Execution failed: {error_msg}"


# Singleton instance
_daytona_client: Optional[DaytonaClient] = None


def get_daytona_client() -> DaytonaClient:
    """Get or create Daytona client singleton"""
    global _daytona_client
    if _daytona_client is None:
        _daytona_client = DaytonaClient()
    return _daytona_client
