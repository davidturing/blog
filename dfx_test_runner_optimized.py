#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片良率工程 DFX 性能测试对比 - 优化版
Pandas+DuckDB vs Polars+DuckDB (全量并行优化)
测试环境: Apple M4 / 24GB
"""

import os
import sys
import time
import logging
import warnings
import gc
import concurrent.futures
from contextlib import contextmanager

# 禁用 Pandas 链式赋值警告
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

try:
    import pandas as pd
    import polars as pl
    import duckdb
    import psutil
    from memory_profiler import memory_usage
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as e:
    print(f"缺少必要依赖: {e}")
    sys.exit(1)

# === 🔥 POLARS 全量并行优化配置 ===
# 强制设置 Polars 使用所有 CPU 核心（M4 最多 10 核心）
pl.Config.set_global_string_cache(True)  # 启用全局字符串缓存
pl.Config.set_streaming_chunk_size(100_000)  # 流式处理块大小
os.environ["POLARS_MAX_THREADS"] = "10"  # 强制 Polars 使用 10 线程
os.environ["POLARS_FORCE_ASYNC"] = "1"   # 强制异步执行
os.environ["POLARS_VERBOSE"] = "1"       # 详细日志（可选）

# 初始化 Polars 并行配置
pl.threadpool_size(10)  # 设置线程池大小为 10

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dfx_performance_optimized.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局配置
CONFIG = {
    'data_dir': './dfx_data_optimized',
    'seed': 42,
    'threads': 10, # 针对 M4 优化的并行度
    'chunk_size': 1_000_000,
    'base_rows': 10_000_000,
    'ext_rows': 5_000_000,
    'wafer_rows': 2_000_000
}

# 设定固定随机种子保证可重复性
np.random.seed(CONFIG['seed'])
pl.set_random_seed(CONFIG['seed'])

class Monitor:
    """性能监控器"""
    @staticmethod
    @contextmanager
    def measure():
        process = psutil.Process()
        start_time = time.time()
        start_mem = process.memory_info().rss / (1024 * 1024)
        process.cpu_percent(interval=None) 
        
        metrics = {}
        try:
            yield metrics
        finally:
            end_time = time.time()
            cpu_util = process.cpu_percent(interval=None)
            end_mem = process.memory_info().rss / (1024 * 1024)
            
            metrics['time'] = end_time - start_time
            metrics['cpu'] = cpu_util / psutil.cpu_count()
            metrics['mem_diff'] = max(0, end_mem - start_mem)
            metrics['peak_mem'] = end_mem

class ConnectionPool:
    """DuckDB 线程安全连接池"""
    def __init__(self, size=16):
        self.size = size
        self.pool = []
        for _ in range(size):
            conn = duckdb.connect()
            conn.execute(f"SET threads TO {CONFIG['threads']}")
            conn.execute("SET memory_limit='16GB'")
            self.pool.append(conn)
            
    def get(self):
        return self.pool.pop() if self.pool else duckdb.connect()
        
    def put(self, conn):
        if len(self.pool) < self.size:
            self.pool.append(conn)
        else:
            conn.close()
            
    def close_all(self):
        for c in self.pool:
            c.close()

class DataGenerator:
    """测试数据生成 (分块写入防 OOM)"""
    @staticmethod
    def generate_base(path, rows):
        logger.info(f"生成基础良率数据: {rows} 行 -> {path}")
        chunks = rows // CONFIG['chunk_size']
        for i in range(chunks):
            n = CONFIG['chunk_size']
            df = pd.DataFrame({
                'LotID': np.random.choice([f'LOT_{j:05d}' for j in range(5000)], n),
                'WaferID': np.random.choice([f'W_{j:05d}' for j in range(50000)], n),
                'Bin': np.random.choice([f'BIN_{j:03d}' for j in range(200)], n),
                'DeviceID': np.random.choice([f'DEV_{j:02d}' for j in range(50)], n),
                'XCoord': np.random.randint(0, 1000, n),
                'YCoord': np.random.randint(0, 1000, n),
                'TestResult': np.random.normal(1.0, 0.1, n),
                'Timestamp': pd.date_range('2025-01-01', periods=n, freq='S')
            })
            mode = 'w' if i == 0 else 'a'
            header = True if i == 0 else False
            
            if path.endswith('.csv'):
                df.to_csv(path, mode=mode, header=header, index=False)
            else:
                table = pa.Table.from_pandas(df)
                if i == 0:
                    writer = pq.ParquetWriter(path, table.schema)
                writer.write_table(table)
                if i == chunks - 1:
                    writer.close()

    @staticmethod
    def generate_wafer(path, rows):
        logger.info(f"生成WaferMap数据: {rows} 行 -> {path}")
        df = pd.DataFrame({
            'WaferID': np.random.choice([f'W_{j:05d}' for j in range(50000)], rows),
            'Bin': np.random.choice([f'BIN_{j:03d}' for j in range(200)], rows)
        })
        for j in range(50):
            df[f'Param_{j}'] = np.random.normal(1.0, 0.2, rows)
        df.to_parquet(path, index=False)

class DFXTestOptimized:
    def __init__(self):
        self.pool = ConnectionPool()
        self.res = {'load': [], 'agg': [], 'filter': [], 'wafer': [], 'concurrency': [], 'export': []}
        os.makedirs(CONFIG['data_dir'], exist_ok=True)
        self.base_pq = f"{CONFIG['data_dir']}/base.parquet"
        self.base_csv = f"{CONFIG['data_dir']}/base.csv"
        self.wafer_pq = f"{CONFIG['data_dir']}/wafer.parquet"
        
    def prepare_data(self):
        if not os.path.exists(self.base_pq):
            DataGenerator.generate_base(self.base_pq, CONFIG['base_rows'])
        if not os.path.exists(self.base_csv):
            DataGenerator.generate_base(self.base_csv, 1_000_000)
        if not os.path.exists(self.wafer_pq):
            DataGenerator.generate_wafer(self.wafer_pq, CONFIG['wafer_rows'])

    # === 🚀 优化版本 1: 数据加载 ===
    def test_1_loading_optimized(self):
        logger.info("--- 优化测试1: 大规模数据加载 ---")
        scenarios = [('Parquet (10M)', self.base_pq, 10_000_000), ('CSV (1M)', self.base_csv, 1_000_000)]
        
        for name, path, rows in scenarios:
            # Pandas + DuckDB (保持原样用于对比)
            conn = self.pool.get()
            with Monitor.measure() as m_pd:
                df_pd = conn.execute(f"SELECT * FROM '{path}'").df()
            self.pool.put(conn)
            
            # === 🔥 Polars 原生并行加载 (关键优化!) ===
            with Monitor.measure() as m_pl:
                if path.endswith('.parquet'):
                    # 使用 scan_parquet 进行惰性并行加载
                    df_pl = pl.scan_parquet(path).collect(streaming=True)
                else:
                    # 使用 scan_csv 进行惰性并行加载
                    df_pl = pl.scan_csv(path).collect(streaming=True)
            
            self.res['load'].append({
                '场景': name, 'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                'Pandas峰值(MB)': m_pd['peak_mem'], 'Polars峰值(MB)': m_pl['peak_mem']
            })
            del df_pd, df_pl
            gc.collect()

    # === 🚀 优化版本 2: 多维度聚合 ===
    def test_2_aggregation_optimized(self):
        logger.info("--- 优化测试2: 多维度聚合 ---")
        # === 🔥 Polars 原生聚合 (关键优化!) ===
        # 直接使用 Polars 扫描文件进行聚合，避免通过 DuckDB 中转
        df_pl_lazy = pl.scan_parquet(self.base_pq)
        
        queries = [
            ("LotID", ["LotID"], "Lot级别"),
            ("LotID, WaferID", ["LotID", "WaferID"], "Wafer级别"), 
            ("Bin, DeviceID", ["Bin", "DeviceID"], "Bin+设备")
        ]
        
        for cols_str, cols_list, desc in queries:
            # Pandas + DuckDB (对比基准)
            conn = self.pool.get()
            df_pd = conn.execute(f"SELECT * FROM '{self.base_pq}'").df()
            sql = f"SELECT {cols_str}, COUNT(*), AVG(TestResult), STDDEV(TestResult) FROM tbl GROUP BY {cols_str}"
            conn.register('tbl', df_pd)
            with Monitor.measure() as m_pd:
                _ = conn.execute(sql).df()
            conn.unregister('tbl')
            self.pool.put(conn)
            
            # === 🔥 Polars 原生聚合 (关键优化!) ===
            with Monitor.measure() as m_pl:
                # 使用 Polars 原生表达式进行并行聚合
                result = df_pl_lazy.group_by(cols_list).agg([
                    pl.count(),
                    pl.col("TestResult").mean(),
                    pl.col("TestResult").std()
                ]).collect(streaming=True)
            
            rows = CONFIG['base_rows']
            self.res['agg'].append({
                '场景': desc, 
                'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                'Pandas吞吐(行/s)': rows / m_pd['time'], 'Polars吞吐(行/s)': rows / m_pl['time']
            })
            del result
            gc.collect()

    # === 🚀 优化版本 3: 条件过滤 ===
    def test_3_filtering_optimized(self):
        logger.info("--- 优化测试3: 条件过滤与查询 ---")
        df_pl_lazy = pl.scan_parquet(self.base_pq)
        
        filters = [
            (pl.col("DeviceID") == "DEV_01", "单字段等值"),
            ((pl.col("DeviceID") == "DEV_01") & (pl.col("Bin") == "BIN_001"), "多字段AND"),
            ((pl.col("TestResult").is_between(0.8, 1.2)) & (pl.col("DeviceID") == "DEV_05"), "区间+等值"),
        ]
        
        for filter_expr, desc in filters:
            # Pandas + DuckDB (对比基准)
            conn = self.pool.get()
            df_pd = conn.execute(f"SELECT * FROM '{self.base_pq}'").df()
            cond = str(filter_expr)
            # 转换为 SQL 条件
            if "DEV_01" in desc and "BIN_001" in desc:
                sql_cond = "DeviceID = 'DEV_01' AND Bin = 'BIN_001'"
            elif "DEV_01" in desc:
                sql_cond = "DeviceID = 'DEV_01'"
            else:
                sql_cond = "TestResult BETWEEN 0.8 AND 1.2 AND DeviceID = 'DEV_05'"
            
            sql = f"SELECT * FROM tbl WHERE {sql_cond}"
            conn.register('tbl', df_pd)
            with Monitor.measure() as m_pd:
                _ = conn.execute(sql).df()
            conn.unregister('tbl')
            self.pool.put(conn)
            
            # === 🔥 Polars 原生过滤 (关键优化!) ===
            with Monitor.measure() as m_pl:
                result = df_pl_lazy.filter(filter_expr).collect(streaming=True)
            
            self.res['filter'].append({
                '场景': desc, 
                'Pandas耗时(ms)': m_pd['time']*1000, 'Polars耗时(ms)': m_pl['time']*1000,
                'Pandas_CPU(%)': m_pd['cpu'], 'Polars_CPU(%)': m_pl['cpu']
            })
            del result
            gc.collect()

    # === 🚀 优化版本 4: 宽表运算 ===
    def test_4_wafer_map_optimized(self):
        logger.info("--- 优化测试4: 宽表衍生运算 ---")
        w_pl_lazy = pl.scan_parquet(self.wafer_pq)
        
        scenarios = [5, 15, 50]
        for n in scenarios:
            param_cols = [f"Param_{i}" for i in range(n)]
            
            # Pandas + DuckDB (对比基准)
            conn = self.pool.get()
            w_pd = conn.execute(f"SELECT * FROM '{self.wafer_pq}'").df()
            exprs = ", ".join([f"AVG({c}) as avg_{c}, STDDEV({c}) as std_{c}" for c in param_cols])
            sql = f"SELECT WaferID, {exprs} FROM tbl GROUP BY WaferID"
            conn.register('tbl', w_pd)
            with Monitor.measure() as m_pd:
                _ = conn.execute(sql).df()
            conn.unregister('tbl')
            self.pool.put(conn)
            
            # === 🔥 Polars 原生宽表聚合 (关键优化!) ===
            agg_exprs = []
            for col in param_cols:
                agg_exprs.extend([
                    pl.col(col).mean().alias(f"avg_{col}"),
                    pl.col(col).std().alias(f"std_{col}")
                ])
            
            with Monitor.measure() as m_pl:
                result = w_pl_lazy.group_by("WaferID").agg(agg_exprs).collect(streaming=True)
            
            self.res['wafer'].append({
                '指标数': n*2,
                'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                'Pandas内存(MB)': m_pd['peak_mem'], 'Polars内存(MB)': m_pl['peak_mem']
            })
            del result
            gc.collect()

    # === 🚀 优化版本 5: 多任务并发 ===
    def test_5_concurrency_optimized(self):
        logger.info("--- 优化测试5: 多任务并发性能 ---")
        
        def run_query_optimized(engine):
            if engine == 'pandas':
                conn = self.pool.get()
                df_pd = conn.execute(f"SELECT * FROM '{self.base_pq}'").df()
                start = time.time()
                _ = conn.execute("SELECT LotID, AVG(TestResult) FROM tbl GROUP BY LotID").df()
                conn.unregister('tbl')
                self.pool.put(conn)
                return time.time() - start
            else:
                # === 🔥 Polars 并发优化 (关键优化!) ===
                start = time.time()
                # 每个线程独立扫描文件，避免共享状态
                result = pl.scan_parquet(self.base_pq).group_by("LotID").agg(pl.col("TestResult").mean()).collect(streaming=True)
                return time.time() - start

        for workers in [4, 8, 16]:
            # Pandas
            pd_times = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                start_all = time.time()
                futures = [executor.submit(run_query_optimized, 'pandas') for _ in range(workers * 2)]
                pd_times = [f.result() for f in concurrent.futures.as_completed(futures)]
                pd_total = time.time() - start_all

            # Polars (优化版本)
            pl_times = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                start_all = time.time()
                futures = [executor.submit(run_query_optimized, 'polars') for _ in range(workers * 2)]
                pl_times = [f.result() for f in concurrent.futures.as_completed(futures)]
                pl_total = time.time() - start_all
                
            tasks = workers * 2
            self.res['concurrency'].append({
                '并发数': workers,
                'Pandas延迟(ms)': (sum(pd_times)/len(pd_times))*1000, 
                'Polars延迟(ms)': (sum(pl_times)/len(pl_times))*1000,
                'Pandas_QPS': tasks / pd_total,
                'Polars_QPS': tasks / pl_total,
                'Pandas慢查(>1s)': sum(1 for t in pd_times if t > 1),
                'Polars慢查(>1s)': sum(1 for t in pl_times if t > 1)
            })

    # === 🚀 优化版本 6: 数据导出 ===
    def test_6_export_optimized(self):
        logger.info("--- 优化测试6: 数据导出落盘 ---")
        out_pq = f"{CONFIG['data_dir']}/out_optimized.parquet"
        out_csv = f"{CONFIG['data_dir']}/out_optimized.csv"
        
        # 截取100W行用于导出测试
        export_pd = pd.read_parquet(self.base_pq).head(1_000_000)
        export_pl = pl.scan_parquet(self.base_pq).limit(1_000_000).collect()
        
        formats = [('Parquet', out_pq), ('CSV', out_csv)]
        for fmt, path in formats:
            # Pandas
            with Monitor.measure() as m_pd:
                if fmt == 'Parquet': export_pd.to_parquet(path, engine='pyarrow')
                else: export_pd.to_csv(path, index=False)
            size_mb = os.path.getsize(path) / (1024*1024)
            
            # === 🔥 Polars 原生导出 (关键优化!) ===
            with Monitor.measure() as m_pl:
                if fmt == 'Parquet': 
                    export_pl.write_parquet(path, use_pyarrow=True)
                else: 
                    export_pl.write_csv(path)
                
            self.res['export'].append({
                '格式': fmt,
                'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                '文件大小(MB)': size_mb
            })

    def generate_report(self):
        report = ["# 芯片良率工程 DFX 性能对比测试: Pandas+DuckDB vs Polars+DuckDB (优化版)", ""]
        
        sections = [
            ('load', "1. 大规模良率数据加载性能"),
            ('agg', "2. 多维度聚合统计"),
            ('filter', "3. 复杂条件过滤与查询"),
            ('wafer', "4. Wafer Map类宽表运算"),
            ('concurrency', "5. 多任务并发性能"),
            ('export', "6. 数据导出与落盘性能")
        ]
        
        for key, title in sections:
            report.append(f"## {title}")
            data = self.res[key]
            if not data: continue
            
            headers = list(data[0].keys())
            report.append("| " + " | ".join(headers) + " |")
            report.append("|" + "|".join(["---"] * len(headers)) + "|")
            
            for row in data:
                vals = []
                for v in row.values():
                    if isinstance(v, float):
                        vals.append(f"{v:.2f}")
                    else:
                        vals.append(str(v))
                report.append("| " + " | ".join(vals) + " |")
            report.append("")
            
        with open("dfx_performance_report_optimized.md", "w", encoding='utf-8') as f:
            f.write("\n".join(report))
        logger.info("优化版报告已生成: dfx_performance_report_optimized.md")

if __name__ == "__main__":
    tester = DFXTestOptimized()
    tester.prepare_data()
    tester.test_1_loading_optimized()
    tester.test_2_aggregation_optimized()
    tester.test_3_filtering_optimized()
    tester.test_4_wafer_map_optimized()
    tester.test_5_concurrency_optimized()
    tester.test_6_export_optimized()
    tester.generate_report()
    tester.pool.close_all()
    logger.info("DFX性能测试对比优化任务全部完成。")