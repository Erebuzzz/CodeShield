"""Debug CometAPI integration"""

import os
import httpx
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

api_key = os.getenv("COMETAPI_KEY")
print(f"API Key: {api_key[:20]}..." if api_key else "No key found")

# Try different base URLs and models
configs = [
    ("https://api.cometapi.com/v1", "deepseek-chat"),
    ("https://api.cometapi.com/v1", "gpt-4o-mini"),
    ("https://api.cometapi.com", "deepseek-chat"),
]

client = httpx.Client(timeout=60.0)

for base_url, model in configs:
    print(f"\nTrying: {base_url} with {model}")
    try:
        response = client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say 'hello'"}],
                "max_tokens": 10,
            },
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response: {data['choices'][0]['message']['content']}")
            break
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
