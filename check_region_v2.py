import os
import dashscope

# 设置 API Key
dashscope.api_key = "sk-sp-2fdaeff8397a4f8da6883ebdafb3e6e0"

# 尝试调用一个简单的文本模型来测试地域
try:
    response = dashscope.Generation.call(
        model="qwen-max",
        prompt="Hello, what region am I in?"
    )
    if response.status_code == 200:
        print("✅ API Key works for text models")
        print("Response:", response.output.text[:100])
    else:
        print(f"❌ Text model call failed: {response.status_code}")
        print("Error:", response.output.error)
except Exception as e:
    print(f"❌ Exception: {e}")