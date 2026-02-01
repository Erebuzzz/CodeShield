"""Test API integrations with real keys"""

import os
import sys

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

sys.path.insert(0, 'src')

print("=" * 50)
print("Testing API Integrations")
print("=" * 50)

# Test 1: Check environment variables
print("\n1. Environment Variables:")
print(f"   DAYTONA_API_KEY: {'✓ Set' if os.getenv('DAYTONA_API_KEY') else '✗ Missing'}")
print(f"   COMETAPI_KEY: {'✓ Set' if os.getenv('COMETAPI_KEY') else '✗ Missing'}")
print(f"   AIML_API_KEY: {'✓ Set' if os.getenv('AIML_API_KEY') else '✗ Missing'}")
print(f"   LEANMCP_KEY: {'✓ Set' if os.getenv('LEANMCP_KEY') else '✗ Missing'}")
print(f"   OLACV_API_KEY: {'✓ Set' if os.getenv('OLACV_API_KEY') else '✗ Missing'}")

# Test 2: Test LLM Client
print("\n2. Testing LLM Client (CometAPI):")
try:
    from codeshield.utils.llm import LLMClient
    client = LLMClient()
    
    response = client.chat(
        prompt="Say 'CodeShield works!' in exactly 3 words.",
        max_tokens=20
    )
    
    if response:
        print(f"   ✓ Response: {response.content}")
        print(f"   ✓ Provider: {response.provider}")
        print(f"   ✓ Model: {response.model}")
    else:
        print("   ✗ No response from LLM")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Test Daytona (if SDK installed)
print("\n3. Testing Daytona Sandbox:")
try:
    from codeshield.utils.daytona import DaytonaClient
    daytona = DaytonaClient()
    
    if daytona.is_available():
        print("   ✓ Daytona SDK available")
        result = daytona.execute_code("print('Hello from Daytona!')")
        print(f"   ✓ Execution result: {result.stdout.strip()}")
    else:
        print("   ⚠ Daytona SDK not installed, using local fallback")
        result = daytona.execute_code("print('Hello from local!')")
        print(f"   ✓ Local execution: {result.stdout.strip()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 50)
print("API Integration Tests Complete!")
print("=" * 50)
