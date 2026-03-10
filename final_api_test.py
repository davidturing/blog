#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, '/Users/zhaoqinhuang/david_project/venv/lib/python3.14/site-packages')

import dashscope

# 设置 API Key
api_key = 'sk-sp-2fdaeff8397a4f8da6883ebdafb3e6e0'

# 测试文本模型（应该工作）
try:
    print("🔍 测试文本模型 (qwen-max)...")
    response = dashscope.Generation.call(
        api_key=api_key,
        model='qwen-max',
        prompt='你好，测试API Key是否有效'
    )
    
    if response.status_code == 200:
        print("✅ 文本模型测试成功!")
        print(f"响应: {response.output.text[:50]}...")
    else:
        print(f"❌ 文本模型测试失败: {response.status_code}")
        if hasattr(response, 'output') and hasattr(response.output, 'error'):
            print(f"错误详情: {response.output.error}")
            
except Exception as e:
    print(f"❌ 文本模型异常: {e}")

print("\n" + "="*50 + "\n")

# 测试图像模型
try:
    print("🎨 测试图像模型 (qwen-image-max)...")
    messages = [
        {
            "role": "user",
            "content": [
                {"text": "生成一个简单的蓝色方块"}
            ]
        }
    ]
    
    response = dashscope.MultiModalConversation.call(
        api_key=api_key,
        model="qwen-image-max",
        messages=messages,
        size="1024*1024",
        n=1
    )
    
    if response.status_code == 200:
        print("✅ 图像模型测试成功!")
        print("图像生成成功")
    else:
        print(f"❌ 图像模型测试失败: {response.status_code}")
        if hasattr(response, 'output') and hasattr(response.output, 'error'):
            print(f"错误详情: {response.output.error}")
            
except Exception as e:
    print(f"❌ 图像模型异常: {e}")