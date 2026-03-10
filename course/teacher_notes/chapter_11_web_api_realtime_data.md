# 第11章：Web API与实时数据处理

## 课程目标
本章将教授学生如何通过Web API获取实时数据，并进行流式处理和分析。学生将掌握现代数据科学中不可或缺的实时数据处理技能。

## 核心知识点

### 11.1 Web API基础
- **RESTful API概念**：理解HTTP方法（GET、POST、PUT、DELETE）和状态码
- **API认证机制**：API Key、OAuth 2.0、Bearer Token等认证方式
- **请求限流处理**：理解Rate Limiting并实现优雅的重试机制
- **异步请求处理**：使用asyncio和aiohttp进行高效并发请求

### 11.2 实时数据源接入
- **金融数据API**：Yahoo Finance、Alpha Vantage等金融数据接口
- **社交媒体API**：Twitter/X API、Reddit API等社交数据获取
- **天气和地理数据**：OpenWeatherMap、Google Maps Geocoding API
- **新闻和舆情数据**：News API、Google News API等

### 11.3 流式数据处理
- **生成器模式**：使用Python生成器处理无限数据流
- **队列系统**：Redis、Kafka等消息队列的基本使用
- **实时数据管道**：构建端到端的实时数据处理流水线
- **内存优化**：处理大数据流时的内存管理策略

### 11.4 实时可视化
- **动态图表更新**：使用Plotly Dash创建实时仪表板
- **WebSocket集成**：实现实时数据推送和更新
- **性能优化**：确保实时可视化的流畅性和响应性

## 教学重点与难点

### 重点
1. **API设计原则**：理解RESTful架构的核心思想
2. **错误处理**：网络请求中的异常处理和重试策略
3. **数据格式转换**：JSON、XML等格式的解析和转换
4. **实时系统架构**：理解流式处理的基本架构模式

### 难点
1. **异步编程模型**：理解和正确使用async/await语法
2. **并发控制**：避免API请求过载和资源竞争
3. **数据一致性**：在实时处理中保证数据的完整性和一致性
4. **性能调优**：平衡实时性和系统资源消耗

## 实践案例

### 案例1：股票价格实时监控
```python
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime

async def fetch_stock_price(symbol, session):
    """异步获取单个股票价格"""
    url = f"https://api.example.com/stocks/{symbol}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'symbol': symbol,
                    'price': data['price'],
                    'timestamp': datetime.now()
                }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

async def monitor_multiple_stocks(symbols):
    """监控多个股票的实时价格"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_stock_price(symbol, session) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

# 使用示例
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
prices = asyncio.run(monitor_multiple_stocks(symbols))
df = pd.DataFrame(prices)
print(df)
```

### 案例2：实时新闻情感分析
```python
import requests
import json
from textblob import TextBlob
import time

def fetch_news_articles(api_key, query="technology"):
    """获取最新新闻文章"""
    url = f"https://newsapi.org/v2/everything"
    params = {
        'q': query,
        'apiKey': api_key,
        'sortBy': 'publishedAt',
        'pageSize': 10
    }
    response = requests.get(url, params=params)
    return response.json()

def analyze_sentiment(text):
    """分析文本情感"""
    blob = TextBlob(text)
    return blob.sentiment.polarity

# 实时监控循环
while True:
    try:
        news_data = fetch_news_articles("YOUR_API_KEY")
        articles = news_data.get('articles', [])
        
        for article in articles[:5]:  # 分析前5篇文章
            title = article.get('title', '')
            description = article.get('description', '')
            content = f"{title} {description}"
            
            sentiment = analyze_sentiment(content)
            print(f"Article: {title[:50]}...")
            print(f"Sentiment: {sentiment:.2f}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(300)  # 每5分钟更新一次
```

## 作业设计

### 基础作业
1. **API探索**：选择一个公开API，编写脚本获取数据并转换为Pandas DataFrame
2. **错误处理**：为API请求添加完整的错误处理和重试机制
3. **数据存储**：将获取的数据保存到CSV文件，并实现增量更新

### 进阶作业
1. **实时仪表板**：使用Dash创建一个显示实时数据的Web应用
2. **多源数据融合**：从多个API获取相关数据并进行关联分析
3. **性能优化**：实现并发请求以提高数据获取效率

## 扩展阅读
- **《Designing Data-Intensive Applications》** - Martin Kleppmann
- **《Python Concurrency with asyncio》** - Matthew Fowler  
- **REST API最佳实践指南**
- **Real-time Data Processing Patterns**

## 下一章预告
第12章将整合前面所有知识，通过AI辅助的方式完成一个完整的数据分析项目，展示现代数据科学家的工作流程。