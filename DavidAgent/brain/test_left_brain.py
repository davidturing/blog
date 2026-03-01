#!/usr/bin/env python3
"""
左脑图谱构建器测试入口
模拟X网站推文，测试左脑的精准控流能力
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from brain.left_brain.graph_constructor import LeftBrainGraphConstructor

async def run_left_brain_test():
    """测试左脑图谱构建功能"""
    
    # 模拟从X网站抓取的推文
    raw_x_post = """
    今天深入研究了一下 OpenClaw 这个 Multi-Agent 框架。它底层是基于 Node.js 的，非常适合做 I/O 密集型任务。
    我打算把通义千问（qwen3-coder-plus）接入进去作为主控大脑，然后把 Gemini 2.5 Pro 挂载为专门处理多模态和图谱提取的外部 Tool。
    相比于传统的 LangChain，OpenClaw 的事件总线机制更优雅。
    """
    
    print("🧪 开始左脑图谱构建测试...")
    print("=" * 60)
    
    try:
        # 初始化左脑构建器
        left_brain = LeftBrainGraphConstructor()
        
        # 1. 提取知识图谱
        print("🧠 [左脑-Gemini] 开始深度解析文本...")
        graph_data = await left_brain.extract_knowledge(raw_x_post)
        
        # 2. 显示提取结果
        print(f"✅ 提取成功！发现 {len(graph_data.entities)} 个实体, {len(graph_data.triples)} 个关系")
        print("\n📊 提取的实体:")
        for entity in graph_data.entities:
            print(f"   - {entity.name} ({entity.type}): {entity.definition}")
            
        print("\n🔗 提取的关系:")
        for triple in graph_data.triples:
            context = f" (依据: {triple.context})" if triple.context else ""
            print(f"   - {triple.subject} --{triple.predicate}--> {triple.object}{context}")
            
        print(f"\n📝 语义摘要: {graph_data.summary}")
        
        # 3. 存储到PageIndex目录
        print("\n💾 开始持久化到PageIndex...")
        file_path = await left_brain.save_to_pageindex(graph_data, "OpenClaw_MultiAgent_Architecture")
        print(f"✅ 知识图谱已写入: {file_path}")
        
        # 4. 验证文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n📄 生成的Markdown预览:")
            print(content[:500] + "..." if len(content) > 500 else content)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise

if __name__ == "__main__":
    # 设置环境变量（如果需要）
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  请设置 GEMINI_API_KEY 环境变量")
        sys.exit(1)
        
    asyncio.run(run_left_brain_test())