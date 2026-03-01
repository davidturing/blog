
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from brain.sensors.x_spider import XSpider
from brain.memory.blackboard import get_blackboard
from brain.memory.episodic_memory import get_episodic_memory_db

async def test_ingestion():
    print("🚀 开始感知器 (Perceptor) 验证测试...")
    
    blackboard = get_blackboard()
    spider = XSpider(blackboard=blackboard)
    
    # 清理旧数据（可选，但为了验证准确性，我们可以检查当前记录数）
    db = get_episodic_memory_db()
    initial_tasks = db.get_recent_tasks(limit=100)
    print(f"📊 当前数据库中已有记录数: {len(initial_tasks)}")
    
    # 执行批量抓取 (每个账号 1 条)
    # 为了测试速度，我们可以尝试抓取前 3 个账号，或者全部抓取
    # 用户要求抓取 20+ 账号，我们执行全量抓取
    print("🕸️ 正在执行全量批量抓取 (预计 21 个账号)...")
    await spider.batch_ingest(count_per_handle=1)
    
    # 给一点时间让异步保存任务完成
    print("⏳ 等待持久化任务完成...")
    await asyncio.sleep(5)
    
    # 验证数据库记录
    final_tasks = db.get_recent_tasks(limit=100)
    print(f"📊 抓取后数据库总记录数: {len(final_tasks)}")
    
    new_records = len(final_tasks) - len(initial_tasks)
    print(f"✨ 新增摄入记录数: {new_records}")
    
    if new_records > 0:
        print("✅ 验证成功: 感知器已成功将原始推文存入情景记忆。")
        # 打印最新一条记录确认内容
        latest = db.get_task_details(final_tasks[0]['task_id'])
        if latest:
            print(f"📝 最新摄入 ID: {latest['task_id']}")
            print(f"📝 状态: {latest['workflow_status']}")
            print(f"📝 内容预览: {latest['raw_source'][:50]}...")
    else:
        print("❌ 验证失败: 未发现新增记录。")

if __name__ == "__main__":
    asyncio.run(test_ingestion())
