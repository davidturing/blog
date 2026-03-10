"""
API配置与全局限流
"""

import asyncio
import os
from typing import Optional

# 全局信号量，限制并发API调用数量
API_SEMAPHORE = asyncio.Semaphore(3)

# 指数退避重试参数
MAX_RETRIES = 3
BASE_DELAY = 1.0  # 初始延迟秒数
MAX_DELAY = 60.0  # 最大延迟秒数

# API密钥配置（从环境变量或DavidAgent/.env文件加载）
def load_api_keys():
    """加载API密钥"""
    # 尝试从DavidAgent/.env加载
    env_path = "/Users/zhaoqinhuang/david_project/DavidAgent/.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # 返回必要的API密钥
    return {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY"),
        "qwen_api_key": os.environ.get("QWEN_API_KEY"),
        "dashscope_api_key": os.environ.get("DASHSCOPE_API_KEY")
    }

API_KEYS = load_api_keys()