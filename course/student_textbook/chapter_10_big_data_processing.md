# 第10章：大数据处理技术

## 10.1 大数据挑战与解决方案

### 10.1.1 传统Pandas的局限性
在处理大规模数据集时，传统的Pandas库会遇到以下挑战：

- **内存限制**：Pandas将所有数据加载到内存中，对于GB级数据容易导致内存溢出
- **单线程处理**：无法充分利用多核CPU的优势
- **I/O瓶颈**：文件读写速度成为性能瓶颈

### 10.1.2 现代大数据处理框架
2026年的Python大数据生态系统提供了多种解决方案：

#### Dask - 并行计算库
```python
import dask.dataframe as dd

# 读取大型CSV文件（分块处理）
df = dd.read_csv('large_dataset.csv')

# 延迟计算 - 只有在需要结果时才执行
result = df.groupby('category').value.mean().compute()
```

#### Polars - 高性能DataFrame库
```python
import polars as pl

# 内存效率高，支持并行处理
df = pl.read_csv('large_dataset.csv')

# 向量化操作，速度比Pandas快5-10倍
result = df.group_by('category').agg(pl.col('value').mean())
```

#### Vaex - 虚拟内存DataFrame
```python
import vaex

# 支持TB级数据处理，使用内存映射
df = vaex.open('huge_dataset.hdf5')

# 即时计算，无需加载到内存
result = df.groupby('category').agg({'value': 'mean'})
```

## 10.2 实战案例：处理10GB电商数据集

### 10.2.1 数据准备
假设我们有一个10GB的电商交易数据集，包含以下字段：
- `user_id`: 用户ID
- `product_id`: 商品ID  
- `category`: 商品类别
- `price`: 价格
- `timestamp`: 交易时间
- `quantity`: 数量

### 10.2.2 使用Dask进行分析
```python
import dask.dataframe as dd
import dask

# 配置Dask
dask.config.set(scheduler='threads', num_workers=4)

# 读取数据（自动分块）
df = dd.read_csv('ecommerce_transactions_10gb.csv', 
                 dtype={'user_id': 'object', 'product_id': 'object'})

# 基础统计信息
print("数据形状:", df.shape[0].compute(), "行")
print("内存使用:", df.memory_usage(deep=True).sum().compute())

# 按类别分组统计
category_stats = df.groupby('category').agg({
    'price': ['mean', 'sum'],
    'quantity': 'sum',
    'user_id': 'nunique'
}).compute()

print(category_stats)
```

### 10.2.3 使用Polars优化性能
```python
import polars as pl
import time

# Polars读取（通常比Pandas快3-5倍）
start_time = time.time()
df_polars = pl.read_csv('ecommerce_transactions_10gb.csv')
print(f"Polars读取时间: {time.time() - start_time:.2f}秒")

# 高效聚合操作
result = (df_polars
          .group_by('category')
          .agg([
              pl.col('price').mean().alias('avg_price'),
              pl.col('price').sum().alias('total_revenue'),
              pl.col('quantity').sum().alias('total_quantity'),
              pl.col('user_id').n_unique().alias('unique_users')
          ])
          .sort('total_revenue', descending=True))

print(result)
```

## 10.3 云原生大数据处理

### 10.3.1 AWS S3 + Dask
```python
import s3fs
import dask.dataframe as dd

# 直接从S3读取数据
s3 = s3fs.S3FileSystem(anon=False)
df = dd.read_csv('s3://my-bucket/large-dataset/*.csv', 
                 storage_options={'anon': False})

# 分布式计算
result = df.groupby('region').sales.sum().compute()
```

### 10.3.2 Google Cloud Storage + Polars
```python
import gcsfs
import polars as pl

# 从GCS读取Parquet文件
gcs = gcsfs.GCSFileSystem()
df = pl.read_parquet('gs://my-bucket/dataset.parquet', 
                     storage_options=gcs.storage_options)

# 高效查询
filtered_df = df.filter(pl.col('date') >= '2026-01-01')
```

## 10.4 性能对比与最佳实践

### 10.4.1 不同场景下的工具选择

| 数据规模 | 推荐工具 | 优势 |
|---------|---------|------|
| < 1GB | Pandas | 简单易用，功能丰富 |
| 1-10GB | Polars | 高性能，内存效率高 |
| 10-100GB | Dask | 分布式，可扩展 |
| > 100GB | Vaex/Dask | 虚拟内存/分布式 |

### 10.4.2 性能优化技巧

#### 1. 数据类型优化
```python
# 选择合适的数据类型
df = df.with_columns([
    pl.col('category').cast(pl.Categorical),
    pl.col('price').cast(pl.Float32),  # 而不是Float64
    pl.col('quantity').cast(pl.UInt32)  # 而不是Int64
])
```

#### 2. 列式存储格式
```python
# 使用Parquet格式（列式存储，压缩率高）
df.write_parquet('optimized_data.parquet')

# 读取时只选择需要的列
df_subset = pl.read_parquet('optimized_data.parquet', 
                           columns=['user_id', 'price'])
```

#### 3. 并行处理配置
```python
# Dask配置
import dask
dask.config.set({
    'scheduler': 'threads',
    'num_workers': 8,
    'threading_layer': 'tbb'  # Intel TBB加速
})
```

## 10.5 动手练习

### 练习10.1：性能基准测试
创建一个脚本来比较Pandas、Polars和Dask在不同数据规模下的性能：

```python
import pandas as pd
import polars as pl
import dask.dataframe as dd
import time
import numpy as np

def benchmark_performance(data_size):
    # 生成测试数据
    np.random.seed(42)
    data = {
        'id': range(data_size),
        'value': np.random.randn(data_size),
        'category': np.random.choice(['A', 'B', 'C'], data_size)
    }
    
    # Pandas测试
    start = time.time()
    df_pd = pd.DataFrame(data)
    result_pd = df_pd.groupby('category')['value'].mean()
    pandas_time = time.time() - start
    
    # Polars测试  
    start = time.time()
    df_pl = pl.DataFrame(data)
    result_pl = df_pl.group_by('category').agg(pl.col('value').mean())
    polars_time = time.time() - start
    
    print(f"数据规模: {data_size:,}")
    print(f"Pandas时间: {pandas_time:.2f}s")
    print(f"Polars时间: {polars_time:.2f}s")
    print(f"加速比: {pandas_time/polars_time:.2f}x\n")

# 测试不同规模
for size in [100_000, 1_000_000, 10_000_000]:
    benchmark_performance(size)
```

### 练习10.2：真实数据集分析
下载一个大型公开数据集（如Kaggle的New York City Taxi Trip Duration），使用Polars或Dask进行分析：

1. 数据清洗和预处理
2. 探索性数据分析
3. 性能优化
4. 结果可视化

## 10.6 本章小结

- **大数据挑战**：内存限制、单线程、I/O瓶颈
- **现代解决方案**：Dask（分布式）、Polars（高性能）、Vaex（虚拟内存）
- **云集成**：直接与AWS S3、Google Cloud等集成
- **最佳实践**：数据类型优化、列式存储、并行配置
- **工具选择**：根据数据规模选择合适的工具

通过本章的学习，你应该能够处理GB级别的数据集，并根据具体需求选择最适合的大数据处理工具。记住，工具的选择应该基于数据规模、硬件资源和性能要求来决定。