# 第一章：Python 数据分析导论

## 课程目标

本章将帮助学生建立对 Python 数据分析领域的整体认知，了解现代数据科学的工作流程和工具生态系统。

## 1.1 什么是数据分析？

数据分析是通过统计学、机器学习和可视化技术从数据中提取有价值信息的过程。在 2026 年，数据分析已经成为几乎所有行业的核心竞争力。

## 1.2 Python 数据分析生态系统

Python 拥有最丰富的数据分析库生态系统：

* Pandas：数据处理和分析的核心库
* NumPy：数值计算的基础
* Matplotlib/Seaborn：数据可视化
* Scikit-learn：机器学习
* Polars：高性能数据处理（2026 年新趋势）
* Dask：大规模并行计算

## 1.3 现代数据分析工作流程

典型的数据分析项目包含以下步骤：

1. 问题定义
2. 数据收集
3. 数据清洗
4. 探索性数据分析（EDA）
5. 模型构建
6. 结果解释
7. 部署和监控

## 1.4 开发环境设置

推荐使用以下开发环境：

* JupyterLab：交互式开发
* VS Code：代码编辑
* GitHub Codespaces：云端开发环境
* Docker：环境隔离

## 1.5 实践练习

安装必要的库并运行第一个数据分析脚本：

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 创建示例数据
data = {'name': ['Alice', 'Bob', 'Charlie'], 
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]}
df = pd.DataFrame(data)

# 基本数据分析
print(df.describe())
df.plot(x='age', y='salary', kind='scatter')
plt.show()
```

## 教学建议

* 强调实践的重要性，每节课都要有动手环节
* 使用真实世界的数据集，如 Kaggle 数据集
* 鼓励学生参与开源项目
* 介绍 AI 辅助编程工具的使用
