# Lesson 01: 推荐系统基础 — 协同过滤 (UserCF & ItemCF)

## 课程目标
- 理解协同过滤的基本原理
- 掌握User-Based和Item-Based协同过滤算法
- 能够实现和评估协同过滤推荐系统
- 了解协同过滤的优缺点和适用场景

## 1. 协同过滤概述

协同过滤（Collaborative Filtering, CF）是推荐系统中最经典和广泛使用的算法之一。其核心思想是：**相似的用户会有相似的偏好，相似的物品会被相似的用户喜欢**。

### 1.1 基本假设
- 用户行为数据反映了用户的偏好
- 相似的用户对物品的评价也相似
- 相似的物品会获得相似的用户评价

### 1.2 数据表示
推荐系统通常用用户-物品交互矩阵表示：
- 行：用户（Users）
- 列：物品（Items）  
- 元素：评分/交互强度（Ratings）

## 2. User-Based Collaborative Filtering (UserCF)

### 2.1 算法原理
1. **计算用户相似度**：基于用户的历史行为计算用户之间的相似度
2. **寻找相似用户**：为目标用户找到最相似的K个邻居用户
3. **预测评分**：基于邻居用户的评分进行加权平均预测

### 2.2 相似度计算方法
- **余弦相似度（Cosine Similarity）**：
  ```
  sim(u,v) = (Σ r_ui * r_vi) / (√Σ r_ui² * √Σ r_vi²)
  ```
- **皮尔逊相关系数（Pearson Correlation）**：
  ```
  sim(u,v) = Σ(r_ui - r̄_u)(r_vi - r̄_v) / (√Σ(r_ui - r̄_u)² * √Σ(r_vi - r̄_v)²)
  ```

### 2.3 预测评分公式
```
r̂_ui = r̄_u + (Σ sim(u,v) * (r_vi - r̄_v)) / Σ |sim(u,v)|
```

## 3. Item-Based Collaborative Filtering (ItemCF)

### 3.1 算法原理
1. **计算物品相似度**：基于物品被用户评价的情况计算物品之间的相似度
2. **寻找相似物品**：为目标物品找到最相似的K个邻居物品
3. **预测评分**：基于用户对相似物品的评分进行加权平均预测

### 3.2 物品相似度计算
- **余弦相似度**：
  ```
  sim(i,j) = (Σ r_ui * r_uj) / (√Σ r_ui² * √Σ r_uj²)
  ```

### 3.3 预测评分公式
```
r̂_ui = (Σ sim(i,j) * r_uj) / Σ |sim(i,j)|
```

## 4. UserCF vs ItemCF 对比

| 特性 | UserCF | ItemCF |
|------|--------|--------|
| **稳定性** | 用户兴趣变化快，相似度不稳定 | 物品属性相对稳定 |
| **可解释性** | "和你相似的用户也喜欢" | "喜欢这个物品的用户也喜欢" |
| **计算复杂度** | 在线计算，实时性要求高 | 可离线预计算 |
| **适用场景** | 社交性强的场景 | 电商、内容推荐 |

## 5. 实现要点

### 5.1 数据预处理
- 处理稀疏性问题
- 标准化评分（减去用户均值）
- 处理冷启动问题

### 5.2 相似度优化
- 使用Jaccard相似度处理隐式反馈
- 加入时间衰减因子
- 考虑置信度权重

### 5.3 评估指标
- **MAE (Mean Absolute Error)**：平均绝对误差
- **RMSE (Root Mean Square Error)**：均方根误差
- **Precision@K**：前K个推荐的准确率
- **Recall@K**：前K个推荐的召回率

## 6. 实践建议

1. **从小规模数据开始**：先在MovieLens-100K上实验
2. **对比不同相似度方法**：余弦 vs 皮尔逊
3. **调参优化**：邻居数量K的选择
4. **考虑业务场景**：选择UserCF还是ItemCF

## 参考资料
- [GroupLens Research Datasets](https://grouplens.org/datasets/)
- "Recommender Systems: The Textbook" by Charu C. Aggarwal
- "Programming Collective Intelligence" by Toby Segaran

---
*讲师：推荐系统老师·David*
*日期：2026年3月1日*