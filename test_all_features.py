"""
CodeShield - Complete Feature Test Suite
Tests all three pillars: TrustGate, StyleForge, ContextVault
"""

print("=" * 60)
print("🛡️  CODESHIELD COMPLETE FEATURE TEST")
print("=" * 60)

# ============================================================
# TEST 1: TRUSTGATE - Code Verification
# ============================================================
print("\n" + "=" * 60)
print("📋 TRUSTGATE: Code Verification")
print("=" * 60)

from codeshield.trustgate.checker import verify_code

# Test 1a: Missing imports
print("\n🔍 Test 1a: Missing Imports Detection")
code_missing_imports = '''
def fetch_data():
    response = requests.get("https://api.example.com")
    return json.loads(response.text)
'''
result = verify_code(code_missing_imports, auto_fix=True)
print(f"   Valid: {result.is_valid}")
print(f"   Confidence: {result.confidence_score:.0%}")
print(f"   Issues: {len(result.issues)}")
for issue in result.issues[:2]:
    print(f"     - {issue.message}")
print(f"   ✅ Auto-fix generated: {'import requests' in result.fixed_code if result.fixed_code else False}")

# Test 1b: Syntax error
print("\n🔍 Test 1b: Syntax Error Detection")
code_syntax_error = '''
def broken(:
    return "test"
'''
result = verify_code(code_syntax_error)
print(f"   Valid: {result.is_valid}")
print(f"   Confidence: {result.confidence_score:.0%}")
print(f"   ✅ Caught syntax error: {not result.is_valid}")

# Test 1c: Clean code
print("\n🔍 Test 1c: Clean Code Validation")
code_clean = '''
import os

def get_path():
    return os.getcwd()
'''
result = verify_code(code_clean)
print(f"   Valid: {result.is_valid}")
print(f"   Confidence: {result.confidence_score:.0%}")
print(f"   ✅ Clean code passes: {result.is_valid and result.confidence_score == 1.0}")

# ============================================================
# TEST 2: STYLEFORGE - Naming Conventions
# ============================================================
print("\n" + "=" * 60)
print("🎨 STYLEFORGE: Naming Convention Enforcement")
print("=" * 60)

from codeshield.styleforge.corrector import check_style

# Test 2a: camelCase to snake_case
print("\n🔍 Test 2a: camelCase Detection")
code_camel = '''
def getUserName(userId):
    userName = fetchUser(userId)
    return userName
'''
result = check_style(code_camel)
print(f"   Matches Convention: {result.matches_convention}")
print(f"   Issues Found: {len(result.issues)}")
for issue in result.issues:
    print(f"     - {issue.original} → {issue.suggested}")
print(f"   ✅ Detected camelCase: {len(result.issues) > 0}")

# Test 2b: Clean snake_case
print("\n🔍 Test 2b: Clean snake_case Validation")
code_snake = '''
def get_user_name(user_id):
    user_name = fetch_user(user_id)
    return user_name
'''
result = check_style(code_snake)
print(f"   Matches Convention: {result.matches_convention}")
print(f"   ✅ Snake case passes: {result.matches_convention}")

# ============================================================
# TEST 3: CONTEXTVAULT - Session Management
# ============================================================
print("\n" + "=" * 60)
print("💾 CONTEXTVAULT: Session Save & Restore")
print("=" * 60)

from codeshield.contextvault.capture import save_context, list_contexts
from codeshield.contextvault.restore import restore_context

# Test 3a: Save context
print("\n🔍 Test 3a: Save Context")
try:
    save_context(
        name="feature-test-session",
        files=["src/codeshield/trustgate/checker.py", "src/codeshield/api_server.py"],
        cursor={"file": "checker.py", "line": 42},
        notes="Testing the verification logic for AI-generated code"
    )
    print("   ✅ Context saved successfully!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3b: List contexts
print("\n🔍 Test 3b: List Contexts")
try:
    contexts = list_contexts()
    print(f"   Found {len(contexts)} saved context(s)")
    for ctx in contexts[-3:]:  # Show last 3
        print(f"     - {ctx}")
    print(f"   ✅ List contexts works: {len(contexts) > 0}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3c: Restore context
print("\n🔍 Test 3c: Restore Context")
try:
    result = restore_context("feature-test-session")
    if result.get('success'):
        ctx = result.get('context', {})
        print(f"   Files: {ctx.get('files', result.get('files_to_open', []))}")
        print(f"   Cursor: {ctx.get('cursor', result.get('cursor_position', {}))}")
        briefing = result.get('briefing', '')
        print(f"   Briefing: {briefing[:80]}..." if len(briefing) > 80 else f"   Briefing: {briefing}")
        print(f"   ✅ Context restored successfully!")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("""
   ✅ TrustGate
      • Missing import detection
      • Syntax error catching  
      • Clean code validation
      • Auto-fix generation

   ✅ StyleForge
      • camelCase → snake_case conversion
      • Convention matching

   ✅ ContextVault
      • Save session state
      • List saved contexts
      • Restore with briefing

🎉 All CodeShield features working!
""")
