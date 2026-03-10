# 第2章：Pandas基础与数据结构 - PPT大纲

## 幻灯片1：章节标题
- **第2章：Pandas基础与数据结构**
- Python数据分析的核心工具
- 2026年最新特性与最佳实践

## 幻灯片2：学习目标
- 掌握Pandas核心数据结构（Series, DataFrame）
- 理解Pandas 3.0的新特性与性能优势
- 学会高效的数据读取与写入技巧
- 掌握基本数据操作与索引方法
- 了解Polars作为高性能替代方案

## 幻灯片3：Pandas生态系统概览
- **历史发展**：从2008年至今的演进
- **核心定位**：数据分析的瑞士军刀
- **2026年地位**：仍然是数据科学的基石工具
- **与其他工具的关系**：
  - NumPy：底层计算引擎
  - Matplotlib/Seaborn：可视化后端
  - Scikit-learn：机器学习接口

## 幻灯片4：Series对象详解
- **定义**：一维带标签的数组
- **特点**：
  - 自动对齐索引
  - 支持多种数据类型
  - 内置缺失值处理
- **创建方式**：
  ```python
  pd.Series([1, 3, 5, np.nan, 6, 8])
  pd.Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])
  ```

## 幻灯片5：DataFrame对象详解
- **定义**：二维表格型数据结构
- **核心特性**：
  - 每列可不同数据类型
  - 行列都有标签
  - 强大的索引和选择功能
- **创建示例**：
  ```python
  df = pd.DataFrame({
      'A': 1.,
      'B': pd.Timestamp('2026-01-01'),
      'C': pd.Series(1, index=list(range(4)), dtype='float32'),
      'E': pd.Categorical(["test", "train", "test", "train"])
  })
  ```

## 幻灯片6：Pandas 3.0革命性更新
- **Arrow集成**（核心亮点）：
  - 默认使用Apache Arrow内存格式
  - 性能提升2-5倍
  - 内存效率大幅提升
- **Lazy Evaluation**：
  - 延迟计算优化
  - 减少中间结果内存占用
- **并行处理**：
  - 内置多线程支持
  - 自动利用多核CPU

## 幻灯片7：Arrow集成实战演示
- **代码对比**：
  ```python
  # 传统Pandas
  df_traditional = pd.DataFrame({'strings': ['hello', 'world']})
  
  # Pandas 3.0 + Arrow
  df_arrow = pd.DataFrame({
      'strings': pd.array(['hello', 'world'], dtype="string[pyarrow]"),
      'ints': pd.array([1, 2], dtype="int64[pyarrow]")
  })
  ```
- **性能指标**：
  - 内存使用：减少40-60%
  - 计算速度：提升200-500%
  - I/O性能：Parquet读写加速300%

## 幻灯片8：高效数据I/O策略
- **支持的格式**：
  - CSV/TSV、Excel、JSON、Parquet、HDF5
- **高性能读取技巧**：
  - 分块读取大文件（chunksize）
  - 指定数据类型优化内存（dtype）
  - 使用Arrow格式存储（Parquet）
- **最佳实践**：
  - 生产环境优先使用Parquet
  - 开发环境使用CSV便于调试

## 幻灯片9：数据选择与索引
- **列选择**：
  - `df['column']` vs `df[['col1', 'col2']]`
- **行选择**：
  - `.loc[]`：标签索引
  - `.iloc[]`：位置索引
- **条件选择**：
  - 布尔索引：`df[df['value'] > 100]`
  - 查询方法：`df.query('value > 100 and category == "A"')`

## 幻灯片10：基本数据操作
- **添加/删除列**：
  - `df['new_col'] = ...`
  - `df.drop('col', axis=1)`
- **重命名与排序**：
  - `df.rename(columns={'old': 'new'})`
  - `df.sort_values('col', ascending=False)`
- **聚合操作**：
  - `groupby()`、`agg()`、`transform()`

## 幻灯片11：Polars vs Pandas对比
- **Polars优势**：
  - Rust底层引擎，极致性能
  - Lazy API查询优化
  - 多线程原生支持
- **Pandas优势**：
  - 生态系统丰富
  - 学习曲线平缓
  - 社区支持强大
- **选择建议**：
  - <1GB数据：Pandas 3.0
  - >1GB数据：考虑Polars

## 幻灯片12：Polars实战演示
- **API对比**：
  ```python
  # Pandas
  result_pd = df.groupby('category').sum()
  
  # Polars
  result_pl = (df_pl
      .filter(pl.col('A') > 1)
      .select(['A', 'B'])
      .sort('A'))
  ```
- **性能测试场景**：
  - 10GB数据集聚合操作
  - 内存使用对比
  - 执行时间对比

## 幻灯片13：实践练习指导
- **练习2.1**：学生信息DataFrame创建
  - 包含学号、姓名、年龄、专业、GPA
  - 实现基本CRUD操作
- **练习2.2**：Pandas vs Polars性能对比
  - 相同数据集，相同操作
  - 记录时间和内存使用
- **练习2.3**：大文件I/O优化
  - Kaggle数据集处理
  - 不同策略效果对比

## 幻灯片14：常见陷阱与解决方案
- **内存溢出**：
  - 解决方案：分块处理、指定dtype
- **数据类型错误**：
  - 解决方案：显式转换、使用Arrow类型
- **性能瓶颈**：
  - 解决方案：向量化操作、避免循环
- **兼容性问题**：
  - 解决方案：版本锁定、依赖管理

## 幻灯片15：本章总结
- ✅ Pandas核心数据结构掌握
- ✅ Pandas 3.0新特性理解
- ✅ 高效数据操作技能
- ✅ Polars替代方案认知
- ✅ 实战练习完成

## 幻灯片16：下章预告
- **第3章：数据可视化基础**
- Matplotlib、Seaborn、Plotly深度解析
- 2026年可视化最佳实践
- 交互式图表与AI辅助可视化