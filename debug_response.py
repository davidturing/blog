#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 Google GenAI SDK 响应结构
"""

import os
from google import genai

def debug_response():
    """调试响应结构"""
    print("🔍 调试 Google GenAI SDK 响应结构...")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 未找到 GOOGLE_API_KEY")
        return
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello, what is your name?",
            config={
                "response_mime_type": "text/plain",
                "temperature": 0.7,
                "max_output_tokens": 100
            }
        )
        
        print(f"响应类型: {type(response)}")
        print(f"响应内容: {response}")
        print(f"响应属性: {dir(response)}")
        
        # 尝试不同的属性访问
        if hasattr(response, 'text'):
            print(f"Text: {response.text}")
        elif hasattr(response, 'candidates'):
            print(f"Candidates: {response.candidates}")
        else:
            print("无法找到文本内容")
            
    except Exception as e:
        print(f"❌ 调试时发生错误: {e}")

if __name__ == "__main__":
    debug_response()