#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片良率工程DFX性能测试 - Pandas+DuckDB vs Polars+DuckDB

核心测试目标：
基于原芯片良率工程千万级数据DFX非功能性测试方案，开发对比代码，
验证Pandas+DuckDB与Polars+DuckDB组合在半导体良率大数据场景下的性能差异。
"""

import os
import sys
import time
import logging
import warnings
from typing import Dict, Any, Tuple, Callable
from contextlib import contextmanager
import gc

# 禁用Pandas链式赋值警告
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

# 导入依赖库
try:
    import pandas as pd
    import polars as pl
    import duckdb
    import psutil
    from memory_profiler import memory_usage
    import numpy as np
except ImportError as e:
    print(f"缺少必要依赖: {e}")
    print("请安装: pip install pandas polars duckdb psutil memory-profiler numpy")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dfx_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 测试配置
TEST_CONFIG = {
    'data_path': './test_data',
    'random_seed': 42,
    'parallel_threads': 10,  # M4芯片优化并行度
    'chunk_size': 1000000,   # 分块处理大小
    'repetitions': 3,        # 每个测试重复次数取平均
}

# 设置随机种子
np.random.seed(TEST_CONFIG['random_seed'])
pl.set_random_seed(TEST_CONFIG['random_seed'])

class PerformanceMonitor:
    """性能监控器"""
    
    @staticmethod
    @contextmanager
    def monitor_resources():
        """监控CPU和内存使用情况"""
        process = psutil.Process()
        
        # 记录初始状态
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 开始监控
        start_time = time.time()
        cpu_percentages = []
        memory_usage_mb = []
        
        try:
            yield {'cpu': cpu_percentages, 'memory': memory_usage_mb, 'start_time': start_time}
        finally:
            # 记录最终状态
            end_time = time.time()
            final_cpu = process.cpu_percent()
            final_memory = process.memory_info().rss / 1024 / 1024
            
            # 计算峰值内存（使用memory_profiler）
            mem_usage = memory_usage((lambda: None, ()), interval=0.1, timeout=1)
            peak_memory = max(mem_usage) if mem_usage else final_memory
            
            logger.info(f"执行时间: {end_time - start_time:.3f}s")
            logger.info(f"CPU利用率: {final_cpu:.1f}%")
            logger.info(f"峰值内存: {peak_memory:.1f}MB")

class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_base_yield_data(rows: int = 10000000) -> pd.DataFrame:
        """生成基础良率数据 (1000万行)"""
        logger.info(f"生成基础良率数据: {rows:,} 行")
        
        data = {
            'LotID': np.random.choice([f'LOT_{i:06d}' for i in range(5000)], rows),
            'WaferID': np.random.choice([f'WAFER_{i:06d}' for i in range(1000000)], rows),
            'Bin': np.random.choice([f'BIN_{i:03d}' for i in range(200)], rows),
            'DeviceID': np.random.choice([f'DEV_{i:02d}' for i in range(50)], rows),
            'XCoord': np.random.randint(0, 1000, rows),
            'YCoord': np.random.randint(0, 1000, rows),
            'TestResult': np.random.normal(1.0, 0.1, rows),
            'Timestamp': pd.date_range('2025-01-01', periods=rows, freq='1S')[
                np.random.randint(0, 15768000, rows)  # 6个月范围
            ]
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_extended_yield_data(rows: int = 5000000) -> pd.DataFrame:
        """生成扩展良率数据 (500万行)"""
        logger.info(f"生成扩展良率数据: {rows:,} 行")
        
        param_names = [f'PARAM_{i:03d}' for i in range(100)]
        data = {
            'LotID': np.random.choice([f'LOT_{i:06d}' for i in range(5000)], rows),
            'WaferID': np.random.choice([f'WAFER_{i:06d}' for i in range(1000000)], rows),
            'ParamName': np.random.choice(param_names, rows),
            'ParamValue': np.random.normal(50.0, 10.0, rows),
            'UpperLimit': 70.0,
            'LowerLimit': 30.0,
            'Status': np.random.choice(['PASS', 'FAIL'], rows, p=[0.95, 0.05])
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_wafer_map_data(rows: int = 2000000) -> pd.DataFrame:
        """生成Wafer Map数据 (200万行)"""
        logger.info(f"生成Wafer Map数据: {rows:,} 行")
        
        data = {
            'WaferID': np.random.choice([f'WAFER_{i:06d}' for i in range(1000000)], rows),
            'DieX': np.random.randint(0, 100, rows),
            'DieY': np.random.randint(0, 100, rows),
            'BinCode': np.random.choice([f'BIN_{i:03d}' for i in range(200)], rows),
        }
        # 添加50个电气参数
        for i in range(50):
            data[f'ElectricalParam{i+1:02d}'] = np.random.normal(1.0, 0.2, rows)
        
        return pd.DataFrame(data)

class DuckDBConnectionPool:
    """DuckDB连接池"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.connections = []
        self._create_connections()
    
    def _create_connections(self):
        """创建连接池"""
        for _ in range(self.max_connections):
            conn = duckdb.connect()
            # 启用多线程和内存池优化
            conn.execute("SET threads TO 10")
            conn.execute("SET memory_limit='16GB'")
            conn.execute("SET enable_progress_bar=false")
            self.connections.append(conn)
    
    def get_connection(self):
        """获取连接"""
        if self.connections:
            return self.connections.pop()
        else:
            # 如果连接池空了，创建新连接
            conn = duckdb.connect()
            conn.execute("SET threads TO 10")
            conn.execute("SET memory_limit='16GB'")
            return conn
    
    def return_connection(self, conn):
        """归还连接"""
        if len(self.connections) < self.max_connections:
            self.connections.append(conn)
        else:
            conn.close()
    
    def close_all(self):
        """关闭所有连接"""
        for conn in self.connections:
            conn.close()
        self.connections.clear()

