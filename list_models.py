#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出可用的 Google GenAI 模型
"""

import os
from google import genai

def list_available_models():
    """列出可用的模型"""
    print("🔍 列出可用的 Google GenAI 模型...")
    
    # 配置 API 密钥
    api_key = None
    if "GOOGLE_API_KEY" in os.environ:
        api_key = os.environ["GOOGLE_API_KEY"]
        print("Using GOOGLE_API_KEY.")
    elif "GEMINI_API_KEY" in os.environ:
        api_key = os.environ["GEMINI_API_KEY"]
        print("Using GEMINI_API_KEY.")
    else:
        print("❌ 错误: 未找到 GOOGLE_API_KEY 或 GEMINI_API_KEY 环境变量")
        return False
    
    if not api_key:
        print("❌ 错误: API 密钥为空")
        return False
    
    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)
        
        # 列出模型
        models = client.models.list()
        
        print("✅ 可用模型列表:")
        for model in models:
            print(f"  - {model.name}: {model.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ 列出模型时发生错误: {e}")
        return False

if __name__ == "__main__":
    list_available_models()