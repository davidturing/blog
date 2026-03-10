#!/usr/bin/env python3
"""
03_rca_with_duckdb.py: Perform Root Cause Analysis (RCA) using DuckDB for batch-level analysis.
"""

import duckdb
import polars as pl

def analyze_with_duckdb():
    """Use DuckDB to analyze yield by lot and defect type impact."""
    # Connect DuckDB and register Polars LazyFrames
    con = duckdb.connect()
    df_wafer = pl.scan_csv('../data/wm811k.csv')
    con.register('wafer_table', df_wafer)

    print('=== DuckDB Batch-Level Analysis ===')
    
    # Yield by Lot
    lot_yield_query = '''
        SELECT 
            lotName,
            COUNT(*) as total_wafers,
            SUM(CASE WHEN failureType = 'none' THEN 1 ELSE 0 END) as good_wafers,
            AVG(CASE WHEN failureType = 'none' THEN 1.0 ELSE 0.0 END) as yield_rate
        FROM wafer_table
        GROUP BY lotName
        ORDER BY yield_rate DESC
    '''
    lot_yield = con.execute(lot_yield_query).fetchdf()
    
    print('Top 5 High-Yield Lots:')
    print(lot_yield.head(5))
    print('\nBottom 5 Low-Yield Lots:')
    print(lot_yield.tail(5))

    # Defect Type Impact
    defect_impact_query = '''
        SELECT 
            failureType,
            COUNT(*) as count,
            AVG(CASE WHEN failureType = 'none' THEN 1.0 ELSE 0.0 END) as yield_rate
        FROM wafer_table
        GROUP BY failureType
        ORDER BY yield_rate ASC
    '''
    defect_impact = con.execute(defect_impact_query).fetchdf()
    
    print('\nDefect Type Impact on Yield:')
    print(defect_impact)

if __name__ == '__main__':
    analyze_with_duckdb()