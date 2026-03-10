# 第一章：Python数据分析导论

## 教学目标
- 了解数据分析的基本概念和应用场景
- 掌握Python数据分析生态系统的组成
- 熟悉Jupyter Notebook开发环境
- 能够运行第一个数据分析程序

## 教学重点与难点
**重点：**
- Python数据分析工具链介绍
- Jupyter Notebook基本操作
- 数据分析工作流程

**难点：**
- 环境配置问题排查
- 理解数据分析的迭代特性

## 教学方法建议
### 1. 课堂演示（30分钟）
- **开场案例**：展示一个简单的数据分析案例（如学生成绩分析）
- **工具演示**：现场演示Jupyter Notebook的使用
- **代码实战**：带领学生完成"Hello World"数据分析

### 2. 学生实践（45分钟）
- **环境搭建**：指导学生安装Anaconda
- **第一个程序**：编写简单的数据加载和可视化代码
- **常见问题解答**：收集并解决学生遇到的问题

### 3. 课后作业
- 完成环境配置检查清单
- 编写一个简单的数据分析脚本

## 详细教学内容

### 1.1 什么是数据分析？
**定义**：数据分析是从原始数据中提取有用信息和形成结论的过程。

**核心价值**：
- 发现模式和趋势
- 支持决策制定  
- 预测未来行为
- 优化业务流程

**应用领域**：
- 金融风控
- 电商推荐
- 医疗诊断
- 社交媒体分析
- 智能制造

### 1.2 Python数据分析生态系统

#### 核心库介绍
| 库名称 | 功能 | 重要性 |
|--------|------|--------|
| NumPy | 数值计算基础 | ⭐⭐⭐⭐⭐ |
| Pandas | 数据处理和分析 | ⭐⭐⭐⭐⭐ |
| Matplotlib | 基础可视化 | ⭐⭐⭐⭐ |
| Seaborn | 统计可视化 | ⭐⭐⭐⭐ |
| Scikit-learn | 机器学习 | ⭐⭐⭐⭐ |

#### 2026年新技术趋势
- **Polars**: 新一代高性能DataFrame库
- **Plotly Express**: 交互式可视化
- **Streamlit**: 快速构建数据应用
- **DuckDB**: 嵌入式分析数据库

### 1.3 Jupyter Notebook使用指南

#### 基本操作
- Cell类型：Code vs Markdown
- 快捷键：Shift+Enter, Ctrl+Enter
- Magic命令：%timeit, %matplotlib inline

#### 最佳实践
- 代码组织：模块化、注释清晰
- 版本控制：定期保存和备份
- 协作分享：导出为HTML/PDF

### 1.4 第一个数据分析程序

```python
# 导入必要的库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 创建示例数据
data = {
    'student_id': range(1, 101),
    'math_score': np.random.normal(75, 15, 100),
    'english_score': np.random.normal(80, 12, 100),
    'class': np.random.choice(['A', 'B', 'C'], 100)
}

df = pd.DataFrame(data)

# 基本统计分析
print("数据基本信息：")
print(df.describe())

# 简单可视化
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.hist(df['math_score'], bins=20, alpha=0.7)
plt.title('数学成绩分布')
plt.xlabel('分数')
plt.ylabel('人数')

plt.subplot(1, 2, 2)
sns.boxplot(data=df, x='class', y='math_score')
plt.title('各班级数学成绩对比')

plt.tight_layout()
plt.show()
```

## 教学资源
### 推荐阅读
- 《Python for Data Analysis》 - Wes McKinney
- 《利用Python进行数据分析》 - 中文版
- 官方文档：pandas.pydata.org

### 在线资源
- Kaggle Learn: Python and Pandas courses
- Real Python tutorials
- DataCamp interactive lessons

## 常见问题与解决方案
### Q1: 安装包时出现依赖冲突
**解决方案**：使用conda而不是pip，或者创建独立的虚拟环境

### Q2: 中文显示乱码
**解决方案**：设置matplotlib字体
```python
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
```

### Q3: Jupyter Notebook无法启动
**解决方案**：检查Python版本兼容性，重新安装jupyter

## 扩展思考题
1. 为什么Python成为数据分析的主流语言？
2. 如何选择合适的数据分析工具？
3. 数据分析与数据科学的区别是什么？

## 下节课预告
第二章将深入学习Pandas的核心数据结构：Series和DataFrame，这是整个数据分析的基础。