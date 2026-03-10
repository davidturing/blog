#!/usr/bin/env python3
"""
02_eda.py: Perform Exploratory Data Analysis (EDA) on semiconductor datasets.
"""

import polars as pl

def wafer_eda(df_wafer):
    """Perform EDA on the WaferMap dataset."""
    print('=== WaferMap Dataset EDA ===')
    total_wafers = df_wafer.select(pl.count()).collect().item()
    unique_lots = df_wafer.select(pl.col("lotName").n_unique()).collect().item()
    
    print(f'Total wafers: {total_wafers}')
    print(f'Unique lots: {unique_lots}')
    
    print('\nYield distribution by failure type:')
    yield_stats = (
        df_wafer
        .group_by('failureType')
        .agg(pl.count())
        .sort('count', descending=True)
        .collect()
    )
    print(yield_stats)

def secom_eda(df_secom):
    """Perform EDA on the SECOM dataset."""
    print('\n=== SECOM Dataset EDA ===')
    total_records = df_secom.select(pl.count()).collect().item()
    num_features = len(df_secom.collect_schema())
    
    print(f'Total records: {total_records}')
    print(f'Number of features: {num_features}')
    
    print('\nMissing value counts per feature (SECOM uses -9999 for missing):')
    missing_count = df_secom.select([
        pl.col(c).eq(-9999).sum() for c in df_secom.collect_schema().names()
    ]).collect()
    print(missing_count.transpose(include_header=True))

if __name__ == '__main__':
    df_wafer = pl.scan_csv('../data/wm811k.csv')
    df_secom = pl.scan_csv('../data/secom.data', separator=' ', has_header=False)
    
    wafer_eda(df_wafer)
    secom_eda(df_secom)