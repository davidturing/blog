# 第7章：时间序列分析

## 幻灯片1: 课程标题
- **第7章：时间序列分析**
- Python数据分析课程
- 讲师：David Turing

## 幻灯片2: 学习目标
- 理解时间序列数据的基本特征
- 掌握时间序列的预处理技术
- 学习经典时间序列分析方法
- 掌握现代时间序列预测模型
- 实践真实时间序列数据集分析

## 幻灯片3: 时间序列基础概念
- **时间序列定义**：按时间顺序排列的数据点序列
- **关键特征**：
  - 趋势性（Trend）
  - 季节性（Seasonality）
  - 周期性（Cyclicity）
  - 随机性（Randomness）
- **平稳性**：均值、方差、自协方差不随时间变化

## 幻灯片4: Pandas 3.0中的时间序列功能
- **日期时间处理**：
  - `pd.to_datetime()`：灵活的日期解析
  - `pd.date_range()`：生成日期范围
- **时间序列索引**：
  - `DatetimeIndex`：高效的日期索引
  - `PeriodIndex`：周期索引
- **新特性**：`resample_auto()`（Pandas 3.0新增智能重采样）

## 幻灯片5: 时间序列预处理
- **缺失值处理**：
  - 前向填充/后向填充
  - 插值方法：线性、多项式、样条
- **异常值检测**：
  - 移动窗口统计
  - 季节性分解方法
- **频率转换**：
  - 升采样（Upsampling）
  - 降采样（Downsampling）

## 幻灯片6: 实战示例 - 时间序列预处理
```python
# 使用Pandas 3.0处理时间序列
import pandas as pd

# 加载时间序列数据
ts_data = pd.read_csv('stock_prices.csv', 
                     parse_dates=['date'], 
                     index_col='date')

# 智能重采样
daily_data = ts_data.resample_auto('D')  # 新增方法

# 缺失值插值
ts_filled = daily_data.interpolate(method='time')

# 异常值检测
rolling_stats = ts_filled.rolling(window=30)
outliers = ts_filled[(ts_filled > rolling_stats.mean() + 3*rolling_stats.std())]
```

## 幻灯片7: 经典时间序列分析方法
- **移动平均法**（MA）：
  - 简单移动平均
  - 加权移动平均
  - 指数平滑
- **自回归模型**（AR）：
  - AR(p)模型
  - 参数估计
- **ARIMA模型**：
  - 差分整合
  - 模型识别与诊断

## 幻灯片8: 季节性分解与分析
- **STL分解**（Seasonal-Trend decomposition using Loess）：
  ```python
  from statsmodels.tsa.seasonal import STL
  
  stl = STL(ts_data, seasonal=13)
  result = stl.fit()
  ```
  
- **X-13ARIMA-SEATS**：
  - 官方统计机构标准方法
  - 处理复杂季节模式

## 幻灯片9: 现代时间序列预测模型
- **Prophet**（Facebook）：
  - 自动处理趋势和季节性
  - 内置节假日效应
  - 不确定性量化
  
- **LSTM神经网络**：
  - 处理长期依赖
  - 非线性模式捕捉
  - 多变量时间序列

## 幻灯片10: Prophet实战示例
```python
from prophet import Prophet

# 准备数据（Prophet要求特定格式）
df_prophet = ts_data.reset_index()
df_prophet.columns = ['ds', 'y']

# 创建并拟合模型
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)
model.fit(df_prophet)

# 预测未来30天
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 可视化结果
fig = model.plot(forecast)
```

## 幻灯片11: LSTM时间序列预测
- **模型架构**：
  - 输入层：时间步长序列
  - LSTM层：记忆单元
  - 输出层：预测值
  
- **实现要点**：
  ```python
  from tensorflow.keras.models import Sequential
  from tensorflow.keras.layers import LSTM, Dense
  
  model = Sequential([
      LSTM(50, return_sequences=True, input_shape=(timesteps, features)),
      LSTM(50, return_sequences=False),
      Dense(25),
      Dense(1)
  ])
  
  model.compile(optimizer='adam', loss='mean_squared_error')
  model.fit(X_train, y_train, batch_size=1, epochs=1)
  ```

## 幻灯片12: 多变量时间序列分析
- **VAR模型**（向量自回归）：
  - 处理多个相关时间序列
  - 格兰杰因果检验
  
- **状态空间模型**：
  - Kalman滤波器
  - 动态线性模型
  
- **图神经网络**（GNN）：
  - 处理时空数据
  - 节点间依赖关系建模

## 幻灯片13: 时间序列可视化最佳实践
- **交互式可视化**：
  - Plotly：动态缩放和悬停
  - Bokeh：实时更新
  
- **多尺度展示**：
  - 整体趋势视图
  - 局部细节放大
  - 季节性模式高亮

- **预测不确定性可视化**：
  - 置信区间带
  - 分位数预测

## 幻灯片14: Polars在时间序列处理中的优势
- **性能对比**：
  | 操作 | Pandas 3.0 | Polars |
  |------|------------|--------|
  | 重采样1M点 | 8s | 2s |
  | 滚动窗口计算 | 12s | 3s |
  | 日期解析 | 5s | 1s |

- **表达式API**：
  ```python
  # Polars时间序列处理
  import polars as pl
  
  df_polars = pl.read_csv('ts_data.csv')
  result = df_polars.with_columns([
      pl.col('value').rolling_mean(window_size=30).alias('rolling_avg'),
      pl.col('date').dt.weekday().alias('weekday')
  ])
  ```

## 幻灯片15: Dask处理大规模时间序列
- **分布式时间序列分析**：
  ```python
  import dask.dataframe as dd
  
  # 处理TB级时间序列数据
  large_ts = dd.read_csv('massive_ts_data_*.csv', 
                        parse_dates=['timestamp'])
  
  # 分布式重采样和聚合
  daily_stats = large_ts.set_index('timestamp').resample('D').agg({
      'value': ['mean', 'std', 'count']
  }).compute()
  ```

## 幻灯片16: AI辅助时间序列分析
- **自动模型选择**：
  - AutoARIMA
  - AutoML时间序列
  - 模型集成
  
- **异常检测AI**：
  ```python
  # 使用AI工具进行异常检测
  from aits import TimeSeriesAnomalyDetector
  
  detector = TimeSeriesAnomalyDetector()
  anomalies = detector.detect(ts_data, method='ensemble')
  ```

## 幻灯片17: 完整时间序列分析流程
1. **数据探索**：了解时间序列特征
2. **预处理**：处理缺失值、异常值、频率转换
3. **分解分析**：分离趋势、季节性、残差
4. **模型选择**：根据数据特征选择合适模型
5. **模型训练与验证**：交叉验证、性能评估
6. **预测与可视化**：生成预测结果并可视化

## 幻灯片18: 实践项目
- **项目目标**：分析股票价格时间序列
- **数据集**：S&P 500历史价格数据
- **任务要求**：
  - 预处理和可视化时间序列
  - 实现多种预测模型（ARIMA、Prophet、LSTM）
  - 比较模型性能
  - 生成投资建议报告

## 幻灯片19: 总结与下一步
- **关键要点回顾**：
  - 时间序列分析需要专门的预处理技术
  - 经典方法与现代AI方法各有优势
  - 可视化对理解时间序列至关重要
  
- **下一章预告**：第8章 - 机器学习入门

## 幻灯片20: Q&A
- **问题与讨论**
- 联系方式：david.turing@example.com