"""
Code Interception Hooks

This module provides hooks that can be integrated into:
1. Pre-commit hooks (Git)
2. CI/CD pipelines
3. IDE save actions (if supported)

It serves as the entry point for automated code verification.
"""

import sys
import os
from pathlib import Path
from codeshield.trustgate.checker import verify_code, verify_file

def pre_commit_hook(files: list[str]) -> bool:
    """
    Git pre-commit hook: Verify all changed files.
    Returns True if verification passes, False otherwise.
    """
    print("🛡️ CodeShield Verification Hook Running...")
    
    all_passed = True
    
    for file_path in files:
        if not file_path.endswith('.py'):
            continue
            
        print(f"Checking {file_path}...")
        
        # Verify file
        try:
            result = verify_file(file_path)
            
            if not result.is_valid:
                all_passed = False
                print(f"❌ Issues in {file_path}:")
                for issue in result.issues:
                    print(f"  [{issue.severity}] {issue.message}")
            else:
                print(f"✅ {file_path} passed ({result.confidence_score:.0%} confidence)")
                
        except Exception as e:
            print(f"⚠️ Error checking {file_path}: {e}")
            all_passed = False
            
    return all_passed

def code_interceptor(code: str, source: str = "unknown") -> dict:
    """
    General purpose interceptor for any code snippet.
    Useful for IDE plugins or content scripts to verify code on the fly.
    """
    result = verify_code(code)
    return result.to_dict()

if __name__ == "__main__":
    # Example CLI usage: python -m codeshield.mcp.hooks file1.py file2.py
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        success = pre_commit_hook(files)
        sys.exit(0 if success else 1)
    else:
        print("Usage: python -m codeshield.mcp.hooks <file1> <file2> ...")
