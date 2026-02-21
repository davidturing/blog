#!/usr/bin/env python3
"""
ag (antigravity) 引擎主程序 - 史诗级双脑多智能体闭环
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import BrainBlackboard
from brain.left_brain.analyzer import LeftBrainAnalyzer  
from brain.right_brain.controller import RightBrainController
from brain.executor.wordpress_executor import WordPressExecutor
from brain.executor.local_executor import LocalExecutor


class AGEngine:
    """ag (antigravity) 引擎主控制器"""
    
    def __init__(self):
        # 1. 初始化虚拟胼胝体（共享内存总线）
        self.blackboard = BrainBlackboard()
        
        # 2. 唤醒所有智能体与器官，它们将自动挂载到黑板上待命
        self.left_brain = LeftBrainAnalyzer(self.blackboard)      # 负责提取与核查
        self.right_brain = RightBrainController(self.blackboard)  # 负责创意与编码
        self.motor_cortex = WordPressExecutor(self.blackboard)    # 负责物理输出
        self.local_nerve = LocalExecutor(self.blackboard)         # 负责本地执行
        
        # 3. [可选] 监听全局状态，做一个漂亮的控制台Dashboard
        self.blackboard.subscribe_global(self._on_global_state_update)
        
    async def _on_global_state_update(self, snapshot: dict):
        """全局状态更新回调"""
        print(f"\n🚥 [系统状态大盘] 当前阶段: {snapshot.get('workflow_status', 'UNKNOWN')}")
        
    async def process_tweet(self, tweet_content: str):
        """处理单条推文 - 触发多米诺骨牌效应"""
        print("\n📡 [感知器] 捕获到外部高价值信息，系统开始运转...\n")
        self.blackboard.update('raw_source', tweet_content, 'SYSTEM_SPIDER')
        
    def get_status(self):
        """获取当前状态"""
        return self.blackboard.get_snapshot()
        
    async def wait_for_completion(self, timeout_seconds: int = 300):
        """等待处理完成（用于测试）"""
        start_time = asyncio.get_event_loop().time()
        while True:
            status = await self.blackboard.read('workflow_status')
            if status in ['PUBLISHED', 'ERROR']:
                break
            if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                raise TimeoutError("处理超时")
            await asyncio.sleep(1)


async def main():
    """启动ag引擎"""
    print("=" * 50)
    print("🌌 ag (antigravity) 双脑多智能体引擎启动中...")
    print("=" * 50)
    
    # 初始化引擎
    engine = AGEngine()
    
    # 注入第一口"草料"，触发多米诺骨牌！
    # 在真实生产环境中，这部分会被替换为爬虫监听Twitter API、RSS订阅源等
    new_x_post = """
今天深入研究了一下 OpenClaw 这个 Multi-Agent 框架。它底层是基于 Node.js 的，
非常适合做 I/O 密集型任务。我打算把通义千问（qwen3-coder-plus）接入进去作为主控大脑，
然后把 Gemini 2.5 Pro 挂载为专门处理多模态和图谱提取的外部 Tool。
相比于传统的 LangChain，OpenClaw 的事件总线机制更优雅。
"""
    
    # 这行代码执行后，主线程就可以去喝咖啡了，剩下的全靠事件驱动自动完成：
    # raw_source 更新 -> 左脑提取 -> 图谱落盘 -> 右脑写草稿 -> 左脑核查 -> 执行器发布
    await engine.process_tweet(new_x_post)
    
    # 等待处理完成（实际应用中应该用事件监听而不是等待）
    try:
        await engine.wait_for_completion(timeout_seconds=300)
        final_status = await engine.blackboard.read('workflow_status')
        print(f"\n🏁 [处理完成] 最终状态: {final_status}")
        
        if final_status == 'PUBLISHED':
            print("✅ ag引擎成功完成完整生命周期！")
        else:
            print("⚠️  处理过程中遇到问题，请检查日志。")
            
    except TimeoutError:
        print("⏰ 处理超时，请检查各组件是否正常工作。")


if __name__ == "__main__":
    asyncio.run(main())