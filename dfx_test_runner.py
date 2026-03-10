#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片良率工程 DFX 性能测试对比
Pandas+DuckDB vs Polars+DuckDB
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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dfx_performance.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局配置
CONFIG = {
    'data_dir': './dfx_data',
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
        
        # 简单记录CPU，更精细的内存追踪依赖于外部或采样
        process.cpu_percent(interval=None) 
        
        metrics = {}
        try:
            yield metrics
        finally:
            end_time = time.time()
            cpu_util = process.cpu_percent(interval=None)
            end_mem = process.memory_info().rss / (1024 * 1024)
            
            metrics['time'] = end_time - start_time
            metrics['cpu'] = cpu_util / psutil.cpu_count() # 归一化到整体 CPU %
            metrics['mem_diff'] = max(0, end_mem - start_mem)
            metrics['peak_mem'] = end_mem # 简化处理，真实峰值可通过 memory_profiler
            
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

class DFXTest:
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
            DataGenerator.generate_base(self.base_csv, 1_000_000) # CSV控制在100W行防写爆磁盘
        if not os.path.exists(self.wafer_pq):
            DataGenerator.generate_wafer(self.wafer_pq, CONFIG['wafer_rows'])

    # --- 1. 加载性能 ---
    def test_1_loading(self):
        logger.info("--- 测试1: 大规模数据加载 ---")
        scenarios = [('Parquet (10M)', self.base_pq, 10_000_000), ('CSV (1M)', self.base_csv, 1_000_000)]
        
        for name, path, rows in scenarios:
            # Pandas + DuckDB
            conn = self.pool.get()
            with Monitor.measure() as m_pd:
                df_pd = conn.execute(f"SELECT * FROM '{path}'").df()
            self.pool.put(conn)
            
            # Polars + DuckDB (Lazy)
            conn = self.pool.get()
            with Monitor.measure() as m_pl:
                # Polars 可以通过 scan_parquet / scan_csv 原生 lazy 读，
                # 但按要求需用DuckDB接口读，再转LazyFrame
                # 实际上Polars + DuckDB的最佳集成是通过 Arrow
                arrow_tbl = conn.execute(f"SELECT * FROM '{path}'").arrow()
                df_pl = pl.from_arrow(arrow_tbl)
                if hasattr(df_pl, "lazy"):
                    df_pl = df_pl.lazy().collect()
            self.pool.put(conn)
            
            self.res['load'].append({
                '场景': name, 'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                'Pandas峰值(MB)': m_pd['peak_mem'], 'Polars峰值(MB)': m_pl['peak_mem']
            })
            del df_pd, df_pl, arrow_tbl
            gc.collect()

    # --- 2. 多维度聚合 ---
    def test_2_aggregation(self):
        logger.info("--- 测试2: 多维度聚合 ---")
        # 预加载数据供后续使用
        conn = self.pool.get()
        self.df_pd = conn.execute(f"SELECT * FROM '{self.base_pq}'").df()
        self.df_pl = pl.from_arrow(conn.execute(f"SELECT * FROM '{self.base_pq}'").arrow())
        self.pool.put(conn)
        
        queries = [
            ("LotID", "LotID", "Lot级别"),
            ("LotID, WaferID", "LotID, WaferID", "Wafer级别"),
            ("Bin, DeviceID", "Bin, DeviceID", "Bin+设备")
        ]
        
        for name, cols, desc in queries:
            sql = f"SELECT {cols}, COUNT(*), AVG(TestResult), STDDEV(TestResult) FROM tbl GROUP BY {cols}"
            
            # Pandas
            conn = self.pool.get()
            conn.register('tbl', self.df_pd)
            with Monitor.measure() as m_pd:
                _ = conn.execute(sql).df()
            conn.unregister('tbl')
            self.pool.put(conn)
            
            # Polars
            conn = self.pool.get()
            arrow_tbl = self.df_pl.to_arrow()
            conn.register('tbl', arrow_tbl)
            with Monitor.measure() as m_pl:
                # 返回Arrow再转Polars保持完整链路
                res = conn.execute(sql).arrow()
                _ = pl.from_arrow(res)
            conn.unregister('tbl')
            self.pool.put(conn)
            
            rows = CONFIG['base_rows']
            self.res['agg'].append({
                '场景': desc, 
                'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                'Pandas吞吐(行/s)': rows / m_pd['time'], 'Polars吞吐(行/s)': rows / m_pl['time']
            })

    # --- 3. 条件过滤 ---
    def test_3_filtering(self):
        logger.info("--- 测试3: 条件过滤与查询 ---")
        queries = [
            ("DeviceID = 'DEV_01'", "单字段等值"),
            ("DeviceID = 'DEV_01' AND Bin = 'BIN_001'", "多字段AND"),
            ("TestResult BETWEEN 0.8 AND 1.2 AND DeviceID = 'DEV_05'", "区间+等值"),
        ]
        
        for cond, desc in queries:
            sql = f"SELECT * FROM tbl WHERE {cond}"
            
            # Pandas
            conn = self.pool.get()
            conn.register('tbl', self.df_pd)
            with Monitor.measure() as m_pd:
                _ = conn.execute(sql).df()
            conn.unregister('tbl')
            self.pool.put(conn)
            
            # Polars
            conn = self.pool.get()
            arrow_tbl = self.df_pl.to_arrow()
            conn.register('tbl', arrow_tbl)
            with Monitor.measure() as m_pl:
                res = conn.execute(sql).arrow()
                _ = pl.from_arrow(res)
            conn.unregister('tbl')
            self.pool.put(conn)
            
            self.res['filter'].append({
                '场景': desc, 
                'Pandas耗时(ms)': m_pd['time']*1000, 'Polars耗时(ms)': m_pl['time']*1000,
                'Pandas_CPU(%)': m_pd['cpu'], 'Polars_CPU(%)': m_pl['cpu']
            })

    # --- 4. 宽表运算 ---
    def test_4_wafer_map(self):
        logger.info("--- 测试4: 宽表衍生运算 ---")
        conn = self.pool.get()
        w_pd = conn.execute(f"SELECT * FROM '{self.wafer_pq}'").df()
        w_pl = pl.from_arrow(conn.execute(f"SELECT * FROM '{self.wafer_pq}'").arrow())
        self.pool.put(conn)
        
        scenarios = [5, 15, 50]
        for n in scenarios:
            cols = [f"Param_{i}" for i in range(n)]
            exprs = ", ".join([f"AVG({c}) as avg_{c}, STDDEV({c}) as std_{c}" for c in cols])
            sql = f"SELECT WaferID, {exprs} FROM tbl GROUP BY WaferID"
            
            # Pandas
            conn = self.pool.get()
            conn.register('tbl', w_pd)
            with Monitor.measure() as m_pd:
                _ = conn.execute(sql).df()
            conn.unregister('tbl')
            self.pool.put(conn)
            
            # Polars
            conn = self.pool.get()
            conn.register('tbl', w_pl.to_arrow())
            with Monitor.measure() as m_pl:
                _ = pl.from_arrow(conn.execute(sql).arrow())
            conn.unregister('tbl')
            self.pool.put(conn)
            
            self.res['wafer'].append({
                '指标数': n*2,
                'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                'Pandas内存(MB)': m_pd['peak_mem'], 'Polars内存(MB)': m_pl['peak_mem']
            })
            
        del w_pd, w_pl
        gc.collect()

    # --- 5. 多任务并发 ---
    def test_5_concurrency(self):
        logger.info("--- 测试5: 多任务并发性能 ---")
        
        def run_query(engine):
            conn = self.pool.get()
            try:
                start = time.time()
                if engine == 'pandas':
                    conn.register('tbl', self.df_pd)
                    _ = conn.execute("SELECT LotID, AVG(TestResult) FROM tbl GROUP BY LotID").df()
                else:
                    conn.register('tbl', self.df_pl.to_arrow())
                    _ = pl.from_arrow(conn.execute("SELECT LotID, AVG(TestResult) FROM tbl GROUP BY LotID").arrow())
                conn.unregister('tbl')
                return time.time() - start
            finally:
                self.pool.put(conn)

        for workers in [4, 8, 16]:
            # Pandas
            pd_times = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                start_all = time.time()
                futures = [executor.submit(run_query, 'pandas') for _ in range(workers * 2)]
                pd_times = [f.result() for f in concurrent.futures.as_completed(futures)]
                pd_total = time.time() - start_all

            # Polars
            pl_times = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                start_all = time.time()
                futures = [executor.submit(run_query, 'polars') for _ in range(workers * 2)]
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

    # --- 6. 导出落盘 ---
    def test_6_export(self):
        logger.info("--- 测试6: 数据导出落盘 ---")
        out_pq = f"{CONFIG['data_dir']}/out.parquet"
        out_csv = f"{CONFIG['data_dir']}/out.csv"
        
        # 截取100W行用于导出测试
        export_pd = self.df_pd.head(1_000_000)
        export_pl = self.df_pl.head(1_000_000)
        
        formats = [('Parquet', out_pq), ('CSV', out_csv)]
        for fmt, path in formats:
            # Pandas
            with Monitor.measure() as m_pd:
                if fmt == 'Parquet': export_pd.to_parquet(path, engine='pyarrow')
                else: export_pd.to_csv(path, index=False)
            size_mb = os.path.getsize(path) / (1024*1024)
            
            # Polars
            with Monitor.measure() as m_pl:
                if fmt == 'Parquet': export_pl.write_parquet(path)
                else: export_pl.write_csv(path)
                
            self.res['export'].append({
                '格式': fmt,
                'Pandas耗时(s)': m_pd['time'], 'Polars耗时(s)': m_pl['time'],
                '文件大小(MB)': size_mb
            })

    def generate_report(self):
        report = ["# 芯片良率工程 DFX 性能对比测试: Pandas+DuckDB vs Polars+DuckDB", ""]
        
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
            
        with open("dfx_performance_report.md", "w", encoding='utf-8') as f:
            f.write("\n".join(report))
        logger.info("报告已生成: dfx_performance_report.md")

if __name__ == "__main__":
    tester = DFXTest()
    tester.prepare_data()
    tester.test_1_loading()
    tester.test_2_aggregation()
    tester.test_3_filtering()
    tester.test_4_wafer_map()
    tester.test_5_concurrency()
    tester.test_6_export()
    tester.generate_report()
    tester.pool.close_all()
    logger.info("DFX性能测试对比任务全部完成。")