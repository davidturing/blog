#!/usr/bin/env python3
"""
04_feature_correlation.py: Analyze correlation between SECOM process features and yield.
"""

import polars as pl

def calculate_feature_correlations():
    """Calculate correlation between SECOM features and the pass/fail label."""
    # Load data
    df_secom_labels = pl.scan_csv('../data/secom.labels', separator=' ', has_header=False).select(pl.col('column_1').alias('label'))
    df_secom_features = pl.scan_csv('../data/secom.data', separator=' ', has_header=False)

    # Combine features and labels
    df_secom_full = pl.concat([df_secom_features, df_secom_labels], how='horizontal')

    # Calculate correlation with yield (label: 1=pass, -1=fail)
    correlations = []
    for col in df_secom_full.collect_schema().names()[:-1]: # Exclude label
        corr = df_secom_full.select(pl.corr(pl.col(col), pl.col('label'))).collect().item()
        correlations.append((col, corr))

    # Sort by absolute correlation
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)
    
    print('=== Top 10 Features Most Correlated with Yield ===')
    for feat, corr in correlations[:10]:
        print(f'{feat}: {corr:.4f}')

if __name__ == '__main__':
    calculate_feature_correlations()