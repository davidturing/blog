#!/usr/bin/env python3
"""
UserCF Implementation - Mike's Submission
Based on MovieLens-100K dataset
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class UserCF:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.user_item_matrix = None
        self.user_similarity = None
        
    def build_user_item_matrix(self):
        """Build user-item rating matrix"""
        self.user_item_matrix = self.data.pivot(
            index='user_id', 
            columns='item_id', 
            values='rating'
        ).fillna(0)
        
    def compute_user_similarity(self):
        """Compute user similarity using cosine similarity"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
            
        # Convert to numpy array for efficiency
        ratings_matrix = self.user_item_matrix.values
        self.user_similarity = cosine_similarity(ratings_matrix)
        
        # Set diagonal to 0 to avoid self-similarity
        np.fill_diagonal(self.user_similarity, 0)
        
    def recommend(self, user_id, top_k=10):
        """Recommend top-k items for a given user"""
        if self.user_similarity is None:
            self.compute_user_similarity()
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_ratings = self.user_item_matrix.iloc[user_idx]
        
        # Find unrated items
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Calculate predicted ratings
        predictions = {}
        for item in unrated_items:
            item_idx = self.user_item_matrix.columns.get_loc(item)
            rated_users = np.where(self.user_item_matrix.iloc[:, item_idx] > 0)[0]
            
            if len(rated_users) == 0:
                continue
                
            # Weighted average of ratings from similar users
            sim_scores = self.user_similarity[user_idx][rated_users]
            ratings = self.user_item_matrix.iloc[rated_users, item_idx]
            
            if np.sum(sim_scores) == 0:
                predicted_rating = np.mean(ratings)
            else:
                predicted_rating = np.dot(sim_scores, ratings) / np.sum(sim_scores)
                
            predictions[item] = predicted_rating
            
        # Return top-k recommendations
        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        return sorted_predictions[:top_k]

if __name__ == "__main__":
    # Example usage
    usercf = UserCF("/Users/zhaoqinhuang/david_project/course/datasets/recommender_systems/movielens-100k/interactions.csv")
    recommendations = usercf.recommend(user_id=1, top_k=10)
    print(f"Recommendations for user 1: {recommendations}")