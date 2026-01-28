import google.generativeai as genai
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 配置 Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_with_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini 生成失败: {e}")
        return None

def generate_with_doubao(prompt):
    """
    使用豆包 (Volcengine) 生成内容
    Env Requirement: 
        DOUBAO_API_KEY
        DOUBAO_ENDPOINT_ID (e.g., ep-20250101...)
    """
    api_key = os.getenv("DOUBAO_API_KEY")
    endpoint_id = os.getenv("DOUBAO_ENDPOINT_ID")
    
    if not api_key or not endpoint_id:
        print("Doubao 配置缺失: 请在 .env 设置 DOUBAO_API_KEY 和 DOUBAO_ENDPOINT_ID")
        return None

    try:
        # Volcengine compatible with OpenAI SDK
        client = OpenAI(
            api_key=api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        
        response = client.chat.completions.create(
            model=endpoint_id,
            messages=[
                {"role": "system", "content": "你是专业的科技博主。"},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Doubao 生成失败: {e}")
        return None

def generate_tweet_content(topic="2026年AI数据治理趋势", provider="gemini"):
    """
    根据主题生成推文
    Args:
        topic: 主题
        provider: 'gemini' or 'doubao'
    """
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
    
    if provider == 'doubao':
        return generate_with_doubao(prompt)
    else:
        return generate_with_gemini(prompt)
    
if __name__ == "__main__":
    # Test
    # print("Testing Gemini...")
    # print(generate_tweet_content("测试Gemini"))
    # print("Testing Doubao...")
    # print(generate_tweet_content("测试豆包: 2026年AI发展", provider="doubao"))
    pass