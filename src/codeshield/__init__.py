"""
CodeShield - The Complete AI Coding Safety Net

Verify, Enforce, Remember - AI-powered code verification for safe development.

Example usage:
    >>> from codeshield import verify_code, check_style, full_verify
    >>> 
    >>> # Quick verification
    >>> result = verify_code("print('hello')")
    >>> print(result.is_valid)
    True
    >>> 
    >>> # Full verification with sandbox execution
    >>> result = full_verify("x = 1 + 2\\nprint(x)")
    >>> print(result['overall_valid'])
    True
"""

__version__ = "0.1.0"
__author__ = "CodeShield Team"
__license__ = "MIT"

# Core verification functions
from codeshield.trustgate.checker import verify_code, VerificationResult
from codeshield.trustgate.sandbox import full_verification as full_verify, SandboxVerification

# Style checking
from codeshield.styleforge.corrector import check_style, StyleCheckResult

# Context management
from codeshield.contextvault.capture import save_context, list_contexts, get_context
from codeshield.contextvault.restore import restore_context

# Utilities
from codeshield.utils.daytona import DaytonaClient, get_daytona_client
from codeshield.utils.llm import LLMClient, get_llm_client

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core verification
    "verify_code",
    "full_verify",
    "VerificationResult",
    "SandboxVerification",
    # Style
    "check_style",
    "StyleCheckResult",
    # Context
    "save_context",
    "restore_context",
    "list_contexts",
    "get_context",
    # Utilities
    "DaytonaClient",
    "get_daytona_client",
    "LLMClient",
    "get_llm_client",
]
