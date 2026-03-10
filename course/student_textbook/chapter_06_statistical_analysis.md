# 第6章：统计分析基础

## 6.1 描述性统计

描述性统计是数据分析的基础，它帮助我们理解数据的基本特征。在Python中，我们可以使用`pandas`和`scipy`库来进行描述性统计分析。

### 6.1.1 基本统计量

```python
import pandas as pd
import numpy as np

# 创建示例数据
data = pd.DataFrame({
    'score': [85, 92, 78, 96, 88, 76, 94, 82, 89, 91],
    'hours_studied': [5, 8, 3, 10, 6, 2, 9, 4, 7, 8]
})

# 基本描述性统计
print("基本统计信息:")
print(data.describe())

# 具体统计量
print(f"\n均值: {data['score'].mean():.2f}")
print(f"中位数: {data['score'].median():.2f}")
print(f"标准差: {data['score'].std():.2f}")
print(f"方差: {data['score'].var():.2f}")
print(f"偏度: {data['score'].skew():.2f}")
print(f"峰度: {data['score'].kurtosis():.2f}")
```

### 6.1.2 分布可视化

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 直方图
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.hist(data['score'], bins=5, alpha=0.7, color='skyblue')
plt.title('成绩分布直方图')
plt.xlabel('分数')
plt.ylabel('频次')

# 箱线图
plt.subplot(1, 3, 2)
plt.boxplot(data['score'])
plt.title('成绩箱线图')
plt.ylabel('分数')

# Q-Q图
from scipy import stats
plt.subplot(1, 3, 3)
stats.probplot(data['score'], dist="norm", plot=plt)
plt.title('Q-Q图 (正态性检验)')

plt.tight_layout()
plt.show()
```

## 6.2 推断性统计

推断性统计帮助我们从样本数据推断总体特征。

### 6.2.1 假设检验

#### t检验（比较两组均值）

```python
from scipy import stats

# 示例：比较两个班级的成绩
class_a = [85, 92, 78, 96, 88, 76, 94, 82, 89, 91]
class_b = [78, 85, 72, 88, 82, 70, 86, 75, 83, 87]

# 独立样本t检验
t_stat, p_value = stats.ttest_ind(class_a, class_b)
print(f"t统计量: {t_stat:.4f}")
print(f"p值: {p_value:.4f}")

if p_value < 0.05:
    print("结论: 两个班级的成绩存在显著差异")
else:
    print("结论: 两个班级的成绩无显著差异")
```

#### 卡方检验（分类变量关联性）

```python
# 示例：性别与课程偏好的关联性
import numpy as np
from scipy.stats import chi2_contingency

# 列联表
contingency_table = np.array([
    [30, 20, 15],  # 男生：数学、语文、英语
    [25, 28, 22]   # 女生：数学、语文、英语
])

chi2, p, dof, expected = chi2_contingency(contingency_table)
print(f"卡方统计量: {chi2:.4f}")
print(f"p值: {p:.4f}")
print(f"自由度: {dof}")
print(f"期望频次:\n{expected}")
```

### 6.2.2 置信区间

```python
# 计算均值的置信区间
from scipy import stats
import numpy as np

scores = np.array([85, 92, 78, 96, 88, 76, 94, 82, 89, 91])
confidence_level = 0.95
degrees_freedom = len(scores) - 1
sample_mean = np.mean(scores)
sample_std = np.std(scores, ddof=1)

# 计算t临界值
t_critical = stats.t.ppf((1 + confidence_level) / 2, degrees_freedom)

# 计算标准误差
standard_error = sample_std / np.sqrt(len(scores))

# 计算置信区间
margin_of_error = t_critical * standard_error
confidence_interval = (sample_mean - margin_of_error, 
                      sample_mean + margin_of_error)

print(f"样本均值: {sample_mean:.2f}")
print(f"{int(confidence_level*100)}%置信区间: ({confidence_interval[0]:.2f}, {confidence_interval[1]:.2f})")
```

## 6.3 相关性分析

相关性分析用于研究变量之间的关系。

### 6.3.1 皮尔逊相关系数

```python
# 计算相关系数矩阵
correlation_matrix = data.corr()
print("相关系数矩阵:")
print(correlation_matrix)

# 可视化相关性热力图
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('变量相关性热力图')
plt.show()

# 计算具体的相关系数和p值
from scipy.stats import pearsonr

corr_coef, p_value = pearsonr(data['score'], data['hours_studied'])
print(f"\n学习时间与成绩的相关系数: {corr_coef:.4f}")
print(f"p值: {p_value:.4f}")

if abs(corr_coef) > 0.7:
    strength = "强"
elif abs(corr_coef) > 0.3:
    strength = "中等"
else:
    strength = "弱"

direction = "正" if corr_coef > 0 else "负"
print(f"结论: 学习时间与成绩呈{direction}{strength}相关")
```

### 6.3.2 斯皮尔曼等级相关

```python
from scipy.stats import spearmanr

# 当数据不满足正态分布时使用斯皮尔曼相关
spearman_corr, p_value = spearmanr(data['score'], data['hours_studied'])
print(f"斯皮尔曼相关系数: {spearman_corr:.4f}")
print(f"p值: {p_value:.4f}")
```

## 6.4 回归分析基础

回归分析用于建立变量之间的数学关系。

### 6.4.1 简单线性回归

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

# 准备数据
X = data[['hours_studied']]
y = data['score']

# 训练模型
model = LinearRegression()
model.fit(X, y)

# 预测
y_pred = model.predict(X)

# 模型评估
r2 = r2_score(y, y_pred)
mse = mean_squared_error(y, y_pred)
rmse = np.sqrt(mse)

print(f"回归方程: y = {model.intercept_:.2f} + {model.coef_[0]:.2f} * x")
print(f"R² (决定系数): {r2:.4f}")
print(f"RMSE (均方根误差): {rmse:.2f}")

# 可视化回归结果
plt.figure(figsize=(10, 6))
plt.scatter(X, y, alpha=0.7, label='实际数据')
plt.plot(X, y_pred, color='red', linewidth=2, label='回归线')
plt.xlabel('学习时间 (小时)')
plt.ylabel('成绩')
plt.title('学习时间与成绩的线性回归')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## 6.5 实践练习

### 练习6.1：学生成绩分析
使用提供的学生成绩数据集，完成以下任务：
1. 计算各科目的基本统计量
2. 进行正态性检验
3. 分析不同性别学生的成绩差异（假设检验）
4. 研究学习时间与各科目成绩的相关性

### 练习6.2：商品销售分析
使用销售数据集，分析：
1. 不同产品类别的销售额分布
2. 广告投入与销售额的关系
3. 季节性对销售的影响
4. 建立简单的销售预测模型

## 6.6 本章小结

- **描述性统计**：了解数据的基本特征（均值、中位数、标准差等）
- **推断性统计**：从样本推断总体（假设检验、置信区间）
- **相关性分析**：研究变量间的关系（皮尔逊、斯皮尔曼相关）
- **回归分析**：建立变量间的数学模型
- **实践应用**：将统计方法应用于实际问题

统计分析是数据分析的核心技能，掌握这些基础方法将为后续的机器学习和高级分析奠定坚实基础。