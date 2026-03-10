import os
import dashscope

# 测试 API Key 的基本连通性
api_key = "sk-sp-2fdaeff8397a4f8da6883ebdafb3e6e0"

try:
    # 尝试获取模型列表来检测地域和权限
    response = dashscope.Model.list(api_key=api_key)
    if response.status_code == 200:
        print("✅ API Key 有效")
        print("可用模型列表:")
        for model in response.output:
            if 'image' in model.get('name', '').lower():
                print(f"  - {model['name']}")
    else:
        print(f"❌ API Key 无效或无权限, 状态码: {response.status_code}")
        print(f"错误信息: {response.output}")
except Exception as e:
    print(f"❌ 连接错误: {e}")