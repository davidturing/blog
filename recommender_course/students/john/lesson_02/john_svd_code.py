#!/usr/bin/env python3
"""
Quick SVD Implementation - John's Submission
"""

import pandas as pd
import numpy as np

# Simple SVD using numpy
def quick_svd_recommend(data_path, user_id, k=10):
    # Load data
    data = pd.read_csv(data_path)
    
    # Create user-item matrix
    matrix = data.pivot(index='user_id', columns='item_id', values='rating').fillna(0)
    
    # Simple SVD
    U, s, Vt = np.linalg.svd(matrix.values, full_matrices=False)
    
    # Reconstruct with top k components
    k = min(k, len(s))
    reconstructed = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
    
    # Get recommendations for user
    user_idx = matrix.index.get_loc(user_id)
    user_preds = reconstructed[user_idx]
    
    # Filter out already rated items
    user_ratings = matrix.iloc[user_idx]
    unrated_items = user_ratings[user_ratings == 0].index
    
    recommendations = []
    for item in unrated_items:
        item_idx = matrix.columns.get_loc(item)
        recommendations.append((item, user_preds[item_idx]))
    
    return sorted(recommendations, key=lambda x: x[1], reverse=True)[:10]

# Test
print("SVD recommendations:", quick_svd_recommend("/Users/zhaoqinhuang/david_project/course/datasets/recommender_systems/movielens-1m/interactions.csv", 1))