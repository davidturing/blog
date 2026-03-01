#!/usr/bin/env python3
"""
API弹性组件 - 防爆盾（高并发熔断与指数退避）
为左右脑提供工业级API保护，防止并发击穿和429限流
"""

import asyncio
import functools
from typing import Callable, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局并发锁：强制规定同一时间最多只有3个任务在请求大模型API
# 无论爬虫瞬间塞进50还是100个任务，超出的都会在内存中乖乖排队，绝不击穿厂商API
GLOBAL_API_SEMAPHORE = asyncio.Semaphore(3)

def with_resilience(max_retries: int = 3, base_delay: int = 2):
    """
    工业级API熔断与重试装饰器 (Exponential Backoff)
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 1. 拿号排队（限制绝对并发量）
            async with GLOBAL_API_SEMAPHORE:
                for attempt in range(max_retries):
                    try:
                        # 2. 尝试执行API调用
                        return await func(*args, **kwargs)
                    
                    except Exception as e:
                        error_msg = str(e).lower()
                        # 3. 熔断判定：只有遇到429限流或超时，才触发指数退避
                        if "429" in error_msg or "too many requests" in error_msg or "timeout" in error_msg:
                            delay = base_delay * (2 ** attempt)  # 2s, 4s, 8s...
                            logger.warning(
                                f"⚠️ [熔断保护] 触发API流量控制 (429/超时)！"
                                f"等待 {delay} 秒后重试 ({attempt+1}/{max_retries})..."
                            )
                            await asyncio.sleep(delay)
                        else:
                            # 语法错误、逻辑错误等直接抛出，不浪费重试次数
                            logger.error(f"❌ [严重错误] 非网络层异常，停止重试: {e}")
                            raise e
                            
                raise Exception(f"🚨 [系统崩溃] 接口连续 {max_retries} 次熔断失败，任务已丢弃。")
        return wrapper
    return decorator


class TokenTracker:
    """Token消耗追踪器 - 用于成本监控"""
    
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        
    def record_tokens(self, prompt_tokens: int, completion_tokens: int, model: str = "unknown"):
        """记录Token消耗"""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        
        # 简单的成本估算（实际成本需要根据具体模型定价）
        if "gemini" in model.lower():
            # Gemini Pro: $0.00025 / 1K tokens input, $0.0005 / 1K tokens output
            cost = (prompt_tokens * 0.00025 + completion_tokens * 0.0005) / 1000
        elif "qwen" in model.lower():
            # Qwen Coder Plus: 假设类似定价
            cost = (prompt_tokens * 0.0002 + completion_tokens * 0.0004) / 1000
        else:
            cost = (prompt_tokens + completion_tokens) * 0.0000001  # 默认估算
            
        self.total_cost += cost
        
        logger.info(f"💰 [Token消耗] 模型: {model}, Prompt: {prompt_tokens}, Completion: {completion_tokens}, 成本: ${cost:.6f}")
        
    def get_stats(self):
        """获取Token统计信息"""
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_cost": self.total_cost,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens
        }