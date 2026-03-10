# 第11章：Web API与实时数据处理

## 11.1 Web API基础概念

### 什么是API？
API（Application Programming Interface，应用程序编程接口）是不同软件系统之间进行通信的桥梁。在数据分析领域，Web API让我们能够：
- 获取实时数据（股票价格、天气、新闻等）
- 访问第三方服务（社交媒体、地图、支付等）
- 集成不同的数据源

### RESTful API
REST（Representational State Transfer）是目前最流行的Web API设计风格，具有以下特点：
- **无状态性**：每个请求都包含所有必要信息
- **统一接口**：使用标准HTTP方法（GET、POST、PUT、DELETE）
- **资源导向**：每个URL代表一个资源

```python
# 基本的API请求示例
import requests

# GET请求获取数据
response = requests.get('https://api.example.com/data')
data = response.json()

# POST请求发送数据
payload = {'key': 'value'}
response = requests.post('https://api.example.com/submit', json=payload)
```

## 11.2 Python中的API客户端

### requests库
`requests`是Python中最流行的HTTP库，简单易用：

```python
import requests
import json

# 设置请求头
headers = {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
}

# 处理查询参数
params = {
    'limit': 100,
    'offset': 0
}

response = requests.get(
    'https://api.example.com/users',
    headers=headers,
    params=params
)

# 错误处理
if response.status_code == 200:
    data = response.json()
else:
    print(f"Error: {response.status_code}")
```

### 异步API调用
对于大量API请求，使用异步可以提高效率：

```python
import asyncio
import aiohttp

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    urls = ['https://api1.com', 'https://api2.com', 'https://api3.com']
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    return results

# 运行异步函数
data = asyncio.run(main())
```

## 11.3 常见API认证方式

### API Key
最简单的认证方式，在请求头或URL参数中传递：

```python
# 在请求头中
headers = {'X-API-Key': 'your-api-key'}

# 在URL参数中
params = {'api_key': 'your-api-key'}
```

### Bearer Token
使用JWT或其他令牌进行认证：

```python
headers = {'Authorization': 'Bearer your-jwt-token'}
```

### OAuth 2.0
用于授权第三方应用访问用户数据：

```python
from requests_oauthlib import OAuth2Session

# OAuth 2.0流程
oauth = OAuth2Session(
    client_id='your-client-id',
    redirect_uri='https://your-app.com/callback',
    scope=['read', 'write']
)

# 获取授权URL
authorization_url, state = oauth.authorization_url(
    'https://api.example.com/oauth/authorize'
)

# 用户授权后，用授权码换取访问令牌
token = oauth.fetch_token(
    'https://api.example.com/oauth/token',
    authorization_response=redirect_response,
    client_secret='your-client-secret'
)
```

## 11.4 实时数据流处理

### WebSocket连接
WebSocket提供全双工通信，适合实时数据：

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    # 发送订阅消息
    ws.send(json.dumps({'action': 'subscribe', 'channel': 'market_data'}))

