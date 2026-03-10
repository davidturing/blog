#!/usr/bin/env python3
"""
Performance test for symbol switch cumsum implementations
"""

import time
import pandas as pd
import numpy as np
import polars as pl
import duckdb
import tempfile
import os

# Generate test data
def generate_test_data(n_rows=1000000):
    """Generate test data with symbol switches"""
    np.random.seed(42)
    symbols = np.random.choice(['A', 'B', 'C', 'D', 'E'], n_rows)
    values = np.random.randn(n_rows)
    
    # Create DataFrame
    df = pd.DataFrame({
        'symbol': symbols,
        'value': values
    })
    
    return df

def test_pandas_cumsum(df):
    """Test pandas implementation"""
    start_time = time.time()
    result = df.groupby('symbol')['value'].cumsum()
    end_time = time.time()
    return end_time - start_time, len(result)

def test_polars_cumsum(df):
    """Test polars implementation"""
    start_time = time.time()
    df_pl = pl.from_pandas(df)
    result = df_pl.with_columns(
        pl.col('value').cum_sum().over('symbol').alias('cumsum_value')
    )
    end_time = time.time()
    return end_time - start_time, len(result)

def test_duckdb_cumsum(df):
    """Test duckdb implementation"""
    start_time = time.time()
    con = duckdb.connect()
    # Add row number first
    df_with_rowid = con.execute("""
        SELECT *, ROW_NUMBER() OVER () as rowid FROM df
    """).fetchdf()
    con.register('df_with_rowid', df_with_rowid)
    result = con.execute("""
        SELECT symbol, value, 
               SUM(value) OVER (PARTITION BY symbol ORDER BY rowid) as cumsum_value
        FROM df_with_rowid
    """).fetchdf()
    con.close()
    end_time = time.time()
    return end_time - start_time, len(result)

def test_bodo_cumsum(df):
    """Test bodo implementation (if available)"""
    try:
        import bodo
        
        @bodo.jit
        def bodo_cumsum_impl(symbols, values):
            # This is a simplified version - actual Bodo implementation would be more complex
            df = pd.DataFrame({'symbol': symbols, 'value': values})
            result = df.groupby('symbol')['value'].cumsum()
            return result.values
        
        start_time = time.time()
        result = bodo_cumsum_impl(df['symbol'].values, df['value'].values)
        end_time = time.time()
        return end_time - start_time, len(result)
    except ImportError:
        print("Bodo not available")
        return None, 0
    except Exception as e:
        print(f"Bodo error: {e}")
        return None, 0

def run_performance_tests():
    """Run all performance tests"""
    print("Generating test data...")
    df = generate_test_data(100000)  # Smaller dataset for initial testing
    
    print(f"Test data shape: {df.shape}")
    print(f"Unique symbols: {df['symbol'].nunique()}")
    
    results = {}
    
    # Test Pandas
    print("\nTesting Pandas...")
    time_pandas, size_pandas = test_pandas_cumsum(df.copy())
    results['Pandas'] = time_pandas
    print(f"Pandas time: {time_pandas:.4f} seconds")
    
    # Test Polars
    print("\nTesting Polars...")
    time_polars, size_polars = test_polars_cumsum(df.copy())
    results['Polars'] = time_polars
    print(f"Polars time: {time_polars:.4f} seconds")
    
    # Test DuckDB
    print("\nTesting DuckDB...")
    time_duckdb, size_duckdb = test_duckdb_cumsum(df.copy())
    results['DuckDB'] = time_duckdb
    print(f"DuckDB time: {time_duckdb:.4f} seconds")
    
    # Test Bodo (if available)
    print("\nTesting Bodo...")
    time_bodo, size_bodo = test_bodo_cumsum(df.copy())
    if time_bodo is not None:
        results['Bodo'] = time_bodo
        print(f"Bodo time: {time_bodo:.4f} seconds")
    else:
        print("Bodo not available or failed")
    
    # Print comparison
    print("\n" + "="*50)
    print("PERFORMANCE COMPARISON")
    print("="*50)
    for method, time_taken in results.items():
        print(f"{method:10}: {time_taken:.4f} seconds")
    
    if len(results) > 1:
        fastest = min(results, key=results.get)
        slowest = max(results, key=results.get)
        speedup = results[slowest] / results[fastest]
        print(f"\nFastest: {fastest}")
        print(f"Slowest: {slowest}")
        print(f"Speedup: {speedup:.2f}x")
    
    return results

if __name__ == "__main__":
    run_performance_tests()