# 第三章：数据可视化基础

## 教学目标
- 掌握 Matplotlib 和 Seaborn 的基本用法
- 理解不同图表类型的适用场景
- 学会创建专业的数据可视化作品
- 了解 Plotly 等交互式可视化工具

## 教学重点
- 图表类型选择原则
- 颜色搭配和视觉设计
- 多子图布局和组合
- 交互式可视化入门

## 教学难点
- 高维数据的可视化策略
- 动态数据的实时可视化
- 可视化中的认知偏差避免

## 教学方法
- 演示驱动：现场编码展示
- 案例分析：优秀可视化作品解析
- 实践练习：学生动手创建图表
- 项目作业：完整可视化项目

## 代码示例
```python
# 基础散点图
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建示例数据
import numpy as np
x = np.random.randn(100)
y = 2 * x + np.random.randn(100)

# 基础散点图
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.6)
plt.xlabel('X变量')
plt.ylabel('Y变量')
plt.title('基础散点图示例')
plt.show()
```

## 2026年新技术融入
- **AI辅助可视化**：使用 LLM 自动生成可视化建议
- **自动化图表优化**：智能颜色搭配和布局调整
- **WebGL加速**：大规模数据的高性能渲染
- **AR/VR数据可视化**：沉浸式数据分析体验

## 课堂练习
1. 使用给定数据集创建至少3种不同类型的图表
2. 对比 Matplotlib 和 Seaborn 的语法差异
3. 尝试使用 Plotly 创建交互式图表

## 课后作业
- 完成一个完整的数据可视化项目
- 分析一个真实世界的数据集并创建信息图
- 撰写可视化设计报告，解释选择理由