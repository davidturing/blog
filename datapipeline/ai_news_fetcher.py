import os
import datetime
import tweepy
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
import time

# Load environment variables
load_dotenv()

# Configuration
X_CONSUMER_KEY = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def fetch_ai_news_from_twitter():
    print("Fetching AI news from Twitter...")
    client = tweepy.Client(
        consumer_key=X_CONSUMER_KEY,
        consumer_secret=X_CONSUMER_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    
    # Simple search query for AI news
    query = "(AI news OR #AI OR #LLM OR #GenerativeAI) lang:en -is:retweet"
    
    try:
        # Search for recent tweets (v2 API)
        tweets = client.search_recent_tweets(query=query, max_results=50, tweet_fields=['created_at', 'public_metrics', 'text'])
        
        if not tweets.data:
            print("No tweets found.")
            return []
            
        tweet_list = [t.text for t in tweets.data]
        return tweet_list
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []

def summarize_with_gemini_to_markdown(tweets):
    if not tweets:
        return "No news found today."
        
    print("Summarizing with Gemini to Markdown...")
    prompt = f"""
    Below is a list of recent tweets about AI. 
    Please filter out noise and identify the top 10 most relevant AI news items or trends.
    
    For each item, provide:
    1. A catchy title with an emoji.
    2. A concise 2-3 sentence summary.
    3. An "Importance" section using a blockquote or callout style.
    
    Format the entire output as a rich Markdown document. 
    Use horizontal rules to separate items.
    Include a main header '# 🤖 Daily AI News - {datetime.date.today().strftime('%Y-%m-%d')}' at the top.
    
    Tweets:
    {chr(10).join(tweets[:50])}
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_markdown_file(content):
    today = datetime.date.today().strftime('%Y%m%d')
    filename = f"ai_news_{today}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated {filename}")
    return filename

def push_to_github(filename):
    print(f"Pushing {filename} to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Add daily AI news: {filename}"], check=True)
        # Pull latest changes to avoid rejection
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        # Explicitly push to origin main
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Successfully pushed to GitHub.")
    except Exception as e:
        print(f"Error pushing to GitHub: {e}")

def main():
    tweets = fetch_ai_news_from_twitter()
    
    if not tweets:
        print("Falling back to simulated data for demonstration if API fails...")
        tweets = [
            "OpenAI announces GPT-5 release window.",
            "NVIDIA reaches record high as AI chip demand soars.",
            "Microsoft integrates more AI into Windows 11.",
            "Google DeepMind's new agent can play complex games better than humans.",
            "Anthropic releases Claude 4 with 1M context window.",
            "Meta open sources Llama 4 400B model.",
            "New AI regulation passed in EU focusing on safety headers.",
            "Mistral AI reveals new lightweight vision model.",
            "Tesla FSD improves significantly with new neural network architecture.",
            "AI-powered medical diagnostics tool approved by FDA."
        ]
        
    markdown_content = summarize_with_gemini_to_markdown(tweets)
    
    # Clean up markdown code blocks if gemini wraps it
    if "```markdown" in markdown_content:
        markdown_content = markdown_content.split("```markdown")[1].split("```")[0]
    elif "```" in markdown_content:
        markdown_content = markdown_content.split("```")[1].split("```")[0]

    filename = generate_markdown_file(markdown_content)
    push_to_github(filename)

if __name__ == "__main__":
    main()
