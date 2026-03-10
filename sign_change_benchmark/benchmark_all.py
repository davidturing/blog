import time
import psutil
import os
import gc
import polars as pl
import pandas as pd
import numpy as np
import subprocess

# 1. Polars Python UDF version
def polars_udf_version(df_pl: pl.DataFrame) -> pl.DataFrame:
    def sign_change_state_machine(s: pl.Series) -> pl.Series:
        arr = s.to_numpy()
        group_id = 0
        result = np.zeros(len(arr), dtype=np.int64)
        if len(arr) == 0:
            return pl.Series(result)
            
        last_sign = arr[0] >= 0
        for i in range(len(arr)):
            curr_sign = arr[i] >= 0
            if curr_sign != last_sign:
                group_id += 1
                last_sign = curr_sign
            result[i] = group_id
        return pl.Series(result)

    return df_pl.with_columns(
        pl.col("value").map_batches(
            sign_change_state_machine,
            return_dtype=pl.Int64
        ).alias("group_id")
    )

# 2. Polars Native Expression version
def polars_native_version(df_pl: pl.DataFrame) -> pl.DataFrame:
    return df_pl.with_columns(
        ((pl.col("value") >= 0) != (pl.col("value").shift(1).fill_null(pl.col("value").head(1) >= 0)))
        .cast(pl.Int64).cum_sum().alias("group_id")
    )

def polars_rust_plugin_version(df_pl: pl.DataFrame) -> pl.DataFrame:
    # Need to load the compiled plugin. Let's build it first.
    return df_pl.with_columns(
        pl.col("value").sign_change.compute_sign_change().alias("group_id")
    )

def pandas_bodo_version():
    script_path = os.path.join(os.path.dirname(__file__), 'bodo_bench.py')
    with open(script_path, 'w') as f:
        f.write('''import time
import pandas as pd
import numpy as np
import os
import psutil

try:
    import bodo
    @bodo.jit
    def symbol_switch_cumsum_pandas_bodo(df: pd.DataFrame) -> pd.DataFrame:
        is_non_negative = df['value'] >= 0
        switch_points = is_non_negative != is_non_negative.shift(1).fillna(False)
        # Fix first row condition by doing cumsum and subtracting 1 (or matching initial state)
        group_id = switch_points.cumsum() - 1
        return df.copy().assign(group_id=group_id)

    if __name__ == "__main__":
        np.random.seed(42)
        N = 10_000_000
        data = np.random.randn(N)
        df_pd = pd.DataFrame({"value": data})
        
        # Warmup
        symbol_switch_cumsum_pandas_bodo(df_pd.head(10))
        
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        cpu_times_before = process.cpu_times()
        start_time = time.perf_counter()
        
        res = symbol_switch_cumsum_pandas_bodo(df_pd)
        
        end_time = time.perf_counter()
        cpu_times_after = process.cpu_times()
        mem_after = process.memory_info().rss
        
        wall_time = end_time - start_time
        cpu_time = (cpu_times_after.user - cpu_times_before.user) + (cpu_times_after.system - cpu_times_before.system)
        
        print(f"BODO_TIME:{wall_time}")
        print(f"BODO_MEM:{(process.memory_info().rss) / (1024 * 1024)}")
        print(f"BODO_CPU:{(cpu_time / wall_time) * 100 if wall_time > 0 else 0}")
except Exception as e:
    print(f"Bodo error: {e}")
''')
    
    # Run the script in bodo conda env
    result = subprocess.run(
        ["/Users/zhaoqinhuang/david_project/bodo-test/bin/python3", script_path],
        capture_output=True, text=True
    )
    
    metrics = {"wall_time": float('inf'), "mem_peak_mb": 0, "cpu_efficiency": 0}
    for line in result.stdout.split('\n'):
        if line.startswith('BODO_TIME:'): metrics['wall_time'] = float(line.split(':')[1])
        if line.startswith('BODO_MEM:'): metrics['mem_peak_mb'] = float(line.split(':')[1])
        if line.startswith('BODO_CPU:'): metrics['cpu_efficiency'] = float(line.split(':')[1])
        
    return metrics, None