# 创建WebSocket连接
ws = websocket.WebSocketApp(
    "wss://stream.example.com",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

### Server-Sent Events (SSE)
服务器向客户端推送事件：

```python
import requests

def listen_to_events(url):
    response = requests.get(url, stream=True)
    
    for line in response.iter_lines():
        if line:
            event = line.decode('utf-8')
            if event.startswith('data:'):
                data = event[5:].strip()
                yield json.loads(data)

# 使用SSE
for event in listen_to_events('https://api.example.com/events'):
    print(f"Event: {event}")
```

## 11.5 数据管道与ETL

### 构建数据管道
将API数据集成到分析流程中：

```python
import pandas as pd
from datetime import datetime, timedelta

class DataPipeline:
    def __init__(self, api_base_url, api_key):
        self.api_base_url = api_base_url
        self.headers = {'Authorization': f'Bearer {api_key}'}
    
    def extract(self, endpoint, params=None):
        """从API提取数据"""
        url = f"{self.api_base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def transform(self, raw_data):
        """转换数据格式"""
        df = pd.DataFrame(raw_data)
        # 数据清洗和转换
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        return df
    
    def load(self, df, output_path):
        """加载数据到文件或数据库"""
        df.to_csv(output_path, index=False)
        return df
    
    def run_pipeline(self, endpoint, output_path, **kwargs):
        """运行完整的ETL管道"""
        raw_data = self.extract(endpoint, **kwargs)
        transformed_data = self.transform(raw_data)
        loaded_data = self.load(transformed_data, output_path)
        return loaded_data

# 使用数据管道
pipeline = DataPipeline('https://api.example.com', 'your-api-key')
data = pipeline.run_pipeline('market-data', 'market_data.csv', days=7)
```

## 11.6 错误处理与重试机制

### 指数退避重试
处理API限流和临时错误：

```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    
                    # 计算退避延迟
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=5, base_delay=1, max_delay=30)
def fetch_api_data(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
```

### 速率限制处理
遵守API的速率限制：

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.call_times = deque()
    
    def wait_if_needed(self):
        now = time.time()
        # 移除超过1秒前的调用记录
        while self.call_times and self.call_times[0] < now - 1:
            self.call_times.popleft()
        
        # 如果调用次数达到限制，等待
        if len(self.call_times) >= self.calls_per_second:
            sleep_time = 1 - (now - self.call_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.call_times.append(time.time())

# 使用速率限制器
limiter = RateLimiter(calls_per_second=2)

for i in range(10):
    limiter.wait_if_needed()
    data = fetch_api_data(f"https://api.example.com/data/{i}", headers)
    process_data(data)
```

## 11.7 实战案例：构建实时股票监控系统

### 项目概述
创建一个实时股票价格监控系统，包括：
- 从金融API获取实时股票数据
- 数据存储和历史记录
- 实时价格变动通知
- 技术指标计算

### 完整实现

```python
import pandas as pd
import numpy as np
import requests
import time
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

class StockMonitor:
    def __init__(self, api_key, db_path='stocks.db'):
        self.api_key = api_key
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_stock_price(self, symbol):
        """获取单个股票价格"""
        url = f"https://api.financialdata.com/stock/{symbol}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                'symbol': symbol,
                'price': data['price'],
                'volume': data.get('volume', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def save_price(self, price_data):
        """保存价格数据到数据库"""
        if price_data is None:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO stock_prices (symbol, price, volume, timestamp) VALUES (?, ?, ?, ?)',
            (price_data['symbol'], price_data['price'], price_data['volume'], price_data['timestamp'])
        )
        conn.commit()
        conn.close()
    
    def calculate_indicators(self, symbol, window=14):
        """计算技术指标"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            f"SELECT * FROM stock_prices WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT {window*2}",
            conn
        )
        conn.close()
        
        if len(df) < window:
            return None
        
        # 计算RSI (相对强弱指数)
        df['price_change'] = df['price'].diff()
        df['gain'] = df['price_change'].where(df['price_change'] > 0, 0)
        df['loss'] = -df['price_change'].where(df['price_change'] < 0, 0)
        
        avg_gain = df['gain'].rolling(window=window).mean()
        avg_loss = df['loss'].rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 计算移动平均线
        ma_20 = df['price'].rolling(window=20).mean().iloc[-1]
        ma_50 = df['price'].rolling(window=50).mean().iloc[-1]
        
        return {
            'rsi': rsi.iloc[-1],
            'ma_20': ma_20,
            'ma_50': ma_50,
            'current_price': df['price'].iloc[0]
        }
    
    def send_alert(self, symbol, message):
        """发送价格警报"""
        # 这里可以集成邮件、短信或其他通知服务
        print(f"ALERT for {symbol}: {message}")
    
    def monitor_stocks(self, symbols, check_interval=60):
        """监控多个股票"""
        print(f"Starting stock monitor for: {symbols}")
        
        while True:
            for symbol in symbols:
                # 获取当前价格
                price_data = self.get_stock_price(symbol)
                if price_data:
                    self.save_price(price_data)
                    
                    # 计算技术指标
                    indicators = self.calculate_indicators(symbol)
                    if indicators:
                        # 检查交易信号
                        if indicators['rsi'] < 30:
                            self.send_alert(symbol, f"RSI oversold: {indicators['rsi']:.2f}")
                        elif indicators['rsi'] > 70:
                            self.send_alert(symbol, f"RSI overbought: {indicators['rsi']:.2f}")
                        
                        # 检查移动平均线交叉
                        if indicators['ma_20'] > indicators['ma_50']:
                            self.send_alert(symbol, "Golden Cross detected!")
                        elif indicators['ma_20'] < indicators['ma_50']:
                            self.send_alert(symbol, "Death Cross detected!")
                
                time.sleep(1)  # 避免API调用过于频繁
            
            print(f"Completed monitoring cycle at {datetime.now()}")
            time.sleep(check_interval)

# 使用示例
if __name__ == "__main__":
    monitor = StockMonitor('your-financial-api-key')
    stocks_to_monitor = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    monitor.monitor_stocks(stocks_to_monitor, check_interval=300)  # 每5分钟检查一次
```

## 11.8 最佳实践与安全考虑

### API密钥管理
- **不要硬编码**：使用环境变量或配置文件
- **最小权限原则**：只申请必要的API权限
- **定期轮换**：定期更换API密钥

```python
# 使用环境变量
import os
api_key = os.getenv('FINANCIAL_API_KEY')

# 使用配置文件
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['API']['financial_key']
```

### 数据缓存
减少不必要的API调用：

```python
import pickle
from pathlib import Path

class DataCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key, ttl_seconds=3600):
        """从缓存获取数据"""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < ttl_seconds:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        return None
    
    def set(self, key, data):
        """保存数据到缓存"""
        cache_file = self.cache_dir / f"{key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)

# 使用缓存
cache = DataCache()
cached_data = cache.get('stock_AAPL')
if cached_data is None:
    cached_data = fetch_stock_data('AAPL')
    cache.set('stock_AAPL', cached_data)
```

### 监控与日志
跟踪API使用情况和错误：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_usage.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def monitored_api_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"API call {func.__name__} succeeded in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API call {func.__name__} failed after {duration:.2f}s: {e}")
            raise e
    return wrapper
```

## 11.9 本章小结

本章介绍了Web API和实时数据处理的核心概念和技术：
- **API基础**：理解RESTful API的设计原则和使用方法
- **Python工具**：掌握requests、aiohttp等库的使用
- **认证安全**：了解各种API认证方式和安全最佳实践
- **实时处理**：学习WebSocket和SSE等实时通信技术
- **数据管道**：构建完整的ETL流程
- **错误处理**：实现健壮的错误处理和重试机制
- **实战应用**：通过股票监控系统案例整合所学知识

通过本章的学习，你应该能够：
1. 熟练使用各种Web API获取数据
2. 构建可靠的数据管道处理实时数据
3. 实现专业的错误处理和性能优化
4. 将API数据集成到数据分析项目中

## 11.10 练习题

### 基础练习
1. 使用OpenWeatherMap API获取指定城市的当前天气信息
2. 实现一个简单的GitHub API客户端，获取用户的仓库列表
3. 使用Alpha Vantage API获取股票的历史价格数据

### 进阶练习
1. 构建一个新闻聚合器，从多个新闻API获取并合并数据
2. 实现实时Twitter情感分析系统，监控特定关键词的情感变化
3. 创建一个自动化数据备份系统，定期从API获取数据并存储备份

### 项目挑战
**实时疫情数据仪表板**：
- 从WHO或CDC的API获取全球疫情数据
- 实现实时数据更新和可视化
- 添加地理信息和趋势分析功能
- 部署为Web应用供团队使用

---

**下一章预告**：第12章将介绍AI辅助数据分析，包括如何使用大型语言模型（LLM）来自动化数据分析流程、生成洞察报告，以及构建智能数据分析助手。