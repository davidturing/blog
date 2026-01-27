import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

def post_to_x(content):
    """
    使用 Tweepy 发布推文
    """
    # 获取凭证
    consumer_key = os.getenv("X_CONSUMER_KEY")
    consumer_secret = os.getenv("X_CONSUMER_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    # X API v2 认证
    client = tweepy.Client(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )

    try:
        # 发布推文
        response = client.create_tweet(text=content)
        print(f"✅ 推文发布成功! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        return False