# 第11章：Web API与实时数据

## 幻灯片1: 课程标题
- **第11章：Web API与实时数据**
- Python数据分析课程
- 讲师：David Turing

## 幻灯片2: 学习目标
- 理解Web API的基本概念和工作原理
- 掌握使用Python请求API数据的方法
- 学习处理JSON和XML格式的数据
- 掌握实时数据流的处理技术
- 实践构建数据管道从API获取实时数据

## 幻灯片3: Web API基础
- **什么是API**：
  - 应用程序编程接口（Application Programming Interface）
  - 允许不同软件系统之间通信的接口
  
- **RESTful API特点**：
  - 基于HTTP协议
  - 无状态性
  - 资源导向
  - 标准HTTP方法（GET, POST, PUT, DELETE）

- **常见API认证方式**：
  - API Key
  - OAuth 2.0
  - Bearer Token

## 幻灯片4: Python中的API请求
- **requests库**：
  ```python
  import requests
  
  # GET请求
  response = requests.get('https://api.example.com/data')
  
  # 带参数的请求
  params = {'limit': 100, 'offset': 0}
  response = requests.get('https://api.example.com/data', params=params)
  
  # 带认证的请求
  headers = {'Authorization': 'Bearer YOUR_TOKEN'}
  response = requests.get('https://api.example.com/data', headers=headers)
  ```

- **异步请求**：
  ```python
  import aiohttp
  import asyncio
  
  async def fetch_data():
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.example.com/data') as response:
              return await response.json()
  ```

## 幻灯片5: 处理API响应数据
- **JSON数据处理**：
  ```python
  # 解析JSON响应
  data = response.json()
  
  # 转换为Pandas DataFrame
  df = pd.DataFrame(data['results'])
  
  # 处理嵌套JSON
  df_normalized = pd.json_normalize(data['results'])
  ```

- **错误处理**：
  ```python
  try:
      response = requests.get(url)
      response.raise_for_status()  # 抛出HTTP错误
      data = response.json()
  except requests.exceptions.RequestException as e:
      print(f"请求失败: {e}")
  except ValueError as e:
      print(f"JSON解析失败: {e}")
  ```

## 幻灯片6: 实时数据流处理
- **WebSocket连接**：
  ```python
  import websocket
  import json
  
  def on_message(ws, message):
      data = json.loads(message)
      # 处理实时数据
      process_realtime_data(data)
  
  ws = websocket.WebSocketApp("wss://stream.example.com",
                             on_message=on_message)
  ws.run_forever()
  ```

- **Server-Sent Events (SSE)**：
  ```python
  import sseclient
  
  response = requests.get('https://api.example.com/stream', stream=True)
  client = sseclient.SSEClient(response)
  
  for event in client.events():
      data = json.loads(event.data)
      process_realtime_data(data)
  ```

## 幻灯片7: 数据管道构建
- **ETL流程**：
  1. **Extract**：从API提取数据
  2. **Transform**：清洗和转换数据
  3. **Load**：加载到存储系统

- **使用Apache Airflow**：
  ```python
  from airflow import DAG
  from airflow.operators.python import PythonOperator
  
  def extract_from_api():
      # API数据提取逻辑
      pass
      
  def transform_data():
      # 数据转换逻辑
      pass
      
  dag = DAG('api_data_pipeline', schedule_interval='@hourly')
  
  extract_task = PythonOperator(task_id='extract', python_callable=extract_from_api, dag=dag)
  transform_task = PythonOperator(task_id='transform', python_callable=transform_data, dag=dag)
  
  extract_task >> transform_task
  ```

## 幻灯片8: 高级API集成技术
- **GraphQL查询**：
  ```python
  import requests
  
  query = """
  {
    users(first: 10) {
      id
      name
      email
      posts {
        title
        content
      }
    }
  }
  """
  
  response = requests.post('https://api.example.com/graphql',
                          json={'query': query})
  ```

