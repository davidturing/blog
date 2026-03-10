#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建DavidAgent的完整测试数据集
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta

def create_test_dataset():
    """创建完整的测试数据集"""
    db_path = "david_agent_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建测试数据
    test_data = [
        # GitHub Trending 数据
        {
            'signal_id': 'gh_trending_20260222_001',
            'content_hash': hashlib.md5(b'langchain v0.2.0 released').hexdigest(),
            'handle': 'github_trending',
            'author_name': 'GitHub',
            'timestamp': '2026-02-22T10:00:00Z',
            'likes': 0,
            'retweets': 0,
            'raw_text': '【标题】: LangChain v0.2.0 Released\n【正文提取】: Major performance improvements and new agent tools',
            'raw_json': json.dumps({'tokens_used': 1250, 'repos_processed': 50}),
            'signal_type': 'github_repo'
        },
        # Hacker News 技术新闻
        {
            'signal_id': 'hn_39281720',
            'content_hash': hashlib.md5(b'AI Coding Assistant Comparison').hexdigest(),
            'handle': 'hacker_news',
            'author_name': 'tech_writer',
            'timestamp': '2026-02-22T09:30:00Z',
            'likes': 156,
            'retweets': 0,
            'raw_text': '【标题】: Comprehensive Comparison of AI Coding Assistants in 2026\n【正文提取】: Cursor vs GitHub Copilot vs CodeWhisperer - detailed benchmark results',
            'raw_json': json.dumps({'url': 'https://example.com/ai-coding-comparison'}),
            'signal_type': 'tech_news'
        },
        # RSS 技术博客
        {
            'signal_id': 'rss_hf_blog_001',
            'content_hash': hashlib.md5(b'GGML joins HuggingFace').hexdigest(),
            'handle': 'huggingface_blog',
            'author_name': 'HuggingFace Team',
            'timestamp': '2026-02-22T08:15:00Z',
            'likes': 0,
            'retweets': 0,
            'raw_text': '【标题】: GGML and llama.cpp join HF to ensure the long-term progress of Local AI\n【正文提取】: This integration brings local AI inference to the next level',
            'raw_json': json.dumps({'feed_url': 'https://huggingface.co/blog/feed.xml'}),
            'signal_type': 'rss_article'
        },
        # Twitter 技术讨论
        {
            'signal_id': 'x_1760123456789012345',
            'content_hash': hashlib.md5(b'Qwen3-Coder-Plus SOTA').hexdigest(),
            'handle': '@AI_Researcher',
            'author_name': 'AI_Researcher',
            'timestamp': '2026-02-22T07:00:00Z',
            'likes': 1250,
            'retweets': 340,
            'raw_text': 'Just released Qwen3-Coder-Plus! This new model achieves SOTA on HumanEval with 85.2% pass@1.',
            'raw_json': json.dumps({'hashtags': ['AI', 'CodeGeneration', 'Qwen']}),
            'signal_type': 'tweet'
        }
    ]
    
    # 插入测试数据
    for data in test_data:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO raw_signals 
                (signal_id, content_hash, handle, author_name, timestamp, likes, retweets, raw_text, raw_json, signal_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['signal_id'], data['content_hash'], data['handle'], data['author_name'],
                data['timestamp'], data['likes'], data['retweets'], data['raw_text'],
                data['raw_json'], data['signal_type']
            ))
            print(f"✅ 插入测试数据: {data['signal_id']}")
        except Exception as e:
            print(f"❌ 插入失败: {e}")
    
    # 创建对应的trace_logs数据用于运维查询测试
    trace_data = [
        ('gh_trending_task_1', '2026-02-22T10:00:00Z', 'SUCCESS', '{"tokens_used": 1250, "repos_processed": 50}'),
        ('gh_trending_task_2', '2026-02-22T11:00:00Z', 'ERROR', '{"error": "rate_limit_exceeded"}'),
        ('devpulse_task_1', '2026-02-22T09:30:00Z', 'SUCCESS', '{"tokens_used": 890, "articles_processed": 3}'),
        ('x_spider_task_1', '2026-02-22T07:00:00Z', 'SUCCESS', '{"tokens_used": 450, "tweets_processed": 10}')
    ]
    
    for task_id, timestamp, status, source in trace_data:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO trace_logs 
                (task_id, timestamp, workflow_status, raw_source)
                VALUES (?, ?, ?, ?)
            """, (task_id, timestamp, status, source))
            print(f"✅ 插入trace数据: {task_id}")
        except Exception as e:
            print(f"❌ 插入trace失败: {e}")
    
    conn.commit()
    conn.close()
    print("\n✅ 测试数据集创建完成！")

if __name__ == "__main__":
    create_test_dataset()