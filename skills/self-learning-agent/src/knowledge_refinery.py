import os
import json
import subprocess
from datetime import datetime

# Configuration
RAW_TWEETS_FILE = "skills/self-learning-agent/data/raw/x_tweets.json"
KNOWLEDGE_BASE_DIR = "skills/self-learning-agent/pageindex/knowledge"

def load_tweets():
    if not os.path.exists(RAW_TWEETS_FILE):
        return []
    try:
        with open(RAW_TWEETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def extract_knowledge(tweet):
    """
    Use LLM (via exec or direct API call if possible) to extract structured knowledge.
    For this PoC, we simulate the LLM call or use a simple heuristic, 
    but in production this would call `openclaw sessions spawn` with a specific prompt.
    """
    text = tweet.get("full_text") or tweet.get("text", "")
    if not text:
        return None
        
    # Placeholder for LLM extraction logic
    # Real implementation: Call LLM to summarize
    summary = f"Summary of tweet: {text[:50]}..." 
    tags = ["#AI", "#Tech"] # Placeholder
    
    return {
        "summary": summary,
        "tags": tags,
        "original_text": text,
        "author": tweet.get("user", {}).get("screen_name", "unknown"),
        "created_at": tweet.get("created_at"),
        "id": tweet.get("id_str")
    }

def save_to_pageindex(knowledge):
    """Save extracted knowledge as a markdown file in PageIndex structure."""
    if not knowledge:
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    daily_dir = os.path.join(KNOWLEDGE_BASE_DIR, date_str)
    os.makedirs(daily_dir, exist_ok=True)
    
    filename = f"tweet_{knowledge['id']}.md"
    filepath = os.path.join(daily_dir, filename)
    
    content = f"""---
title: "Tweet from @{knowledge['author']}"
date: {knowledge['created_at']}
tags: {json.dumps(knowledge['tags'])}
source: x.com
id: {knowledge['id']}
---

# Core Insight
{knowledge['summary']}

# Original Content
> {knowledge['original_text']}

# Metadata
- Author: @{knowledge['author']}
- Ingested: {datetime.now().isoformat()}
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[Refinery] Saved knowledge: {filepath}")

def process_new_tweets():
    tweets = load_tweets()
    print(f"[Refinery] Processing {len(tweets)} tweets...")
    
    # In a real system, we track processed IDs to avoid re-processing.
    # For now, process the last 5 for demonstration.
    for tweet in tweets[-5:]:
        knowledge = extract_knowledge(tweet)
        save_to_pageindex(knowledge)

if __name__ == "__main__":
    process_new_tweets()
