"""
内置OHLC测试数据
"""

import polars as pl
from datetime import datetime, timedelta

def create_test_ohlc_data():
    """创建测试用的OHLC数据"""
    # 创建日期范围（过去100个交易日）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=140)  # 考虑周末
    
    dates = []
    current_date = start_date
    while len(dates) < 100:
        if current_date.weekday() < 5:  # 周一到周五
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    # 生成模拟价格数据（随机游走）
    import random
    random.seed(42)  # 固定随机种子以确保可重现性
    
    open_prices = [100.0]
    for _ in range(99):
        change = random.uniform(-0.02, 0.02)  # 每日变动-2%到+2%
        new_price = open_prices[-1] * (1 + change)
        open_prices.append(new_price)
    
    # 生成高、低、收价格
    high_prices = []
    low_prices = []
    close_prices = []
    
    for i, open_price in enumerate(open_prices):
        daily_range = open_price * random.uniform(0.01, 0.03)  # 日内波动1%-3%
        high = open_price + daily_range * random.uniform(0, 1)
        low = open_price - daily_range * random.uniform(0, 1)
        
        # 确保high >= open >= low
        high = max(high, open_price)
        low = min(low, open_price)
        
        # 收盘价在high和low之间
        close = low + (high - low) * random.random()
        
        high_prices.append(high)
        low_prices.append(low)
        close_prices.append(close)
    
    # 创建Polars DataFrame
    df = pl.DataFrame({
        "date": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": [random.randint(100000, 1000000) for _ in range(100)]  # 随机成交量
    })
    
    return df