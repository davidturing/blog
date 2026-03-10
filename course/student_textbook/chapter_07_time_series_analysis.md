# 第7章：时间序列分析

## 学习目标
- 理解时间序列数据的特点和处理方法
- 掌握Pandas中时间序列操作的核心功能
- 学会使用statsmodels进行时间序列建模
- 能够进行基本的预测分析

## 7.1 时间序列基础概念

### 什么是时间序列？
时间序列是按时间顺序排列的数据点序列。在现实世界中，很多数据都具有时间维度：
- 股票价格随时间变化
- 气温记录
- 网站访问量统计
- 销售数据

### 时间序列的组成部分
一个典型的时间序列通常包含以下组成部分：

1. **趋势（Trend）**：长期的上升或下降模式
2. **季节性（Seasonality）**：固定周期内的重复模式
3. **周期性（Cyclic）**：不固定周期的波动
4. **随机噪声（Noise）**：无法解释的随机波动

## 7.2 Pandas时间序列操作

### 创建时间序列
```python
import pandas as pd
import numpy as np

# 创建日期范围
dates = pd.date_range('2026-01-01', periods=365, freq='D')
# 创建时间序列数据
ts = pd.Series(np.random.randn(365), index=dates)
print(ts.head())
```

### 时间索引操作
```python
# 选择特定日期
ts['2026-01-15']

# 选择日期范围
ts['2026-01-01':'2026-01-31']

# 重采样（Resampling）
monthly_data = ts.resample('M').mean()  # 月度平均
weekly_data = ts.resample('W').sum()    # 周度总和
```

### 时间偏移和移动窗口
```python
# 移动平均
ts.rolling(window=7).mean()  # 7天移动平均

# 滞后和领先
ts.shift(1)   # 滞后1期
ts.shift(-1)  # 领先1期

# 差分
ts.diff()     # 一阶差分
ts.diff(2)    # 二阶差分
```

## 7.3 时间序列可视化

### 基础时间序列图
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
ts.plot()
plt.title('时间序列数据')
plt.xlabel('日期')
plt.ylabel('数值')
plt.show()
```

### 分解时间序列
```python
from statsmodels.tsa.seasonal import seasonal_decompose

# 添加一些趋势和季节性
trend = np.linspace(0, 10, 365)
seasonal = np.sin(np.arange(365) * 2 * np.pi / 365 * 4)  # 季度季节性
noise = np.random.randn(365) * 0.5
ts_with_pattern = pd.Series(trend + seasonal + noise, index=dates)

# 分解
decomposition = seasonal_decompose(ts_with_pattern, model='additive', period=90)
decomposition.plot()
plt.show()
```

## 7.4 时间序列建模

### 自相关和偏自相关
```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
plot_acf(ts_with_pattern, lags=30, ax=ax1)
plot_pacf(ts_with_pattern, lags=30, ax=ax2)
plt.show()
```

### ARIMA模型
```python
from statsmodels.tsa.arima.model import ARIMA

# 拟合ARIMA模型
model = ARIMA(ts_with_pattern, order=(1, 1, 1))
fitted_model = model.fit()

# 预测
forecast = fitted_model.forecast(steps=30)
print(forecast)
```

## 7.5 实战案例：股票价格分析

让我们用真实的数据来练习时间序列分析。

```python
# 模拟股票价格数据
np.random.seed(42)
returns = np.random.normal(0.001, 0.02, 252)  # 日收益率
prices = 100 * np.exp(np.cumsum(returns))      # 价格序列
stock_dates = pd.date_range('2026-01-01', periods=252, freq='B')  # 工作日
stock_data = pd.Series(prices, index=stock_dates)

# 基本分析
print("股票价格统计:")
print(stock_data.describe())

# 可视化
plt.figure(figsize=(12, 6))
stock_data.plot(title='模拟股票价格 (2026年)')
plt.ylabel('价格 ($)')
plt.show()

# 计算技术指标
# 移动平均线
stock_data_ma20 = stock_data.rolling(window=20).mean()
stock_data_ma50 = stock_data.rolling(window=50).mean()

plt.figure(figsize=(12, 6))
stock_data.plot(label='价格', alpha=0.7)
stock_data_ma20.plot(label='20日均线', linewidth=2)
stock_data_ma50.plot(label='50日均线', linewidth=2)
plt.legend()
plt.title('股票价格与移动平均线')
plt.show()
```

## 7.6 高级话题

### 多变量时间序列
```python
# 创建多变量时间序列
data = {
    'temperature': np.random.normal(20, 5, 365),
    'humidity': np.random.normal(60, 10, 365),
    'pressure': np.random.normal(1013, 10, 365)
}
weather_data = pd.DataFrame(data, index=dates)

# 相关性分析
correlation_matrix = weather_data.corr()
print("相关性矩阵:")
print(correlation_matrix)
```

### 时间序列聚类
```python
from sklearn.cluster import KMeans

# 对时间序列进行聚类（需要特征工程）
features = weather_data.rolling(window=7).mean().dropna()
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(features)
print(f"聚类结果: {np.bincount(clusters)}")
```

## 7.7 本章小结

- 时间序列数据具有独特的时间依赖性特征
- Pandas提供了强大的时间序列处理功能
- 时间序列分析包括描述性分析、建模和预测
- 实际应用中需要结合领域知识进行分析

## 练习题

1. **基础练习**：创建一个包含1000个数据点的时间序列，计算其7天、30天和90天的移动平均。

2. **中级练习**：使用`seasonal_decompose`函数对一个包含明显季节性的数据集进行分解，并解释每个组成部分的含义。

3. **高级练习**：选择一个真实的时间序列数据集（如股票价格、气温数据等），进行完整的分析流程，包括数据预处理、可视化、模型拟合和预测。

4. **挑战练习**：实现一个简单的交易策略，基于移动平均线交叉信号进行买卖决策，并计算策略的收益率。

## 扩展阅读

- Hyndman, R.J., & Athanasopoulos, G. (2021). Forecasting: principles and practice.
- Hamilton, J.D. (1994). Time Series Analysis.
- Pandas官方文档中的时间序列章节

---
*本章内容基于2026年最新的Python数据分析技术栈，涵盖了从基础到进阶的时间序列分析方法。*