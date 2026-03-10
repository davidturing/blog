# 第5章：探索性数据分析(EDA)

## 幻灯片1: 课程标题
- **第5章：探索性数据分析(EDA)**
- Python数据分析课程
- 讲师：David Turing

## 幻灯片2: 学习目标
- 理解EDA的核心概念和重要性
- 掌握单变量、双变量和多变量分析技术
- 学习使用现代可视化工具进行数据探索
- 掌握自动化EDA工具的使用
- 实践真实数据集的完整EDA流程

## 幻灯片3: 什么是探索性数据分析？
- **定义**：EDA是通过可视化和统计方法理解数据特征的过程
- **目标**：
  - 发现数据模式和关系
  - 识别异常值和异常模式
  - 验证假设和直觉
  - 为后续建模提供指导
- **与传统统计分析的区别**：更注重发现而非验证

## 幻灯片4: EDA的核心原则
- **保持开放心态**：不要预设立场
- **迭代过程**：从简单到复杂，逐步深入
- **可视化优先**：图形比数字更能揭示模式
- **质疑一切**：对每个发现都要验证
- **记录过程**：保持分析的可重现性

## 幻灯片5: 单变量分析
- **数值变量**：
  - 分布形状（偏度、峰度）
  - 集中趋势（均值、中位数、众数）
  - 离散程度（方差、标准差、IQR）
- **分类变量**：
  - 频数分布
  - 比例分析
  - 类别平衡性

## 幻灯片6: Pandas 3.0中的单变量分析工具
```python
# 数值变量分析
df['numeric_col'].describe()
df['numeric_col'].hist(bins=30)
df['numeric_col'].plot.box()

# 分类变量分析
df['categorical_col'].value_counts()
df['categorical_col'].value_counts(normalize=True).plot.bar()
```

## 幻灯片7: 双变量分析
- **数值 vs 数值**：
  - 散点图
  - 相关性分析
  - 回归线拟合
- **数值 vs 分类**：
  - 箱线图
  - 小提琴图
  - 分组统计
- **分类 vs 分类**：
  - 交叉表
  - 堆叠条形图
  - 卡方检验

## 幻灯片8: 多变量分析
- **相关矩阵热力图**
- **平行坐标图**
- **散点图矩阵（Pair Plot）**
- **主成分分析（PCA）可视化**
- **聚类分析结果可视化**

## 幻灯片9: 现代可视化库对比
| 库 | 优势 | 适用场景 |
|---|---|---|
| **Matplotlib** | 完全控制、稳定 | 基础图表、出版质量 |
| **Seaborn** | 统计友好、美观 | 快速EDA、统计图表 |
| **Plotly** | 交互性强、Web友好 | 仪表板、交互式探索 |
| **Altair** | 声明式语法、简洁 | 快速原型、复杂图表 |
| **Bokeh** | 大数据支持、流数据 | Web应用、实时数据 |

## 幻灯片10: Seaborn 2026新特性
- **自动配色方案**：基于数据特征智能选择
- **增强的统计功能**：
  ```python
  # 新增的统计图表
  sns.regplot_with_ci(x, y, ci_method='bootstrap')
  sns.distribution_plot(data, kind='kde', bw_adjust=0.5)
  ```
- **更好的分类数据支持**：
  - 自动处理高基数分类变量
  - 智能排序和分组

## 幻灯片11: Plotly Express实战
```python
import plotly.express as px

# 一键创建交互式图表
fig = px.scatter(df, x='feature1', y='feature2', 
                 color='category', size='value',
                 hover_data=['additional_info'])
fig.show()

# 3D可视化
fig_3d = px.scatter_3d(df, x='x', y='y', z='z', 
                       color='target')
```

## 幻灯片12: 自动化EDA工具
- **Pandas Profiling (now ydata-profiling)**：
  ```python
  from ydata_profiling import ProfileReport
  profile = ProfileReport(df, title="EDA Report")
  profile.to_file("eda_report.html")
  ```
  
- **Sweetviz**：
  ```python
  import sweetviz as sv
  report = sv.analyze(df)
  report.show_html("sweetviz_report.html")
  ```

## 幻灯片13: Polars在EDA中的优势
- **性能优势**：
  - 列式存储，内存效率高
  - 多线程并行处理
  - 懒惰计算优化
  
- **EDA专用函数**：
  ```python
  # Polars的描述性统计
  df.describe()
  
  # 高效的分组聚合
  df.groupby('category').agg([
      pl.col('value').mean().alias('mean_value'),
      pl.col('value').std().alias('std_value')
  ])
  ```

## 幻灯片14: 时间序列EDA
- **时间模式分析**：
  - 趋势检测
  - 季节性分析
  - 周期性模式
- **时间序列可视化**：
  - 折线图
  - 季节性分解图
  - 自相关图
- **Pandas 3.0时间序列新特性**：
  ```python
  df.resample('D').agg({'value': ['mean', 'std']})
  ```

## 幻灯片15: 地理空间EDA
- **地理数据可视化**：
  - 热力图
  - 点密度图
  - 区域填充图
- **常用库**：
  - GeoPandas + Matplotlib
  - Folium（交互式地图）
  - Plotly Geo

## 幻灯片16: AI辅助EDA
- **自动洞察发现**：
  - 模式识别
  - 异常检测
  - 关系建议
- **智能可视化推荐**：
  ```python
  # 使用AI工具
  from aieda import AutoEDA
  insights = AutoEDA(df).get_insights()
  recommended_viz = AutoEDA(df).recommend_visualizations()
  ```

## 幻灯片17: 完整EDA工作流程
1. **数据概览**：基本统计信息
2. **单变量分析**：理解每个变量
3. **双变量分析**：探索变量间关系
4. **多变量分析**：发现复杂模式
5. **特殊数据类型处理**：时间、地理、文本
6. **生成报告**：总结发现和建议

## 幻灯片18: 实践项目
- **项目目标**：对电商用户行为数据进行全面EDA
- **数据集特点**：
  - 包含用户基本信息
  - 用户行为日志
  - 购买记录
  - 时间戳信息
- **任务要求**：
  - 生成完整的EDA报告
  - 发现至少3个有趣的业务洞察
  - 提出后续分析建议

## 幻灯片19: 总结与下一步
- **关键要点回顾**：
  - EDA是数据分析的基础步骤
  - 现代工具链大大提升了EDA效率
  - 自动化工具可以快速获得初步洞察
- **下一章预告**：第6章 - 统计分析基础

## 幻灯片20: Q&A
- **问题与讨论**
- 联系方式：david.turing@example.com