- **gRPC客户端**：
  ```python
  import grpc
  import api_pb2
  import api_pb2_grpc
  
  channel = grpc.secure_channel('api.example.com:443', grpc.ssl_channel_credentials())
  stub = api_pb2_grpc.DataServiceStub(channel)
  
  response = stub.GetData(api_pb2.GetDataRequest(limit=100))
  ```

## 幻灯片9: 实时数据可视化
- **使用Dash构建实时仪表板**：
  ```python
  import dash
  from dash import dcc, html
  from dash.dependencies import Input, Output
  
  app = dash.Dash(__name__)
  
  app.layout = html.Div([
      dcc.Graph(id='live-graph'),
      dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
  ])
  
  @app.callback(Output('live-graph', 'figure'), [Input('interval-component', 'n_intervals')])
  def update_graph(n):
      # 获取最新数据并更新图表
      return create_figure(get_latest_data())
  ```

- **使用Streamlit**：
  ```python
  import streamlit as st
  import pandas as pd
  
  st.title("实时数据监控")
  
  # 自动刷新
  placeholder = st.empty()
  
  while True:
      with placeholder.container():
          df = get_latest_data()
          st.line_chart(df)
      time.sleep(5)
  ```

## 幻灯片10: 性能优化与最佳实践
- **缓存策略**：
  - HTTP缓存头
  - 本地缓存（Redis, Memcached）
  - 请求去重

- **速率限制处理**：
  ```python
  import time
  from ratelimit import limits, sleep_and_retry
  
  @sleep_and_retry
  @limits(calls=100, period=60)  # 每分钟100次请求
  def call_api():
      return requests.get('https://api.example.com/data')
  ```

- **批量处理**：
  - 使用批量API端点
  - 数据分页处理
  - 异步并发请求

## 幻灯片11: 安全考虑
- **API密钥管理**：
  - 环境变量存储
  - 密钥轮换
  - 最小权限原则

- **数据安全**：
  - HTTPS加密传输
  - 敏感数据脱敏
  - 输入验证和清理

- **合规性**：
  - GDPR数据保护
  - API使用条款遵守
  - 数据保留策略

## 幻灯片12: 案例研究：金融数据API集成
- **项目背景**：
  - 实时股票价格监控
  - 多数据源整合
  - 风险预警系统

- **技术栈**：
  - Alpha Vantage API + Yahoo Finance API
  - Pandas 3.0数据处理
  - WebSocket实时推送
  - Dash仪表板展示

- **成果**：
  - 实时价格更新（<1秒延迟）
  - 异常波动自动预警
  - 历史数据回测功能

## 幻灯片13: 案例研究：社交媒体数据流分析
- **项目背景**：
  - Twitter/X实时数据流
  - 情感分析和趋势检测
  - 影响力评估

- **技术栈**：
  - Twitter API v2
  - Polars高性能数据处理
  - NLP情感分析模型
  - Kafka消息队列

- **成果**：
  - 实时话题趋势检测
  - 品牌声誉监控
  - KOL影响力排名

## 幻灯片14: 2026年API技术趋势
- **AI原生API**：
  - 自动生成API文档
  - 智能速率限制
  - 预测性缓存

- **边缘计算集成**：
  - 边缘API网关
  - 低延迟数据处理
  - 分布式数据源

- **无服务器架构**：
  - Serverless API函数
  - 自动扩展
  - 按需计费

## 幻灯片15: 实践项目
- **项目目标**：构建实时天气数据监控系统
- **技术要求**：
  - OpenWeatherMap API集成
  - 实时数据流处理
  - 可视化仪表板
  - 异常天气预警

- **交付物**：
  - 完整的数据管道代码
  - 实时可视化界面
  - 项目文档和演示

## 幻灯片16: 总结与下一步
- **关键要点回顾**：
  - API是现代数据科学的重要数据源
  - 实时数据处理需要特殊的技术栈
  - 数据管道设计要考虑性能和可靠性
  - 安全和合规性不可忽视

- **下一章预告**：第12章 - AI辅助数据分析与项目实战

## 幻灯片17: Q&A
- **问题与讨论**
- 联系方式：david.turing@example.com