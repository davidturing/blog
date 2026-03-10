import time
import requests
import os

def call_gemini_api(payload, url, max_retries=5):
    """
    Call Gemini API with exponential backoff to handle rate limits.
    """
    headers = {"Content-Type": "application/json"}
    retry_delay = 2  # Start with 2 seconds

    for i in range(max_retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if resp.status_code == 200:
                return resp.json()
            
            # If rate limited (429) or server error (500, 503)
            if resp.status_code in [429, 500, 503]:
                print(f"⚠️ Gemini API returned {resp.status_code}. Retrying in {retry_delay}s... (Attempt {i+1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                print(f"❌ Gemini API Error: {resp.status_code} - {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request Exception: {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 2
            
    print("❌ Max retries reached for Gemini API.")
    return None
