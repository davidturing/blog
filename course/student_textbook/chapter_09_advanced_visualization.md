# 第9章：高级数据可视化

## 9.1 交互式可视化

### 9.1.1 Plotly基础
Plotly是一个强大的交互式可视化库，支持Python、R、JavaScript等多种语言。在Python中，我们主要使用`plotly.express`和`plotly.graph_objects`。

```python
import plotly.express as px
import plotly.graph_objects as go

# 使用plotly.express创建交互式散点图
fig = px.scatter(df, x='gdp_per_capita', y='life_expectancy', 
                 color='continent', size='population',
                 hover_name='country', log_x=True, size_max=60)
fig.show()
```

### 9.1.2 Dash应用开发
Dash是基于Flask、React和Plotly构建的Python Web应用框架，专门用于数据分析应用。

```python
import dash
from dash import dcc, html
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("交互式数据分析仪表板"),
    dcc.Graph(id='scatter-plot'),
    dcc.Slider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=df['year'].min(),
        marks={str(year): str(year) for year in df['year'].unique()},
        step=None
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
```

## 9.2 地理空间可视化

### 9.2.1 GeoPandas与地图绘制
GeoPandas扩展了Pandas，专门处理地理空间数据。

```python
import geopandas as gpd
import matplotlib.pyplot as plt

# 读取地理数据
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# 绘制世界地图
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world.plot(column='pop_est', ax=ax, legend=True, 
           legend_kwds={'label': "Population by Country"})
plt.title('World Population Distribution')
plt.show()
```

### 9.2.2 Folium交互式地图
Folium基于Leaflet.js，创建交互式Web地图。

```python
import folium
from folium import plugins

# 创建地图对象
m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)

# 添加标记
folium.Marker([39.9042, 116.4074], popup='Beijing').add_to(m)

# 添加热力图
heat_data = [[row['lat'], row['lon']] for index, row in df.iterrows()]
plugins.HeatMap(heat_data).add_to(m)

m.save('beijing_map.html')
```

## 9.3 3D可视化

### 9.3.1 Matplotlib 3D绘图
```python
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# 创建3D散点图
ax.scatter(x, y, z, c=z, cmap='viridis')
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label') 
ax.set_zlabel('Z Label')
plt.show()
```

### 9.3.2 Plotly 3D可视化
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Scatter3d(
    x=x, y=y, z=z,
    mode='markers',
    marker=dict(
        size=12,
        color=z,
        colorscale='Viridis',
        showscale=True
    )
)])

fig.update_layout(title='3D Scatter Plot')
fig.show()
```

## 9.4 动画与动态可视化

### 9.4.1 Matplotlib动画
```python
import matplotlib.animation as animation

fig, ax = plt.subplots()
line, = ax.plot([], [], 'o-', lw=2)

def init():
    ax.set_xlim(0, 2*np.pi)
    ax.set_ylim(-1, 1)
    return line,

def animate(i):
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + i/10)
    line.set_data(x, y)
    return line,

ani = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=200, interval=50, blit=True)
plt.show()
```

### 9.4.2 Plotly动画
```python
import plotly.express as px

fig = px.scatter(df, x="gdpPercap", y="lifeExp", 
                 animation_frame="year", animation_group="country",
                 size="pop", color="continent", hover_name="country",
                 log_x=True, size_max=55, range_x=[100,100000], 
                 range_y=[25,90])
fig.show()
```

## 9.5 可视化最佳实践

### 9.5.1 颜色选择原则
- **避免彩虹色谱**：使用感知均匀的颜色映射
- **考虑色盲友好**：使用ColorBrewer等工具
- **保持一致性**：同一项目中使用统一的配色方案

### 9.5.2 图表类型选择指南
| 数据类型 | 推荐图表 |
|---------|---------|
| 时间序列 | 折线图、面积图 |
| 分类比较 | 柱状图、条形图 |
| 分布分析 | 直方图、箱线图、小提琴图 |
| 关系分析 | 散点图、气泡图 |
| 地理数据 | 地图、热力图 |
| 多维数据 | 平行坐标、雷达图 |

### 9.5.3 可访问性考虑
- **字体大小**：确保在不同设备上可读
- **对比度**：文本与背景有足够的对比度
- **替代文本**：为图表提供描述性文本

## 9.6 实战案例：新冠疫情数据可视化

让我们用真实数据来练习高级可视化技术。

```python
# 获取COVID-19数据
import pandas as pd
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
df = pd.read_csv(url)

# 数据预处理
df_melted = df.melt(id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'], 
                    var_name='Date', value_name='Cases')

# 创建交互式时间序列图
fig = px.line(df_melted.groupby(['Country/Region', 'Date'])['Cases'].sum().reset_index(), 
              x='Date', y='Cases', color='Country/Region',
              title='COVID-19 Cases by Country')
fig.show()
```

## 9.7 本章小结

本章学习了：
- ✅ 交互式可视化工具（Plotly、Dash）
- ✅ 地理空间数据可视化（GeoPandas、Folium）
- ✅ 3D和动画可视化技术
- ✅ 可视化最佳实践和可访问性

## 9.8 练习题

1. **基础练习**：使用Plotly创建一个交互式散点图，展示GDP与预期寿命的关系
2. **进阶练习**：使用GeoPandas绘制中国各省份的人口密度地图
3. **挑战练习**：创建一个Dash应用，允许用户选择不同的数据集进行可视化
4. **项目练习**：选择一个感兴趣的数据集，创建一个包含多种高级可视化技术的综合报告

## 9.9 扩展阅读

- [Plotly官方文档](https://plotly.com/python/)
- [Dash用户指南](https://dash.plotly.com/)
- [GeoPandas教程](https://geopandas.org/en/stable/docs/user_guide.html)
- [数据可视化最佳实践](https://www.tableau.com/learn/articles/best-practices-for-dashboard-design)