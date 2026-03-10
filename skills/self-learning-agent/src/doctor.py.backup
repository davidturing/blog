import os
import sys
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (force reload)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path, override=True)

def check_network(host="8.8.8.8", port=53, timeout=3):
    """Check basic network connectivity."""
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True, "Online"
    except Exception as ex:
        return False, f"Offline ({ex})"

def check_gemini():
    """Verify Gemini API connectivity and model availability."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return False, "Missing GEMINI_API_KEY"
    
    genai.configure(api_key=api_key)
    try:
        # Use config model or default to gemini-3-pro-preview
        model_name = os.getenv("MODEL_DEFAULT", "gemini-3-pro-preview")
        print(f"Testing model: {model_name}")
        model = genai.GenerativeModel(model_name)
        start = time.time()
        # Simple generation
        response = model.generate_content("Ping")
        latency = (time.time() - start) * 1000
        return True, f"Operational ({latency:.0f}ms)"
    except Exception as e:
        # If rate limited, try fallback model
        if "429" in str(e):
            print(f"  ⚠️ Rate limit on {model_name}. Trying fallback gemini-1.5-flash...")
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content("Ping")
                return True, "Operational (Fallback: gemini-2.0-flash)"
            except Exception as e2:
                 return False, f"Error (both models): {e2}"
        return False, f"Error: {e}"

def check_github():
    """Verify GitHub Token and Rate Limits."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return False, "Missing GITHUB_TOKEN"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    try:
        # Check Rate Limit
        resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # The structure might vary, but usually resources->core
            if 'resources' in data and 'core' in data['resources']:
                core = data['resources']['core']
                remaining = core['remaining']
                limit = core['limit']
                reset_time = time.strftime('%H:%M:%S', time.localtime(core['reset']))
                return True, f"Valid (Quota: {remaining}/{limit}, Resets: {reset_time})"
            else:
                return True, "Valid (Quota info unavailable)"
        elif resp.status_code == 401:
            return False, "Invalid Token (401)"
        else:
            return False, f"API Error ({resp.status_code})"
    except Exception as e:
        return False, f"Connection Error: {e}"

def check_wordpress():
    """Verify WordPress XML-RPC connection."""
    url = os.getenv("WP_URL")
    # user = os.getenv("WP_USERNAME")
    # pwd = os.getenv("WP_PASSWORD")
    
    if not url:
        return False, "Missing WP_URL"
        
    try:
        # Simple POST to check if endpoint is alive
        resp = requests.post(url, headers={'Content-Type': 'text/xml'}, data='<methodCall><methodName>system.listMethods</methodName></methodCall>', timeout=5)
        if resp.status_code == 200:
             return True, "Endpoint Accessible"
        else:
             return False, f"Endpoint Error ({resp.status_code})"
    except Exception as e:
        return False, f"Connection Error: {e}"

def generate_report():
    print("--- 🏥 David Agent Health Check ---")
    
    checks = [
        ("Network (DNS)", check_network("google.com", 80)),
        ("Gemini API", check_gemini()),
        ("GitHub API", check_github()),
        ("WordPress", check_wordpress()),
    ]
    
    all_passed = True
    report = []
    
    print(f"{'COMPONENT':<20} | {'STATUS':<10} | {'DETAILS'}")
    print("-" * 60)
    
    for name, (passed, details) in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_passed = False
            status = "❌ FAIL"
        
        # Safe print
        print(f"{name:<20} | {status:<10} | {details}")
        report.append(f"- **{name}**: {status} - {details}")

    # Save report to file
    report_path = "skills/self-learning-agent/data/insights/health_report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# David Agent Health Report\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("\n".join(report))
        
    return all_passed

if __name__ == "__main__":
    success = generate_report()
    if not success:
        sys.exit(1)
