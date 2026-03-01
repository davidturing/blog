
import asyncio
import os
import sys
import hashlib
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from brain.sensors.x_spider import XSpider
from brain.memory.blackboard import get_blackboard
from brain.memory.episodic_memory import get_episodic_memory_db

async def verify_rich_perceptor():
    print("🚀 开始感知层 (Phase 18) 强化验证测试...")
    
    db = get_episodic_memory_db()
    blackboard = get_blackboard()
    spider = XSpider(blackboard=blackboard)
    
    # 账号示例
    test_handle = "kloss_xyz"
    
    print(f"📡 1. 执行第一次抓取 (@{test_handle})...")
    tweets = await spider.fetch_tweets_by_handle(test_handle, count=1)
    
    if not tweets:
        print("❌ 无法获取测试推文，请检查网络或认证。")
        return

    await spider.ingest_to_blackboard(test_handle, count=1)
    
    print("📡 2. 检查数据库记录 (元数据验证)...")
    signals = db.get_recent_signals(limit=1)
    if signals:
        sig = signals[0]
        print(f"✅ 记录发现: {sig['signal_id']}")
        print(f"✅ 作者: {sig['author_name']}")
        print(f"✅ 互动: Likes({sig['likes']}), Retweets({sig['retweets']})")
        print(f"✅ Hash: {sig['content_hash']}")
    
        # 3. 验证去重
        print("📡 3. 执行第二次重复抓取 (去重验证)...")
        # 直接调用入库逻辑，应该被跳过
        await spider.ingest_to_blackboard(test_handle, count=1)
        # 如果逻辑正确，日志中应出现 "跳过重复内容"
        
        print("✅ 验证完成，请检查控制台日志确认去重逻辑。")
    else:
        print("❌ 未能在数据库中找到原始信号记录。")

if __name__ == "__main__":
    asyncio.run(verify_rich_perceptor())
