#!/usr/bin/env python3
"""
最小化向量连通性测试脚本
- 仅测试 GLM-5 向量生成
- 不使用 core_embedding.py (因其基于 sentence-transformers)
- 直接调用 ZhipuAI API
"""

import os
import sys
from zhipuai import ZhipuAI

# 从环境变量加载凭据
api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    print("❌ 错误: 未找到 ZHIPU_API_KEY 环境变量")
    sys.exit(1)

client = ZhipuAI(api_key=api_key)

def test_glm5_embedding():
    """执行单次 GLM-5 向量生成测试"""
    test_text = "这是一个用于测试 GLM-5 向量连通性的最小化文本。"
    
    try:
        print("📡 正在连接 GLM-5 向量引擎...")
        response = client.embeddings.create(
            model="embedding-3",
            input=[test_text]
        )
        
        # 检查响应
        if response.data and len(response.data) > 0:
            vector = response.data[0].embedding
            print(f"✅ GLM-5 向量连通成功!")
            print(f"✅ 向量生成成功! 维度: {len(vector)}")
            print(f"✅ 未触发 API rate limit (请求成功)")
            return True
        else:
            print("❌ 错误: API 返回空数据")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 设置环境变量
    os.environ["ZHIPU_API_KEY"] = api_key
    
    success = test_glm5_embedding()
    sys.exit(0 if success else 1)