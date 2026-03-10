# 第8章：机器学习入门

## 幻灯片1: 课程标题
- **第8章：机器学习入门**
- Python数据分析课程
- 讲师：David Turing

## 幻灯片2: 学习目标
- 理解机器学习的基本概念和分类
- 掌握监督学习与无监督学习的区别
- 学习常用机器学习算法的原理
- 实践使用scikit-learn构建ML模型
- 了解模型评估和验证方法

## 幻灯片3: 什么是机器学习？
- **定义**：让计算机系统从数据中自动学习模式和规律
- **核心思想**：通过算法从经验（数据）中改进性能
- **与传统编程的区别**：
  - 传统编程：规则 + 数据 → 答案
  - 机器学习：数据 + 答案 → 规则

## 幻灯片4: 机器学习分类
- **监督学习**（Supervised Learning）：
  - 分类（Classification）
  - 回归（Regression）
  
- **无监督学习**（Unsupervised Learning）：
  - 聚类（Clustering）
  - 降维（Dimensionality Reduction）
  
- **强化学习**（Reinforcement Learning）

## 幻灯片5: 监督学习基础
- **训练数据**：包含输入特征和对应标签
- **目标**：学习从输入到输出的映射函数
- **常见算法**：
  - 线性回归、逻辑回归
  - 决策树、随机森林
  - 支持向量机（SVM）
  - 神经网络

## 幻灯片6: 无监督学习基础
- **训练数据**：只有输入特征，没有标签
- **目标**：发现数据中的隐藏结构或模式
- **常见算法**：
  - K-means聚类
  - 层次聚类
  - 主成分分析（PCA）
  - t-SNE

## 幻灯片7: scikit-learn简介
- **Python ML库的事实标准**
- **统一的API设计**：
  ```python
  from sklearn.model_selection import train_test_split
  from sklearn.ensemble import RandomForestClassifier
  
  # 数据分割
  X_train, X_test, y_train, y_test = train_test_split(X, y)
  
  # 模型训练
  model = RandomForestClassifier()
  model.fit(X_train, y_train)
  
  # 预测
  predictions = model.predict(X_test)
  ```

## 幻灯片8: 特征工程
- **特征选择**：选择最相关的特征
- **特征提取**：从原始数据创建新特征
- **特征缩放**：标准化、归一化
- **编码分类变量**：
  - One-hot编码
  - Label编码
  - Target编码

## 幻灯片9: 模型评估指标
- **分类问题**：
  - 准确率（Accuracy）
  - 精确率（Precision）、召回率（Recall）
  - F1分数
  - ROC-AUC
  
- **回归问题**：
  - 均方误差（MSE）
  - 平均绝对误差（MAE）
  - R²分数

## 幻灯片10: 交叉验证
- **目的**：更可靠地评估模型性能
- **K折交叉验证**：
  ```python
  from sklearn.model_selection import cross_val_score
  
  scores = cross_val_score(model, X, y, cv=5)
  print(f"平均准确率: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
  ```
  
- **时间序列交叉验证**（TimeSeriesSplit）

## 幻灯片11: 超参数调优
- **网格搜索**（Grid Search）：
  ```python
  from sklearn.model_selection import GridSearchCV
  
  param_grid = {'n_estimators': [100, 200], 'max_depth': [3, 5, 7]}
  grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
  grid_search.fit(X_train, y_train)
  ```
  
- **随机搜索**（Random Search）
- **贝叶斯优化**

## 幻灯片12: 过拟合与欠拟合
- **过拟合**：模型在训练集上表现很好，但在测试集上表现差
- **欠拟合**：模型在训练集和测试集上都表现不佳
- **解决方案**：
  - 正则化（L1/L2）
  - 早停（Early stopping）
  - Dropout（神经网络）
  - 增加训练数据

## 幻灯片13: 集成学习
- **Bagging**：并行训练多个模型，取平均/投票
  - 随机森林（Random Forest）
  
- **Boosting**：串行训练，每个模型修正前一个的错误
  - AdaBoost
  - Gradient Boosting
  - XGBoost, LightGBM

## 幻灯片14: 2026年ML工具生态
- **传统工具**：scikit-learn, TensorFlow, PyTorch
- **新兴工具**：
  - **AutoML工具**：H2O.ai, Auto-sklearn
  - **MLflow**：实验跟踪和模型管理
  - **DVC**：数据版本控制
  - **Weights & Biases**：实验可视化

## 幻灯片15: 实战项目 - 房价预测
- **项目目标**：基于房屋特征预测价格
- **数据集**：Boston Housing Dataset
- **任务流程**：
  1. 数据探索和预处理
  2. 特征工程
  3. 模型选择和训练
  4. 超参数调优
  5. 模型评估和部署

## 幻灯片16: 实战项目 - 客户分群
- **项目目标**：基于客户行为进行分群
- **数据集**：电商客户数据
- **任务流程**：
  1. 数据清洗和特征提取
  2. 选择合适的聚类算法
  3. 确定最优聚类数量
  4. 分析和解释聚类结果
  5. 业务应用建议

## 幻灯片17: 总结与下一步
- **关键要点回顾**：
  - 机器学习是数据分析的重要组成部分
  - 选择合适的算法和评估方法至关重要
  - 特征工程往往比算法选择更重要
  
- **下一章预告**：第9章 - 高级数据可视化

## 幻灯片18: Q&A
- **问题与讨论**
- 联系方式：david.turing@example.com