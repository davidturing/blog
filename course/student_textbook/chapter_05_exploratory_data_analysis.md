# 第5章：探索性数据分析（EDA）

## 5.1 什么是探索性数据分析

探索性数据分析（Exploratory Data Analysis, EDA）是数据分析的第一步，也是最重要的一步。它的目标是通过可视化和统计方法来理解数据的基本特征、发现模式、识别异常值，并为后续的建模和分析提供方向。

### 5.1.1 EDA的核心目标

- **理解数据分布**：了解每个变量的取值范围、集中趋势和离散程度
- **发现变量关系**：识别变量之间的相关性、依赖关系或模式
- **检测异常值**：找出可能影响分析结果的异常数据点
- **验证假设**：检验关于数据的初步假设是否成立
- **指导后续分析**：为特征工程、模型选择等提供依据

### 5.1.2 EDA的基本流程

1. **数据概览**：使用 `df.info()`, `df.describe()` 等方法快速了解数据
2. **单变量分析**：分析每个变量的分布特征
3. **双变量分析**：分析两个变量之间的关系
4. **多变量分析**：分析多个变量的复杂关系
5. **总结洞察**：形成对数据的整体理解

## 5.2 单变量分析

单变量分析关注单个变量的特征和分布。

### 5.2.1 数值型变量分析

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 创建示例数据
data = pd.read_csv('example_dataset.csv')

# 基本统计信息
print(data['price'].describe())

# 直方图
plt.figure(figsize=(10, 6))
plt.hist(data['price'], bins=30, alpha=0.7)
plt.title('价格分布直方图')
plt.xlabel('价格')
plt.ylabel('频次')
plt.show()

# 箱线图
plt.figure(figsize=(8, 6))
sns.boxplot(y=data['price'])
plt.title('价格箱线图')
plt.show()
```

### 5.2.2 分类型变量分析

```python
# 频数统计
category_counts = data['category'].value_counts()
print(category_counts)

# 条形图
plt.figure(figsize=(10, 6))
category_counts.plot(kind='bar')
plt.title('类别分布')
plt.xlabel('类别')
plt.ylabel('数量')
plt.xticks(rotation=45)
plt.show()

# 饼图
plt.figure(figsize=(8, 8))
plt.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
plt.title('类别占比')
plt.show()
```

## 5.3 双变量分析

双变量分析探索两个变量之间的关系。

### 5.3.1 数值型 vs 数值型

```python
# 散点图
plt.figure(figsize=(10, 8))
plt.scatter(data['area'], data['price'], alpha=0.6)
plt.title('面积 vs 价格')
plt.xlabel('面积 (平方米)')
plt.ylabel('价格 (万元)')
plt.show()

