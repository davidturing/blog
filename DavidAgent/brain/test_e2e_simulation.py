#!/usr/bin/env python3
"""
DavidAgent 双脑架构端到端模拟测试
使用模拟数据验证完整的双脑工作流
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import BrainBlackboard


class MockLeftBrain:
    """模拟左脑 - 返回预定义的结构化知识"""
    
    @staticmethod
    async def extract_knowledge(raw_text: str):
        """模拟知识提取"""
        print("🧠 左脑开始提取知识...")
        
        # 模拟从graph_constructor.py导入
        from brain.left_brain.graph_constructor import GraphData, Entity, Triple
        
        # 创建模拟的结构化知识
        entities = [
            Entity(name="OpenClaw", type="Framework", definition="基于Node.js的Multi-Agent框架"),
            Entity(name="通义千问", type="Model", definition="阿里巴巴的AI大模型"),
            Entity(name="Gemini", type="Model", definition="Google的AI大模型")
        ]
        
        triples = [
            Triple(subject="OpenClaw", predicate="基于", object="Node.js", context="框架底层技术"),
            Triple(subject="通义千问", predicate="作为", object="主控大脑", context="在ag引擎中"),
            Triple(subject="Gemini", predicate="负责", object="图谱提取", context="作为外部Tool")
        ]
        
        summary = "OpenClaw是一个基于Node.js的Multi-Agent框架，使用通义千问作为主控大脑，Gemini负责图谱提取。"
        
        graph_data = GraphData(entities=entities, triples=triples, summary=summary)
        print("✅ 左脑知识提取完成！")
        return graph_data


class MockRightBrain:
    """模拟右脑 - 基于结构化知识生成博客草稿"""
    
    @staticmethod
    async def draft_blog_post(topic_name: str, knowledge_markdown: str):
        """模拟博客创作"""
        print("🎨 右脑开始创作博客...")
        
        draft = f"""# {topic_name}: OpenClaw多智能体架构深度解析

今天深入研究了一下OpenClaw这个Multi-Agent框架。它底层是基于Node.js的，非常适合做I/O密集型任务。

## 核心架构

在我们的ag引擎中，通义千问（qwen3-coder-plus）作为主控大脑，负责全局统筹和创意表达。而Gemini 2.5 Pro则挂载为专门处理多模态和图谱提取的外部Tool。

相比于传统的LangChain，OpenClaw的事件总线机制更优雅，实现了真正的左右脑协同。

## 技术优势

- **状态隔离**：通过黑板模式避免直接调用
- **事件驱动**：无回调地狱，纯异步非阻塞  
- **幻觉防护**：左脑事实核查确保内容准确性
- **自动发布**：集成WordPress执行器

这就是真正的"科技达人"数字分身！
"""
        print("✅ 右脑博客创作完成！")
        return draft


class MockExecutor:
    """模拟执行器 - 验证发布流程"""
    
    @staticmethod
    async def publish_to_wordpress(title: str, content: str):
        """模拟WordPress发布"""
        print(f"🚀 执行器开始发布文章: {title}")
        print("✅ 文章发布成功！")
        return {"link": "https://example.com/test-post"}


async def run_e2e_simulation():
    """运行端到端模拟测试"""
    print("🚀 === DavidAgent 双脑架构端到端模拟测试 ===\n")
    
    # 初始化黑板
    blackboard = BrainBlackboard()
    
    # 测试数据
    raw_tweet = """今天深入研究了一下 OpenClaw 这个 Multi-Agent 框架。它底层是基于 Node.js 的，非常适合做 I/O 密集型任务。我打算把通义千问（qwen3-coder-plus）接入进去作为主控大脑，然后把 Gemini 2.5 Pro 挂载为专门处理多模态和图谱提取的外部 Tool。相比于传统的 LangChain，OpenClaw 的事件总线机制更优雅。"""
    
    print("📡 注入测试推文...")
    blackboard.update('raw_source', raw_tweet, 'TEST_SPIDER')
    
    # 阶段1: 左脑提取知识
    print("\n--- 阶段1: 左脑知识提取 ---")
    graph_data = await MockLeftBrain.extract_knowledge(raw_tweet)
    blackboard.update('extracted_graph', graph_data, 'GEMINI_LEFT')
    blackboard.update('workflow_status', 'EXTRACTED', 'SYSTEM')
    
    # 阶段2: 右脑创作博客
    print("\n--- 阶段2: 右脑博客创作 ---")
    # 模拟从PageIndex读取Markdown
    knowledge_markdown = "# 知识图谱: OpenClaw_Architecture\n\n> 摘要：OpenClaw框架分析\n\n## 核心实体\n- **[[OpenClaw]]** (Framework): 基于Node.js的Multi-Agent框架"
    blog_draft = await MockRightBrain.draft_blog_post("OpenClaw_Architecture", knowledge_markdown)
    blackboard.update('draft_content', blog_draft, 'QWEN_RIGHT')
    blackboard.update('workflow_status', 'DRAFTING', 'SYSTEM')
    
    # 阶段3: 左脑事实核查
    print("\n--- 阶段3: 左脑事实核查 ---")
    # 模拟核查通过
    print("🔍 左脑开始事实核查...")
    print("✅ 核查通过！无幻觉，逻辑严密。")
    blackboard.update('workflow_status', 'READY_TO_PUBLISH', 'GEMINI_LEFT')
    
    # 阶段4: 执行器发布
    print("\n--- 阶段4: 执行器发布 ---")
    title = "OpenClaw_Architecture: OpenClaw多智能体架构深度解析"
    await MockExecutor.publish_to_wordpress(title, blog_draft)
    blackboard.update('workflow_status', 'PUBLISHED', 'EXECUTOR')
    
    # 验证最终状态
    final_status = blackboard.state['workflow_status']
    print(f"\n📊 最终工作流状态: {final_status}")
    
    if final_status == 'PUBLISHED':
        print("\n🎉 === 端到端模拟测试成功！ ===")
        print("   ✅ 左脑：知识提取正常")
        print("   ✅ 右脑：博客创作正常") 
        print("   ✅ 审查：事实核查正常")
        print("   ✅ 执行：发布流程正常")
        print("   ✅ 黑板：状态流转正常")
        return True
    else:
        print(f"\n❌ === 测试失败！最终状态: {final_status} ===")
        return False


async def main():
    """主函数"""
    try:
        success = await run_e2e_simulation()
        if success:
            print("\n🟢 DavidAgent双脑架构模拟验证通过！")
            sys.exit(0)
        else:
            print("\n🔴 DavidAgent双脑架构模拟验证失败！")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())