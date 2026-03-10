# 替换DFX测试数据集指南

## 数据集规格详情

### 基本参数
- **文件名**: `yield_10gb.parquet`
- **目标大小**: ~10GB (zstd压缩后)
- **总行数**: 650,000,000 (6.5亿行)
- **总列数**: 39列
- **压缩格式**: Parquet + zstd (level 3)

### 字段说明
| 字段类型 | 字段名 | 数据类型 | 说明 |
|---------|--------|----------|------|
| 基础标识 | LotID, WaferID, DeviceID, BinCode | Utf8 (字典编码) | 批次、晶圆、设备、Bin标识 |
| 状态标志 | PassFlag | Boolean | 通过/失败标志 (95%良率) |
| 位置信息 | XCoord, YCoord | Int32 | 晶圆坐标位置 |
| 环境参数 | Temp, Voltage | Float32 | 温度(25°C±2°C)、电压(3.3V±0.1V) |
| 测试指标 | Metric_00-Metric_19 | Float32 | 20个测试指标 (不同分布特征) |
| Wafer Map | WaferParam_00-WaferParam_09 | Float32 | 10个Wafer Map宽表参数 |

### 分布特征
- **Metric指标**: 包含正态分布、对数正态分布、指数分布、均匀分布四种类型
- **良率**: 95%通过率，符合真实生产环境
- **数据相关性**: 同一批次/晶圆的数据具有相似的分布特征

## 替换现有测试数据步骤

### 1. 生成10GB数据集
```bash
cd /Users/zhaoqinhuang/david_project
python3 generate_10gb_yield_data.py
```

### 2. 备份原有数据（可选）
```bash
# 备份原有dfx_data目录
mv dfx_data dfx_data_backup
```

### 3. 创建新的测试数据目录
```bash
mkdir -p dfx_data_10gb
```

### 4. 复制10GB数据集
```bash
cp yield_10gb.parquet dfx_data_10gb/base.parquet
```

### 5. 修改测试脚本配置
编辑 `dfx_test_runner_optimized.py` 文件，修改以下配置：

```python
# 原配置
CONFIG = {
    'data_dir': './dfx_data_optimized',
    'base_rows': 10_000_000,  # 1000万行
    # ...
}

# 修改为
CONFIG = {
    'data_dir': './dfx_data_10gb',
    'base_rows': 650_000_000,  # 6.5亿行
    # ...
}
```

同时修改文件路径：
```python
# 原路径
self.base_pq = f"{CONFIG['data_dir']}/base.parquet"

# 确保指向新数据集
self.base_pq = f"{CONFIG['data_dir']}/base.parquet"  # 已经正确
```

### 6. 更新数据生成逻辑（可选）
如果需要保留CSV版本，可以从Parquet转换：
```python
import polars as pl
# 转换100万行作为CSV样本
df_sample = pl.read_parquet("yield_10gb.parquet").limit(1_000_000)
df_sample.write_csv("dfx_data_10gb/base.csv")
```

### 7. 运行压测
```bash
python3 dfx_test_runner_optimized.py
```

## 性能预期

使用10GB/6.5亿行数据集后，性能差异将更加显著：

| 场景 | 预期Polars优势 |
|------|---------------|
| 数据加载 | 2-3倍速度提升 |
| 多维度聚合 | 3-5倍速度提升 |
| 宽表运算 | 4-6倍速度提升 |
| 高并发查询 | 2-4倍QPS提升 |
| 内存使用 | 减少40-60%峰值内存 |

## 注意事项

1. **磁盘空间**: 确保有至少12GB可用空间
2. **内存要求**: 生成过程需要4-8GB内存，运行压测需要16GB+内存
3. **时间预估**: 生成10GB数据约需30-60分钟，压测约需15-30分钟
4. **断点续传**: 如果生成中断，可以使用 `resume_from` 参数继续
5. **验证数据**: 生成完成后会自动验证schema和文件完整性

## 兼容性保证

- ✅ 完全兼容 DuckDB 直接查询
- ✅ 完全兼容 Pandas DataFrame 加载  
- ✅ 完全兼容 Polars LazyFrame 扫描
- ✅ 支持所有DFX压测场景（加载、聚合、过滤、宽表、并发、导出）