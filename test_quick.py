"""Quick test script for CodeShield"""

import sys
sys.path.insert(0, 'src')

from codeshield.trustgate.checker import verify_code

# Test 1: Missing imports
print("=" * 50)
print("TEST 1: Missing imports")
print("=" * 50)

code = '''
def fetch_data():
    response = requests.get("https://api.example.com")
    return json.loads(response.text)
'''

result = verify_code(code)
print(f"Valid: {result.is_valid}")
print(f"Confidence: {result.confidence_score:.0%}")
print(f"Issues found: {len(result.issues)}")
for issue in result.issues:
    print(f"  [{issue.severity}] {issue.message}")
    if issue.fix_available:
        print(f"       Fix: {issue.fix_description}")

if result.fixed_code:
    print("\n--- Fixed Code ---")
    print(result.fixed_code)

# Test 2: Syntax error
print("\n" + "=" * 50)
print("TEST 2: Syntax error")
print("=" * 50)

bad_code = '''
def foo(
    pass
'''

result2 = verify_code(bad_code)
print(f"Valid: {result2.is_valid}")
print(f"Confidence: {result2.confidence_score:.0%}")
for issue in result2.issues:
    print(f"  [{issue.severity}] {issue.message}")

# Test 3: Clean code
print("\n" + "=" * 50)
print("TEST 3: Clean code")
print("=" * 50)

good_code = '''
import json

def parse_data(data: str) -> dict:
    return json.loads(data)
'''

result3 = verify_code(good_code)
print(f"Valid: {result3.is_valid}")
print(f"Confidence: {result3.confidence_score:.0%}")
print(f"Issues: {len(result3.issues)}")

print("\n✅ All tests completed!")
