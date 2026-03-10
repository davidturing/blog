#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际执行SQL查询并展示结果
"""

import sqlite3
import json

def execute_sql_query():
    """执行实际的SQL查询"""
    db_path = "david_agent_memory.db"
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 实际执行SQL查询演示")
    print("=" * 50)
    
    # 查询1: 最近抓取的数据类型统计
    print("\n📝 查询: 最近一周都抓取了哪些类型的数据？")
    sql1 = """
    SELECT signal_type, COUNT(*) as count
    FROM raw_signals 
    WHERE timestamp >= datetime('now', '-7 days')
    GROUP BY signal_type
    ORDER BY count DESC
    """
    
    print(f"⚙️  执行SQL:\n{sql1}")
    cursor.execute(sql1)
    results1 = cursor.fetchall()
    
    print("📊 查询结果:")
    for signal_type, count in results1:
        print(f"   • {signal_type}: {count} 条")
    
    # 查询2: 技术新闻统计  
    print("\n📝 查询: 最近有多少条技术相关的新闻？")
    sql2 = """
    SELECT COUNT(*) as tech_news_count
    FROM raw_signals 
    WHERE signal_type IN ('rss_article', 'tech_news')
    AND timestamp >= datetime('now', '-7 days')
    """
    
    print(f"⚙️  执行SQL:\n{sql2}")
    cursor.execute(sql2)
    results2 = cursor.fetchone()
    
    print(f"📊 查询结果: {results2[0]} 条技术新闻")
    
    conn.close()
    print("\n✅ SQL查询执行完成！")

if __name__ == "__main__":
    execute_sql_query()