#!/usr/bin/env python3
"""
01_data_loading.py: Load and perform initial exploration of semiconductor datasets.
"""

import polars as pl

def load_wafer_data():
    """Load the WM-811K wafer defect dataset."""
    df = pl.scan_csv('data/wm811k.csv')
    print('=== WaferMap Schema ===')
    print(df.collect_schema())
    print('\n=== Sample Records ===')
    print(df.head(3).collect())
    return df

def load_secom_data():
    """Load the SECOM manufacturing process dataset."""
    df = pl.scan_csv('data/secom.data', separator=' ', has_header=False)
    print('=== SECOM Schema ===')
    print(df.collect_schema())
    print('\n=== Sample Records ===')
    print(df.head(3).collect())
    return df

if __name__ == '__main__':
    load_wafer_data()
    load_secom_data()