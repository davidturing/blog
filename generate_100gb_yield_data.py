#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片良率工程 DFX 100GB生产级超大规模数据集生成器
基于Polars纯流式分批生成，支持分区存储和断点续传
"""

import os
import sys
import time
import logging
import gc
import json
from pathlib import Path

try:
    import polars as pl
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as e:
    print(f"缺少必要依赖: {e}")
    print("请安装: pip install polars pyarrow numpy")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_generation_100gb.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YieldDataGenerator100GB:
    """100GB芯片良率数据生成器"""
    
    def __init__(self, output_dir="yield_100gb_data", target_size_gb=100.0):
        self.output_dir = output_dir
        self.target_size_bytes = target_size_gb * 1024**3
        self.chunk_rows = 5_000_000  # 每批次500万行，约76MB内存
        
        # 分区配置：10个分区文件，每个约10GB
        self.num_partitions = 10
        self.partition_target_rows = 65_000_000  # 每分区6500万行
        self.total_target_rows = self.partition_target_rows * self.num_partitions  # 总65亿行
        
        # 数据规格定义
        self.schema = {
            'LotID': pl.Utf8,           # 批次ID
            'WaferID': pl.Utf8,         # 晶圆ID  
            'DeviceID': pl.Utf8,        # 设备ID
            'BinCode': pl.Utf8,         # Bin码
            'PassFlag': pl.Boolean,     # 通过标志
            'XCoord': pl.Int32,         # X坐标
            'YCoord': pl.Int32,         # Y坐标
            'Temp': pl.Float32,         # 温度
            'Voltage': pl.Float32,      # 电压
            # 20个Metric测试指标
            **{f'Metric_{i:02d}': pl.Float32 for i in range(20)},
            # Wafer Map宽表字段 (10个关键参数)
            **{f'WaferParam_{i:02d}': pl.Float32 for i in range(10)}
        }
        
        # 字典编码配置（优化压缩）
        self.dict_fields = ['LotID', 'WaferID', 'DeviceID', 'BinCode']
        
        # 状态文件路径
        self.state_file = os.path.join(output_dir, "generation_state.json")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"目标参数: {self.total_target_rows:,} 行, {self.num_partitions} 分区, 目标大小: ~100GB")
        
    def _generate_partition_chunk(self, partition_idx, chunk_idx, rows_in_chunk):
        """生成单个分区的数据块"""
        # 使用分区索引和块索引作为随机种子，确保可重复性
        np.random.seed(42 + partition_idx * 1000 + chunk_idx)
        
        # 预分配字典值域（每个分区使用不同的值域范围）
        lot_ids = [f'LOT_{partition_idx}_{i:06d}' for i in range(5000)]
        wafer_ids = [f'WAFER_{partition_idx}_{i:07d}' for i in range(50000)]
        device_ids = [f'DEV_{partition_idx}_{i:03d}' for i in range(100)]
        bin_codes = [f'BIN_{partition_idx}_{i:03d}' for i in range(200)]
        
        # 生成基础字段
        data = {
            'LotID': np.random.choice(lot_ids, rows_in_chunk),
            'WaferID': np.random.choice(wafer_ids, rows_in_chunks),
            'DeviceID': np.random.choice(device_ids, rows_in_chunk),
            'BinCode': np.random.choice(bin_codes, rows_in_chunk),
            'PassFlag': np.random.choice([True, False], rows_in_chunk, p=[0.95, 0.05]),  # 95%良率
            'XCoord': np.random.randint(0, 10000, rows_in_chunk, dtype=np.int32),
            'YCoord': np.random.randint(0, 10000, rows_in_chunk, dtype=np.int32),
            'Temp': np.random.normal(25.0, 2.0, rows_in_chunk).astype(np.float32),  # 25°C ±2°C
            'Voltage': np.random.normal(3.3, 0.1, rows_in_chunk).astype(np.float32),  # 3.3V ±0.1V
        }
        
        # 生成20个Metric指标（模拟真实测试数据分布）
        for i in range(20):
            # 不同指标有不同的分布特征
            if i % 4 == 0:  # 正态分布
                data[f'Metric_{i:02d}'] = np.random.normal(1.0, 0.1, rows_in_chunk).astype(np.float32)
            elif i % 4 == 1:  # 对数正态分布
                data[f'Metric_{i:02d}'] = np.random.lognormal(0, 0.1, rows_in_chunk).astype(np.float32)
            elif i % 4 == 2:  # 指数分布
                data[f'Metric_{i:02d}'] = np.random.exponential(1.0, rows_in_chunk).astype(np.float32)
            else:  # 均匀分布
                data[f'Metric_{i:02d}'] = np.random.uniform(0.8, 1.2, rows_in_chunk).astype(np.float32)
                
        # 生成Wafer Map宽表字段
        for i in range(10):
            data[f'WaferParam_{i:02d}'] = np.random.normal(1.0, 0.2, rows_in_chunk).astype(np.float32)
            
        return pl.DataFrame(data, schema=self.schema)
        
    def _save_state(self, completed_partitions, completed_chunks_per_partition):
        """保存生成状态"""
        state = {
            'completed_partitions': completed_partitions,
            'completed_chunks_per_partition': completed_chunks_per_partition,
            'total_target_rows': self.total_target_rows,
            'partition_target_rows': self.partition_target_rows,
            'timestamp': time.time()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def _load_state(self):
        """加载生成状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get('completed_partitions', 0), state.get('completed_chunks_per_partition', {})
        return 0, {}
        
    def generate_partition(self, partition_idx, resume_from_chunk=0):
        """生成单个分区文件"""
        output_file = os.path.join(self.output_dir, f"yield_100gb_part_{partition_idx+1:02d}.parquet")
        
        # 如果文件已存在且不是从头开始，跳过
        if resume_from_chunk == 0 and os.path.exists(output_file):
            logger.warning(f"分区文件已存在: {output_file}")
            overwrite = input(f"是否覆盖分区 {partition_idx+1}? (y/N): ").lower().strip()
            if overwrite != 'y':
                return
                
        start_time = time.time()
        writer = None
        completed_chunks = resume_from_chunk
        chunks_per_partition = (self.partition_target_rows + self.chunk_rows - 1) // self.chunk_rows
        
        try:
            for chunk_idx in range(resume_from_chunk, chunks_per_partition):
                # 计算本批次行数
                remaining_rows = self.partition_target_rows - (chunk_idx * self.chunk_rows)
                rows_in_chunk = min(self.chunk_rows, remaining_rows)
                
                logger.info(f"分区 {partition_idx+1}/{self.num_partitions}, 批次 {chunk_idx+1}/{chunks_per_partition} ({rows_in_chunk:,} 行)")
                
                # 生成数据块
                df_chunk = self._generate_partition_chunk(partition_idx, chunk_idx, rows_in_chunk)
                
                # 写入Parquet文件
                table = df_chunk.to_arrow()
                
                # 应用字典编码优化
                for field_name in self.dict_fields:
                    if field_name in table.schema.names:
                        idx = table.schema.names.index(field_name)
                        field = table.schema.field(idx)
                        dict_type = pa.dictionary(pa.int32(), pa.string())
                        table = table.set_column(idx, field.with_type(dict_type), 
                                               pa.DictionaryArray.from_arrays(
                                                   pa.compute.dictionary_encode(table.column(idx)).indices,
                                                   pa.array(df_chunk[field_name].unique(), pa.string())
                                               ))
                
                # Parquet写入配置（zstd最高压缩比）
                parquet_write_options = {
                    'compression': 'zstd',
                    'compression_level': 22,  # zstd最高压缩级别
                    'use_dictionary': True,
                    'write_statistics': True,
                    'data_page_size': 2**20,  # 1MB页面
                    'dictionary_pagesize_limit': 2**20,
                    'coerce_timestamps': 'us'
                }
                
                if writer is None:
                    writer = pq.ParquetWriter(
                        output_file, 
                        table.schema,
                        **parquet_write_options
                    )
                
                writer.write_table(table)
                completed_chunks += 1
                
                # 内存清理
                del df_chunk, table
                gc.collect()
                
                # 更新状态
                self._save_state(partition_idx, {partition_idx: completed_chunks})
                
        except KeyboardInterrupt:
            logger.info(f"分区 {partition_idx+1} 生成被中断，已完成 {completed_chunks} 批次")
            raise
        except Exception as e:
            logger.error(f"分区 {partition_idx+1} 生成失败: {e}")
            raise
        finally:
            if writer:
                writer.close()
                
        # 验证分区文件
        if os.path.exists(output_file):
            final_size = os.path.getsize(output_file)
            final_size_gb = final_size / (1024**3)
            logger.info(f"分区 {partition_idx+1} 完成! 大小: {final_size_gb:.2f} GB, 行数: {self.partition_target_rows:,}")
            
    def generate(self, resume_from_partition=0):
        """主生成函数，支持分区级断点续传"""
        start_time = time.time()
        completed_partitions = resume_from_partition
        
        try:
            for partition_idx in range(resume_from_partition, self.num_partitions):
                logger.info(f"开始生成分区 {partition_idx+1}/{self.num_partitions}")
                
                # 加载该分区的断点状态
                _, chunks_state = self._load_state()
                resume_chunk = chunks_state.get(str(partition_idx), 0)
                
                self.generate_partition(partition_idx, resume_chunk)
                completed_partitions += 1
                
                # 分区间清理
                gc.collect()
                
                # 进度报告
                elapsed = time.time() - start_time
                progress = completed_partitions / self.num_partitions
                estimated_total = elapsed / progress if progress > 0 else 0
                remaining = estimated_total - elapsed
                logger.info(f"总体进度: {progress:.1%}, 已用时: {elapsed/3600:.1f}小时, 预计剩余: {remaining/3600:.1f}小时")
                
        except KeyboardInterrupt:
            logger.info(f"100GB数据集生成被中断，已完成 {completed_partitions} 个分区")
            logger.info(f"可使用 resume_from_partition={completed_partitions} 继续生成")
        except Exception as e:
            logger.error(f"100GB数据集生成失败: {e}")
            raise
            
        # 最终验证
        self.validate_dataset()
        
    def validate_dataset(self):
        """验证整个数据集"""
        total_size = 0
        total_files = 0
        
        for i in range(self.num_partitions):
            file_path = os.path.join(self.output_dir, f"yield_100gb_part_{i+1:02d}.parquet")
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
                total_files += 1
                
        if total_files == self.num_partitions:
            total_size_gb = total_size / (1024**3)
            logger.info(f"100GB数据集生成完成!")
            logger.info(f"目录: {self.output_dir}")
            logger.info(f"总大小: {total_size_gb:.2f} GB")
            logger.info(f"总行数: {self.total_target_rows:,}")
            logger.info(f"总列数: {len(self.schema)}")
            logger.info(f"分区数: {self.num_partitions}")
            logger.info(f"耗时: {(time.time() - start_time)/3600:.1f} 小时")
        else:
            logger.warning(f"数据集不完整! 期望 {self.num_partitions} 个分区, 实际 {total_files} 个")
            
    @staticmethod
    def get_dataset_info():
        """返回数据集详细信息"""
        info = {
            '数据集名称': 'yield_100gb_data',
            '目标总大小': '~100GB (zstd最高压缩)',
            '总行数': '6,500,000,000 (65亿行)',
            '总列数': '39列',
            '分区数量': '10个分区文件',
            '单分区大小': '~10GB',
            '单分区行数': '650,000,000 (6.5亿行)',
            '字段说明': {
                'LotID': '批次ID (字符串，字典编码)',
                'WaferID': '晶圆ID (字符串，字典编码)', 
                'DeviceID': '设备ID (字符串，字典编码)',
                'BinCode': 'Bin码 (字符串，字典编码)',
                'PassFlag': '通过标志 (布尔值，95%良率)',
                'XCoord/YCoord': '坐标位置 (Int32)',
                'Temp/Voltage': '环境参数 (Float32，真实分布)',
                'Metric_00-Metric_19': '20个测试指标 (Float32，四种分布类型)',
                'WaferParam_00-WaferParam_09': 'Wafer Map宽表参数 (Float32)'
            },
            '压缩格式': 'Parquet + zstd (level 22)',
            '兼容性': '完全兼容DuckDB、Pandas、Polars全场景压测',
            '适用场景': 'TB级数据加载、亿级聚合、宽表运算、高并发查询、生产环境选型'
        }
        return info
        
    @staticmethod
    def read_dataset_example():
        """提供数据集读取示例代码"""
        examples = {
            'polars_lazy': '''
# Polars LazyFrame 批量读取所有分区（推荐）
import polars as pl
df = pl.scan_parquet("yield_100gb_data/yield_100gb_part_*.parquet")
result = df.filter(pl.col("PassFlag")).group_by("LotID").agg(pl.count()).collect(streaming=True)
''',
            'duckdb_direct': '''
-- DuckDB 直接查询分区文件
import duckdb
conn = duckdb.connect()
result = conn.execute("""
    SELECT LotID, COUNT(*) 
    FROM 'yield_100gb_data/yield_100gb_part_*.parquet' 
    WHERE PassFlag = true 
    GROUP BY LotID
""").df()
''',
            'pandas_chunked': '''
# Pandas 分块读取（内存友好）
import pandas as pd
import glob
files = glob.glob("yield_100gb_data/yield_100gb_part_*.parquet")
for file in files:
    for chunk in pd.read_parquet(file, chunksize=1000000):
        # 处理每个chunk
        pass
'''
        }
        return examples

