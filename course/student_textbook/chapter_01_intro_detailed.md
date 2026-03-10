---
title: 第一章 Python数据分析入门 - 学生指南
slug: python-data-analysis-chapter-01-student
summary: 本章将带你从零开始学习Python数据分析，掌握Jupyter Notebook、Pandas基础和数据探索的核心技能。
coverImage: imgs/chapter01_cover.png
---

# 第一章 Python数据分析入门

## 🎯 学习目标

完成本章后，你将能够：
- **熟练使用Jupyter Notebook**进行交互式编程
- **理解Pandas核心数据结构**：Series和DataFrame
- **掌握基本数据操作**：读取、查看、筛选数据
- **进行初步的数据探索**：描述性统计和简单可视化

## 💻 环境准备

### 1.1 安装必要的库

在开始之前，请确保你的环境中安装了以下库：

```bash
# 使用pip安装
pip install pandas numpy matplotlib seaborn jupyter

# 或者使用conda（推荐）
conda install pandas numpy matplotlib seaborn jupyter
```

### 1.2 启动Jupyter Notebook

打开终端，输入以下命令：

```bash
jupyter notebook
```

这将在你的默认浏览器中打开Jupyter界面。

## 📊 Pandas基础概念

### 2.1 什么是Pandas？

Pandas是一个强大的Python数据分析库，提供了高效的数据结构和数据分析工具。它的两个核心数据结构是：

- **Series**: 一维带标签的数组
- **DataFrame**: 二维表格型数据结构

### 2.2 创建DataFrame

让我们从创建一个简单的DataFrame开始：

```python
import pandas as pd

# 从字典创建DataFrame
data = {
    '姓名': ['张三', '李四', '王五', '赵六'],
    '年龄': [20, 22, 21, 23],
    '成绩': [85, 92, 78, 88],
    '专业': ['计算机', '数学', '物理', '化学']
}

df = pd.DataFrame(data)
print(df)
```

输出结果：
```
   姓名  年龄  成绩   专业
0  张三  20   85  计算机
1  李四  22   92   数学
2  王五  21   78   物理
3  赵六  23   88   化学
```

## 🔍 数据探索基础

### 3.1 查看数据基本信息

```python
# 查看前几行数据
print(df.head())

# 查看数据形状
print(f"数据形状: {df.shape}")

# 查看数据类型
print(df.dtypes)

# 查看基本统计信息
print(df.describe())
```

### 3.2 数据筛选和选择

```python
# 选择特定列
names = df['姓名']
print(names)

# 选择多列
subset = df[['姓名', '成绩']]
print(subset)

# 条件筛选
high_scores = df[df['成绩'] > 85]
print(high_scores)
```

## 📈 简单数据可视化

### 4.1 使用Matplotlib

```python
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建成绩分布图
plt.figure(figsize=(8, 6))
plt.bar(df['姓名'], df['成绩'])
plt.title('学生成绩分布')
plt.xlabel('学生姓名')
plt.ylabel('成绩')
plt.show()
```

### 4.2 使用Seaborn（更美观）

```python
import seaborn as sns

# 设置样式
sns.set_style("whitegrid")

# 创建散点图
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='年龄', y='成绩', hue='专业', s=100)
plt.title('年龄与成绩关系')
plt.show()
```

## 🏗️ 动手实践

### 5.1 练习1：数据加载

下载一个CSV文件（例如：`students.csv`），并加载到DataFrame中：

```python
# 加载CSV文件
df_students = pd.read_csv('students.csv')

# 查看数据
print(df_students.head())
print(df_students.info())
```

### 5.2 练习2：数据清洗

处理缺失值和异常值：

```python
# 检查缺失值
print(df_students.isnull().sum())

# 填充缺失值
df_students['成绩'].fillna(df_students['成绩'].mean(), inplace=True)

# 删除异常值（成绩不在0-100范围内）
df_clean = df_students[(df_students['成绩'] >= 0) & (df_students['成绩'] <= 100)]
```

### 5.3 练习3：基本分析

```python
# 按专业分组统计平均成绩
avg_by_major = df_clean.groupby('专业')['成绩'].mean()
print(avg_by_major)

# 找出最高分学生
top_student = df_clean.loc[df_clean['成绩'].idxmax()]
print(f"最高分学生: {top_student['姓名']}, 成绩: {top_student['成绩']}")
```

## 📚 本章小结

- **Jupyter Notebook** 是数据分析的理想环境
- **Pandas DataFrame** 是处理表格数据的核心工具
- **数据探索** 包括查看、筛选、统计和可视化
- **动手实践** 是掌握技能的关键

## 🎯 下一步

在下一章中，我们将深入学习Pandas的高级功能，包括数据合并、重塑和时间序列处理。

## ❓ 自测题

1. 如何创建一个包含学生信息的DataFrame？
2. `df.head()` 和 `df.tail()` 的区别是什么？
3. 如何筛选成绩大于90的学生？
4. 为什么在可视化时需要设置中文字体？

> **提示**：尝试在Jupyter Notebook中运行所有代码示例，并修改参数观察结果变化！