---
title: 第2章：Pandas基础与数据结构
slug: pandas-basics
summary: 掌握Pandas的核心数据结构DataFrame和Series，学会基本的数据操作方法。
coverImage: ./imgs/chapter_02_cover.png
---

# 第2章：Pandas基础与数据结构

## 2.1 Pandas简介

Pandas是Python数据分析的核心库，提供了高效的数据结构和数据分析工具。在2026年，Pandas 3.0版本带来了显著的性能提升和新特性。

### 2.1.1 为什么选择Pandas？

- **高性能**：基于NumPy构建，支持向量化操作
- **易用性**：直观的API设计，学习曲线平缓
- **功能丰富**：数据清洗、转换、分析、可视化一体化
- **生态系统**：与SciPy、Scikit-learn、Matplotlib等库无缝集成

```python
# 安装Pandas 3.0
pip install pandas==3.0.0

# 导入Pandas
import pandas as pd
import numpy as np
```

## 2.2 核心数据结构

### 2.2.1 Series（一维数据）

Series是一维带标签的数组，可以存储任何数据类型。

```python
# 创建Series
s1 = pd.Series([1, 3, 5, np.nan, 6, 8])
print(s1)

# 带自定义索引的Series
s2 = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
print(s2)

# 从字典创建Series
data_dict = {'apple': 45, 'banana': 32, 'orange': 67}
s3 = pd.Series(data_dict)
print(s3)
```

### 2.2.2 DataFrame（二维表格）

DataFrame是二维的表格型数据结构，类似于Excel表格或SQL表。

```python
# 从字典创建DataFrame
data = {
    'name': ['张三', '李四', '王五'],
    'age': [25, 30, 35],
    'city': ['北京', '上海', '广州']
}
df = pd.DataFrame(data)
print(df)

# 查看DataFrame基本信息
print(f"形状: {df.shape}")
print(f"列名: {df.columns.tolist()}")
print(f"数据类型:\n{df.dtypes}")
```

## 2.3 数据读取与写入

### 2.3.1 读取CSV文件

```python
# 读取CSV文件
df_csv = pd.read_csv('data/students.csv')

# 指定编码和分隔符
df_csv = pd.read_csv('data/students.csv', encoding='utf-8', sep=',')

# 只读取前1000行（大数据集处理）
df_sample = pd.read_csv('data/large_dataset.csv', nrows=1000)
```

### 2.3.2 读取Excel文件

```python
# 读取Excel文件
df_excel = pd.read_excel('data/report.xlsx', sheet_name='Sheet1')

# 读取多个工作表
excel_file = pd.ExcelFile('data/multi_sheet.xlsx')
df_sheet1 = excel_file.parse('Sheet1')
df_sheet2 = excel_file.parse('Sheet2')
```

### 2.3.3 写入数据

```python
# 写入CSV
df.to_csv('output/result.csv', index=False, encoding='utf-8-sig')

# 写入Excel
df.to_excel('output/report.xlsx', sheet_name='Results', index=False)
```

## 2.4 基本数据操作

### 2.4.1 查看数据

```python
# 查看前5行
print(df.head())

# 查看后5行
print(df.tail())

# 查看随机5行
print(df.sample(5))

# 查看统计摘要
print(df.describe())

# 查看数据信息
print(df.info())
```

### 2.4.2 选择数据

```python
# 选择单列
ages = df['age']

# 选择多列
subset = df[['name', 'age']]

# 按位置选择（iloc）
first_row = df.iloc[0]  # 第一行
first_three_rows = df.iloc[:3]  # 前三行

# 按标签选择（loc）
named_row = df.loc[df['name'] == '张三']
```

### 2.4.3 条件筛选

```python
# 单条件筛选
adults = df[df['age'] >= 18]

# 多条件筛选
beijing_adults = df[(df['age'] >= 18) & (df['city'] == '北京')]

# 使用isin进行多值筛选
selected_cities = df[df['city'].isin(['北京', '上海'])]
```

## 2.5 数据类型处理

### 2.5.1 查看和转换数据类型

```python
# 查看数据类型
print(df.dtypes)

# 转换数据类型
df['age'] = df['age'].astype('int32')
df['score'] = pd.to_numeric(df['score'], errors='coerce')
```

### 2.5.2 日期时间处理

```python
# 转换为日期时间
df['date'] = pd.to_datetime(df['date_string'])

# 提取日期组件
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
```

## 2.6 实践练习

### 练习2.1：学生成绩分析

```python
# 创建学生成绩数据
students_data = {
    '姓名': ['张三', '李四', '王五', '赵六', '钱七'],
    '数学': [85, 92, 78, 88, 95],
    '英语': [78, 85, 82, 90, 87],
    '物理': [88, 90, 75, 85, 92]
}

df_students = pd.DataFrame(students_data)

# 计算总分和平均分
df_students['总分'] = df_students[['数学', '英语', '物理']].sum(axis=1)
df_students['平均分'] = df_students[['数学', '英语', '物理']].mean(axis=1)

print("学生成绩表:")
print(df_students)

# 找出平均分最高的学生
top_student = df_students.loc[df_students['平均分'].idxmax(), '姓名']
print(f"\n平均分最高的学生: {top_student}")
```

### 练习2.2：数据探索

使用真实数据集进行探索：
1. 下载iris数据集
2. 加载数据并查看基本信息
3. 进行基本的统计分析
4. 筛选出特定条件的数据

## 2.7 本章小结

本章介绍了Pandas的基础知识，包括：
- **Series和DataFrame**：Pandas的两个核心数据结构
- **数据读取与写入**：支持多种文件格式
- **基本操作**：数据选择、筛选、查看
- **数据类型处理**：类型转换和日期处理

掌握这些基础知识是进行高级数据分析的前提。下一章将深入学习数据清洗和预处理技术。

## 2.8 扩展阅读

- [Pandas官方文档](https://pandas.pydata.org/docs/)
- [10分钟入门Pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- [Pandas 3.0新特性](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)