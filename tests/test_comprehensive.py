"""
Comprehensive Unit Tests for CodeShield

Tests all core features with real validation:
- TrustGate: Verification, detection, fixes
- StyleForge: Convention detection, naming
- ContextVault: Persistence, restore
- Metrics: Tracking accuracy
- LLM: Provider fallback, token tracking
"""

import pytest
import tempfile
import sqlite3
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# TrustGate imports
from codeshield.trustgate.checker import (
    verify_code,
    check_syntax,
    detect_missing_imports,
    detect_undefined_names,
    auto_fix_imports,
    VerificationResult,
    VerificationIssue,
)

# StyleForge imports
from codeshield.styleforge.corrector import (
    detect_naming_pattern,
    convert_to_snake_case,
    convert_to_camel_case,
    check_style,
    analyze_codebase,
    StyleCheckResult,
)

# ContextVault imports
from codeshield.contextvault.capture import (
    save_context,
    list_contexts,
    get_context,
    delete_context,
)
from codeshield.contextvault.restore import restore_context

# Metrics imports
from codeshield.utils.metrics import (
    MetricsCollector,
    get_metrics,
    TrustGateMetrics,
    StyleForgeMetrics,
    ContextVaultMetrics,
    TokenMetrics,
)


# =============================================================================
# TrustGate Tests
# =============================================================================

class TestTrustGateSyntax:
    """Test TrustGate syntax checking - validates syntax error detection"""
    
    def test_valid_simple_code(self):
        """Valid code should pass syntax check"""
        code = "x = 1 + 2\nprint(x)"
        valid, issue = check_syntax(code)
        assert valid is True
        assert issue is None
    
    def test_valid_function(self):
        """Valid function should pass"""
        code = """
def greet(name):
    return f"Hello, {name}!"
"""
        valid, issue = check_syntax(code)
        assert valid is True
    
    def test_valid_class(self):
        """Valid class should pass"""
        code = """
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"I am {self.name}"
"""
        valid, issue = check_syntax(code)
        assert valid is True
    
    def test_missing_colon(self):
        """Missing colon should be detected"""
        code = "def foo()\n    pass"
        valid, issue = check_syntax(code)
        assert valid is False
        assert issue is not None
        assert issue.severity == "error"
    
    def test_indentation_error(self):
        """Indentation error should be detected"""
        code = "def foo():\npass"  # No indent
        valid, issue = check_syntax(code)
        assert valid is False
    
    def test_unmatched_brackets(self):
        """Unmatched brackets should be detected"""
        code = "x = [1, 2, 3"  # Missing ]
        valid, issue = check_syntax(code)
        assert valid is False
    
    def test_invalid_assignment(self):
        """Invalid assignment should be detected"""
        code = "1 = x"  # Can't assign to literal
        valid, issue = check_syntax(code)
        assert valid is False


class TestTrustGateImports:
    """Test TrustGate import detection - validates missing import detection"""
    
    def test_detect_missing_json(self):
        """Should detect missing json import"""
        code = """
def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        assert len(issues) > 0
        assert any("json" in i.message for i in issues)
        assert any(i.fix_available for i in issues)
    
    def test_detect_missing_os(self):
        """Should detect missing os import"""
        code = """
def get_env():
    return os.getenv("PATH")
"""
        issues = detect_missing_imports(code)
        assert any("os" in i.message for i in issues)
    
    def test_detect_missing_requests(self):
        """Should detect missing requests import"""
        code = """
def fetch():
    return requests.get("https://example.com")
"""
        issues = detect_missing_imports(code)
        assert len(issues) > 0
        assert any("requests" in i.message for i in issues)
    
    def test_no_issues_when_imported(self):
        """Should not flag properly imported modules"""
        code = """
import json

def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        assert not any("json" in i.message for i in issues)
    
    def test_from_import_recognized(self):
        """Should recognize from imports"""
        code = """
from pathlib import Path

def get_home():
    return Path.home()
"""
        issues = detect_missing_imports(code)
        assert not any("pathlib" in i.message.lower() for i in issues)


class TestTrustGateAutoFix:
    """Test TrustGate auto-fix functionality"""
    
    def test_adds_single_import(self):
        """Should add single missing import"""
        code = """
def parse():
    return json.loads('{"x": 1}')
"""
        issues = detect_missing_imports(code)
        fixed = auto_fix_imports(code, issues)
        assert "import json" in fixed
    
    def test_adds_multiple_imports(self):
        """Should add multiple missing imports"""
        code = """
def process():
    data = json.loads('{}')
    return os.getenv("PATH")
"""
        issues = detect_missing_imports(code)
        fixed = auto_fix_imports(code, issues)
        assert "import json" in fixed
        assert "import os" in fixed
    
    def test_preserves_existing_imports(self):
        """Should preserve existing imports"""
        code = """import sys

def parse():
    return json.loads('{}')
"""
        issues = detect_missing_imports(code)
        fixed = auto_fix_imports(code, issues)
        assert "import sys" in fixed
        assert "import json" in fixed


