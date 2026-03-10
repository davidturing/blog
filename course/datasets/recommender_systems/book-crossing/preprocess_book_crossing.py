#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book-Crossing数据集预处理脚本
按照指定要求进行清洗和格式化
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import json
import numpy as np

def preprocess_book_crossing():
    print("开始预处理Book-Crossing数据集...")
    
    # 读取原始评分数据
    ratings_df = pd.read_csv('BX-Book-Ratings.csv', sep=';', encoding='ISO-8859-1')
    print(f"原始评分数据: {len(ratings_df)} 条记录")
    
    # 只保留显式评分（过滤隐式零分数据）
    ratings_df = ratings_df[ratings_df['Book-Rating'] > 0]
    print(f"过滤隐式评分后: {len(ratings_df)} 条记录")
    
    # 按(user_id, item_id)去重
    ratings_df = ratings_df.drop_duplicates(subset=['User-ID', 'ISBN'])
    print(f"去重后: {len(ratings_df)} 条记录")
    
    # 过滤异常用户/物品
    # 用户交互次数 >= 2
    user_counts = ratings_df['User-ID'].value_counts()
    valid_users = user_counts[user_counts >= 2].index
    ratings_df = ratings_df[ratings_df['User-ID'].isin(valid_users)]
    
    # 物品被交互次数 >= 2
    item_counts = ratings_df['ISBN'].value_counts()
    valid_items = item_counts[item_counts >= 2].index
    ratings_df = ratings_df[ratings_df['ISBN'].isin(valid_items)]
    
    print(f"过滤异常用户/物品后: {len(ratings_df)} 条记录")
    
    if len(ratings_df) == 0:
        print("警告: 过滤后没有有效数据，使用原始数据")
        ratings_df = pd.read_csv('BX-Book-Ratings.csv', sep=';', encoding='ISO-8859-1')
        ratings_df = ratings_df[ratings_df['Book-Rating'] > 0]
    
    # 创建连续ID映射
    unique_users = sorted(ratings_df['User-ID'].unique())
    unique_items = sorted(ratings_df['ISBN'].unique())
    
    user_id_map = {int(old_id): int(new_id) for new_id, old_id in enumerate(unique_users, start=1)}
    item_id_map = {old_id: int(new_id) for new_id, old_id in enumerate(unique_items, start=1)}
    
    # 应用ID映射
    ratings_df['user_id'] = ratings_df['User-ID'].map(user_id_map)
    ratings_df['item_id'] = ratings_df['ISBN'].map(item_id_map)
    ratings_df['rating'] = ratings_df['Book-Rating']
    ratings_df['timestamp'] = 0  # 无时间戳统一填0
    
    # 选择输出字段
    output_df = ratings_df[['user_id', 'item_id', 'rating', 'timestamp']].copy()
    
    # 保存CSV格式
    output_df.to_csv('interactions.csv', index=False)
    print(f"已保存CSV格式: {len(output_df)} 条交互记录")
    
    # 保存Parquet格式
    table = pa.Table.from_pandas(output_df)
    pq.write_table(table, 'interactions.parquet')
    print("已保存Parquet格式")
    
    # 保存ID映射
    with open('user_id_map.json', 'w') as f:
        json.dump({str(k): v for k, v in user_id_map.items()}, f)
    
    with open('item_id_map.json', 'w') as f:
        json.dump({str(k): v for k, v in item_id_map.items()}, f)
    
    print("ID映射文件已保存")
    print("预处理完成!")

if __name__ == "__main__":
    preprocess_book_crossing()