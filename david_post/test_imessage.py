# test_agent.py (修改版)
import google.generativeai as genai
import os
from dotenv import load_dotenv
from imessage import send_to_iphone  # <--- 导入新模块

load_dotenv()

# 配置 Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')

def get_ai_content():
    try:
        # 让 AI 简单写一句
        prompt = "用中文写一条关于'周五下班'的幽默推文，20个字以内。"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini 出错: {e}")
        return None

if __name__ == "__main__":
    print("--- 开始测试 ag ---")
    
    # 1. 生成内容
    content = get_ai_content()
    
    if content:
        print(f"📝 生成内容: {content}")
        
        # 2. 发送 iMessage
        print("🚀 正在发送到 iPhone...")
        send_to_iphone(content)
        
    else:
        print("⚠️ 生成内容为空")