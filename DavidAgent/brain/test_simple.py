#!/usr/bin/env python3
"""
简单测试脚本 - 验证黑板基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import BrainBlackboard


async def test_blackboard():
    """测试黑板基本功能"""
    print("🧪 测试黑板基本功能...")
    
    blackboard = BrainBlackboard()
    
    # 测试状态更新
    blackboard.update('raw_source', 'test tweet', 'TEST')
    print(f"✅ 状态更新成功: {blackboard.state['raw_source']}")
    
    # 测试状态读取
    snapshot = blackboard.get_snapshot()
    print(f"✅ 状态读取成功: {snapshot['raw_source']}")
    
    # 测试事件监听
    received_data = None
    
    def on_raw_source_change(new_value, old_value):
        nonlocal received_data
        received_data = new_value
        print(f"✅ 事件监听成功: {new_value}")
    
    blackboard.subscribe('state_changed:raw_source', on_raw_source_change)
    
    # 触发事件
    blackboard.update('raw_source', 'new test tweet', 'TEST2')
    
    # 等待事件处理
    await asyncio.sleep(0.1)
    
    if received_data == 'new test tweet':
        print("✅ 黑板事件监听功能正常")
        return True
    else:
        print("❌ 黑板事件监听功能异常")
        return False


async def main():
    success = await test_blackboard()
    if success:
        print("\n🟢 黑板基础功能验证通过！")
        return 0
    else:
        print("\n🔴 黑板基础功能验证失败！")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)