# 相关性热力图
correlation_matrix = data[['area', 'price', 'rooms']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('变量相关性热力图')
plt.show()
```

### 5.3.2 分类型 vs 数值型

```python
# 箱线图比较
plt.figure(figsize=(12, 8))
sns.boxplot(x='category', y='price', data=data)
plt.title('不同类别下的价格分布')
plt.xlabel('类别')
plt.ylabel('价格')
plt.xticks(rotation=45)
plt.show()

# 小提琴图
plt.figure(figsize=(12, 8))
sns.violinplot(x='category', y='price', data=data)
plt.title('不同类别下的价格分布（小提琴图）')
plt.xlabel('类别')
plt.ylabel('价格')
plt.xticks(rotation=45)
plt.show()
```

### 5.3.3 分类型 vs 分类型

```python
# 交叉表
crosstab = pd.crosstab(data['category'], data['region'])
print(crosstab)

# 堆叠条形图
crosstab.plot(kind='bar', stacked=True, figsize=(12, 8))
plt.title('类别与区域的交叉分布')
plt.xlabel('类别')
plt.ylabel('数量')
plt.xticks(rotation=45)
plt.legend(title='区域')
plt.show()
```

## 5.4 多变量分析

多变量分析处理三个或更多变量的复杂关系。

### 5.4.1 多维散点图矩阵

```python
# 散点图矩阵
numeric_cols = ['price', 'area', 'rooms', 'age']
sns.pairplot(data[numeric_cols])
plt.suptitle('数值变量散点图矩阵', y=1.02)
plt.show()
```

### 5.4.2 分组分析

```python
# 按多个维度分组
grouped = data.groupby(['category', 'region'])['price'].agg(['mean', 'std', 'count'])
print(grouped)

# 可视化分组结果
plt.figure(figsize=(14, 8))
grouped['mean'].unstack().plot(kind='bar', figsize=(14, 8))
plt.title('不同类别和区域的平均价格')
plt.xlabel('类别')
plt.ylabel('平均价格')
plt.legend(title='区域')
plt.xticks(rotation=45)
plt.show()
```

## 5.5 自动化EDA工具

现代Python生态提供了多种自动化EDA工具，可以快速生成全面的数据分析报告。

### 5.5.1 使用pandas-profiling

```python
# 安装: pip install pandas-profiling
from pandas_profiling import ProfileReport

# 生成完整报告
profile = ProfileReport(data, title="数据分析报告", explorative=True)
profile.to_file("eda_report.html")
```

### 5.5.2 使用Sweetviz

```python
# 安装: pip install sweetviz
import sweetviz as sv

# 生成对比报告
report = sv.analyze(data)
report.show_html("sweetviz_report.html")
```

### 5.5.3 使用AutoViz

```python
# 安装: pip install autoviz
from autoviz.AutoViz_Class import AutoViz_Class

AV = AutoViz_Class()
dft = AV.AutoViz('example_dataset.csv')
```

## 5.6 实战案例：房价数据EDA

让我们通过一个完整的房价数据集来演示EDA的全过程。

### 5.6.1 数据加载和概览

```python
# 加载数据
house_data = pd.read_csv('house_prices.csv')

# 数据概览
print("数据形状:", house_data.shape)
print("\n数据类型:")
print(house_data.dtypes)
print("\n缺失值:")
print(house_data.isnull().sum())
print("\n基本统计:")
print(house_data.describe())
```

### 5.6.2 关键变量分析

```python
# 目标变量分析
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.hist(house_data['price'], bins=50, alpha=0.7)
plt.title('房价分布')
plt.xlabel('价格')

plt.subplot(1, 2, 2)
plt.hist(np.log(house_data['price']), bins=50, alpha=0.7)
plt.title('房价对数分布')
plt.xlabel('log(价格)')

plt.tight_layout()
plt.show()
```

### 5.6.3 特征重要性初步分析

```python
# 相关性分析
target_corr = house_data.corr()['price'].sort_values(ascending=False)
print("与房价的相关性:")
print(target_corr)

# 可视化前10个最相关的特征
plt.figure(figsize=(10, 8))
top_features = target_corr.iloc[1:11]  # 排除自身
plt.barh(range(len(top_features)), top_features.values)
plt.yticks(range(len(top_features)), top_features.index)
plt.xlabel('相关系数')
plt.title('与房价最相关的10个特征')
plt.show()
```

## 5.7 EDA最佳实践

### 5.7.1 迭代式分析

EDA不是一次性的过程，而是一个迭代的过程：
- 从简单分析开始
- 根据发现提出新问题
- 进行更深入的分析
- 不断验证和修正假设

### 5.7.2 文档化发现

在EDA过程中，及时记录重要的发现：
- 异常值的位置和可能原因
- 变量间的有趣关系
- 数据质量问题
- 对后续分析的建议

### 5.7.3 可重现性

确保EDA过程的可重现性：
- 使用版本控制管理代码
- 记录使用的库和版本
- 保存关键的可视化结果
- 编写清晰的注释和文档

## 5.8 本章小结

- EDA是数据分析的基础步骤，帮助我们理解数据的本质特征
- 单变量、双变量和多变量分析构成了EDA的完整框架
- 现代Python工具提供了强大的自动化EDA能力
- 良好的EDA实践能够显著提高后续分析的质量和效率
- EDA是一个迭代和探索的过程，需要保持开放和好奇的心态

## 5.9 练习题

1. **基础练习**：选择一个公开数据集，进行完整的单变量分析
2. **进阶练习**：分析两个数值变量之间的关系，并尝试拟合简单的回归线
3. **挑战练习**：使用自动化EDA工具生成报告，并与手动分析的结果进行对比
4. **项目练习**：选择一个实际业务场景，设计并执行完整的EDA流程

## 5.10 扩展阅读

- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
- Wickham, H., & Grolemund, G. (2016). *R for Data Science*. O'Reilly Media.
- McKinney, W. (2017). *Python for Data Analysis*. O'Reilly Media.