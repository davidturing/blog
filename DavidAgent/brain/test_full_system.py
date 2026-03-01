#!/usr/bin/env python3
"""
全量系统集成验证脚本
测试流程：感知 -> 左脑提取 -> 右脑创作 -> 左脑核查 -> 本地执行 -> 情景记忆保存
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
os.environ['GRPC_DNS_RESOLVER'] = 'native'

# 设置环境
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import get_blackboard
from brain.left_brain.analyzer import LeftBrainAnalyzer
from brain.right_brain.controller import RightBrainController
from brain.executor.local_executor import LocalExecutor

async def verify_system():
    print("🧪 [Test] 启动全量系统集成验证...")
    
    # 1. 初始化黑板
    blackboard = get_blackboard()
    blackboard.clear()
    
    # 2. 初始化组件并关联黑板
    left_brain = LeftBrainAnalyzer(blackboard)
    right_brain = RightBrainController(blackboard)
    local_executor = LocalExecutor(blackboard)
    
    # 3. 模拟外部刺激 (新推文)
    test_tweet = """
    建议在 DavidAgent 根目录下创建一个 'verification_success.txt' 文件，
    内容写入 'Bionic Brain integration test passed!'。
    同时，利用 'ls' 命令确认文件是否已生成。
    """
    
    print(f"[*] 注入测试指令: {test_tweet[:50]}...")
    
    # 开始流程：感知
    blackboard.update('topic_id', 'test_task_e2e_001', 'TEST_SUITE')
    blackboard.update('raw_source', test_tweet, 'TEST_SUITE')
    blackboard.update('workflow_status', 'START', 'TEST_SUITE')
    
    # 手动模拟工作流流转（因为 app.py 是完整封装，这里我们手动步进核对每个环节）
    await asyncio.sleep(1)
    
    # A. 触发左脑提取
    print("\n--- 环节 A: 左脑提取 ---")
    await left_brain.extract_information(test_tweet)
    
    # B. 触发右脑创作 (右脑会自动监听 extracted_graph)
    print("\n--- 环节 B: 等待右脑创作... ---")
    await asyncio.sleep(5) # 给 Qwen 一点时间
    
    # C. 模拟左脑事实核查
    print("\n--- 环节 C: 左脑事实核查 ---")
    draft = await blackboard.read('draft_content')
    if draft:
        await left_brain.fact_check(draft)
    
    # D. 模拟本地执行指令下发
    print("\n--- 环节 D: 本地执行测试 ---")
    command = "touch verification_success.txt && echo 'Bionic Brain integration test passed!' > verification_success.txt && ls verification_success.txt"
    blackboard.update('local_command', command, 'TEST_SUITE')
    blackboard.update('workflow_status', 'LOCAL_EXECUTION', 'TEST_SUITE')
    
    # 等待执行完成
    await asyncio.sleep(3)
    
    # 4. 结果核对
    snapshot = blackboard.get_snapshot()
    print("\n" + "="*50)
    print("🔍 [验证结果报告]")
    print(f"最终工作流状态: {snapshot.get('workflow_status')}")
    print(f"本地执行成功: {snapshot.get('execution_result', {}).get('success')}")
    print(f"STDOUT: {snapshot.get('execution_result', {}).get('stdout')}")
    print("="*50)
    
    if os.path.exists("verification_success.txt"):
        print("🎉 物理文件验证成功！")
        os.remove("verification_success.txt")
    else:
        print("❌ 物理文件丢失。")

if __name__ == "__main__":
    asyncio.run(verify_system())
