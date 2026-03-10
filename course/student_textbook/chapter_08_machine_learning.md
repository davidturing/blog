# 第8章：机器学习入门

## 8.1 机器学习基础概念

### 8.1.1 什么是机器学习？

机器学习（Machine Learning）是人工智能的一个重要分支，它让计算机系统能够从数据中自动学习模式和规律，而无需显式编程。在数据分析领域，机器学习为我们提供了强大的预测和分类能力。

**核心思想**：通过算法从历史数据中学习，然后对新数据进行预测或决策。

### 8.1.2 机器学习的类型

#### 监督学习（Supervised Learning）
- **定义**：使用带有标签的训练数据来学习输入到输出的映射关系
- **常见任务**：
  - 分类（Classification）：预测离散类别标签
  - 回归（Regression）：预测连续数值

#### 无监督学习（Unsupervised Learning）
- **定义**：从未标记的数据中发现隐藏的模式或结构
- **常见任务**：
  - 聚类（Clustering）：将相似的数据点分组
  - 降维（Dimensionality Reduction）：减少特征数量同时保留重要信息

#### 强化学习（Reinforcement Learning）
- **定义**：通过试错和奖励机制来学习最优策略
- **应用场景**：游戏AI、机器人控制、推荐系统优化

## 8.2 Scikit-learn 入门

Scikit-learn 是Python中最流行的机器学习库，提供了简单高效的工具用于数据挖掘和数据分析。

### 8.2.1 安装和导入

```python
# 安装 scikit-learn
pip install scikit-learn

# 基本导入
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
```

### 8.2.2 Scikit-learn 的通用API

Scikit-learn 遵循一致的API设计：

```python
# 1. 创建模型实例
model = SomeEstimator()

# 2. 训练模型（拟合数据）
model.fit(X_train, y_train)

# 3. 进行预测
predictions = model.predict(X_test)

# 4. 评估模型性能
score = model.score(X_test, y_test)
```

## 8.3 分类任务实战

让我们通过一个具体的例子来学习分类任务。

### 8.3.1 数据准备

```python
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 加载鸢尾花数据集
iris = load_iris()
X = iris.data  # 特征
y = iris.target  # 标签

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 特征标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### 8.3.2 使用逻辑回归

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

# 创建和训练模型
lr_model = LogisticRegression(random_state=42)
lr_model.fit(X_train_scaled, y_train)

# 预测
y_pred = lr_model.predict(X_test_scaled)

# 评估
print("准确率:", accuracy_score(y_test, y_pred))
print("\n分类报告:")
print(classification_report(y_test, y_pred))
print("\n混淆矩阵:")
print(confusion_matrix(y_test, y_pred))
```

### 8.3.3 使用随机森林

```python
from sklearn.ensemble import RandomForestClassifier

# 创建和训练随机森林模型
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# 预测和评估
y_pred_rf = rf_model.predict(X_test_scaled)
print("随机森林准确率:", accuracy_score(y_test, y_pred_rf))

# 特征重要性
feature_importance = rf_model.feature_importances_
feature_names = iris.feature_names
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

print("\n特征重要性:")
print(importance_df)
```

## 8.4 回归任务实战

### 8.4.1 简单线性回归

```python
from sklearn.datasets import load_boston
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

# 注意：load_boston 在新版本中已被弃用，这里仅作示例
# 实际使用时可以使用其他回归数据集

# 创建线性回归模型
linear_reg = LinearRegression()
linear_reg.fit(X_train, y_train)

# 预测
y_pred_reg = linear_reg.predict(X_test)

# 评估回归性能
print("R² 分数:", r2_score(y_test, y_pred_reg))
print("均方误差:", mean_squared_error(y_test, y_pred_reg))
print("平均绝对误差:", mean_absolute_error(y_test, y_pred_reg))
```

## 8.5 模型评估与验证

### 8.5.1 交叉验证

```python
from sklearn.model_selection import cross_val_score

# 5折交叉验证
cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
print(f"交叉验证准确率: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
```

### 8.5.2 学习曲线

```python
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt

# 绘制学习曲线
train_sizes, train_scores, val_scores = learning_curve(
    rf_model, X_train_scaled, y_train, cv=5, n_jobs=-1
)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, np.mean(train_scores, axis=1), 'o-', label='Training score')
plt.plot(train_sizes, np.mean(val_scores, axis=1), 'o-', label='Validation score')
plt.xlabel('Training Set Size')
plt.ylabel('Accuracy Score')
plt.title('Learning Curve')
plt.legend()
plt.grid(True)
plt.show()
```

## 8.6 超参数调优

### 8.6.1 网格搜索

```python
from sklearn.model_selection import GridSearchCV

# 定义参数网格
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}

# 网格搜索
grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train_scaled, y_train)

print("最佳参数:", grid_search.best_params_)
print("最佳交叉验证分数:", grid_search.best_score_)
```

## 8.7 实际项目：客户流失预测

让我们应用所学知识解决一个实际问题：预测电信客户是否会流失。

### 8.7.1 数据加载和探索

```python
# 假设我们有一个客户流失数据集
# df = pd.read_csv('customer_churn.csv')

# 数据基本信息
print(df.info())
print(df.describe())

# 目标变量分布
print(df['churn'].value_counts())
```

### 8.7.2 特征工程

```python
# 处理分类变量
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
categorical_columns = ['gender', 'contract_type', 'payment_method']

for col in categorical_columns:
    df[col + '_encoded'] = le.fit_transform(df[col])

# 选择特征
feature_columns = ['tenure', 'monthly_charges', 'total_charges'] + \
                 [col + '_encoded' for col in categorical_columns]
X = df[feature_columns]
y = df['churn']
```

### 8.7.3 模型训练和评估

```python
# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 训练最佳模型
best_model = grid_search.best_estimator_
best_model.fit(X_train_scaled, y_train)

# 预测和评估
y_pred_churn = best_model.predict(X_test_scaled)
print("客户流失预测准确率:", accuracy_score(y_test, y_pred_churn))
```

## 8.8 本章小结

- **机器学习基础**：理解了监督学习、无监督学习和强化学习的区别
- **Scikit-learn 使用**：掌握了通用的API模式和基本操作流程
- **分类和回归**：通过实际例子学习了两种主要的监督学习任务
- **模型评估**：学会了使用交叉验证、学习曲线等方法评估模型性能
- **超参数调优**：掌握了网格搜索等调优技术
- **实际应用**：通过客户流失预测项目将理论知识应用到实践中

## 8.9 练习题

1. **基础练习**：使用葡萄酒数据集（wine dataset）训练一个分类模型，比较不同算法的性能。

2. **进阶练习**：在一个回归数据集上实现完整的机器学习流程，包括数据预处理、模型选择、超参数调优和结果解释。

3. **项目练习**：选择一个你感兴趣的数据集，设计并实现一个完整的机器学习解决方案，撰写项目报告。

## 8.10 扩展阅读

- **《Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow》** by Aurélien Géron
- **Scikit-learn 官方文档**: https://scikit-learn.org/stable/
- **Kaggle 机器学习竞赛**: https://www.kaggle.com/competitions

通过本章的学习，你应该已经掌握了机器学习的基本概念和实践技能。下一章我们将深入探讨高级数据可视化技术，让你的数据分析结果更加直观和有说服力。