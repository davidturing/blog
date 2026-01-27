import os
import tweepy
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 加载 .env 环境变量
print("⚙️  正在加载环境变量...")
load_dotenv() # 默认加载同级目录下的 .env

# 获取 Keys
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CONSUMER_KEY = os.getenv("X_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# 检查 Keys 是否读取成功
if not GEMINI_KEY:
    print("❌ 错误: 未找到 GEMINI_API_KEY，请检查 .env 文件！")
    exit()
if not CONSUMER_KEY:
    print("❌ 错误: 未找到 X_CONSUMER_KEY，请检查 .env 文件！")
    exit()

print("✅ 环境变量加载成功！")

# 2. 配置 Gemini (大脑)
print("🧠 正在唤醒 Gemini 大脑...")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def get_ai_tweet():
    try:
        # 简单测试 Prompt
        prompt = "用中文写一条关于'AI将颠覆企业数据治理'的幽默推文，包含一个emoji，500字以内。"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini 生成失败: {e}")
        return None

# 3. 配置 Tweepy (手脚)
print("🐦 正在连接 Twitter (X) API...")
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

def send_tweet(text):
    try:
        response = client.create_tweet(text=text)
        print(f"✅ 发送成功！Tweet ID: {response.data['id']}")
        return True
    except tweepy.errors.Forbidden as e:
        print(f"❌ 权限错误 (403): 请检查你的 App 是否开启了 'Read and Write' 权限，并重新生成了 Access Token。")
        print(f"详细错误: {e}")
    except tweepy.errors.Unauthorized as e:
        print(f"❌ 认证错误 (401): API Key 或 Token 填写错误。")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

# 4. 执行测试主流程
if __name__ == "__main__":
    print("--- 开始测试 ---")
    
    # 获取内容
    tweet_content = get_ai_tweet()
    
    if tweet_content:
        print(f"📝 AI 生成的内容: {tweet_content}")
        
        # 询问用户是否发送 (作为安全阀)
        confirm = input("❓ 确认发送这条推文吗? (y/n): ")
        
        if confirm.lower() == 'y':
            send_tweet(tweet_content)
        else:
            print("🚫 已取消发送。")
    else:
        print("⚠️ 无法获取内容，测试终止。")