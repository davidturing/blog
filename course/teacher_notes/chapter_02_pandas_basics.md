# 第二章：Pandas 数据处理基础

## 教学目标
- 掌握 Pandas 的核心数据结构：Series 和 DataFrame
- 熟练进行数据读取、写入和基本操作
- 理解索引、选择和过滤的基本原理

## 教学重点与难点
**重点：**
- DataFrame 的创建和基本属性
- 数据选择和过滤的各种方法
- 常用的数据处理函数

**难点：**
- 多层次索引的理解和应用
- 条件选择的复杂组合
- 内存优化和性能考虑

## 教学内容

### 2.1 Pandas 核心数据结构
```python
import pandas as pd
import numpy as np

# Series: 一维带标签的数组
s = pd.Series([1, 3, 5, np.nan, 6, 8])
print(s)

# DataFrame: 二维表格型数据结构
df = pd.DataFrame({
    'A': 1.,
    'B': pd.Timestamp('2026-01-01'),
    'C': pd.Series(1, index=list(range(4)), dtype='float32'),
    'D': np.array([3] * 4, dtype='int32'),
    'E': pd.Categorical(["test", "train", "test", "train"]),
    'F': 'foo'
})
print(df)
```

### 2.2 数据读取与写入
- CSV 文件：`pd.read_csv()`, `df.to_csv()`
- Excel 文件：`pd.read_excel()`, `df.to_excel()`
- JSON 文件：`pd.read_json()`, `df.to_json()`
- 数据库：`pd.read_sql()`

### 2.3 数据选择与过滤
- 按列选择：`df['column']`, `df[['col1', 'col2']]`
- 按行选择：`df.loc[]`, `df.iloc[]`
- 条件过滤：`df[df['column'] > value]`
- 布尔索引和查询方法

### 2.4 常用数据处理操作
- 缺失值处理：`isna()`, `dropna()`, `fillna()`
- 数据类型转换：`astype()`
- 数据排序：`sort_values()`, `sort_index()`
- 数据去重：`drop_duplicates()`

## 教学建议
1. **实践导向**：每讲解一个概念后立即让学生动手练习
2. **案例驱动**：使用真实数据集（如鸢尾花数据集、泰坦尼克号数据集）
3. **对比教学**：对比 NumPy 数组和 Pandas DataFrame 的差异
4. **性能意识**：强调大数据量下的性能优化技巧

## 课堂练习
1. 从 CSV 文件读取学生成绩数据
2. 筛选出数学成绩大于80分的学生
3. 计算各科平均分并添加到数据框中
4. 处理缺失的成绩数据

## 课后作业
- 完成 Kaggle 上的 Titanic 数据分析入门项目
- 编写函数实现自动化的数据清洗流程