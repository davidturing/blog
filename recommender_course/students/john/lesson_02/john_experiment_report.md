# John's Lesson 02 Experiment Report

## Quick SVD Implementation

I implemented a simple SVD-based recommender using numpy's built-in SVD function. It works by:

1. Creating a user-item matrix from the ratings data
2. Applying SVD decomposition 
3. Reconstructing with top-k components
4. Generating recommendations for unrated items

The implementation is straightforward and gives reasonable results. I didn't implement RMSE/MAE evaluation yet, but the recommendations look sensible.

For ALS, I'll try to implement it similarly using alternating optimization between user and item factors.

**Key insight**: Matrix factorization captures latent factors that represent user preferences and item characteristics in a lower-dimensional space.