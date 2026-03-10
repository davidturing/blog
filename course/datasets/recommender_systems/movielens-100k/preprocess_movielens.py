#!/usr/bin/env python3
"""
预处理MovieLens-100K数据集，转换为标准交互格式
"""
import pandas as pd
import json
import os

def preprocess_movielens():
    print("开始预处理MovieLens-100K数据集...")
    
    # 读取原始数据
    data_path = "ml-100k/u.data"
    df = pd.read_csv(data_path, sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
    print(f"原始评分数据: {len(df)} 条记录")
    
    # 过滤隐式评分（只保留显式评分）
    # MovieLens数据都是显式评分，所以不需要过滤
    
    # 去重
    df = df.drop_duplicates(subset=['user_id', 'item_id'])
    print(f"去重后: {len(df)} 条记录")
    
    # 过滤异常用户/物品
    user_counts = df['user_id'].value_counts()
    item_counts = df['item_id'].value_counts()
    
    valid_users = user_counts[user_counts >= 2].index
    valid_items = item_counts[item_counts >= 2].index
    
    df = df[df['user_id'].isin(valid_users) & df['item_id'].isin(valid_items)]
    print(f"过滤异常用户/物品后: {len(df)} 条记录")
    
    # 创建连续ID映射
    unique_users = sorted(df['user_id'].unique())
    unique_items = sorted(df['item_id'].unique())
    
    user_id_map = {old_id: new_id for new_id, old_id in enumerate(unique_users, 1)}
    item_id_map = {old_id: new_id for new_id, old_id in enumerate(unique_items, 1)}
    
    # 应用映射
    df['user_id'] = df['user_id'].map(user_id_map)
    df['item_id'] = df['item_id'].map(item_id_map)
    
    # 保存CSV格式
    output_dir = "."
    csv_path = os.path.join(output_dir, "interactions.csv")
    df.to_csv(csv_path, index=False)
    print(f"已保存CSV格式: {len(df)} 条交互记录")
    
    # 保存Parquet格式
    parquet_path = os.path.join(output_dir, "interactions.parquet")
    df.to_parquet(parquet_path, index=False)
    print("已保存Parquet格式")
    
    # 保存ID映射文件
    with open(os.path.join(output_dir, "user_id_map.json"), 'w') as f:
        json.dump({str(k): int(v) for k, v in user_id_map.items()}, f)
    
    with open(os.path.join(output_dir, "item_id_map.json"), 'w') as f:
        json.dump({str(k): int(v) for k, v in item_id_map.items()}, f)
    
    print("ID映射文件已保存")
    print("预处理完成!")

if __name__ == "__main__":
    preprocess_movielens()