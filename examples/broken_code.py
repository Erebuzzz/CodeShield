"""
Demo: Broken code that AI often produces

This file demonstrates typical AI-generated code issues
that CodeShield catches and fixes.
"""

# Issue 1: Missing imports
# AI often forgets to import modules it uses

def fetch_api_data(url: str) -> dict:
    """Fetch data from an API - AI forgot imports!"""
    response = requests.get(url)  # Missing: import requests
    return json.loads(response.text)  # Missing: import json


# Issue 2: Wrong variable names
# AI uses different naming conventions than your codebase

def processUserData(userData):  # camelCase instead of snake_case
    userName = userData.get("name")  # should be user_name
    userAge = userData.get("age")  # should be user_age
    return f"{userName} is {userAge} years old"


# Issue 3: Undefined variables
# AI hallucinates variables that don't exist

def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * tax_rate  # Where is tax_rate defined?
    return total


# Issue 4: Typos in function/variable names
# AI sometimes adds/removes letters

def get_user_informations(user_id):  # "informations" is wrong
    # Should be "information" (singular)
    pass
