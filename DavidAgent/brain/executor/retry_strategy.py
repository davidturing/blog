#!/usr/bin/env python3
"""
重试策略模块 - 为WordPress执行器提供智能重试能力
"""

import asyncio
import random
from typing import Callable, Any, Optional
from functools import wraps


class RetryStrategy:
    """重试策略配置"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: tuple = (Exception,),
        retry_on_status_codes: tuple = (429, 500, 502, 503, 504)
    ):
        """
        初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            backoff_factor: 退避因子
            jitter: 是否添加随机抖动
            retry_on_exceptions: 需要重试的异常类型
            retry_on_status_codes: 需要重试的HTTP状态码
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_on_exceptions = retry_on_exceptions
        self.retry_on_status_codes = retry_on_status_codes
    
    def calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 重试次数（从1开始）
            
        Returns:
            float: 延迟时间（秒）
        """
        delay = min(
            self.base_delay * (self.backoff_factor ** (attempt - 1)),
            self.max_delay
        )
        
        if self.jitter:
            # 添加±10%的随机抖动，避免惊群效应
            jitter_amount = delay * 0.1
            delay += random.uniform(-jitter_amount, jitter_amount)
            
        return max(0.1, delay)  # 确保最小延迟为0.1秒


def with_retry(strategy: RetryStrategy):
    """
    重试装饰器
    
    Args:
        strategy: 重试策略配置
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(strategy.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except strategy.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt >= strategy.max_retries:
                        print(f"❌ [重试失败] {func.__name__} 在 {strategy.max_retries + 1} 次尝试后仍然失败")
                        raise last_exception
                    
                    delay = strategy.calculate_delay(attempt + 1)
                    print(f"⚠️ [重试中] {func.__name__} 第 {attempt + 1} 次失败，{delay:.2f}秒后重试...")
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    # 不在重试列表中的异常直接抛出
                    raise e
                    
            # 这行理论上不会执行到
            raise last_exception
            
        return wrapper
    return decorator


# 预定义的重试策略
WORDPRESS_RETRY_STRATEGY = RetryStrategy(
    max_retries=3,
    base_delay=1.0,
    max_delay=10.0,
    backoff_factor=2.0,
    jitter=True,
    retry_on_exceptions=(ConnectionError, TimeoutError, asyncio.TimeoutError),
    retry_on_status_codes=(429, 500, 502, 503, 504)
)

NETWORK_RETRY_STRATEGY = RetryStrategy(
    max_retries=5,
    base_delay=0.5,
    max_delay=15.0,
    backoff_factor=1.5,
    jitter=True,
    retry_on_exceptions=(ConnectionError, TimeoutError, asyncio.TimeoutError),
    retry_on_status_codes=(429, 500, 502, 503, 504)
)