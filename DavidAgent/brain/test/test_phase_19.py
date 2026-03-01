
import asyncio
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from brain.sensors.x_spider import XSpider
from brain.memory.blackboard import get_blackboard
from brain.memory.episodic_memory import get_episodic_memory_db

async def verify_phase_19():
    print("🚀 开始 Phase 19 (原创过滤 & 文章采集) 验证测试...")
    
    db = get_episodic_memory_db()
    blackboard = get_blackboard()
    spider = XSpider(blackboard=blackboard)
    
    # 测试 1: 验证回复过滤 (Reply Filtering)
    # 我们找一个已知的回复推文或者模拟
    test_handle = "kloss_xyz"
    print(f"📡 1. 验证回复过滤 (@{test_handle})...")
    # 抓取最近 5 条，通常会包含回复
    await spider.ingest_to_blackboard(test_handle, count=5)
    
    # 测试 2: 验证文章采集 (Article Extraction)
    target_id = "2022101005064974600"
    print(f"📡 2. 验证文章采集 (Target ID: {target_id})...")
    
    # 直接通过 ingest 接口测试特定 ID 摄入
    await spider.ingest_to_blackboard("kloss_xyz", tweet_ids=[target_id])
    
    # 我们通过 fetch_tweet_by_id 拿到的数据来展示验证
    tweets = await spider.fetch_tweet_by_id(target_id)
    if tweets:
        tweet = tweets[0]
        raw_data = tweet.get('_raw', tweet)
        note_tweet = raw_data.get('note_tweet', {})
        note_text = note_tweet.get('note_tweet_results', {}).get('result', {}).get('text')
        text = note_text or tweet.get('text') or raw_data.get('legacy', {}).get('full_text', "")
        is_article = bool(note_tweet or len(text) > 280)
        print(f"✅ 识别结果: 类型={'Article' if is_article else 'Post'}, 字符数={len(text)}")
    else:
        print("❌ 无法通过 ID 抓取该文章。")
    
    print("📡 3. 检查数据库记录...")
    signals = db.get_recent_signals(limit=10)
    for sig in signals:
        type_str = sig.get('signal_type', 'unknown')
        print(f"✅ ID: {sig['signal_id']} | 类型: {type_str} | 字符数: {len(sig['raw_text'])}")
        
    print("✅ 验证流程结束。")

if __name__ == "__main__":
    asyncio.run(verify_phase_19())
