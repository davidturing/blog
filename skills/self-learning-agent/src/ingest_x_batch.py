import os
import json
import time
import random
import subprocess
from datetime import datetime

# Configuration
DATA_DIR = "skills/self-learning-agent/data/raw"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "x_accounts.json")
TWEETS_FILE = os.path.join(DATA_DIR, "x_tweets.json")
STATE_FILE = os.path.join(DATA_DIR, "x_ingest_state.json")

# Rate limit configuration (Plan C)
RATE_LIMIT_DELAY = 15  # seconds

def load_json(filepath, default=None):
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default if default is not None else []

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_bird_search(query, count=5):
    """Run bird search command."""
    try:
        cmd = ["bird", "search", query, "-n", str(count), "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"[Ingest] Error for query '{query}': {result.stderr.strip()}")
            return []
            
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[Ingest] Exception for query '{query}': {e}")
        return []

def ingest_batch():
    print(f"[Ingest] Starting batch ingestion at {datetime.now().isoformat()}...")
    
    accounts = load_json(ACCOUNTS_FILE, [])
    if not accounts:
        print("[Ingest] No accounts found in x_accounts.json")
        return

    # Load existing tweets to avoid duplicates (naive approach for now)
    # In production, we'd use a database or ID set.
    existing_tweets = load_json(TWEETS_FILE, [])
    existing_ids = set(t.get("id_str") or t.get("id") for t in existing_tweets)
    
    # Load state (last processed ID per user)
    state = load_json(STATE_FILE, {})
    
    new_tweets_count = 0
    
    for i, account in enumerate(accounts):
        handle = account.get("handle")
        if not handle:
            continue
            
        print(f"[Ingest] [{i+1}/{len(accounts)}] Fetching @{handle}...")
        
        # Determine query: if we have state, maybe use since_id? 
        # Bird CLI might not support since_id directly in search, but we filter later.
        tweets = run_bird_search(f"from:{handle}", count=5)
        
        user_new_count = 0
        latest_id = state.get(handle)
        
        for tweet in tweets:
            tid = tweet.get("id_str") or tweet.get("id")
            if tid and tid not in existing_ids:
                # Add metadata
                tweet["_ingested_at"] = datetime.now().isoformat()
                tweet["_source_handle"] = handle
                
                existing_tweets.append(tweet)
                existing_ids.add(tid)
                user_new_count += 1
                
                # Update latest ID state if this one is newer (lexicographically for IDs works)
                if not latest_id or str(tid) > str(latest_id):
                    latest_id = str(tid)
        
        if user_new_count > 0:
            print(f"[Ingest] Added {user_new_count} new tweets from @{handle}")
            state[handle] = latest_id
        else:
            print(f"[Ingest] No new tweets from @{handle}")

        # Save intermediate results frequently
        save_json(TWEETS_FILE, existing_tweets)
        save_json(STATE_FILE, state)
        
        # Enforce Rate Limit (Plan C)
        if i < len(accounts) - 1:
            print(f"[Ingest] Sleeping {RATE_LIMIT_DELAY}s for rate limiting...")
            time.sleep(RATE_LIMIT_DELAY)

    print(f"[Ingest] Batch complete. Total tweets: {len(existing_tweets)}")

if __name__ == "__main__":
    ingest_batch()