class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self):
        self.conn_pool = DuckDBConnectionPool()
        self.results = {}
        
    def setup_test_data(self):
        """设置测试数据"""
        data_path = TEST_CONFIG['data_path']
        os.makedirs(data_path, exist_ok=True)
        
        # 检查数据文件是否存在
        base_parquet = os.path.join(data_path, 'base_yield.parquet')
        base_csv = os.path.join(data_path, 'base_yield.csv')
        extended_parquet = os.path.join(data_path, 'extended_yield.parquet')
        extended_csv = os.path.join(data_path, 'extended_yield.csv')
        wafer_parquet = os.path.join(data_path, 'wafer_map.parquet')
        
        if not os.path.exists(base_parquet):
            logger.info("生成测试数据集...")
            base_df = TestDataGenerator.generate_base_yield_data()
            base_df.to_parquet(base_parquet, index=False)
            base_df.head(1000000).to_csv(base_csv, index=False)  # CSV只保存100万行避免过大
            
        if not os.path.exists(extended_parquet):
            extended_df = TestDataGenerator.generate_extended_yield_data()
            extended_df.to_parquet(extended_parquet, index=False)
            extended_df.head(1000000).to_csv(extended_csv, index=False)
            
        if not os.path.exists(wafer_parquet):
            wafer_df = TestDataGenerator.generate_wafer_map_data()
            wafer_df.to_parquet(wafer_parquet, index=False)
    
    def load_data_pandas_duckdb(self, file_path: str, format_type: str = 'parquet') -> pd.DataFrame:
        """使用Pandas+DuckDB加载数据"""
        conn = self.conn_pool.get_connection()
        try:
            if format_type == 'parquet':
                query = f"SELECT * FROM read_parquet('{file_path}')"
            else:  # csv
                query = f"SELECT * FROM read_csv_auto('{file_path}')"
            
            df = conn.execute(query).fetchdf()
            return df
        finally:
            self.conn_pool.return_connection(conn)
    
    def load_data_polars_duckdb(self, file_path: str, format_type: str = 'parquet') -> pl.DataFrame:
        """使用Polars+DuckDB加载数据"""
        conn = self.conn_pool.get_connection()
        try:
            if format_type == 'parquet':
                query = f"SELECT * FROM read_parquet('{file_path}')"
            else:  # csv
                query = f"SELECT * FROM read_csv_auto('{file_path}')"
            
            # 使用Polars Lazy模式
            df_pandas = conn.execute(query).fetchdf()
            df_polars = pl.from_pandas(df_pandas).lazy()
            return df_polars.collect()
        finally:
            self.conn_pool.return_connection(conn)
    
    def test_data_loading(self):
        """测试大规模良率数据加载性能"""
        logger.info("=== 测试1: 大规模良率数据加载性能 ===")
        
        data_path = TEST_CONFIG['data_path']
        test_files = [
            ('base_yield.parquet', 'parquet', 10000000),
            ('base_yield.csv', 'csv', 1000000),
            ('extended_yield.parquet', 'parquet', 5000000),
            ('extended_yield.csv', 'csv', 1000000),
            ('wafer_map.parquet', 'parquet', 2000000)
        ]
        
        results = []
        
        for file_name, format_type, expected_rows in test_files:
            file_path = os.path.join(data_path, file_name)
            
            # 测试Pandas+DuckDB
            with PerformanceMonitor.monitor_resources() as monitor:
                start_time = time.time()
                df_pandas = self.load_data_pandas_duckdb(file_path, format_type)
                pandas_time = time.time() - start_time
                pandas_memory = monitor['memory'][-1] if monitor['memory'] else 0
                
            # 清理内存
            del df_pandas
            gc.collect()
            
            # 测试Polars+DuckDB
            with PerformanceMonitor.monitor_resources() as monitor:
                start_time = time.time()
                df_polars = self.load_data_polars_duckdb(file_path, format_type)
                polars_time = time.time() - start_time
                polars_memory = monitor['memory'][-1] if monitor['memory'] else 0
                
            # 清理内存
            del df_polars
            gc.collect()
            
            results.append({
                'file': file_name,
                'format': format_type,
                'rows': expected_rows,
                'pandas_time': pandas_time,
                'polars_time': polars_time,
                'pandas_memory': pandas_memory,
                'polars_memory': polars_memory
            })
            
            logger.info(f"{file_name}: Pandas={pandas_time:.2f}s, Polars={polars_time:.2f}s")
        
        self.results['data_loading'] = results
        return results
    
    def test_aggregation(self, df_pandas: pd.DataFrame, df_polars: pl.DataFrame):
        """测试多维度聚合统计"""
        logger.info("=== 测试2: 多维度聚合统计 ===")
        
        aggregation_scenarios = [
            (['LotID'], 'Lot级良率统计'),
            (['LotID', 'WaferID'], 'Wafer级良率分布'),
            (['Bin', 'DeviceID'], 'Bin级不良品分析'),
            (['LotID', 'WaferID', 'Bin'], '多维交叉分析')
        ]
        
        results = []
        
        for group_cols, scenario_name in aggregation_scenarios:
            # Pandas+DuckDB聚合
            conn = self.conn_pool.get_connection()
            try:
                # 将DataFrame注册到DuckDB
                conn.register('temp_table', df_pandas)
                
                group_by_clause = ', '.join(group_cols)
                query = f"""
                SELECT 
                    {group_by_clause},
                    COUNT(*) as count,
                    AVG(TestResult) as avg_result,
                    STDDEV(TestResult) as std_result
                FROM temp_table 
                GROUP BY {group_by_clause}
                """
                
                with PerformanceMonitor.monitor_resources() as monitor:
                    start_time = time.time()
                    result_pandas = conn.execute(query).fetchdf()
                    pandas_time = time.time() - start_time
                    
                pandas_throughput = len(df_pandas) / pandas_time if pandas_time > 0 else 0
                
                # 清理结果
                del result_pandas
            finally:
                conn.unregister('temp_table')
                self.conn_pool.return_connection(conn)
            
            # Polars+DuckDB聚合
            conn = self.conn_pool.get_connection()
            try:
                # 将Polars DataFrame转换为Pandas并注册
                df_pandas_for_polars = df_polars.to_pandas()
                conn.register('temp_table', df_pandas_for_polars)
                
                group_by_clause = ', '.join(group_cols)
                query = f"""
                SELECT 
                    {group_by_clause},
                    COUNT(*) as count,
                    AVG(TestResult) as avg_result,
                    STDDEV(TestResult) as std_result
                FROM temp_table 
                GROUP BY {group_by_clause}
                """
                
                with PerformanceMonitor.monitor_resources() as monitor:
                    start_time = time.time()
                    result_polars = conn.execute(query).fetchdf()
                    polars_time = time.time() - start_time
                    
                polars_throughput = len(df_polars) / polars_time if polars_time > 0 else 0
                
                # 清理结果
                del result_polars
            finally:
                conn.unregister('temp_table')
                self.conn_pool.return_connection(conn)
            
            results.append({
                'scenario': scenario_name,
                'group_cols': group_cols,
                'pandas_time': pandas_time,
                'polars_time': polars_time,
                'pandas_throughput': pandas_throughput,
                'polars_throughput': polars_throughput
            })
            
            logger.info(f"{scenario_name}: Pandas={pandas_time:.2f}s, Polars={polars_time:.2f}s")
        
        self.results['aggregation'] = results
        return results
    
    def test_filtering(self, df_pandas: pd.DataFrame, df_polars: pl.DataFrame):
        """测试复杂条件过滤与查询"""
        logger.info("=== 测试3: 复杂条件过滤与查询 ===")
        
        filter_scenarios = [
            ("DeviceID = 'DEV_01'", "单字段等值查询"),
            ("DeviceID = 'DEV_01' AND Bin = 'BIN_001'", "多字段AND查询"),
            ("DeviceID = 'DEV_01' AND TestResult BETWEEN 0.8 AND 1.2", "区间+等值组合"),
            ("DeviceID = 'DEV_01' OR Bin = 'BIN_001'", "多条件OR查询")
        ]
        
        results = []
        
        for filter_condition, scenario_name in filter_scenarios:
            # Pandas+DuckDB过滤
            conn = self.conn_pool.get_connection()
            try:
                conn.register('temp_table', df_pandas)
                
                query = f"SELECT * FROM temp_table WHERE {filter_condition}"
                
                with PerformanceMonitor.monitor_resources() as monitor:
                    start_time = time.time()
                    result_pandas = conn.execute(query).fetchdf()
                    pandas_time = time.time() - start_time
                    pandas_cpu = monitor['cpu'][-1] if monitor['cpu'] else 0
                
                # 清理结果
                del result_pandas
            finally:
                conn.unregister('temp_table')
                self.conn_pool.return_connection(conn)
            
            # Polars+DuckDB过滤
            conn = self.conn_pool.get_connection()
            try:
                df_pandas_for_polars = df_polars.to_pandas()
                conn.register('temp_table', df_pandas_for_polars)
                
                query = f"SELECT * FROM temp_table WHERE {filter_condition}"
                
                with PerformanceMonitor.monitor_resources() as monitor:
                    start_time = time.time()
                    result_polars = conn.execute(query).fetchdf()
                    polars_time = time.time() - start_time
                    polars_cpu = monitor['cpu'][-1] if monitor['cpu'] else 0
                
                # 清理结果
                del result_polars
            finally:
                conn.unregister('temp_table')
                self.conn_pool.return_connection(conn)
            
            results.append({
                'scenario': scenario_name,
                'condition': filter_condition,
                'pandas_time': pandas_time * 1000,  # 转换为毫秒
                'polars_time': polars_time * 1000,
                'pandas_cpu': pandas_cpu,
                'polars_cpu': polars_cpu
            })
            
            logger.info(f"{scenario_name}: Pandas={pandas_time*1000:.1f}ms, Polars={polars_time*1000:.1f}ms")
        
        self.results['filtering'] = results
        return results
    
    def test_wafer_map_operations(self, df_pandas: pd.DataFrame, df_polars: pl.DataFrame):
        """测试Wafer Map类宽表运算"""
        logger.info("=== 测试4: Wafer Map类宽表运算 ===")
        
        # 选择电气参数列
        electrical_cols = [col for col in df_pandas.columns if col.startswith('ElectricalParam')]
        
        operation_scenarios = [
            (5, '基础电气参数计算'),
            (15, '复杂衍生指标'),
            (50, '全参数相关性分析'),
            (20, 'Wafer级汇总统计')
        ]
        
        results = []
        
        for num_params, scenario_name in operation_scenarios:
            selected_cols = electrical_cols[:num_params]
            
            # Pandas+DuckDB宽表运算
            conn = self.conn_pool.get_connection()
            try:
                conn.register('temp_table', df_pandas)
                
                # 构建衍生指标计算
                derived_expressions = []
                for i, col in enumerate(selected_cols):
                    derived_expressions.append(f"AVG({col}) as avg_{col}")
                    if i < 5:  # 前5个参数计算标准差
                        derived_expressions.append(f"STDDEV({col}) as std_{col}")
                
                query = f"SELECT WaferID, {', '.join(derived_expressions)} FROM temp_table GROUP BY WaferID"
                
                with PerformanceMonitor.monitor_resources() as monitor:
                    start_time = time.time()
                    result_pandas = conn.execute(query).fetchdf()
                    pandas_time = time.time() - start_time
                    pandas_memory = monitor['memory'][-1] if monitor['memory'] else 0
                
                # 清理结果
                del result_pandas
            finally:
                conn.unregister('temp_table')
                self.conn_pool.return_connection(conn)
            
            # Polars+DuckDB宽表运算
            conn = self.conn_pool.get_connection()
            try:
                df_pandas_for_polars = df_polars.to_pandas()
                conn.register('temp_table', df_pandas_for_polars)
                
                derived_expressions = []
                for i, col in enumerate(selected_cols):
                    derived_expressions.append(f"AVG({col}) as avg_{col}")
                    if i < 5:
                        derived_expressions.append(f"STDDEV({col}) as std_{col}")
                
                query = f"SELECT WaferID, {', '.join(derived_expressions)} FROM temp_table GROUP BY WaferID"
                
                with PerformanceMonitor.monitor_resources() as monitor:
                    start_time = time.time()
                    result_polars = conn.execute(query).fetchdf()
                    polars_time = time.time() - start_time
                    polars_memory = monitor['memory'][-1] if monitor['memory'] else 0
                
                # 清理结果
                del result_polars
            finally:
                conn.unregister('temp_table')
                self.conn_pool.return_connection(conn)
            
            results.append({
                'scenario': scenario_name,
                'num_params': num_params,
                'pandas_time': pandas_time,
                'polars_time': polars_time,
                'pandas_memory': pandas_memory,
                'polars_memory': polars_memory
            })
            
            logger.info(f"{scenario_name}: Pandas={pandas_time:.2f}s, Polars={polars_time:.2f}s")
        
        self.results['wafer_map'] = results
        return results
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始DFX性能对比测试...")
        
        # 设置测试数据
        self.setup_test_data()
        
        # 测试1: 数据加载
        self.test_data_loading()
        
        # 加载基础数据用于后续测试
        data_path = TEST_CONFIG['data_path']
        base_df_pandas = self.load_data_pandas_duckdb(os.path.join(data_path, 'base_yield.parquet'))
        base_df_polars = self.load_data_polars_duckdb(os.path.join(data_path, 'base_yield.parquet'))
        
        wafer_df_pandas = self.load_data_pandas_duckdb(os.path.join(data_path, 'wafer_map.parquet'))
        wafer_df_polars = self.load_data_polars_duckdb(os.path.join(data_path, 'wafer_map.parquet'))
        
        # 测试2: 聚合统计
        self.test_aggregation(base_df_pandas, base_df_polars)
        
        # 测试3: 过滤查询
        self.test_filtering(base_df_pandas, base_df_polars)
        
        # 测试4: Wafer Map运算
        self.test_wafer_map_operations(wafer_df_pandas, wafer_df_polars)
        
        # TODO: 实现并发性能测试和数据导出测试
        
        logger.info("所有测试完成!")
        return self.results
    
    def generate_report(self):
        """生成测试报告"""
        report_lines = []
        report_lines.append("# 芯片良率工程 DFX 性能对比测试报告")
        report_lines.append("## Pandas+DuckDB vs Polars+DuckDB")
        report_lines.append("")
        
        # 数据加载测试结果
        if 'data_loading' in self.results:
            report_lines.append("### 1. 大规模良率数据加载性能")
            report_lines.append("| 文件 | 格式 | 行数 | Pandas耗时(s) | Polars耗时(s) | Pandas内存(MB) | Polars内存(MB) |")
            report_lines.append("|------|------|------|---------------|---------------|----------------|----------------|")
            
            for result in self.results['data_loading']:
                report_lines.append(f"| {result['file']} | {result['format']} | {result['rows']:,} | {result['pandas_time']:.2f} | {result['polars_time']:.2f} | {result['pandas_memory']:.1f} | {result['polars_memory']:.1f} |")
            report_lines.append("")
        
        # 聚合统计测试结果
        if 'aggregation' in self.results:
            report_lines.append("### 2. 多维度聚合统计")
            report_lines.append("| 场景 | Pandas耗时(s) | Polars耗时(s) | Pandas吞吐量(行/秒) | Polars吞吐量(行/秒) |")
            report_lines.append("|------|---------------|---------------|---------------------|---------------------|")
            
            for result in self.results['aggregation']:
                report_lines.append(f"| {result['scenario']} | {result['pandas_time']:.2f} | {result['polars_time']:.2f} | {result['pandas_throughput']:,.0f} | {result['polars_throughput']:,.0f} |")
            report_lines.append("")
        
        # 过滤查询测试结果
        if 'filtering' in self.results:
            report_lines.append("### 3. 复杂条件过滤与查询")
            report_lines.append("| 场景 | Pandas耗时(ms) | Polars耗时(ms) | Pandas CPU(%) | Polars CPU(%) |")
            report_lines.append("|------|----------------|----------------|---------------|---------------|")
            
            for result in self.results['filtering']:
                report_lines.append(f"| {result['scenario']} | {result['pandas_time']:.1f} | {result['polars_time']:.1f} | {result['pandas_cpu']:.1f} | {result['polars_cpu']:.1f} |")
            report_lines.append("")
        
        # Wafer Map运算测试结果
        if 'wafer_map' in self.results:
            report_lines.append("### 4. Wafer Map类宽表运算")
            report_lines.append("| 场景 | 参数数量 | Pandas耗时(s) | Polars耗时(s) | Pandas内存(MB) | Polars内存(MB) |")
            report_lines.append("|------|----------|---------------|---------------|----------------|----------------|")
            
            for result in self.results['wafer_map']:
                report_lines.append(f"| {result['scenario']} | {result['num_params']} | {result['pandas_time']:.2f} | {result['polars_time']:.2f} | {result['pandas_memory']:.1f} | {result['polars_memory']:.1f} |")
            report_lines.append("")
        
        return "\n".join(report_lines)

def main():
    """主函数"""
    logger.info("初始化DFX性能对比测试...")
    
    # 创建测试套件
    test_suite = PerformanceTestSuite()
    
    try:
        # 运行测试
        results = test_suite.run_all_tests()
        
        # 生成报告
        report = test_suite.generate_report()
        
        # 保存报告
        with open('dfx_performance_comparison_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("测试报告已保存到: dfx_performance_comparison_report.md")
        
        # 打印摘要
        print("\n=== 测试摘要 ===")
        for test_name, test_results in results.items():
            if test_results:
                print(f"{test_name}: {len(test_results)} 个测试用例完成")
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        raise
    finally:
        # 清理资源
        test_suite.conn_pool.close_all()
        gc.collect()

if __name__ == "__main__":
    main()