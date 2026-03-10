# 第9章：高级数据可视化

## 课程目标
- 掌握交互式可视化技术
- 学习地理空间数据可视化
- 理解3D可视化和动画技术
- 掌握仪表板设计原则

## 9.1 交互式可视化基础

### Plotly高级特性
Plotly是一个强大的交互式可视化库，支持丰富的交互功能：

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 创建交互式散点图
fig = px.scatter(df, x='feature1', y='feature2', 
                 color='category', size='value',
                 hover_data=['name', 'description'])

# 添加交互控件
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            buttons=[
                dict(label="Play", method="animate", args=[None])
            ]
        )
    ]
)
fig.show()
```

### Dash仪表板框架
Dash是基于Plotly的Web应用框架，用于创建交互式仪表板：

```python
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': i, 'value': i} for i in df['category'].unique()],
        value=df['category'].unique()[0]
    ),
    dcc.Graph(id='interactive-graph')
])

@app.callback(
    Output('interactive-graph', 'figure'),
    Input('category-dropdown', 'value')
)
def update_graph(selected_category):
    filtered_df = df[df['category'] == selected_category]
    fig = px.scatter(filtered_df, x='x', y='y')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
```

## 9.2 地理空间数据可视化

### GeoPandas与地图可视化
GeoPandas扩展了Pandas的功能，专门处理地理空间数据：

```python
import geopandas as gpd
import matplotlib.pyplot as plt

# 读取地理数据
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# 创建 choropleth 地图
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world.plot(column='gdp_md_est', ax=ax, legend=True,
           legend_kwds={'label': "GDP by Country"})
plt.title('全球GDP分布')
plt.show()
```

### Folium交互式地图
Folium创建基于Leaflet.js的交互式地图：

```python
import folium
from folium import plugins

# 创建地图
m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)

# 添加标记
folium.Marker([39.9042, 116.4074], popup='北京').add_to(m)

# 添加热力图
heat_data = [[row['lat'], row['lon']] for index, row in df.iterrows()]
plugins.HeatMap(heat_data).add_to(m)

m.save('map.html')
```

## 9.3 3D可视化与动画

### Plotly 3D图表
创建三维散点图、曲面图和体积图：

```python
import plotly.graph_objects as go
import numpy as np

# 3D散点图
fig = go.Figure(data=[go.Scatter3d(
    x=x_data, y=y_data, z=z_data,
    mode='markers',
    marker=dict(
        size=12,
        color=z_data,
        colorscale='Viridis',
        showscale=True
    )
)])

fig.update_layout(title='3D散点图')
fig.show()
```

### Matplotlib 3D动画
使用Matplotlib创建3D动画：

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def animate(frame):
    ax.clear()
    # 更新数据
    ax.scatter(x[frame], y[frame], z[frame])
    ax.set_title(f'Frame {frame}')

ani = animation.FuncAnimation(fig, animate, frames=100, interval=50)
plt.show()
```

## 9.4 仪表板设计最佳实践

### 布局原则
- **KISS原则**：保持简单直观
- **一致性**：统一的颜色方案和字体
- **响应式设计**：适配不同屏幕尺寸
- **性能优化**：避免过度复杂的可视化

### 颜色理论应用
- 使用ColorBrewer调色板
- 考虑色盲友好性
- 限制颜色数量（通常3-5种）
- 使用语义化颜色（红色表示警告，绿色表示成功）

### 用户体验优化
- 提供清晰的导航
- 包含上下文帮助
- 支持数据导出
- 实现加载状态反馈

## 9.5 实战项目：销售仪表板

### 项目要求
创建一个完整的销售数据分析仪表板，包含：
- 销售趋势时间序列图
- 地理分布热力图  
- 产品类别占比饼图
- 交互式筛选控件

### 技术栈
- **前端**：Dash + Plotly
- **后端**：Flask或直接使用Dash
- **数据**：CSV或数据库连接
- **部署**：Heroku或本地服务器

### 代码结构
```
sales_dashboard/
├── app.py              # 主应用文件
├── data/
│   └── sales_data.csv  # 销售数据
├── layouts/
│   ├── header.py       # 头部布局
│   ├── sidebar.py      # 侧边栏
│   └── main_content.py # 主要内容
└── callbacks/
    └── update_charts.py # 回调函数
```

## 本章小结

高级数据可视化不仅仅是创建漂亮的图表，更是关于如何有效地传达信息。通过掌握交互式可视化、地理空间分析、3D技术以及仪表板设计原则，学生将能够创建专业级的数据可视化解决方案。

## 课后练习

1. 使用Plotly创建一个包含多个子图的交互式仪表板
2. 使用GeoPandas可视化中国各省份的人口密度
3. 创建一个3D动画展示股票价格的三维变化
4. 设计并实现一个完整的业务指标仪表板

## 扩展阅读

- [Plotly官方文档](https://plotly.com/python/)
- [Dash用户指南](https://dash.plotly.com/)
- [GeoPandas教程](https://geopandas.org/)
- [Data Visualization Best Practices](https://www.tableau.com/learn/articles/best-practices-for-dashboard-design)