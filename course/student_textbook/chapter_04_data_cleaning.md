# 第4章：数据清洗与预处理

## 学习目标
- 掌握数据质量问题的识别方法
- 学会处理缺失值、重复值和异常值
- 理解数据类型转换和标准化的重要性
- 能够构建完整的数据清洗流程

## 4.1 数据质量问题概述

在实际的数据分析工作中，**原始数据往往存在各种质量问题**。根据2026年的行业调研，超过80%的数据科学家时间都花在了数据清洗上。

### 常见数据质量问题：
- **缺失值（Missing Values）**：某些字段为空或NaN
- **重复值（Duplicates）**：完全相同或部分相同的记录
- **异常值（Outliers）**：明显偏离正常范围的数据点
- **格式不一致**：日期、电话号码、地址等格式混乱
- **数据类型错误**：数值被存储为字符串，日期格式错误等

## 4.2 缺失值处理

### 4.2.1 识别缺失值

```python
import pandas as pd
import numpy as np

# 创建示例数据
df = pd.DataFrame({
    'name': ['张三', '李四', '王五', '赵六'],
    'age': [25, np.nan, 30, 35],
    'salary': [5000, 6000, np.nan, 8000],
    'department': ['IT', 'HR', 'IT', np.nan]
})

# 查看缺失值情况
print("缺失值统计：")
print(df.isnull().sum())
print("\n缺失值比例：")
print(df.isnull().mean())
```

### 4.2.2 处理策略

**1. 删除法**
```python
# 删除包含缺失值的行
df_dropped = df.dropna()

# 删除包含缺失值的列
df_dropped_cols = df.dropna(axis=1)

# 删除全部为缺失值的行
df_dropped_all = df.dropna(how='all')
```

**2. 填充法**
```python
# 用固定值填充
df_filled_const = df.fillna(0)

# 用均值/中位数/众数填充
df['age'].fillna(df['age'].mean(), inplace=True)
df['salary'].fillna(df['salary'].median(), inplace=True)
df['department'].fillna(df['department'].mode()[0], inplace=True)

# 前向填充/后向填充
df_ffill = df.fillna(method='ffill')
df_bfill = df.fillna(method='bfill')
```

**3. 预测填充**
```python
from sklearn.impute import KNNImputer

# 使用KNN算法预测缺失值
imputer = KNNImputer(n_neighbors=2)
df_numeric = df.select_dtypes(include=[np.number])
df_imputed = pd.DataFrame(
    imputer.fit_transform(df_numeric),
    columns=df_numeric.columns,
    index=df.index
)
```

## 4.3 重复值处理

### 4.3.1 识别重复值
```python
# 查看完全重复的行
duplicates = df.duplicated()
print(f"重复行数量: {duplicates.sum()}")

# 查看基于特定列的重复
duplicates_subset = df.duplicated(subset=['name', 'age'])
```

### 4.3.2 处理重复值
```python
# 删除重复行（保留第一个）
df_no_dup = df.drop_duplicates()

# 删除重复行（保留最后一个）
df_no_dup_last = df.drop_duplicates(keep='last')

# 基于特定列删除重复
df_no_dup_subset = df.drop_duplicates(subset=['name'])
```

## 4.4 异常值检测与处理

### 4.4.1 统计方法
```python
# Z-score方法（适用于正态分布）
from scipy import stats

z_scores = np.abs(stats.zscore(df.select_dtypes(include=[np.number])))
outliers_z = (z_scores > 3)

# IQR方法（适用于偏态分布）
Q1 = df['salary'].quantile(0.25)
Q3 = df['salary'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers_iqr = (df['salary'] < lower_bound) | (df['salary'] > upper_bound)
```

### 4.4.2 可视化方法
```python
import matplotlib.pyplot as plt
import seaborn as sns

# 箱线图
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='salary')
plt.title('薪资分布箱线图')
plt.show()

# 散点图
plt.figure(figsize=(10, 6))
plt.scatter(df['age'], df['salary'])
plt.xlabel('年龄')
plt.ylabel('薪资')
plt.title('年龄 vs 薪资散点图')
plt.show()
```

### 4.4.3 处理策略
- **删除异常值**：`df_clean = df[~outliers]`
- **替换为边界值**：将异常值替换为上下界
- **分箱处理**：将连续变量转换为分类变量
- **保持原样**：某些异常值可能是重要的业务信号

## 4.5 数据类型转换

### 4.5.1 字符串到数值
```python
# 清理字符串中的非数字字符
df['price_str'] = df['price_str'].str.replace('¥', '').str.replace(',', '')
df['price'] = pd.to_numeric(df['price_str'], errors='coerce')
```

### 4.5.2 日期时间处理
```python
# 转换日期格式
df['date'] = pd.to_datetime(df['date_str'], format='%Y-%m-%d')

# 提取日期组件
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.day_name()
```

### 4.5.3 分类数据处理
```python
# 转换为分类类型（节省内存）
df['department'] = df['department'].astype('category')

# 标签编码
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['department_encoded'] = le.fit_transform(df['department'])

# One-hot编码
df_encoded = pd.get_dummies(df, columns=['department'])
```

## 4.6 数据标准化与归一化

### 4.6.1 标准化（Z-score）
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
df_scaled = pd.DataFrame(
    scaler.fit_transform(df[['age', 'salary']]),
    columns=['age_scaled', 'salary_scaled']
)
```

### 4.6.2 归一化（Min-Max）
```python
from sklearn.preprocessing import MinMaxScaler

minmax_scaler = MinMaxScaler()
df_normalized = pd.DataFrame(
    minmax_scaler.fit_transform(df[['age', 'salary']]),
    columns=['age_norm', 'salary_norm']
)
```

## 4.7 构建完整的数据清洗流程

```python
def clean_data_pipeline(df):
    """
    完整的数据清洗流程
    """
    # 1. 处理缺失值
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True)
    
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
    
    # 2. 处理重复值
    df.drop_duplicates(inplace=True)
    
    # 3. 处理异常值（使用IQR方法）
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
    
    # 4. 数据类型优化
    for col in categorical_cols:
        if df[col].nunique() / len(df) < 0.5:  # 如果唯一值比例小于50%
            df[col] = df[col].astype('category')
    
    return df

# 使用清洗流程
df_clean = clean_data_pipeline(df.copy())
```

## 实践练习

### 练习4.1：电商数据清洗
下载一个真实的电商数据集（如Kaggle上的电商数据），完成以下任务：
1. 分析数据质量，识别主要问题
2. 设计并实现完整的清洗流程
3. 比较清洗前后的数据分布变化

### 练习4.2：股票数据异常值处理
获取某只股票的历史价格数据，使用多种方法检测异常值，并分析异常值产生的原因（如市场事件、数据错误等）。

## 本章小结

- 数据清洗是数据分析的基础步骤，直接影响后续分析的质量
- 需要根据数据特点选择合适的清洗策略
- 自动化的清洗流程可以提高工作效率
- 清洗过程中要保留数据的业务含义，避免过度处理

## 扩展阅读

- 《Python数据清洗实战》- 2026年最新版
- Pandas官方文档：数据清洗最佳实践
- Google的Data Validation开源工具