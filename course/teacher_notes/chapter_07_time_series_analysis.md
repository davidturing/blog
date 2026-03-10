# 第7章：时间序列分析

## 课程目标
- 掌握时间序列数据的基本概念和特征
- 学会使用Pandas进行时间序列操作
- 理解并应用常见的时间序列分析方法
- 能够构建简单的时间序列预测模型

## 核心知识点

### 7.1 时间序列基础概念
**时间序列定义**：按时间顺序排列的数据点序列，广泛应用于金融、气象、销售等领域。

**时间序列特征**：
- **趋势性（Trend）**：长期上升或下降的模式
- **季节性（Seasonality）**：固定周期内的重复模式
- **周期性（Cyclicity）**：非固定周期的波动
- **随机性（Randomness）**：无法预测的噪声成分

### 7.2 Pandas时间序列操作
```python
import pandas as pd
import numpy as np

# 创建时间序列
dates = pd.date_range('2026-01-01', periods=365, freq='D')
ts = pd.Series(np.random.randn(365), index=dates)

# 时间索引操作
ts['2026-01']  # 获取1月数据
ts['2026-01-01':'2026-01-31']  # 切片操作

# 重采样（Resampling）
daily_data = ts.resample('D').mean()  # 日频数据
monthly_data = ts.resample('M').sum()  # 月频汇总
```

### 7.3 时间序列分解
使用`statsmodels`库进行时间序列分解：

```python
from statsmodels.tsa.seasonal import seasonal_decompose

# 加法模型分解
decomposition = seasonal_decompose(ts, model='additive', period=30)
trend = decomposition.trend
seasonal = decomposition.seasonal  
residual = decomposition.resid

# 可视化分解结果
import matplotlib.pyplot as plt
fig, axes = plt.subplots(4, 1, figsize=(12, 8))
decomposition.observed.plot(ax=axes[0], title='Original')
decomposition.trend.plot(ax=axes[1], title='Trend')
decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
decomposition.resid.plot(ax=axes[3], title='Residual')
plt.tight_layout()
```

### 7.4 平稳性检验与处理
**平稳性重要性**：大多数时间序列模型要求数据平稳。

**ADF检验（Augmented Dickey-Fuller Test）**：
```python
from statsmodels.tsa.stattools import adfuller

def test_stationarity(timeseries):
    result = adfuller(timeseries.dropna())
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    if result[1] <= 0.05:
        print("数据是平稳的")
    else:
        print("数据是非平稳的")

# 差分处理非平稳数据
ts_diff = ts.diff().dropna()
test_stationarity(ts_diff)
```

### 7.5 ARIMA模型基础
**ARIMA(p,d,q)模型**：
- p: 自回归阶数
- d: 差分阶数  
- q: 移动平均阶数

```python
from statsmodels.tsa.arima.model import ARIMA

# 拟合ARIMA模型
model = ARIMA(ts, order=(1,1,1))
fitted_model = model.fit()

# 预测
forecast = fitted_model.forecast(steps=30)
```

### 7.6 实战案例：股票价格分析
**案例目标**：分析某股票的历史价格数据，进行趋势预测。

**数据获取**：
```python
# 使用yfinance获取股票数据（需要安装yfinance）
import yfinance as yf

# 获取苹果公司股票数据
aapl = yf.download('AAPL', start='2025-01-01', end='2026-12-31')
close_price = aapl['Close']

# 基础分析
print(f"数据范围: {close_price.index[0]} 到 {close_price.index[-1]}")
print(f"起始价格: ${close_price.iloc[0]:.2f}")
print(f"结束价格: ${close_price.iloc[-1]:.2f}")
```

**技术指标计算**：
```python
# 移动平均线
close_price['MA_20'] = close_price.rolling(window=20).mean()
close_price['MA_50'] = close_price.rolling(window=50).mean()

# 相对强弱指数(RSI)
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

close_price['RSI'] = calculate_rsi(close_price)
```

## 教学重点与难点

### 重点内容
1. **时间序列的基本操作**：索引、切片、重采样
2. **时间序列分解方法**：理解趋势、季节性和残差
3. **平稳性概念**：为什么需要平稳性，如何检验和处理

### 难点解析
1. **ARIMA参数选择**：通过ACF/PACF图确定p和q值
2. **季节性处理**：季节性差分 vs 季节性ARIMA
3. **模型评估**：使用AIC/BIC准则选择最佳模型

## 课堂练习

### 基础练习
1. 创建一个包含1000个数据点的随机时间序列
2. 对时间序列进行月度重采样
3. 计算7日移动平均线

### 进阶练习
1. 下载某个商品的历史价格数据
2. 进行时间序列分解分析
3. 构建ARIMA模型并进行未来30天的预测

## 课后作业

**作业7.1：空气质量数据分析**
- 数据集：北京2025年空气质量数据（PM2.5浓度）
- 任务：
  1. 分析PM2.5浓度的时间序列特征
  2. 进行季节性分解
  3. 建立预测模型，预测下个月的平均PM2.5浓度
  4. 撰写分析报告（500字）

**评分标准**：
- 数据处理正确性（30%）
- 分析方法合理性（30%）
- 预测结果准确性（20%）
- 报告质量（20%）

## 扩展阅读

1. **《Time Series Analysis: Forecasting and Control》** - George Box
2. **《Practical Time Series Forecasting with R》** - Galit Shmueli
3. **Statsmodels官方文档**：https://www.statsmodels.org/
4. **Pandas时间序列指南**：https://pandas.pydata.org/docs/user_guide/timeseries.html

## 下章预告

第8章将介绍机器学习在数据分析中的应用，包括监督学习和无监督学习的基础算法，以及如何使用scikit-learn库进行实际建模。