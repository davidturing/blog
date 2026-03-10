#!/usr/bin/env python3
"""
Fixed Twitter Insight Pipeline - AI-focused content only
Based on bird CLI for searching AI-related tweets
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def search_ai_tweets():
    """
    Search for AI-related tweets from the last 24 hours
    Only returns tweets that are actually about AI/technology
    """
    # AI-focused search keywords
    ai_keywords = [
        "AI", "Artificial Intelligence", "LLM", "Large Language Model",
        "OpenAI", "Gemini", "Claude", "GPT", "Machine Learning",
        "Deep Learning", "Neural Network", "Agent", "Multi-agent",
        "Vibe Coding", "Agentic AI", "Autonomous Agent",
        "Reinforcement Learning", "RL", "SkillRL", "DAMA"
    ]
    
    # Build search query
    keyword_query = " OR ".join([f'"{kw}"' for kw in ai_keywords])
    search_query = f"({keyword_query}) lang:en min_faves:50"
    
    print(f"🔍 Searching for AI tweets with query: {search_query}")
    
    try:
        # Use bird CLI to search tweets
        result = subprocess.run([
            "bird", "search", 
            search_query,
            "--count", "10",
            "--json"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            tweets = json.loads(result.stdout)
            # Filter to ensure relevance
            filtered_tweets = []
            for tweet in tweets:
                text = tweet.get('text', '').lower()
                # Double-check it's actually AI-related
                if any(kw.lower() in text for kw in ai_keywords):
                    filtered_tweets.append(tweet)
            
            print(f"✅ Found {len(filtered_tweets)} relevant AI tweets")
            return filtered_tweets[:5]  # Limit to top 5
        else:
            print(f"❌ Bird search failed: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

def process_tweets_to_wordpress(tweets):
    """Process tweets and publish to WordPress"""
    if not tweets:
        print("❌ No tweets to process")
        return False
        
    # Create markdown content
    date_str = datetime.now().strftime("%Y-%m-%d")
    content = f"# Twitter 每日精选 ({date_str})\n\n"
    
    for tweet in tweets:
        username = tweet.get('username', 'unknown')
        text = tweet.get('text', '')
        url = f"https://twitter.com/{username}/status/{tweet.get('id', '')}"
        
        # Summarize with Gemini (placeholder for now)
        summary = f"**核心观点**: 这是一条关于 AI 技术的推文。\n\n原文: {text[:100]}..."
        
        content += f"## 🐦 @{username}\n\n{summary}\n\n[查看原文]({url})\n\n---\n\n"
    
    # Save to file for WordPress publishing
    output_file = f"/tmp/twitter_insights_{date_str}.md"
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Content saved to {output_file}")
    return True

def main():
    """Main pipeline execution"""
    print("🚀 Starting AI-focused Twitter Insight Pipeline...")
    
    # Search for AI tweets
    tweets = search_ai_tweets()
    
    # Process and publish
    success = process_tweets_to_wordpress(tweets)
    
    if success:
        print("✅ Pipeline completed successfully!")
    else:
        print("❌ Pipeline failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)