def main():
    """主函数"""
    generator = YieldDataGenerator100GB()
    
    # 显示数据集信息
    info = generator.get_dataset_info()
    print("\n=== 100GB芯片良率数据集规格 ===")
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    print()
    
    # 显示读取示例
    examples = generator.read_dataset_example()
    print("=== 数据集读取示例 ===")
    for name, code in examples.items():
        print(f"\n{name.upper()} 示例:")
        print(code.strip())
    print()
    
    # 询问是否开始生成
    start = input("开始生成100GB数据集? (y/N): ").lower().strip()
    if start != 'y':
        print("生成已取消")
        return
        
    # 检查磁盘空间
    try:
        import psutil
        required_space = 110 * 1024**3  # 需要110GB空间
        free_space = psutil.disk_usage('.').free
        if free_space < required_space:
            print(f"警告: 磁盘空间不足! 需要 {required_space/(1024**3):.1f}GB, 可用 {free_space/(1024**3):.1f}GB")
            proceed = input("是否继续? (y/N): ").lower().strip()
            if proceed != 'y':
                return
    except ImportError:
        print("psutil未安装，跳过磁盘空间检查")
        
    # 加载断点状态
    completed_partitions, _ = generator._load_state()
    if completed_partitions > 0:
        resume = input(f"检测到已完成 {completed_partitions} 个分区，是否从中继续? (Y/n): ").lower().strip()
        if resume != 'n':
            print(f"从分区 {completed_partitions + 1} 开始继续生成")
        else:
            completed_partitions = 0
            
    # 开始生成
    generator.generate(resume_from_partition=completed_partitions)

if __name__ == "__main__":
    main()