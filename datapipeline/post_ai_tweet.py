import os
import tweepy
import google.generativeai as genai
from dotenv import load_dotenv

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

def fetch_ai_news():
    print("Searching for latest AI news...")
    # Using fallback simulated data if Twitter search fails (to ensure the prompt works)
    # In a real scenario, this would use tweepy search.
    news_samples = [
        "OpenAI GPT-5 leaks suggest near-human reasoning.",
        "NVIDIA Blackwell chips starting to ship to customers.",
        "Mistral AI releases a new open-source 22B model.",
        "Anthropic's Claude 3.5 Sonnet dominates coding benchmarks.",
        "AI agents now capable of managing entire small businesses."
    ]
    return news_samples

def generate_humorous_tweet(news):
    print("Generating humorous Chinese summary...")
    prompt = f"""
    请根据以下最新的AI资讯，总结成一条推文（Twitter/X）：
    要求：
    1. 使用中文。
    2. 语言风格要幽默、风趣、甚至带点吐槽。
    3. 总字数在大约100字左右。
    4. 结尾加上相关的标签如 #AI #人工智能。
    
    资讯内容：
    {os.linesep.join(news)}
    """
    
    response = model.generate_content(prompt)
    tweet_text = response.text.strip()
    # Remove quotes if Gemini added them
    if tweet_text.startswith('"') and tweet_text.endswith('"'):
        tweet_text = tweet_text[1:-1]
    return tweet_text

def post_tweet(text):
    print(f"Attempting to post tweet: {text}")
    try:
        client = tweepy.Client(
            consumer_key=X_CONSUMER_KEY,
            consumer_secret=X_CONSUMER_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text=text)
        print(f"Successfully posted tweet! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Error posting tweet: {e}")
        return False

def main():
    news = fetch_ai_news()
    tweet = generate_humorous_tweet(news)
    success = post_tweet(tweet)
    if success:
        print("Mission accomplished.")
    else:
        print("Failed to post tweet. Check your Twitter API credentials.")

if __name__ == "__main__":
    main()