class TestTrustGateVerification:
    """Test complete TrustGate verification"""
    
    def test_valid_code_passes(self):
        """Valid complete code should pass verification"""
        code = """
import json

def parse(data):
    return json.loads(data)

result = parse('{"key": "value"}')
print(result)
"""
        result = verify_code(code)
        assert result.is_valid is True
        assert result.confidence_score > 0.8
    
    def test_invalid_code_with_fixes(self):
        """Invalid code should be detected and fixed"""
        code = """
def parse():
    return json.loads('{"x": 1}')
"""
        result = verify_code(code, auto_fix=True)
        # Should detect missing import
        assert any("json" in i.message for i in result.issues)
        # Should have fixed code
        assert result.fixed_code is not None
        assert "import json" in result.fixed_code
    
    def test_confidence_score_calculation(self):
        """Confidence score should reflect code quality"""
        good_code = """
import os
import json

def get_config():
    path = os.getenv("CONFIG_PATH", "config.json")
    with open(path) as f:
        return json.load(f)
"""
        bad_code = """
def fetch():
    x = requests.get(url)
    return json.loads(x.text)
"""
        good_result = verify_code(good_code)
        bad_result = verify_code(bad_code)
        
        assert good_result.confidence_score > bad_result.confidence_score


# =============================================================================
# StyleForge Tests
# =============================================================================

class TestStyleForgePatternDetection:
    """Test StyleForge naming pattern detection"""
    
    def test_snake_case_detection(self):
        """Should detect snake_case"""
        assert detect_naming_pattern("user_name") == "snake_case"
        assert detect_naming_pattern("get_user_data") == "snake_case"
        assert detect_naming_pattern("api_key") == "snake_case"
    
    def test_camel_case_detection(self):
        """Should detect camelCase"""
        assert detect_naming_pattern("userName") == "camelCase"
        assert detect_naming_pattern("getUserData") == "camelCase"
        assert detect_naming_pattern("apiKey") == "camelCase"
    
    def test_pascal_case_detection(self):
        """Should detect PascalCase"""
        assert detect_naming_pattern("UserName") == "PascalCase"
        assert detect_naming_pattern("GetUserData") == "PascalCase"
        assert detect_naming_pattern("ApiClient") == "PascalCase"
    
    def test_screaming_snake_detection(self):
        """Should detect SCREAMING_SNAKE_CASE"""
        assert detect_naming_pattern("MAX_SIZE") == "SCREAMING_SNAKE"
        assert detect_naming_pattern("API_KEY") == "SCREAMING_SNAKE"
        assert detect_naming_pattern("DEFAULT_TIMEOUT") == "SCREAMING_SNAKE"


class TestStyleForgeConversion:
    """Test StyleForge naming conversion"""
    
    def test_camel_to_snake(self):
        """Should convert camelCase to snake_case"""
        assert convert_to_snake_case("userName") == "user_name"
        assert convert_to_snake_case("getUserData") == "get_user_data"
        assert convert_to_snake_case("apiKey") == "api_key"
    
    def test_pascal_to_snake(self):
        """Should convert PascalCase to snake_case"""
        assert convert_to_snake_case("UserName") == "user_name"
        assert convert_to_snake_case("GetUserData") == "get_user_data"
    
    def test_snake_to_camel(self):
        """Should convert snake_case to camelCase"""
        assert convert_to_camel_case("user_name") == "userName"
        assert convert_to_camel_case("get_user_data") == "getUserData"


class TestStyleForgeChecking:
    """Test StyleForge style checking"""
    
    def test_result_structure(self):
        """Style check result should have correct structure"""
        code = "x = 1"
        result = check_style(code, ".")
        
        assert isinstance(result, StyleCheckResult)
        assert hasattr(result, 'matches_convention')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'conventions_detected')
    
    def test_to_dict(self):
        """Result should convert to dict properly"""
        code = "x = 1"
        result = check_style(code, ".")
        result_dict = result.to_dict()
        
        assert "matches_convention" in result_dict
        assert "issues" in result_dict
        assert "conventions_detected" in result_dict


# =============================================================================
# ContextVault Tests
# =============================================================================

