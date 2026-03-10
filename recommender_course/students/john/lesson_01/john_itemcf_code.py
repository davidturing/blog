#!/usr/bin/env python3
"""
Quick ItemCF Implementation - John's Submission
"""

import pandas as pd
import numpy as np

# Load data
data = pd.read_csv("/Users/zhaoqinhuang/david_project/course/datasets/recommender_systems/movielens-100k/interactions.csv")

def get_item_similarity(item1, item2):
    """Simple correlation-based similarity"""
    item1_data = data[data['item_id'] == item1]
    item2_data = data[data['item_id'] == item2]
    
    # Find users who rated both items
    users1 = set(item1_data['user_id'])
    users2 = set(item2_data['user_id'])
    common_users = users1 & users2
    
    if len(common_users) < 2:
        return 0
    
    # Get ratings from common users
    ratings1 = []
    ratings2 = []
    for user in common_users:
        r1 = item1_data[item1_data['user_id'] == user]['rating'].iloc[0]
        r2 = item2_data[item2_data['user_id'] == user]['rating'].iloc[0]
        ratings1.append(r1)
        ratings2.append(r2)
    
    # Pearson correlation
    if len(ratings1) < 2:
        return 0
        
    corr = np.corrcoef(ratings1, ratings2)[0, 1]
    return max(0, corr) if not np.isnan(corr) else 0

def recommend_items_for_user(target_user, top_k=10):
    """Recommend items based on what similar items the user liked"""
    user_ratings = data[data['user_id'] == target_user]
    user_items = dict(zip(user_ratings['item_id'], user_ratings['rating']))
    
    if len(user_items) == 0:
        return []
    
    # Calculate predictions for all unrated items
    all_items = set(data['item_id'].unique())
    unrated_items = all_items - set(user_items.keys())
    
    predictions = {}
    for unrated_item in unrated_items:
        score = 0
        weight_sum = 0
        
        # Check similarity with each rated item
        for rated_item, rating in user_items.items():
            sim = get_item_similarity(unrated_item, rated_item)
            if sim > 0:
                score += sim * rating
                weight_sum += sim
        
        if weight_sum > 0:
            predictions[unrated_item] = score / weight_sum
    
    # Return top k
    sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    return sorted_preds[:top_k]

# Test
print("Item recommendations for user 1:", recommend_items_for_user(1))