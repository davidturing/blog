#!/usr/bin/env python3
"""
双脑协同工作流完整测试
模拟ag引擎的完整生命周期：左脑提取 → 右脑创作
"""

import asyncio
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from brain.left_brain.graph_constructor import LeftBrainGraphConstructor
from brain.right_brain.persona_synthesizer import RightBrainPersonaSynthesizer


async def run_dual_brain_workflow():
    """运行完整的双脑协同工作流"""
    print("🚀 --- ag 引擎双脑协同流水线启动 ---\n")
    
    # 模拟从X网站抓取的原始推文
    raw_x_post = """
    今天深入研究了一下 OpenClaw 这个 Multi-Agent 框架。它底层是基于 Node.js 的，非常适合做 I/O 密集型任务。
    我打算把通义千问（qwen3-coder-plus）接入进去作为主控大脑，然后把 Gemini 2.5 Pro 挂载为专门处理多模态和图谱提取的外部 Tool。
    相比于传统的 LangChain，OpenClaw 的事件总线机制更优雅。
    """
    
    topic_name = "OpenClaw_Architecture"
    
    # 1. 唤醒左脑 - 知识提取与图谱构建
    print("🧠 [左脑-Gemini] 开始深度解析文本...")
    left_brain = LeftBrainGraphConstructor()
    
    try:
        graph_data = await left_brain.extract_knowledge(raw_x_post)
        saved_file_path = await left_brain.save_to_pageindex(graph_data, topic_name)
        print(f"✅ [左脑] 知识图谱已保存到: {saved_file_path}\n")
    except Exception as e:
        print(f"❌ [左脑] 处理失败: {e}")
        return
    
    # 2. 神经电信号传递
    print("⚡ [神经传导] 左脑已将知识写入海马体，正在唤醒右脑...\n")
    
    # 3. 唤醒右脑 - Persona合成与文章创作
    print("🎨 [右脑-Qwen] 接收到知识骨架，开始构思文章...")
    right_brain = RightBrainPersonaSynthesizer()
    
    try:
        # 从PageIndex读取知识图谱
        knowledge_markdown = await right_brain.load_knowledge_from_file(saved_file_path)
        # 创作博客草稿
        final_blog_draft = await right_brain.draft_blog_post(topic_name, knowledge_markdown)
        print("✅ [右脑] 博客草稿创作完毕！\n")
        
        # 输出最终成果
        print("=" * 60)
        print("📝 最终生成的 WordPress 博客草稿")
        print("=" * 60)
        print(final_blog_draft)
        print("=" * 60)
        
        # 保存草稿到blog目录
        blog_dir = project_root / "blog"
        blog_dir.mkdir(exist_ok=True)
        draft_path = blog_dir / f"{topic_name}_draft_{int(asyncio.get_event_loop().time())}.md"
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(final_blog_draft)
        print(f"\n💾 草稿已保存到: {draft_path}")
        
    except Exception as e:
        print(f"❌ [右脑] 创作失败: {e}")
        return
    
    print("\n🎉 --- ag 引擎双脑协同流水线完成 ---")


if __name__ == "__main__":
    # 检查环境变量
    required_vars = ["GEMINI_API_KEY", "DASHSCOPE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️  缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请在 .env 文件中配置这些变量")
        sys.exit(1)
    
    # 运行异步工作流
    asyncio.run(run_dual_brain_workflow())