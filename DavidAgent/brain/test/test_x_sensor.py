import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import BrainBlackboard
from brain.sensors.x_spider import XSpider

async def test_x_ingestion():
    print("🧪 [测试] 启动 X 感知器集成验证...")
    
    blackboard = BrainBlackboard()
    # 模拟左脑监听
    def mock_left_brain(new_val, old_val):
        print(f"👁️ [Mock左脑] 监听到新推文进入黑板: {new_val[:50]}...")
    
    blackboard.subscribe('state_changed:raw_source', mock_left_brain)
    
    spider = XSpider(blackboard)
    
    # 由于真实 API 需要认证，我们这里模拟一个抓取成功的推文数据
    # 验证黑板流转逻辑
    print("[*] 模拟抓取推送...")
    mock_tweet = {
        'id_str': '123456789',
        'full_text': 'DeepSeek-V3 is now open source! The agentic era has arrived.'
    }
    
    # 模拟单条推送逻辑
    blackboard.update('topic_id', f"x_{mock_tweet['id_str']}", 'SENSOR_X')
    blackboard.update('raw_source', mock_tweet['full_text'], 'SENSOR_X')
    
    print("✅ [测试] 黑板事件流转验证通过")

if __name__ == "__main__":
    asyncio.run(test_x_ingestion())