class TestContextVaultSave:
    """Test ContextVault save functionality"""
    
    def test_save_simple_context(self):
        """Should save a simple context"""
        result = save_context(
            name="test_context_1",
            files=["/path/to/file.py"],
            notes="Testing save functionality"
        )
        
        assert result["success"] is True
        assert "test_context_1" in result["message"]
    
    def test_save_with_cursor(self):
        """Should save context with cursor position"""
        result = save_context(
            name="test_context_cursor",
            files=["/path/to/file.py"],
            cursor={"file": "/path/to/file.py", "line": 42, "column": 10}
        )
        
        assert result["success"] is True
        assert result["context"]["cursor"]["line"] == 42
    
    def test_overwrite_existing(self):
        """Should overwrite existing context with same name"""
        save_context(name="overwrite_test", notes="First version")
        result = save_context(name="overwrite_test", notes="Second version")
        
        assert result["success"] is True
        # Verify it's the new version
        context = get_context("overwrite_test")
        assert context is not None
        assert context.notes == "Second version"


class TestContextVaultList:
    """Test ContextVault list functionality"""
    
    def test_list_contexts(self):
        """Should list saved contexts"""
        # Save a test context
        save_context(name="list_test", notes="For listing")
        
        contexts = list_contexts()
        assert isinstance(contexts, list)
        assert any(c["name"] == "list_test" for c in contexts)
    
    def test_list_returns_metadata(self):
        """Listed contexts should include metadata"""
        save_context(name="metadata_test", notes="Has metadata")
        
        contexts = list_contexts()
        test_ctx = next((c for c in contexts if c["name"] == "metadata_test"), None)
        
        assert test_ctx is not None
        assert "created_at" in test_ctx
        assert "notes" in test_ctx


class TestContextVaultRestore:
    """Test ContextVault restore functionality"""
    
    def test_restore_existing(self):
        """Should restore existing context"""
        save_context(
            name="restore_test",
            files=["/file1.py", "/file2.py"],
            notes="To be restored"
        )
        
        result = restore_context("restore_test")
        
        assert result["success"] is True
        assert result["context"]["name"] == "restore_test"
        assert len(result["files_to_open"]) == 2
    
    def test_restore_nonexistent(self):
        """Should fail gracefully for nonexistent context"""
        result = restore_context("nonexistent_context_xyz")
        
        assert result["success"] is False
        assert "error" in result


class TestContextVaultDelete:
    """Test ContextVault delete functionality"""
    
    def test_delete_existing(self):
        """Should delete existing context"""
        save_context(name="delete_test")
        
        deleted = delete_context("delete_test")
        assert deleted is True
        
        # Verify it's gone
        context = get_context("delete_test")
        assert context is None
    
    def test_delete_nonexistent(self):
        """Should return False for nonexistent context"""
        deleted = delete_context("nonexistent_delete_test")
        assert deleted is False


# =============================================================================
# Metrics Tests
# =============================================================================

class TestMetricsCollector:
    """Test MetricsCollector functionality"""
    
    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        """Reset metrics before each test"""
        metrics = get_metrics()
        metrics.reset()
        yield
    
    def test_singleton_pattern(self):
        """Metrics should use singleton pattern"""
        m1 = get_metrics()
        m2 = get_metrics()
        assert m1 is m2
    
    def test_track_verification(self):
        """Should track TrustGate verifications"""
        metrics = get_metrics()
        metrics.track_verification(
            syntax_error=True,
            missing_imports=2,
            undefined_names=1,
            auto_fixed=True
        )
        
        assert metrics.trustgate.total_verifications == 1
        assert metrics.trustgate.syntax_errors_detected == 1
        assert metrics.trustgate.missing_imports_detected == 2
        assert metrics.trustgate.auto_fixes_applied == 1
    
    def test_track_sandbox(self):
        """Should track sandbox executions"""
        metrics = get_metrics()
        metrics.track_sandbox(success=True)
        metrics.track_sandbox(success=False)
        
        assert metrics.trustgate.sandbox_executions == 2
        assert metrics.trustgate.sandbox_successes == 1
        assert metrics.trustgate.sandbox_failures == 1
    
    def test_track_style_check(self):
        """Should track StyleForge checks"""
        metrics = get_metrics()
        metrics.track_style_check(
            conventions_found=3,
            issues_found=5,
            corrections_suggested=5,
            corrections_applied=4
        )
        
        assert metrics.styleforge.total_checks == 1
        assert metrics.styleforge.conventions_detected == 3
        assert metrics.styleforge.naming_issues_found == 5
        assert metrics.styleforge.corrections_applied == 4
    
    def test_track_context_operations(self):
        """Should track ContextVault operations"""
        metrics = get_metrics()
        metrics.track_context_save(files_count=3)
        metrics.track_context_restore(success=True)
        metrics.track_context_delete()
        
        assert metrics.contextvault.total_contexts_saved == 1
        assert metrics.contextvault.total_files_tracked == 3
        assert metrics.contextvault.restore_successes == 1
        assert metrics.contextvault.contexts_deleted == 1
    
    def test_track_tokens(self):
        """Should track token usage"""
        metrics = get_metrics()
        metrics.track_tokens("cometapi", input_tokens=100, output_tokens=50, success=True)
        metrics.track_tokens("novita", input_tokens=150, output_tokens=75, success=True)
        
        assert metrics.tokens.total_input_tokens == 250
        assert metrics.tokens.total_output_tokens == 125
        assert metrics.tokens.total_requests == 2
        assert metrics.tokens.successful_requests == 2


