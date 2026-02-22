#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Agent 使用示例
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_agent.data_agent import DataAgent

async def main():
    """主函数示例"""
    
    # 初始化Data Agent
    data_agent = DataAgent(
        db_path="./david_agent_memory.db",
        pageindex_dir="./skills/self-learning-agent/pageindex/knowledge"
    )
    
    print("🚀 Data Agent 测试")
    print("=" * 50)
    
    # 测试运维查询
    print("\n1. 测试运维查询 (Operational Query)...")
    try:
        operational_query = "过去一周，我们抓取 GitHub Trending 耗费了多少 Token？"
        result = await data_agent.process_human_query(operational_query)
        print(f"✅ 运维查询结果:\n{result}")
    except Exception as e:
        print(f"❌ 运维查询失败: {e}")
    
    # 测试知识查询
    print("\n2. 测试知识查询 (Knowledge Query)...")
    try:
        knowledge_query = "根据我们最近两周抓取的资料，业界现在对 Node.js 跑大模型底层的态度是什么？"
        result = await data_agent.process_human_query(knowledge_query)
        print(f"✅ 知识查询结果:\n{result}")
    except Exception as e:
        print(f"❌ 知识查询失败: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Data Agent 测试完成！")

if __name__ == "__main__":
    asyncio.run(main())