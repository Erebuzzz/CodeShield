"""Test TrustGate sandbox execution"""

import sys
sys.path.insert(0, 'src')

from codeshield.trustgate.sandbox import verify_in_sandbox, full_verification

# Test 1: Simple working code
print("=" * 50)
print("TEST 1: Working code in sandbox")
print("=" * 50)

code = '''
x = 1 + 2
print(f"Result: {x}")
'''

result = verify_in_sandbox(code)
print(f"Executed: {result.executed}")
print(f"Runs successfully: {result.runs_successfully}")
print(f"Output: {result.output}")
print(f"Time: {result.execution_time_ms}ms")

# Test 2: Code with error
print("\n" + "=" * 50)
print("TEST 2: Code with runtime error")
print("=" * 50)

bad_code = '''
x = 1 / 0  # Division by zero
'''

result2 = verify_in_sandbox(bad_code)
print(f"Executed: {result2.executed}")
print(f"Runs successfully: {result2.runs_successfully}")
print(f"Error: {result2.error}")

# Test 3: Full verification pipeline
print("\n" + "=" * 50)
print("TEST 3: Full verification (static + sandbox)")
print("=" * 50)

code3 = '''
import json

data = json.loads('{"name": "test"}')
print(f"Loaded: {data}")
'''

result3 = full_verification(code3)
print(f"Overall valid: {result3['overall_valid']}")
print(f"Confidence: {result3['confidence_score']:.0%}")
print(f"Static issues: {len(result3['static_analysis']['issues'])}")
if result3['sandbox_execution']:
    print(f"Sandbox output: {result3['sandbox_execution']['output']}")

print("\n✅ Sandbox tests completed!")