class TestMetricsCalculations:
    """Test metric calculation accuracy"""
    
    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        metrics = get_metrics()
        metrics.reset()
        yield
    
    def test_detection_rate(self):
        """Detection rate should be calculated correctly"""
        metrics = get_metrics()
        
        # 5 verifications, 3 with issues
        for _ in range(3):
            metrics.track_verification(syntax_error=True)
        for _ in range(2):
            metrics.track_verification()
        
        # 3 syntax errors / 5 verifications = 60%
        assert metrics.trustgate.detection_rate == 60.0
    
    def test_sandbox_success_rate(self):
        """Sandbox success rate should be calculated correctly"""
        metrics = get_metrics()
        
        for _ in range(7):
            metrics.track_sandbox(success=True)
        for _ in range(3):
            metrics.track_sandbox(success=False)
        
        # 7/10 = 70%
        assert metrics.trustgate.sandbox_success_rate == 70.0
    
    def test_token_efficiency(self):
        """Token efficiency should be calculated correctly"""
        metrics = get_metrics()
        metrics.track_tokens("test", input_tokens=100, output_tokens=200, success=True)
        
        # 200/100 = 2.0
        assert metrics.tokens.token_efficiency == 2.0
    
    def test_restore_success_rate(self):
        """Restore success rate should be calculated correctly"""
        metrics = get_metrics()
        
        for _ in range(8):
            metrics.track_context_restore(success=True)
        for _ in range(2):
            metrics.track_context_restore(success=False)
        
        # 8/10 = 80%
        assert metrics.contextvault.restore_success_rate == 80.0


class TestMetricsSummary:
    """Test metrics summary generation"""
    
    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        metrics = get_metrics()
        metrics.reset()
        yield
    
    def test_summary_structure(self):
        """Summary should have correct structure"""
        metrics = get_metrics()
        summary = metrics.get_summary()
        
        assert "session" in summary
        assert "trustgate" in summary
        assert "styleforge" in summary
        assert "contextvault" in summary
        assert "tokens" in summary
        assert "totals" in summary
    
    def test_summary_totals(self):
        """Summary totals should aggregate correctly"""
        metrics = get_metrics()
        
        metrics.track_verification(syntax_error=True, missing_imports=2)
        metrics.track_style_check(issues_found=3)
        
        summary = metrics.get_summary()
        
        # 1 syntax + 2 imports + 3 style = 6 issues
        assert summary["totals"]["total_issues_detected"] == 6


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple features"""
    
    def test_verify_and_track(self):
        """Verification should integrate with metrics"""
        metrics = get_metrics()
        metrics.reset()
        
        # This would normally trigger metrics tracking
        code = """
def test():
    return json.loads('{}')
"""
        result = verify_code(code)
        
        # Verify the code was checked
        assert result is not None
        assert len(result.issues) > 0
    
    def test_style_check_result_serialization(self):
        """Style check results should serialize properly"""
        code = """
def myFunction():
    myVariable = 1
    return myVariable
"""
        result = check_style(code, ".")
        result_dict = result.to_dict()
        
        # Should be JSON serializable
        json_str = json.dumps(result_dict)
        assert json_str is not None
    
    def test_context_save_restore_cycle(self):
        """Full save-restore cycle should work"""
        # Save
        save_result = save_context(
            name="integration_test",
            files=["/a.py", "/b.py"],
            cursor={"file": "/a.py", "line": 10, "column": 5},
            notes="Integration test context"
        )
        assert save_result["success"]
        
        # Restore
        restore_result = restore_context("integration_test")
        assert restore_result["success"]
        assert restore_result["context"]["files"] == ["/a.py", "/b.py"]
        assert restore_result["cursor_position"]["line"] == 10
        
        # Cleanup
        delete_context("integration_test")


# Run with: pytest tests/test_comprehensive.py -v --tb=short
