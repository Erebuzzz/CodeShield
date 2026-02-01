"""Tests for TrustGate verification engine"""

import pytest
from codeshield.trustgate.checker import (
    verify_code,
    check_syntax,
    detect_missing_imports,
    auto_fix_imports,
    VerificationResult,
)


class TestSyntaxCheck:
    """Test syntax checking"""
    
    def test_valid_syntax(self):
        code = "x = 1 + 2\nprint(x)"
        valid, issue = check_syntax(code)
        assert valid is True
        assert issue is None
    
    def test_invalid_syntax_missing_colon(self):
        code = "def foo()\n    pass"
        valid, issue = check_syntax(code)
        assert valid is False
        assert issue is not None
        assert "Syntax error" in issue.message
    
    def test_invalid_syntax_indentation(self):
        code = "def foo():\npass"
        valid, issue = check_syntax(code)
        assert valid is False


class TestMissingImports:
    """Test missing import detection"""
    
    def test_detect_missing_json(self):
        code = """
def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        assert len(issues) > 0
        assert any("json" in i.message for i in issues)
    
    def test_detect_missing_requests(self):
        code = """
def fetch():
    return requests.get("https://example.com")
"""
        issues = detect_missing_imports(code)
        assert len(issues) > 0
        assert any("requests" in i.message for i in issues)
    
    def test_no_issues_when_imported(self):
        code = """
import json

def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        # No issues for json since it's imported
        assert not any("json" in i.message for i in issues)


class TestAutoFix:
    """Test auto-fix functionality"""
    
    def test_auto_fix_adds_import(self):
        code = """
def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        fixed = auto_fix_imports(code, issues)
        
        assert "import json" in fixed
    
    def test_auto_fix_preserves_existing(self):
        code = """import os

def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        fixed = auto_fix_imports(code, issues)
        
        assert "import os" in fixed
        assert "import json" in fixed


class TestVerifyCode:
    """Test main verification function"""
    
    def test_valid_code_returns_valid(self):
        code = """
import json

def parse(data):
    return json.loads(data)
"""
        result = verify_code(code)
        assert result.is_valid is True
        assert result.confidence_score > 0.5
    
    def test_broken_code_returns_issues(self):
        code = """
def fetch_data():
    response = requests.get("https://api.example.com")
    return json.loads(response.text)
"""
        result = verify_code(code)
        
        assert len(result.issues) > 0
        assert result.fixed_code is not None
        assert "import requests" in result.fixed_code
        assert "import json" in result.fixed_code
    
    def test_syntax_error_returns_invalid(self):
        code = "def foo(\n    pass"
        result = verify_code(code)
        
        assert result.is_valid is False
        assert result.confidence_score == 0.0


# Run with: pytest tests/test_trustgate.py -v
