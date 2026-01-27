import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# 配置 Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_tweet_content(topic="2026年AI数据治理趋势"):
    """
    让 Gemini 根据主题生成推文
    """
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # Prompt Engineering (提示词工程)
    prompt = f"""
    你是一个多年企业数据治理专家，也是关注AI和数字化转型的科技博主。
    请根据主题 "{topic}" 写一条推特（X）。
    
    要求：
    1. 语言犀利或富有洞察力。
    2. 字数限制在 200 字以内（中文）。
    3. 包含 2-3 个相关的 Hashtags。
    4. 适当使用 Emoji。
    5. 不要包含 "这是你的推文" 之类的废话，直接输出内容。
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini 生成失败: {e}")
        return None