#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整运行DevPulse-Sensor并注入到数据库
"""

import sys
import os
import json
import hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensors.devpulse_sensor import DevPulseSensor
import asyncio

async def main():
    """完整运行DevPulse-Sensor"""
    print("🚀 开始完整运行DevPulse-Sensor...")
    
    # 创建传感器实例（不连接黑板，直接返回数据）
    sensor = DevPulseSensor()
    
    # 获取HN技术帖子
    print("\n1. 抓取Hacker News技术帖子...")
    hn_posts = await sensor.fetch_hacker_news_tech_posts(limit=5)
    print(f"✅ 获取到 {len(hn_posts)} 个HN技术帖子")
    
    # 获取RSS技术文章
    print("\n2. 抓取RSS技术文章...")
    rss_articles = await sensor.fetch_rss_tech_articles(limit_per_feed=2)
    print(f"✅ 获取到 {len(rss_articles)} 篇RSS技术文章")
    
    all_payloads = hn_posts + rss_articles
    print(f"\n📊 总共获取到 {len(all_payloads)} 条技术资讯")
    
    # 手动注入到数据库
    if all_payloads:
        from brain.memory.episodic_memory import get_episodic_memory_db
        db = get_episodic_memory_db()
        
        for payload in all_payloads:
            text_content = payload['core_text']
            if not text_content:
                continue
            
            import hashlib
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            
            # 检查全局去重
            if db.check_duplicate(content_hash):
                print(f"⏭️ 跳过重复内容 (Hash: {content_hash[:8]})")
                continue
            
            signal_id = f"devpulse_{payload['source_id']}_{content_hash[:4]}"
            
            # 构造统一信号格式
            signal_data = {
                'signal_id': signal_id,
                'content_hash': content_hash,
                'handle': payload['original_url'],
                'author_name': payload['author'],
                'timestamp': payload['timestamp'],
                'likes': 0,
                'retweets': 0,
                'raw_text': text_content,
                'raw_json': json.dumps(payload, ensure_ascii=False),
                'signal_type': 'tech_news'
            }
            
            # 保存原始信号
            db.save_raw_signal(signal_data)
            print(f"💾 已保存技术资讯: {signal_id}")
    
    print("\n✅ DevPulse-Sensor完整运行完成！")

if __name__ == "__main__":
    asyncio.run(main())