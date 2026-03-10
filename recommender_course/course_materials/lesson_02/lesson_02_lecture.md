# 推荐系统课程 - Lesson 02：矩阵分解技术

## 课程目标
- 理解矩阵分解的基本原理
- 掌握SVD（奇异值分解）在推荐系统中的应用
- 学习ALS（交替最小二乘）算法
- 处理隐式反馈数据

## 核心概念

### 1. 矩阵分解基础
矩阵分解是将用户-物品评分矩阵R分解为两个低维矩阵的乘积：
R ≈ U × V^T

其中：
- U: 用户潜在因子矩阵 (m × k)
- V: 物品潜在因子矩阵 (n × k)  
- k: 潜在因子维度

### 2. SVD（奇异值分解）
- 完整SVD: R = UΣV^T
- 截断SVD: 保留前k个最大的奇异值
- 适用于显式反馈数据

### 3. ALS（交替最小二乘）
- 固定U，优化V
- 固定V，优化U  
- 交替进行直到收敛
- 适合大规模稀疏矩阵

### 4. 隐式反馈处理
- 用户行为数据（点击、浏览、购买等）
- 置信度权重设计
- 负采样策略

## 实践要点
- 潜在因子维度选择
- 正则化参数调优
- 评估指标设计
- 冷启动问题处理

## 参考资料
- Koren, Y., Bell, R., & Volinsky, C. (2009). Matrix factorization techniques for recommender systems.
- Hu, Y., Koren, Y., & Volinsky, C. (2008). Collaborative filtering for implicit feedback datasets.