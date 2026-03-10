import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.linear_model import RidgeCV
import statsmodels.api as sm

class DMLCausalEngine:
    """
    Double/Debiased Machine Learning (DML) 因果推断引擎
    用于评估量化因子的纯因果效应（剔除混淆变量影响）
    """
    def __init__(self, n_splits=2):
        self.n_splits = n_splits
        # 使用 Ridge 回归作为轻量级 ML 模型，防止过拟合和共线性
        self.model_y = RidgeCV()
        self.model_d = RidgeCV()

    def estimate_effect(self, df_pandas, y_col, d_col, x_cols):
        # 剔除缺失值
        df_clean = df_pandas[[y_col, d_col] + x_cols].dropna()
        if len(df_clean) < 100:
            return 0.0, 0.0, 1.0  # 样本量不足
            
        X = df_clean[x_cols].values
        Y = df_clean[y_col].values
        D = df_clean[d_col].values
        
        kf = KFold(n_splits=self.n_splits, shuffle=True, random_state=42)
        y_res = np.zeros_like(Y)
        d_res = np.zeros_like(D)
        
        for train_idx, test_idx in kf.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            Y_train, Y_test = Y[train_idx], Y[test_idx]
            D_train, D_test = D[train_idx], D[test_idx]
            
            # 第一阶段：用 ML 模型拟合 Y ~ X、D ~ X
            self.model_y.fit(X_train, Y_train)
            y_res[test_idx] = Y_test - self.model_y.predict(X_test)
            
            self.model_d.fit(X_train, D_train)
            d_res[test_idx] = D_test - self.model_d.predict(X_test)
            
        # 第二阶段：残差回归，得到 因果系数 θ 和 P值
        d_res_with_const = sm.add_constant(d_res)
        ols_model = sm.OLS(y_res, d_res_with_const).fit()
        
        theta = ols_model.params[1]
        std_err = ols_model.bse[1]
        p_value = ols_model.pvalues[1]
        
        return theta, std_err, p_value

    @staticmethod
    def get_significance_stars(p_value):
        if p_value < 0.01:
            return "***"
        elif p_value < 0.05:
            return "**"
        elif p_value < 0.1:
            return "*"
        return ""
