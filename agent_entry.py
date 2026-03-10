#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 总入口 - 作为 Steven 与 David 沟通的统一接口
集成四重增强架构：SkillRL + ReasoningBank + Memory Alpha + LanceDB 7层检索
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入四重增强架构模块
from DavidAgent.brain.skill_rl.skill_rl import SkillRL
from DavidAgent.brain.reasoning.reasoning_bank import ReasoningBank  
from DavidAgent.brain.memory.memory_alpha import MemoryAlpha
from DavidAgent.brain.memory.lancedb_7layer_integration import get_lancedb_retriever

class DavidAgentEntry:
    """DavidAgent 总入口类 - Steven 与 David 的沟通桥梁"""
    
    def __init__(self):
        print("🚀 初始化 DavidAgent 总入口...")
        self.skill_rl = SkillRL()
        self.reason_bank = ReasoningBank()
        self.mem_alpha = MemoryAlpha()
        self.lancedb_retriever = get_lancedb_retriever()
        print("✅ DavidAgent 四重增强架构加载完成！")
        
    async def process_query(self, user_query: str) -> str:
        """
        处理用户查询 - 四层优先级执行
        
        Args:
            user_query: 用户输入的查询
            
        Returns:
            str: 处理结果
        """
        print(f"\n🗣 用户查询: {user_query}")
        
        # 1. 最高优先级：技能本能（直接秒回）
        skill_result = self.skill_rl.invoke_skill(user_query)
        if skill_result and skill_result["hit"]:
            response = f"🤖 本能技能响应: {skill_result['answer']}"
            print(response)
            return response
        
        # 2. 推理避坑：查错题本
        lessons = self.reason_bank.match(user_query)
        if lessons:
            lesson = lessons[0]
            if lesson[0] == "failure":
                response = f"⚠️ 历史教训: {lesson[1]['fix']}"
            else:
                response = f"💡 成功经验: {lesson[1]['method']}"
            print(f"🤖 {response}")
            return response
        
        # 3. 智能短期记忆
        mem_results = self.mem_alpha.retrieve(top_k=1)
        if mem_results:
            memory_content = mem_results[0]["content"]
            print(f"🤖 记忆提示: {memory_content}")
        
        # 4. 底层7层检索
        try:
            lancedb_result = await self.lancedb_retriever.retrieve_with_lancedb(user_query)
            if "【无相关历史记忆】" not in lancedb_result:
                print(f"🤖 {lancedb_result}")
                return lancedb_result
            else:
                response = "🔍 未找到相关历史记忆，需要从头开始处理。"
                print(f"🤖 {response}")
                return response
        except Exception as e:
            print(f"⚠️ LanceDB检索失败: {e}")
            response = "🔍 检索系统暂时不可用，需要从头开始处理。"
            print(f"🤖 {response}")
            return response
    
    def learn_from_interaction(self, task: str, result: str, detail: str = ""):
        """从交互中学习 - 更新 ReasoningBank 和 SkillRL"""
        # 更新 ReasoningBank
        self.reason_bank.judge_and_learn(task, result, detail)
        
        # 如果是成功结果，尝试提炼为技能
        if result in ["success", "ok", "done", "完成"]:
            self.skill_rl.log_query(task)
            self.skill_rl.try_learn_skill(task, detail)
    
    def get_system_status(self) -> dict:
        """获取系统状态"""
        return {
            "skill_count": len(self.skill_rl.skills),
            "reasoning_rules": len(self.reason_bank.rules["success"]) + len(self.reason_bank.rules["failure"]),
            "memory_items": len(self.mem_alpha.working),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# 全局实例
_DAVIAGENT_ENTRY_INSTANCE = None

def get_david_agent() -> DavidAgentEntry:
    """获取全局 DavidAgent 实例"""
    global _DAVIAGENT_ENTRY_INSTANCE
    if _DAVIAGENT_ENTRY_INSTANCE is None:
        _DAVIAGENT_ENTRY_INSTANCE = DavidAgentEntry()
    return _DAVIAGENT_ENTRY_INSTANCE

async def main():
    """主函数 - 用于测试"""
    agent = get_david_agent()
    
    # 测试查询
    test_queries = [
        "LanceDB七层检索怎么用",
        "调用 Gemini API",
        "WordPress 发布博客"
    ]
    
    for query in test_queries:
        result = await agent.process_query(query)
        print(f"结果: {result}\n")
    
    # 显示系统状态
    status = agent.get_system_status()
    print(f"系统状态: {json.dumps(status, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())