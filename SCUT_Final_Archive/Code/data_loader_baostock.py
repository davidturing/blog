#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baostock 数据加载模块 - 纯 Baostock 实现，无 Qlib 依赖
支持断点续传、分批落盘、重试机制
"""

import os
import time
import logging
from pathlib import Path
import baostock as bs
import polars as pl
import pandas as pd
from tqdm import tqdm

class BaostockDataLoader:
    """Baostock 数据加载器"""
    
    def __init__(self, data_dir="./data/baostock_raw"):
        self.lg = None
        self.stock_pool = []
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def login(self):
        """登录 Baostock"""
        self.lg = bs.login()
        if self.lg.error_code == '0':
            logging.info("Baostock 登录成功")
            return True
        else:
            logging.error(f"Baostock 登录失败: {self.lg.error_msg}")
            return False
            
    def logout(self):
        """退出 Baostock"""
        if self.lg:
            bs.logout()
            logging.info("Baostock 退出成功")
            
    def get_hs300_stocks(self, date="2024-12-31"): # 最新年份安全点
        """获取沪深300成分股"""
        try:
            rs = bs.query_hs300_stocks(date)
            hs300_stocks = []
            while (rs.error_code == '0') & rs.next():
                hs300_stocks.append(rs.get_row_data()[1])  # 股票代码
            self.stock_pool = hs300_stocks
            logging.info(f"获取沪深300成分股 {len(hs300_stocks)} 只")
            return hs300_stocks
        except Exception as e:
            logging.error(f"获取沪深300成分股失败: {e}")
            return []
            
    def download_stock_data(self, stock_code, start_date, end_date, max_retries=3):
        """下载单只股票数据并落盘"""
        file_path = self.data_dir / f"{stock_code}.parquet"
        if file_path.exists():
            return True # 已存在，跳过
            
        fields = "date,code,open,high,low,close,volume"
        
        for attempt in range(max_retries):
            try:
                rs = bs.query_history_k_data_plus(
                    stock_code, fields,
                    start_date=start_date, end_date=end_date,
                    frequency="d", adjustflag="3"
                )
                
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                    
                if data_list:
                    df = pd.DataFrame(data_list, columns=fields.split(','))
                    pl_df = pl.from_pandas(df)
                    # 数据类型转换
                    pl_df = pl_df.with_columns([
                        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d", strict=False),
                        pl.col("open").cast(pl.Float64, strict=False),
                        pl.col("high").cast(pl.Float64, strict=False),
                        pl.col("low").cast(pl.Float64, strict=False),
                        pl.col("close").cast(pl.Float64, strict=False),
                        pl.col("volume").cast(pl.Float64, strict=False)
                    ])
                    pl_df.write_parquet(file_path)
                return True
            except Exception as e:
                logging.warning(f"下载股票 {stock_code} 失败 (尝试 {attempt+1}/{max_retries}): {e}")
                time.sleep(2)
                
        logging.error(f"下载股票 {stock_code} 最终失败。")
        return False
            
    def download_all_data(self, start_date="2016-01-01", end_date="2024-12-31"):
        """下载全部沪深300数据并合并"""
        if not self.stock_pool:
            self.get_hs300_stocks()
            
        logging.info("开始下载数据并进行分批落盘...")
        for stock_code in tqdm(self.stock_pool, desc="Downloading Stocks"):
            self.download_stock_data(stock_code, start_date, end_date)
                
        logging.info("读取所有落盘的 Parquet 文件并合并...")
        parquet_files = list(self.data_dir.glob("*.parquet"))
        if not parquet_files:
            logging.error("没有找到任何下载的数据文件。")
            return pl.DataFrame()
            
        # 使用 Polars 的 scan_parquet 读取整个目录，并使用 Lazy 模式提升性能
        lazy_dfs = [pl.scan_parquet(str(p)) for p in parquet_files]
        if lazy_dfs:
            combined_df = pl.concat(lazy_dfs).collect()
            return combined_df
        else:
            return pl.DataFrame()
            
    def calculate_future_returns(self, df, periods=5):
        """计算未来N日收益率"""
        if df.is_empty():
            return df
        df_sorted = df.sort(["code", "date"])
        df_with_returns = df_sorted.with_columns([
            pl.col("close").shift(-periods).over("code").alias(f"future_close_{periods}"),
            pl.col("close").alias("current_close")
        ]).with_columns([
            ((pl.col(f"future_close_{periods}") - pl.col("current_close")) / 
             pl.col("current_close")).alias(f"return_{periods}d")
        ]).drop([f"future_close_{periods}", "current_close"])
        
        return df_with_returns
        
    def preprocess_data(self, df):
        """数据预处理：清洗和标准化"""
        if df.is_empty():
            return df
        # 移除缺失值
        df_clean = df.drop_nulls()
        
        # 移除异常值（使用3倍标准差）
        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            mean_val = df_clean[col].mean()
            std_val = df_clean[col].std()
            df_clean = df_clean.filter(
                (pl.col(col) >= mean_val - 3*std_val) & 
                (pl.col(col) <= mean_val + 3*std_val)
            )
            
        # Z-Score 标准化
        for col in numeric_cols:
            df_clean = df_clean.with_columns([
                ((pl.col(col) - pl.col(col).mean()) / pl.col(col).std()).alias(f"{col}_zscore")
            ])
            
        return df_clean

def load_baostock_data():
    """提供给外部系统调用的快捷函数"""
    loader = BaostockDataLoader()
    if loader.login():
        df = loader.download_all_data()
        if not df.is_empty():
            df_with_returns = loader.calculate_future_returns(df)
            df_processed = loader.preprocess_data(df_with_returns)
            loader.logout()
            return df_processed
        loader.logout()
    return pl.DataFrame()

if __name__ == "__main__":
    # 测试数据加载
    logging.basicConfig(level=logging.INFO)
    df_processed = load_baostock_data()
    if not df_processed.is_empty():
        print(f"数据加载完成，总记录数: {df_processed.shape[0]}")
        print(df_processed.head())
