#!/usr/bin/env python3
"""
Performance test for symbol switch cumulative sum with larger dataset
"""
import time
import pandas as pd
import numpy as np
import polars as pl
import duckdb

# Test data generation
def generate_test_data(n_rows=1000000, n_symbols=10):
    """Generate test data with specified number of rows and symbols"""
    np.random.seed(42)
    symbols = [f"SYM_{i}" for i in range(n_symbols)]
    df = pd.DataFrame({
        'symbol': np.random.choice(symbols, n_rows),
        'value': np.random.randn(n_rows)
    })
    return df

# Pandas implementation
def test_pandas_cumsum(df):
    start_time = time.time()
    df_pandas = df.copy()
    df_pandas['cumsum_value'] = df_pandas.groupby('symbol')['value'].cumsum()
    end_time = time.time()
    return end_time - start_time, df_pandas.shape[0]

# Polars implementation
def test_polars_cumsum(df):
    start_time = time.time()
    df_pl = pl.from_pandas(df)
    result = df_pl.with_columns([
        pl.col('value').cum_sum().over('symbol').alias('cumsum_value')
    ])
    end_time = time.time()
    return end_time - start_time, result.shape[0]

# DuckDB implementation
def test_duckdb_cumsum(df):
    start_time = time.time()
    con = duckdb.connect()
    # Add row number for ordering
    df_with_id = df.reset_index()
    result = con.execute("""
        SELECT symbol, value,
               SUM(value) OVER (PARTITION BY symbol ORDER BY index) as cumsum_value
        FROM df_with_id
    """).fetchdf()
    con.close()
    end_time = time.time()
    return end_time - start_time, result.shape[0]

# Bodo implementation (placeholder)
def test_bodo_cumsum(df):
    try:
        import bodo
        @bodo.jit
        def bodo_cumsum(df):
            return df.groupby('symbol')['value'].cumsum()
        
        start_time = time.time()
        df_bodo = df.copy()
        df_bodo['cumsum_value'] = bodo_cumsum(df_bodo)
        end_time = time.time()
        return end_time - start_time, df_bodo.shape[0]
    except ImportError:
        return None, None
    except Exception as e:
        print(f"Bodo error: {e}")
        return None, None

def run_performance_tests():
    print("Generating large test data...")
    df = generate_test_data(n_rows=1000000, n_symbols=10)
    print(f"Test data shape: {df.shape}")
    print(f"Unique symbols: {df['symbol'].nunique()}")
    print()
    
    # Test Pandas
    print("Testing Pandas...")
    time_pandas, size_pandas = test_pandas_cumsum(df)
    print(f"Pandas time: {time_pandas:.4f} seconds")
    
    # Test Polars
    print("Testing Polars...")
    time_polars, size_polars = test_polars_cumsum(df)
    print(f"Polars time: {time_polars:.4f} seconds")
    
    # Test DuckDB
    print("Testing DuckDB...")
    time_duckdb, size_duckdb = test_duckdb_cumsum(df)
    print(f"DuckDB time: {time_duckdb:.4f} seconds")
    
    # Test Bodo
    print("Testing Bodo...")
    time_bodo, size_bodo = test_bodo_cumsum(df)
    if time_bodo is not None:
        print(f"Bodo time: {time_bodo:.4f} seconds")
    else:
        print("Bodo not available or failed")
    
    # Summary
    print("\n" + "="*50)
    print("PERFORMANCE COMPARISON (Large Dataset)")
    print("="*50)
    times = {}
    if time_pandas is not None:
        times['Pandas'] = time_pandas
    if time_polars is not None:
        times['Polars'] = time_polars
    if time_duckdb is not None:
        times['DuckDB'] = time_duckdb
    if time_bodo is not None:
        times['Bodo'] = time_bodo
    
    for name, t in times.items():
        print(f"{name:<10}: {t:.4f} seconds")
    
    if times:
        fastest = min(times.items(), key=lambda x: x[1])
        slowest = max(times.items(), key=lambda x: x[1])
        print(f"\nFastest: {fastest[0]}")
        print(f"Slowest: {slowest[0]}")
        if fastest[1] > 0:
            speedup = slowest[1] / fastest[1]
            print(f"Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    run_performance_tests()