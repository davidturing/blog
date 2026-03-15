"""
Intentional Parse Error for Recursive Self-Correction Demonstration
This file contains deliberately broken parsing logic to trigger self-correction.
"""

import json
import re

def broken_json_parser(raw_data: str) -> dict:
    """
    BROKEN FUNCTION: This parser has multiple architectural flaws
    - Uses eval() for JSON parsing (security risk)
    - No error handling 
    - Assumes perfect input format
    - Hard-coded assumptions about data structure
    """
    # SECURITY RISK: Using eval instead of json.loads
    parsed = eval(raw_data)  # This will fail on malformed JSON
    
    # HARD-CODED ASSUMPTION: Expects specific key structure
    result = {
        'title': parsed['metadata']['title'],  # Will fail if metadata missing
        'content': parsed['body']['text'],      # Will fail if body structure changed  
        'author': parsed['author']['name']      # Will fail if author format different
    }
    
    return result

# Test data that will cause failure
test_data_malformed = '{"metadata": {"title": "Test"}, "body": "Not an object", "author": "John"}'
test_data_missing_keys = '{"title": "Simple title", "content": "Simple content"}'

if __name__ == "__main__":
    print("🧪 Testing broken parser...")
    try:
        result1 = broken_json_parser(test_data_malformed)
        print(f"Result 1: {result1}")
    except Exception as e1:
        print(f"❌ Error 1: {e1}")
        
    try:
        result2 = broken_json_parser(test_data_missing_keys)  
        print(f"Result 2: {result2}")
    except Exception as e2:
        print(f"❌ Error 2: {e2}")
        
    print("💥 Intentional parse errors generated for self-correction demonstration!")