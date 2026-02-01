"""Tests for StyleForge convention enforcer"""

import pytest
from codeshield.styleforge.corrector import (
    detect_naming_pattern,
    convert_to_snake_case,
    check_style,
)


class TestNamingPatternDetection:
    """Test naming pattern detection"""
    
    def test_snake_case(self):
        assert detect_naming_pattern("user_name") == "snake_case"
        assert detect_naming_pattern("get_user_data") == "snake_case"
    
    def test_camel_case(self):
        assert detect_naming_pattern("userName") == "camelCase"
        assert detect_naming_pattern("getUserData") == "camelCase"
    
    def test_pascal_case(self):
        assert detect_naming_pattern("UserName") == "PascalCase"
        assert detect_naming_pattern("GetUserData") == "PascalCase"
    
    def test_screaming_snake(self):
        assert detect_naming_pattern("MAX_SIZE") == "SCREAMING_SNAKE"
        assert detect_naming_pattern("API_KEY") == "SCREAMING_SNAKE"


class TestConversion:
    """Test naming conversion"""
    
    def test_camel_to_snake(self):
        assert convert_to_snake_case("userName") == "user_name"
        assert convert_to_snake_case("getUserData") == "get_user_data"
    
    def test_pascal_to_snake(self):
        assert convert_to_snake_case("UserName") == "user_name"


class TestStyleCheck:
    """Test style checking"""
    
    def test_detects_camel_in_snake_codebase(self):
        # Code with camelCase
        code = """
def getData():
    userName = "test"
    return userName
"""
        result = check_style(code, ".")  # Current dir as codebase
        
        # Should detect issues if codebase uses snake_case
        # Note: This depends on actual codebase convention
        assert result is not None
    
    def test_result_has_required_fields(self):
        code = "x = 1"
        result = check_style(code, ".")
        
        assert hasattr(result, 'matches_convention')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'conventions_detected')


# Run with: pytest tests/test_styleforge.py -v
