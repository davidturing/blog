# 第6章：统计分析基础

## 幻灯片1: 课程标题
- **第6章：统计分析基础**
- Python数据分析课程
- 讲师：David Turing

## 幻灯片2: 学习目标
- 理解描述性统计的核心概念
- 掌握概率分布的基本知识
- 学习假设检验的方法和应用
- 掌握置信区间的计算和解释
- 实践使用Python进行统计分析

## 幻灯片3: 描述性统计概述
- **集中趋势度量**：
  - 均值、中位数、众数
  - 几何平均数、调和平均数
- **离散程度度量**：
  - 方差、标准差
  - 四分位距(IQR)
  - 极差
- **分布形状度量**：
  - 偏度(Skewness)
  - 峰度(Kurtosis)

## 幻灯片4: Pandas 3.0中的统计功能
- `describe()`：快速统计摘要
- `mean()`, `median()`, `mode()`：集中趋势
- `std()`, `var()`：离散程度
- `skew()`, `kurt()`：分布形状
- 新特性：`stat_summary()`方法（Pandas 3.0新增）

```python
# 使用Pandas 3.0的新统计功能
df.describe(include='all')
df.stat_summary(groupby='category')  # 新增方法
```

## 幻灯片5: 概率分布基础
- **离散分布**：
  - 二项分布(Binomial)
  - 泊松分布(Poisson)
  - 几何分布(Geometric)
- **连续分布**：
  - 正态分布(Normal)
  - t分布(t-distribution)
  - 卡方分布(Chi-square)
  - F分布(F-distribution)

## 幻灯片6: SciPy.stats在统计分析中的应用
- **概率密度函数(PDF)**：`scipy.stats.norm.pdf()`
- **累积分布函数(CDF)**：`scipy.stats.norm.cdf()`
- **分位数函数(PPF)**：`scipy.stats.norm.ppf()`
- **随机变量生成**：`scipy.stats.norm.rvs()`

```python
import scipy.stats as stats
import numpy as np

# 生成正态分布数据
data = stats.norm.rvs(loc=0, scale=1, size=1000)

# 拟合分布
params = stats.norm.fit(data)
```

## 幻灯片7: 假设检验基础
- **零假设(H₀) vs 备择假设(H₁)**
- **显著性水平(α)**：通常为0.05
- **p值解释**：
  - p < α：拒绝零假设
  - p ≥ α：无法拒绝零假设
- **第一类错误 vs 第二类错误**

## 幻灯片8: 常用假设检验方法
- **t检验**：
  - 单样本t检验
  - 独立样本t检验
  - 配对样本t检验
- **卡方检验**：分类数据的独立性检验
- **ANOVA**：多组均值比较
- **非参数检验**：Mann-Whitney U检验、Wilcoxon符号秩检验

## 幻灯片9: 实战示例 - t检验
```python
from scipy import stats
import pandas as pd

# 加载数据
df = pd.read_csv('experiment_data.csv')

# 独立样本t检验
group_a = df[df['group'] == 'A']['score']
group_b = df[df['group'] == 'B']['score']

t_stat, p_value = stats.ttest_ind(group_a, group_b)
print(f"t-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")

# 结果解释
if p_value < 0.05:
    print("两组存在显著差异")
else:
    print("两组无显著差异")
```

## 幻灯片10: 置信区间
- **置信区间的含义**：
  - 95%置信区间表示：如果重复抽样100次，约有95个区间包含真实参数
- **均值的置信区间**：
  ```python
  from scipy import stats
  import numpy as np
  
  data = np.array([1, 2, 3, 4, 5])
  mean = np.mean(data)
  std_err = stats.sem(data)  # 标准误
  
  ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=std_err)
  print(f"95%置信区间: [{ci[0]:.2f}, {ci[1]:.2f}]")
  ```

## 幻灯片11: 相关性分析
- **Pearson相关系数**：线性相关
- **Spearman相关系数**：单调相关
- **Kendall相关系数**：等级相关
- **相关系数的解释**：
  - |r| > 0.7：强相关
  - 0.3 < |r| ≤ 0.7：中等相关
  - |r| ≤ 0.3：弱相关

## 幻灯片12: 回归分析基础
- **简单线性回归**：
  - y = β₀ + β₁x + ε
  - 最小二乘法估计
- **多元线性回归**：
  - y = β₀ + β₁x₁ + β₂x₂ + ... + βₖxₖ + ε
- **模型评估指标**：
  - R² (决定系数)
  - MSE (均方误差)
  - RMSE (均方根误差)

## 幻灯片13: Statsmodels vs Scikit-learn
- **Statsmodels优势**：
  - 详细的统计输出
  - 假设检验支持
  - 传统统计方法
- **Scikit-learn优势**：
  - 机器学习集成
  - 预测性能优化
  - 现代API设计

```python
# Statsmodels示例
import statsmodels.api as sm
X = sm.add_constant(X)  # 添加截距项
model = sm.OLS(y, X).fit()
print(model.summary())

# Scikit-learn示例
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X, y)
print(f"R²: {model.score(X, y):.4f}")
```

## 幻灯片14: 贝叶斯统计简介
- **贝叶斯定理**：P(A|B) = P(B|A)P(A)/P(B)
- **先验分布 vs 后验分布**
- **共轭先验**的优势
- **PyMC3/PyMC4**在贝叶斯分析中的应用

```python
import pymc3 as pm

with pm.Model() as model:
    # 定义先验
    mu = pm.Normal('mu', mu=0, sigma=10)
    sigma = pm.HalfNormal('sigma', sigma=1)
    
    # 定义似然
    likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, observed=data)
    
    # 采样
    trace = pm.sample(1000)
```

## 幻灯片15: 统计功效分析
- **统计功效(1-β)**：正确拒绝错误零假设的概率
- **影响功效的因素**：
  - 样本大小
  - 效应量
  - 显著性水平
- **功效分析的应用**：
  - 实验设计
  - 样本量计算

```python
from statsmodels.stats.power import TTestPower

# 计算所需样本量
analysis = TTestPower()
sample_size = analysis.solve_power(effect_size=0.5, power=0.8, alpha=0.05)
print(f"所需样本量: {sample_size:.0f}")
```

## 幻灯片16: 多重比较问题
- **多重比较问题**：增加第一类错误概率
- **校正方法**：
  - Bonferroni校正
  - Holm-Bonferroni校正
  - False Discovery Rate (FDR)
- **实际应用场景**：
  - A/B测试
  - 基因表达分析
  - 机器学习特征选择

## 幻灯片17: 实践项目
- **项目目标**：完整的统计分析流程
- **数据集**：医疗临床试验数据
- **任务要求**：
  - 描述性统计分析
  - 假设检验（比较治疗组和对照组）
  - 相关性分析
  - 回归建模
  - 生成统计报告

## 幻灯片18: 总结与下一步
- **关键要点回顾**：
  - 统计分析是数据科学的基础
  - 选择合适的统计方法很重要
  - Python提供了丰富的统计分析工具
- **下一章预告**：第7章 - 时间序列分析

## 幻灯片19: Q&A
- **问题与讨论**
- 联系方式：david.turing@example.com