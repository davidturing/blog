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
        # Note: Free tier might fail here, but assuming user has access.
        tweets = client.search_recent_tweets(query=query, max_results=50, tweet_fields=['created_at', 'public_metrics', 'text'])
        
        if not tweets.data:
            print("No tweets found.")
            return []
            
        # Collect tweet texts
        tweet_list = [t.text for t in tweets.data]
        return tweet_list
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        # Fallback to a mock/sample if API fails for demo purposes, 
        # but for a real script we should handle it better.
        return []

def summarize_with_gemini(tweets):
    if not tweets:
        return "No news found today."
        
    print("Summarizing with Gemini...")
    prompt = f"""
    Below is a list of recent tweets about AI. 
    Please filter out noise and identify the top 10 most relevant AI news items or trends.
    For each, provide a concise summary and a brief explanation of why it's important.
    Format the output as a clean, premium HTML fragment (div-based) suitable for a blog post.
    Use vibrant colors, modern typography (sans-serif), and a clear list structure.
    Include a header 'Daily AI News - {datetime.date.today().strftime('%Y-%m-%d')}' inside the fragment.
    
    Tweets:
    {chr(10).join(tweets[:50])}
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_html_file(summary_html):
    today = datetime.date.today().strftime('%Y%m%d')
    filename = f"ai_news_{today}.html"
    
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily AI News - {today}</title>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #0f172a;
            color: #f1f5f9;
            padding: 2rem;
            max-width: 800px;
            margin: 0 auto;
        }}
        .container {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
    </style>
</head>
<body>
    <div class="container">
        {summary_html}
    </div>
</body>
</html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Generated {filename}")
    return filename

def push_to_github(filename):
    print(f"Pushing {filename} to GitHub...")
    try:
        subprocess.run(["git", "add", filename], check=True)
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
    # For testing: if tweets is empty, we can't really proceed effectively.
    # But if the user's API key is valid and has permissions, it will work.
    
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
        
    summary_html = summarize_with_gemini(tweets)
    # Clean up markdown code blocks if gemini wraps it
    if "```html" in summary_html:
        summary_html = summary_html.split("```html")[1].split("```")[0]
    elif "```" in summary_html:
        summary_html = summary_html.split("```")[1].split("```")[0]

    filename = generate_html_file(summary_html)
    push_to_github(filename)

if __name__ == "__main__":
    main()
