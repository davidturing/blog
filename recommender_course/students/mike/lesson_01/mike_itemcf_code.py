#!/usr/bin/env python3
"""
ItemCF Implementation - Mike's Submission
Based on MovieLens-100K dataset
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from collections import defaultdict

class ItemCF:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.item_user_matrix = None
        self.item_similarity = None
        
    def build_item_user_matrix(self):
        """Build item-user rating matrix"""
        self.item_user_matrix = self.data.pivot(
            index='item_id', 
            columns='user_id', 
            values='rating'
        ).fillna(0)
        
    def compute_item_similarity(self):
        """Compute item similarity using Pearson correlation"""
        if self.item_user_matrix is None:
            self.build_item_user_matrix()
            
        n_items = len(self.item_user_matrix)
        self.item_similarity = np.zeros((n_items, n_items))
        
        for i in range(n_items):
            for j in range(i+1, n_items):
                item_i_ratings = self.item_user_matrix.iloc[i].values
                item_j_ratings = self.item_user_matrix.iloc[j].values
                
                # Find co-rated users
                co_rated = (item_i_ratings > 0) & (item_j_ratings > 0)
                
                if np.sum(co_rated) < 2:
                    similarity = 0
                else:
                    try:
                        similarity, _ = pearsonr(
                            item_i_ratings[co_rated], 
                            item_j_ratings[co_rated]
                        )
                        similarity = max(0, similarity)  # Keep only positive correlations
                    except:
                        similarity = 0
                        
                self.item_similarity[i][j] = similarity
                self.item_similarity[j][i] = similarity
                
    def recommend(self, user_id, top_k=10):
        """Recommend top-k items for a given user"""
        if self.item_similarity is None:
            self.compute_item_similarity()
            
        # Get user's rated items
        user_ratings = self.data[self.data['user_id'] == user_id]
        rated_items = user_ratings.set_index('item_id')['rating']
        
        if len(rated_items) == 0:
            return []
            
        # Calculate predicted ratings for unrated items
        predictions = {}
        all_items = set(self.item_user_matrix.index)
        unrated_items = all_items - set(rated_items.index)
        
        for item in unrated_items:
            item_idx = self.item_user_matrix.index.get_loc(item)
            predicted_rating = 0
            similarity_sum = 0
            
            for rated_item, rating in rated_items.items():
                rated_item_idx = self.item_user_matrix.index.get_loc(rated_item)
                similarity = self.item_similarity[item_idx][rated_item_idx]
                
                if similarity > 0:
                    predicted_rating += similarity * rating
                    similarity_sum += similarity
                    
            if similarity_sum > 0:
                predictions[item] = predicted_rating / similarity_sum
                
        # Return top-k recommendations
        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        return sorted_predictions[:top_k]

if __name__ == "__main__":
    # Example usage
    itemcf = ItemCF("/Users/zhaoqinhuang/david_project/course/datasets/recommender_systems/movielens-100k/interactions.csv")
    recommendations = itemcf.recommend(user_id=1, top_k=10)
    print(f"Recommendations for user 1: {recommendations}")