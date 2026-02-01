"""
Script to verify the CodeShield demo scenarios by calling the Backend API.
"""

import requests
import json
import os

API_URL = "http://localhost:8000"

def test_trustgate():
    print("\n--- Testing TrustGate (Verification) ---")
    with open("examples/broken_code.py", "r") as f:
        code = f.read()
    
    print("Sending broken code...")
    response = requests.post(f"{API_URL}/api/verify", json={"code": code, "auto_fix": True})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Confidence: {result.get('confidence')}")
        print(f"Issues found: {len(result.get('issues', []))}")
        for issue in result.get('issues', []):
            print(f" - [{issue['type']}] {issue['message']}")
        
        if result.get('fixed_code'):
            print("\nAuto-fixed code generated!")
            # print(result['fixed_code'])
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_styleforge():
    print("\n--- Testing StyleForge (Conventions) ---")
    with open("examples/broken_code.py", "r") as f:
        code = f.read()
    
    # Use the examples directory as the codebase to scan
    codebase_path = os.path.abspath("examples")
    
    print(f"Checking style against codebase at: {codebase_path}")
    response = requests.post(f"{API_URL}/api/style", json={"code": code, "codebase_path": codebase_path})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Matches convention: {result.get('matches_convention')}")
        print(f"Suggestions: {len(result.get('suggestions', []))}")
        for suggestion in result.get('suggestions', []):
            print(f" - {suggestion}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        # Check if server is online
        requests.get(API_URL)
        test_trustgate()
        test_styleforge()
    except requests.exceptions.ConnectionError:
        print("Backend is offline. Please start it with 'python -m codeshield.api_server'")
