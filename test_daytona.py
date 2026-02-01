"""Test Daytona with real API key"""

import os
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

from daytona import Daytona, DaytonaConfig

print("Testing Daytona Sandbox...")
print(f"API Key: {os.getenv('DAYTONA_API_KEY')[:20]}...")

try:
    # Initialize with API key
    config = DaytonaConfig(api_key=os.getenv('DAYTONA_API_KEY'))
    daytona = Daytona(config)
    
    print("Creating sandbox...")
    sandbox = daytona.create()
    print(f"✓ Sandbox created: {sandbox.id if hasattr(sandbox, 'id') else 'OK'}")
    
    print("Running code...")
    response = sandbox.process.code_run('print("Hello from Daytona!")')
    print(f"✓ Exit code: {response.exit_code}")
    print(f"✓ Output: {response.result}")
    
    print("Cleaning up...")
    daytona.delete(sandbox)
    print("✓ Sandbox deleted")
    
    print("\n✅ Daytona integration working!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
