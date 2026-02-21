# 第4章：数据清洗与预处理 - PPT大纲

## 幻灯片1: 章节标题
- **第4章：数据清洗与预处理**
- Python数据分析课程
- 2026年春季学期

## 幻灯片2: 学习目标
- 理解数据质量问题的常见类型
- 掌握使用Pandas 3.0进行数据清洗的核心技术
- 学习处理缺失值、异常值和重复数据的方法
- 了解数据标准化和转换的最佳实践
- 实践真实数据集的清洗流程

## 幻灯片3: 数据质量问题概述
- **常见数据质量问题**:
  - 缺失值 (Missing Values)
  - 异常值/离群点 (Outliers)
  - 重复数据 (Duplicates)
  - 不一致的数据格式
  - 错误的数据类型
  - 不合理的数据范围

## 幻灯片4: Pandas 3.0数据清洗新特性
- **Pandas 3.0增强功能**:
  - 更高效的缺失值处理API
  - 内置异常值检测工具
  - 改进的数据类型推断
  - 链式操作优化
  - 与Polars的无缝集成

## 幻灯片5: 处理缺失值
- **识别缺失值**:
  - `isna()`, `notna()`
  - `info()`, `describe()`
- **处理策略**:
  - 删除: `dropna()`
  - 填充: `fillna()`
  - 插值: `interpolate()`
  - 使用统计量填充

## 幻灯片6: 实战示例 - 缺失值处理
```python
# 示例代码
import pandas as pd

# 加载数据
df = pd.read_csv('sales_data.csv')

# 检查缺失值
print(df.isna().sum())

# 填充数值列的缺失值
df['price'].fillna(df['price'].median(), inplace=True)

# 填充分类列的缺失值
df['category'].fillna('Unknown', inplace=True)
```

## 幻灯片7: 处理异常值
- **异常值检测方法**:
  - 箱线图分析 (IQR方法)
  - Z-score标准化
  - 可视化检测
- **处理策略**:
  - 删除异常值
  - 替换为边界值
  - 分箱处理
  - 保持原样（有时异常值很重要）

## 幻灯片8: 实战示例 - 异常值处理
```python
# 使用IQR方法检测异常值
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1

# 定义异常值边界
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# 过滤异常值
df_clean = df[(df['price'] >= lower_bound) & 
              (df['price'] <= upper_bound)]
```

## 幻灯片9: 处理重复数据
- **识别重复数据**:
  - `duplicated()`
  - `value_counts()`
- **处理方法**:
  - `drop_duplicates()`
  - 基于特定列去重
  - 保留首次/最后一次出现

## 幻灯片10: 数据类型转换与标准化
- **数据类型优化**:
  - `astype()`类型转换
  - 内存优化技巧
- **数据标准化**:
  - Min-Max标准化
  - Z-score标准化
  - 对数变换

## 幻灯片11: 实战示例 - 数据标准化
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Z-score标准化
scaler = StandardScaler()
df['price_scaled'] = scaler.fit_transform(df[['price']])

# Min-Max标准化
minmax_scaler = MinMaxScaler()
df['price_normalized'] = minmax_scaler.fit_transform(df[['price']])
```

## 幻灯片12: Polars在数据清洗中的应用
- **为什么使用Polars**:
  - 更快的处理速度
  - 更好的内存效率
  - 现代化的API设计
- **与Pandas的对比**:
  - 语法差异
  - 性能优势
  - 适用场景

## 幻灯片13: 实战示例 - Polars数据清洗
```python
import polars as pl

# 使用Polars加载和清洗数据
df_pl = pl.read_csv('sales_data.csv')

# Polars风格的数据清洗
df_clean = (df_pl
    .filter(pl.col('price') > 0)
    .with_columns([
        pl.col('price').fill_null(strategy='median'),
        pl.col('category').fill_null('Unknown')
    ])
)
```

## 幻灯片14: 完整的数据清洗流程
1. **数据探索**: 了解数据结构和质量
2. **缺失值处理**: 选择合适的填充或删除策略
3. **异常值处理**: 检测并处理离群点
4. **重复数据处理**: 识别并移除重复记录
5. **数据类型优化**: 转换为合适的数据类型
6. **数据标准化**: 根据需要进行标准化处理
7. **验证结果**: 确保清洗后的数据质量

## 幻灯片15: 实战项目 - 电商销售数据清洗
- **项目背景**: 清洗真实的电商销售数据集
- **数据特点**: 包含缺失值、异常价格、重复订单等
- **清洗目标**: 创建可用于分析的干净数据集
- **技术栈**: Pandas 3.0 + Polars + Scikit-learn

## 幻灯片16: AI辅助数据清洗
- **AI在数据清洗中的应用**:
  - 自动检测数据质量问题
  - 智能推荐清洗策略
  - 自动生成清洗代码
- **2026年最新工具**:
  - OpenAI DataCleaner API
  - Google Vertex AI Data Prep
  - 本地LLM辅助清洗

## 幻灯片17: 最佳实践与注意事项
- **数据清洗原则**:
  - 保留原始数据备份
  - 记录所有清洗步骤
  - 验证清洗结果的合理性
  - 考虑业务逻辑约束
- **常见陷阱**:
  - 过度清洗丢失重要信息
  - 忽略数据分布的变化
  - 不考虑上下游依赖

## 幻灯片18: 本章小结
- 数据清洗是数据分析的关键前置步骤
- Pandas 3.0提供了强大的数据清洗工具
- Polars为大数据清洗提供了高性能选择
- 结合AI工具可以提高清洗效率
- 建立标准化的清洗流程很重要

## 幻灯片19: 课后练习
1. 使用提供的数据集完成完整的数据清洗流程
2. 比较Pandas和Polars在相同清洗任务上的性能差异
3. 尝试使用AI工具辅助数据清洗
4. 为特定业务场景设计定制化的清洗策略

## 幻灯片20: 参考资料与扩展阅读
- Pandas 3.0官方文档
- Polars用户指南
- 《Python数据清洗实战》- 2026版
- Kaggle数据清洗竞赛案例
- GitHub开源数据清洗项目