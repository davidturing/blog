
import asyncio
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.episodic_memory import get_episodic_memory_db

async def verify_phase_20():
    print("🚀 开始 Phase 20 (受控批量采样) 验证测试...")
    
    db = get_episodic_memory_db()
    task_name = "x_batch_crawl"
    
    # 1. 模拟启动任务
    print("📡 1. 模拟启动任务...")
    db.set_task_status(task_name, "running", progress="测试中: 准备开始...", config=json.dumps(["test_user"]))
    status = db.get_task_status(task_name)
    print(f"✅ 初始状态验证: {status['status']} | 进度: {status['progress']}")
    
    # 2. 模拟停止信号
    print("📡 2. 发送停止信号...")
    db.set_task_status(task_name, "stopping", progress="测试中: 正在停止...")
    status = db.get_task_status(task_name)
    print(f"✅ 停止信号验证: {status['status']} | 进度: {status['progress']}")
    
    # 3. 恢复 idle 状态
    db.set_task_status(task_name, "idle", progress="测试结束")
    status = db.get_task_status(task_name)
    print(f"✅ 完成状态验证: {status['status']}")
    
    print("✅ 验证流程结束。")

if __name__ == "__main__":
    asyncio.run(verify_phase_20())