def measure_performance(func, *args, **kwargs):
    gc.collect()
    process = psutil.Process(os.getpid())
    
    mem_before = process.memory_info().rss
    cpu_times_before = process.cpu_times()
    start_time = time.perf_counter()
    
    result = func(*args, **kwargs)
    
    end_time = time.perf_counter()
    cpu_times_after = process.cpu_times()
    mem_after = process.memory_info().rss
    
    wall_time = end_time - start_time
    cpu_time = (cpu_times_after.user - cpu_times_before.user) + (cpu_times_after.system - cpu_times_before.system)
    
    return {
        "wall_time": wall_time,
        "mem_peak_mb": (process.memory_info().rss) / (1024 * 1024),
        "cpu_efficiency": (cpu_time / wall_time) * 100 if wall_time > 0 else 0
    }, result

if __name__ == "__main__":
    # Prepare Rust plugin
    import sys
    sys.path.insert(0, "/Users/zhaoqinhuang/david_project/sign_change_benchmark/rust_plugin")
    
    import importlib.util
    plugin_spec = importlib.util.find_spec("sign_change")
    plugin_available = plugin_spec is not None
    
    if plugin_available:
        import sign_change
        
        # register namespace
        @pl.api.register_expr_namespace("sign_change")
        class SignChange:
            def __init__(self, expr: pl.Expr):
                self._expr = expr
            
            def compute_sign_change(self):
                return sign_change.compute_sign_change(self._expr)

    print("Generating 10 million rows of data...")
    np.random.seed(42)
    N = 10_000_000
    data = np.random.randn(N)
    
    df_pl = pl.DataFrame({"value": data})
    
    print("Testing Polars Native Expression...")
    metrics_native, res_native = measure_performance(polars_native_version, df_pl)
    print(f"Native: {metrics_native}")
    
    print("Testing Polars Python UDF...")
    metrics_udf, res_udf = measure_performance(polars_udf_version, df_pl)
    print(f"UDF: {metrics_udf}")
    
    if plugin_available:
        print("Testing Polars Rust Plugin...")
        metrics_rust, res_rust = measure_performance(polars_rust_plugin_version, df_pl)
        print(f"Rust: {metrics_rust}")
    else:
        metrics_rust = None
        print("Rust plugin not built/available.")

    print("Testing Pandas Bodo...")
    metrics_bodo, _ = pandas_bodo_version()
    print(f"Bodo: {metrics_bodo}")
    
    # Save the output to a report file
    with open("/Users/zhaoqinhuang/david_project/sign_change_benchmark/report.md", "w") as f:
        f.write("# 符号切换累计值计算 - 性能测试对比报告\\n\\n")
        f.write("## 1. 性能对比表 (1000 万行随机带符号数据)\\n\\n")
        f.write("| 实现版本 | 执行耗时 (秒) | 内存峰值 (MB) | CPU 效率 (%) |\\n")
        f.write("|----------|-------------|-------------|-------------|\\n")
        f.write(f"| Polars 原生表达式 | {metrics_native['wall_time']:.4f} | {metrics_native['mem_peak_mb']:.2f} | {metrics_native['cpu_efficiency']:.2f} |\\n")
        f.write(f"| Polars Python UDF | {metrics_udf['wall_time']:.4f} | {metrics_udf['mem_peak_mb']:.2f} | {metrics_udf['cpu_efficiency']:.2f} |\\n")
        if metrics_rust:
            f.write(f"| Polars Rust 插件 | {metrics_rust['wall_time']:.4f} | {metrics_rust['mem_peak_mb']:.2f} | {metrics_rust['cpu_efficiency']:.2f} |\\n")
        else:
            f.write(f"| Polars Rust 插件 | N/A | N/A | N/A |\\n")
        f.write(f"| Pandas on Bodo | {metrics_bodo['wall_time']:.4f} | {metrics_bodo['mem_peak_mb']:.2f} | {metrics_bodo['cpu_efficiency']:.2f} |\\n")
