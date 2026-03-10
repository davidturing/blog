# 第8章：机器学习入门

## 课程目标
- 掌握机器学习基本概念和流程
- 学会使用Scikit-learn进行模型训练和评估
- 理解监督学习和无监督学习的区别
- 能够构建完整的机器学习管道

## 教学重点与难点

### 重点内容
1. **机器学习基础概念**
   - 监督学习 vs 无监督学习
   - 分类 vs 回归
   - 训练集、验证集、测试集划分
   - 特征工程基础

2. **Scikit-learn核心组件**
   - Estimator接口统一性
   - 数据预处理模块（preprocessing）
   - 模型选择与评估（model_selection）
   - 常用算法实现

3. **完整机器学习工作流**
   - 数据准备 → 特征工程 → 模型训练 → 模型评估 → 预测部署

### 难点解析
- **过拟合与欠拟合**：通过交叉验证和正则化解决
- **特征缩放的重要性**：不同算法对特征尺度的敏感性
- **模型评估指标选择**：准确率、精确率、召回率、F1分数的适用场景

## 详细教学内容

### 8.1 机器学习概述 (20分钟)
**核心概念讲解**：
- 什么是机器学习？让计算机从数据中学习模式
- 三大类型：监督学习、无监督学习、强化学习（简要介绍）
- 典型应用场景：垃圾邮件分类、房价预测、客户分群

**代码演示**：
```python
# 展示机器学习的基本流程
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 2. 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. 训练模型
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 4. 评估模型
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"准确率: {accuracy:.2f}")
```

### 8.2 Scikit-learn生态系统 (30分钟)
**核心设计理念**：
- 统一的Estimator接口：`fit()`, `predict()`, `transform()`
- 流水线（Pipeline）设计模式
- 参数调优的一致性

**主要模块介绍**：
- `sklearn.preprocessing`：标准化、编码、缺失值处理
- `sklearn.feature_selection`：特征选择方法
- `sklearn.model_selection`：交叉验证、网格搜索
- `sklearn.metrics`：评估指标计算

**实践练习**：
```python
# 构建完整的预处理+模型流水线
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression

# 创建流水线
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])

# 使用流水线
pipeline.fit(X_train, y_train)
score = pipeline.score(X_test, y_test)
```

### 8.3 监督学习算法详解 (45分钟)
**分类算法**：
- 逻辑回归（Logistic Regression）
- 决策树（Decision Tree）
- 随机森林（Random Forest）
- 支持向量机（SVM）

**回归算法**：
- 线性回归（Linear Regression）
- 岭回归（Ridge Regression）
- Lasso回归
- 随机森林回归

**算法选择指南**：
- 小数据集：逻辑回归、SVM
- 大数据集：随机森林、梯度提升
- 需要可解释性：决策树、线性模型
- 高维数据：正则化方法

### 8.4 模型评估与验证 (30分钟)
**评估指标详解**：
- 分类：混淆矩阵、ROC曲线、AUC
- 回归：MSE、MAE、R²
- 聚类：轮廓系数、Calinski-Harabasz指数

**交叉验证技术**：
- K折交叉验证
- 分层K折交叉验证
- 时间序列交叉验证

**代码示例**：
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report

# 交叉验证
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"CV平均准确率: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# 详细分类报告
print(classification_report(y_test, y_pred))
```

### 8.5 实战项目：泰坦尼克号生存预测 (60分钟)
**项目目标**：基于乘客信息预测生存概率

**数据集特点**：
- 混合数据类型（数值、类别、文本）
- 缺失值处理
- 特征工程挑战

**完整解决方案**：
1. 数据探索与可视化
2. 缺失值填充策略
3. 特征编码与转换
4. 模型训练与调优
5. 结果解释与业务洞察

## 教学建议

### 课堂组织
- **理论讲解**：45分钟（概念+原理）
- **代码演示**：30分钟（逐步实现）
- **学生实践**：45分钟（动手练习）
- **答疑讨论**：15分钟

### 教学工具
- Jupyter Notebook实时演示
- Google Colab在线环境（避免本地配置问题）
- Kaggle数据集（真实世界数据）

### 常见问题解答
**Q: 如何选择合适的机器学习算法？**
A: 从简单模型开始（如逻辑回归），逐步尝试复杂模型。考虑数据规模、特征类型、业务需求等因素。

**Q: 为什么需要特征缩放？**
A: 不同特征的量纲差异会影响某些算法（如SVM、KNN、神经网络）的性能，标准化可以消除这种影响。

**Q: 过拟合如何检测和解决？**
A: 通过训练集和验证集性能差异检测；解决方案包括增加数据、正则化、简化模型、早停等。

## 课后作业与扩展

### 基础练习
1. 使用鸢尾花数据集，比较不同分类算法的性能
2. 实现一个完整的房价预测项目
3. 分析不同特征缩放方法对模型性能的影响

### 进阶挑战
1. 参与Kaggle入门竞赛（如Titanic、House Prices）
2. 实现自定义的特征工程函数
3. 探索集成学习方法（Bagging、Boosting）

### 扩展阅读
- 《Hands-On Machine Learning with Scikit-Learn and TensorFlow》
- Scikit-learn官方文档和用户指南
- Kaggle Learn平台的机器学习课程

## 本章小结
本章为学生建立了机器学习的基础框架，重点掌握Scikit-learn的使用方法和完整的机器学习工作流。通过理论与实践相结合的方式，培养学生解决实际问题的能力，为后续章节的深入学习奠定坚实基础。