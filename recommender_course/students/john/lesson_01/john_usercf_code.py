#!/usr/bin/env python3
"""
Quick UserCF Implementation - John's Submission
"""

import pandas as pd
import numpy as np

# Load data
data = pd.read_csv("/Users/zhaoqinhuang/david_project/course/datasets/recommender_systems/movielens-100k/interactions.csv")

# Simple user similarity using cosine
def get_user_similarity(user1, user2):
    user1_data = data[data['user_id'] == user1]
    user2_data = data[data['user_id'] == user2]
    
    # Merge on item_id
    merged = pd.merge(user1_data, user2_data, on='item_id', suffixes=('_1', '_2'))
    
    if len(merged) == 0:
        return 0
    
    ratings1 = merged['rating_1'].values
    ratings2 = merged['rating_2'].values
    
    # Cosine similarity
    dot_product = np.dot(ratings1, ratings2)
    norm1 = np.linalg.norm(ratings1)
    norm2 = np.linalg.norm(ratings2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
        
    return dot_product / (norm1 * norm2)

def recommend_for_user(target_user, top_k=10):
    # Get all users
    all_users = data['user_id'].unique()
    
    # Calculate similarities
    similarities = []
    for user in all_users:
        if user != target_user:
            sim = get_user_similarity(target_user, user)
            if sim > 0.1:  # Only consider similar users
                similarities.append((user, sim))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get recommendations from top similar users
    recommendations = {}
    target_items = set(data[data['user_id'] == target_user]['item_id'])
    
    for similar_user, sim_score in similarities[:5]:  # Top 5 similar users
        similar_user_items = data[data['user_id'] == similar_user]
        for _, row in similar_user_items.iterrows():
            item = row['item_id']
            rating = row['rating']
            if item not in target_items:  # Don't recommend already rated items
                if item not in recommendations:
                    recommendations[item] = 0
                recommendations[item] += sim_score * rating
    
    # Sort and return top k
    sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return sorted_recs[:top_k]

# Test
print("Recommendations for user 1:", recommend_for_user(1))