import time
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
        # Fix first row condition
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
