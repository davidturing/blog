#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询技术新闻的专用脚本
"""

import sqlite3
import json
from pathlib import Path

def query_tech_news():
    """查询最新的技术新闻"""
    db_path = "DavidAgent/david_agent_memory.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询最新的rss_article和tech_news
    cursor.execute("""
        SELECT signal_type, author_name, raw_text, timestamp
        FROM raw_signals 
        WHERE signal_type IN ('rss_article', 'tech_news')
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print("📭 没有找到技术相关的新闻")
        return
    
    print("📰 最新的技术新闻:")
    print("=" * 50)
    
    for i, (signal_type, author, raw_text, timestamp) in enumerate(results, 1):
        print(f"\n{i}. [{signal_type.upper()}] {author}")
        print(f"   时间: {timestamp}")
        
        # 提取标题和正文
        if "【标题】:" in raw_text:
            parts = raw_text.split("【正文提取】:")
            title_part = parts[0].replace("【标题】:", "").strip()
            content_part = parts[1].strip() if len(parts) > 1 else ""
            
            print(f"   标题: {title_part}")
            print(f"   摘要: {content_part[:200]}...")
        else:
            print(f"   内容: {raw_text[:200]}...")
        
        print("-" * 50)

if __name__ == "__main__":
    query_tech_news()