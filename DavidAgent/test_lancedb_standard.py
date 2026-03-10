#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LanceDB 7层混合检索标准实现
"""

import os
import sys
import asyncio

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from brain.memory.hippocampus import LongTermMemory

async def test_lancedb_retrieval():
    """测试LanceDB 7层混合检索"""
    print("🚀 测试 LanceDB 7层混合检索标准实现...")
    
    # 初始化长期记忆管理器
    ltm = LongTermMemory()
    
    # 测试查询
    test_queries = [
        "WordPress 发布博客",
        "DAMA-DMBOK2 教程", 
        "LanceDB 向量检索",
        "Google Gemini API"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        print("-" * 50)
        
        try:
            memory_text, is_pruned = await ltm.retrieve_relevant_memory(query)
            if memory_text:
                print(memory_text)
            else:
                print("❌ 无相关历史记忆")
        except Exception as e:
            print(f"❌ 检索失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_lancedb_retrieval())