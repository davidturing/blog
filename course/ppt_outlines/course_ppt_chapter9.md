# 第9章：高级数据可视化

## 幻灯片1: 课程标题
- **第9章：高级数据可视化**
- Python数据分析课程
- 讲师：David Turing

## 幻灯片2: 学习目标
- 掌握高级可视化库的使用（Plotly, Bokeh, Altair）
- 学习交互式可视化技术
- 理解地理空间数据可视化方法
- 掌握大规模数据集的可视化策略
- 实践多维度数据的可视化表达

## 幻灯片3: 可视化库生态概览
- **Matplotlib**：基础绘图库
- **Seaborn**：统计可视化
- **Plotly**：交互式可视化（2026年最新特性）
- **Bokeh**：Web交互式可视化
- **Altair**：声明式可视化
- **PyGWalker**：AI驱动的可视化探索工具

## 幻灯片4: Plotly 6.0新特性
- **增强的3D可视化**：
  - 体积渲染
  - 等值面绘制
  - 流线图
- **性能优化**：
  - WebGL加速
  - 大数据集处理能力提升50%
- **AI集成**：
  - 自动图表类型推荐
  - 智能配色方案

## 幻灯片5: 交互式可视化实战
```python
import plotly.express as px
import plotly.graph_objects as go

# 创建交互式散点图
fig = px.scatter(df, x='feature1', y='feature2', 
                 color='category', size='value',
                 hover_data=['name', 'description'])

# 添加交互控件
fig.update_layout(
    updatemenus=[
        dict(
            buttons=list([
                dict(args=[{"visible": [True, False]}], label="Show All"),
                dict(args=[{"visible": [False, True]}], label="Show Filtered")
            ])
        )
    ]
)
fig.show()
```

## 幻灯片6: 地理空间数据可视化
- **GeoPandas + Plotly集成**：
  ```python
  import geopandas as gpd
  import plotly.express as px
  
  # 读取地理数据
  gdf = gpd.read_file('china_provinces.shp')
  
  # 创建 choropleth 地图
  fig = px.choropleth(gdf, geojson=gdf.geometry, 
                      locations=gdf.index, 
                      color='population',
                      projection="mercator")
  fig.update_geos(fitbounds="locations")
  fig.show()
  ```

## 幻灯片7: 大规模数据可视化策略
- **数据采样**：随机采样、分层采样
- **聚合可视化**：热力图、六边形binning
- **WebGL加速**：使用Datashader库
- **流式可视化**：实时数据更新
- **分页加载**：按需加载数据块

## 幻灯片8: Datashader高性能可视化
```python
import datashader as ds
import datashader.transfer_functions as tf

# 创建画布
cvs = ds.Canvas(plot_width=800, plot_height=600)

# 聚合大数据点
agg = cvs.points(df, 'x', 'y')

# 渲染图像
img = tf.shade(agg, cmap='viridis')
tf.set_background(img, 'black').show()
```

## 幻灯片9: 多维度数据可视化
- **平行坐标图**：高维数据模式识别
- **雷达图**：多指标比较
- **桑基图**：流程和转换可视化
- **树状图**：层次结构展示
- **网络图**：关系和连接可视化

## 幻灯片10: AI辅助可视化设计
- **自动图表选择**：
  - 基于数据类型和分析目标
  - 考虑受众背景和偏好
- **智能配色**：
  - 色盲友好调色板
  - 品牌一致性
- **布局优化**：
  - 自动标签放置
  - 避免重叠

## 幻灯片11: PyGWalker - AI可视化助手
```python
# 安装：pip install pygwalker
import pygwalker as pyg

# 创建交互式可视化界面
gwalker = pyg.walk(df, env='Jupyter')

# 支持拖拽式操作
# 自动生成洞察报告
# 导出多种格式
```

## 幻灯片12: 可视化最佳实践
- **清晰性优先**：避免过度装饰
- **一致性**：统一的颜色、字体、样式
- **可访问性**：考虑色盲用户
- **上下文**：提供足够的背景信息
- **故事性**：引导观众理解数据

## 幻灯片13: 性能优化技巧
- **预计算聚合**：减少实时计算
- **懒加载**：按需加载详细数据
- **缓存策略**：存储常用可视化结果
- **CDN分发**：加速静态资源加载
- **响应式设计**：适配不同设备

## 幻灯片14: 可视化部署与分享
- **Jupyter Notebook**：交互式文档
- **Dash/Streamlit**：Web应用
- **静态HTML**：离线分享
- **PDF/PNG导出**：打印和演示
- **嵌入式组件**：集成到现有系统

## 幻灯片15: Dash vs Streamlit对比
| 特性 | Dash | Streamlit |
|------|------|-----------|
| 学习曲线 | 较陡 | 平缓 |
| 性能 | 高 | 中等 |
| 自定义程度 | 高 | 中等 |
| 部署复杂度 | 中等 | 简单 |
| 社区支持 | 成熟 | 快速增长 |

## 幻灯片16: 实践项目
- **项目目标**：创建交互式数据仪表板
- **数据集**：全球气候数据
- **要求**：
  - 支持多维度筛选
  - 包含地理空间可视化
  - 实现响应式设计
  - 集成AI洞察功能

## 幻灯片17: 总结与下一步
- **关键要点回顾**：
  - 高级可视化工具提供强大功能
  - 交互性和性能是关键考量
  - AI正在改变可视化设计方式
- **下一章预告**：第10章 - 大数据处理技术

## 幻灯片18: Q&A
- **问题与讨论**
- 联系方式：david.turing@example.com