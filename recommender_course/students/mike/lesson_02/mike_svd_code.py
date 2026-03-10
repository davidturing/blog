#!/usr/bin/env python3
"""
SVD Implementation for Matrix Factorization - Mike's Submission
"""

import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
from sklearn.metrics import mean_squared_error, mean_absolute_error

class SVDRecommender:
    def __init__(self, data_path, k=50):
        self.data = pd.read_csv(data_path)
        self.k = k
        self.user_item_matrix = None
        self.user_means = None
        self.predicted_matrix = None
        
    def build_user_item_matrix(self):
        """Build user-item rating matrix with mean normalization"""
        self.user_item_matrix = self.data.pivot(
            index='user_id', 
            columns='item_id', 
            values='rating'
        ).fillna(0)
        
        # Calculate user means for normalization
        self.user_means = np.mean(self.user_item_matrix.values, axis=1)
        
    def fit(self):
        """Fit SVD model"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
            
        # Mean normalize the matrix
        ratings_matrix = self.user_item_matrix.values
        normalized_matrix = ratings_matrix - self.user_means.reshape(-1, 1)
        
        # Perform SVD
        U, sigma, Vt = svds(normalized_matrix, k=self.k)
        sigma = np.diag(sigma)
        
        # Reconstruct the matrix
        predicted_normalized = np.dot(np.dot(U, sigma), Vt)
        self.predicted_matrix = predicted_normalized + self.user_means.reshape(-1, 1)
        
    def recommend(self, user_id, top_k=10):
        """Recommend top-k items for a given user"""
        if self.predicted_matrix is None:
            self.fit()
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_predictions = self.predicted_matrix[user_idx]
        
        # Get already rated items
        user_ratings = self.user_item_matrix.iloc[user_idx]
        rated_items = user_ratings[user_ratings > 0].index
        
        # Filter out already rated items
        item_indices = []
        predictions = []
        for idx, item in enumerate(self.user_item_matrix.columns):
            if item not in rated_items:
                item_indices.append(item)
                predictions.append(user_predictions[idx])
                
        # Sort by prediction score
        recommendations = sorted(zip(item_indices, predictions), key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
        
    def evaluate(self, test_data):
        """Evaluate model performance"""
        test_df = pd.read_csv(test_data)
        predictions = []
        actuals = []
        
        for _, row in test_df.iterrows():
            user_id = row['user_id']
            item_id = row['item_id']
            actual_rating = row['rating']
            
            if user_id in self.user_item_matrix.index and item_id in self.user_item_matrix.columns:
                user_idx = self.user_item_matrix.index.get_loc(user_id)
                item_idx = self.user_item_matrix.columns.get_loc(item_id)
                pred_rating = self.predicted_matrix[user_idx, item_idx]
                
                predictions.append(pred_rating)
                actuals.append(actual_rating)
                
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        mae = mean_absolute_error(actuals, predictions)
        
        return rmse, mae

if __name__ == "__main__":
    svd_rec = SVDRecommender("/Users/zhaoqinhuang/david_project/course/datasets/recommender_systems/movielens-1m/interactions.csv")
    recommendations = svd_rec.recommend(user_id=1, top_k=10)
    print(f"SVD Recommendations for user 1: {recommendations}")