# 第5章：探索性数据分析（EDA）

## 5.1 EDA的核心概念与流程

探索性数据分析（Exploratory Data Analysis, EDA）是数据科学工作流中的关键环节。本章将深入讲解如何系统性地进行数据探索，发现数据中的模式、异常和关系。

### 5.1.1 EDA的目标与原则
- **理解数据分布**：掌握数据的基本统计特征
- **识别异常值**：发现数据中的异常点和错误
- **探索变量关系**：分析特征之间的相关性和依赖关系
- **形成假设**：为后续建模提供方向和假设

### 5.1.2 EDA的标准流程
1. **数据概览**：shape、info、describe
2. **单变量分析**：分布、中心趋势、离散程度
3. **双变量分析**：相关性、分组比较
4. **多变量分析**：聚类、降维
5. **可视化总结**：制作综合报告

## 5.2 单变量EDA技术

### 5.2.1 数值型变量分析
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 基础统计
df['column'].describe()

# 分布可视化
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
sns.histplot(df['column'], kde=True)
plt.title('直方图 + KDE')

plt.subplot(1, 2, 2)
sns.boxplot(y=df['column'])
plt.title('箱线图')
plt.show()
```

### 5.2.2 分类型变量分析
```python
# 频次统计
df['category'].value_counts()

# 可视化
plt.figure(figsize=(8, 6))
df['category'].value_counts().plot(kind='bar')
plt.title('类别分布')
plt.xticks(rotation=45)
plt.show()
```

## 5.3 多变量EDA技术

### 5.3.1 相关性分析
```python
# 数值变量相关性
correlation_matrix = df.select_dtypes(include=['number']).corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('相关性热力图')
plt.show()
```

### 5.3.2 分组分析
```python
# 按类别分组的数值分析
df.groupby('category')['numeric_column'].agg(['mean', 'std', 'count'])

# 可视化分组比较
sns.boxplot(data=df, x='category', y='numeric_column')
plt.title('分组箱线图')
plt.xticks(rotation=45)
plt.show()
```

## 5.4 自动化EDA工具

### 5.4.1 使用Pandas Profiling
```python
from pandas_profiling import ProfileReport

# 生成完整报告
profile = ProfileReport(df, title="EDA Report")
profile.to_file("eda_report.html")
```

### 5.4.2 使用Sweetviz
```python
import sweetviz as sv

# 快速EDA
report = sv.analyze(df)
report.show_html("sweetviz_report.html")
```

## 5.5 实战案例：电商用户行为分析

### 5.5.1 数据加载与初步探索
```python
# 加载电商数据
ecommerce_df = pd.read_csv('ecommerce_data.csv')
print(f"数据形状: {ecommerce_df.shape}")
print("\n数据信息:")
ecommerce_df.info()
```

### 5.5.2 关键指标分析
- 用户活跃度分布
- 购买金额分布  
- 转化率分析
- 用户生命周期价值(LTV)

### 5.5.3 异常检测与处理
```python
# 使用IQR方法检测异常值
Q1 = ecommerce_df['purchase_amount'].quantile(0.25)
Q3 = ecommerce_df['purchase_amount'].quantile(0.75)
IQR = Q3 - Q1
outliers = ecommerce_df[
    (ecommerce_df['purchase_amount'] < (Q1 - 1.5 * IQR)) | 
    (ecommerce_df['purchase_amount'] > (Q3 + 1.5 * IQR))
]
print(f"发现 {len(outliers)} 个异常值")
```

## 5.6 教学要点与注意事项

### 5.6.1 教学重点
- **循序渐进**：从单变量到多变量，逐步深入
- **实践导向**：每个概念都要配合实际代码演示
- **工具对比**：手动分析 vs 自动化工具的优缺点
- **业务理解**：强调EDA在实际业务场景中的应用价值

### 5.6.2 常见误区
- **过度依赖自动化工具**：忽略对数据的深入理解
- **忽视数据质量**：不检查数据的完整性和准确性
- **缺乏业务背景**：纯技术分析，脱离实际应用场景
- **可视化不当**：选择不适合数据类型的图表

## 5.7 课后练习与项目

### 5.7.1 基础练习
1. 对给定数据集进行完整的单变量分析
2. 计算并可视化变量间的相关性矩阵
3. 使用自动化工具生成EDA报告并解读结果

### 5.7.2 进阶项目
**项目名称**：金融风控数据EDA分析
- **目标**：分析贷款申请数据，识别风险因素
- **要求**：完成完整的EDA流程，提交分析报告
- **评估标准**：分析深度、可视化质量、业务洞察

## 5.8 扩展阅读与资源

- **书籍推荐**：《Python for Data Analysis》第3版
- **在线课程**：Kaggle EDA微课程
- **工具文档**：Pandas Profiling官方文档
- **最佳实践**：Google Data Analysis Best Practices

---
*本章内容适用于985高校工科学生，强调理论与实践结合，培养扎实的数据分析基础能力。*