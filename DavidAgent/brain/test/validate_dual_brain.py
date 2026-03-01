#!/usr/bin/env python3
"""
ag 引擎双脑闭环 E2E 验证方案
验证左脑的"绝对准确"、黑板的"状态流转"以及右脑的"升维表达"
"""

import asyncio
import os
import sys
from pathlib import Path
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入核心模块
from brain.left_brain.graph_constructor import LeftBrainGraphConstructor
from brain.right_brain.persona_synthesizer import RightBrainPersonaSynthesizer
from brain.memory.blackboard import BrainBlackboard


class DualBrainValidator:
    """双脑闭环验证器"""
    
    def __init__(self):
        self.test_topic = "DeepSeek_Qwen_Agent_Arch"
        self.generated_md_path = ""
        self.blackboard = BrainBlackboard()
        
    async def load_test_data(self) -> str:
        """加载测试用的高噪音推文数据"""
        test_file = Path(__file__).parent / "mock_x_post.txt"
        with open(test_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    async def validate_left_brain_extraction(self, raw_x_post: str) -> Dict[str, Any]:
        """验证左脑蛋白质提取阶段"""
        print("⏳ [正在测试] 左脑 Gemini 提取逻辑...")
        
        left_brain = LeftBrainGraphConstructor()
        graph_data = await left_brain.extract_knowledge(raw_x_post)
        
        # 验证目标1: JSON格式强制性
        assert isinstance(graph_data.entities, list), "左脑输出缺少 entities 数组"
        assert isinstance(graph_data.triples, list), "左脑输出缺少 triples 数组"
        assert isinstance(graph_data.summary, str), "左脑输出缺少 summary 字段"
        
        # 验证目标2: 去噪能力
        entity_names = [entity.name for entity in graph_data.entities]
        print(f"  提取的实体: {entity_names}")
        
        # 检查核心实体是否被正确提取
        deepseek_found = any("DeepSeek" in name for name in entity_names)
        qwen_found = any("通义千问" in name or "Qwen" in name for name in entity_names)
        ag_found = any("ag" in name or "引擎" in name for name in entity_names)
        
        assert deepseek_found, "未能提取到核心实体: DeepSeek"
        assert qwen_found, "未能提取到核心实体: 通义千问"
        assert ag_found, "未能提取到核心实体: ag引擎"
        
        # 检查是否过滤了情绪化废话（不应该包含"太卷了兄弟们"）
        noise_filtered = not any("太卷了" in entity.name for entity in graph_data.entities)
        assert noise_filtered, "左脑未能过滤情绪化废话"
        
        print("✅ [通过] 左脑结构化提取精准无误，成功过滤情绪化废话。")
        return graph_data
    
    async def validate_pageindex_persistence(self, graph_data: Dict[str, Any]) -> str:
        """验证PageIndex知识图谱固化"""
        print("⏳ [正在测试] PageIndex 知识图谱落盘...")
        
        left_brain = LeftBrainGraphConstructor()
        md_path = await left_brain.save_to_pageindex(graph_data, self.test_topic)
        self.generated_md_path = md_path
        
        # 验证目标3: PageIndex固化
        assert os.path.exists(md_path), "PageIndex Markdown 文件未成功生成"
        
        # 读取文件内容验证双链语法
        with open(md_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert "[[" in file_content and "]]" in file_content, "Markdown 文件缺少 PageIndex 要求的双链语法 [[ ]]"
        
        # 验证核心实体是否以双链格式存在
        assert "[[DeepSeek" in file_content or "[[通义千问" in file_content, "双链格式中缺少核心实体"
        
        print("✅ [通过] 左脑蛋白质已成功注入 PageIndex 长期记忆库。")
        return file_content
    
    async def validate_blackboard_state(self, graph_data: Dict[str, Any]):
        """验证黑板神经电信号状态流转"""
        print("⏳ [正在测试] 黑板状态机事件驱动...")
        
        # 模拟黑板状态更新
        self.blackboard.write('extracted_facts', graph_data)
        
        # 验证目标4: 事件驱动状态更新
        stored_data = self.blackboard.read('extracted_facts')
        assert stored_data is not None, "黑板未能存储提取的事实数据"
        assert len(stored_data.entities) > 0, "黑板存储的实体数据为空"
        
        print("✅ [通过] 黑板成功触发状态流转，神经电信号传导正常。")
    
    async def validate_right_brain_creation(self, knowledge_markdown: str) -> str:
        """验证右脑米其林烹饪阶段"""
        print("⏳ [正在测试] 右脑 Qwen 烹饪博客草稿...")
        
        right_brain = RightBrainPersonaSynthesizer()
        blog_draft = await right_brain.draft_blog_post(self.test_topic, knowledge_markdown)
        
        # 验证目标5: 幻觉阻断（防投毒）
        assert len(blog_draft) > 200, "右脑生成的文章过短，未完成升维展开"
        assert ("#" in blog_draft or "标题" in blog_draft or "##" in blog_draft), "右脑未生成标准的 Markdown 标题排版"
        
        # 核心防幻觉断言: 检查是否严格遵守了左脑提取的逻辑关系
        assert ("API" in blog_draft or "主控" in blog_draft or "大脑" in blog_draft), "右脑丢失了千问作为主控的核心逻辑"
        assert ("DeepSeek" in blog_draft and "代码" in blog_draft), "右脑丢失了DeepSeek适合写代码的核心逻辑"
        
        # 确保没有捏造原文不存在的模型
        assert "Claude" not in blog_draft, "右脑发生了幻觉，捏造了原文不存在的模型！"
        assert "GPT-4" not in blog_draft or "GPT-4 Turbo" in blog_draft, "右脑对GPT-4的描述不准确"
        
        # 验证目标6: Persona升维
        persona_keywords = ["极客", "架构", "效率", "技术", "智能", "框架", "系统"]
        has_persona = any(keyword in blog_draft for keyword in persona_keywords)
        assert has_persona, "右脑输出缺少科技达人Persona特征词汇"
        
        print("✅ [通过] 右脑成功将硬核三元组升维成带有科技达人 Persona 的连贯文章，且无幻觉。")
        return blog_draft
    
    async def cleanup_test_data(self):
        """清理测试产生的脏数据"""
        if self.generated_md_path and os.path.exists(self.generated_md_path):
            try:
                os.remove(self.generated_md_path)
                print(f"🧹 [清理完成] 已删除测试文件: {self.generated_md_path}")
            except Exception as e:
                print(f"⚠️ [清理警告] 删除测试文件失败: {e}")
    
    async def run_validation(self):
        """运行完整的E2E验证流程"""
        print("🧪 [测试启动] ag 引擎双脑闭环 E2E 验证开始...\n")
        
        try:
            # 加载测试数据
            raw_x_post = await self.load_test_data()
            print(f"📝 测试输入:\n{raw_x_post}\n")
            
            # 阶段1: 左脑提取验证
            graph_data = await self.validate_left_brain_extraction(raw_x_post)
            
            # 阶段2: PageIndex固化验证  
            knowledge_markdown = await self.validate_pageindex_persistence(graph_data)
            
            # 阶段3: 黑板状态验证
            await self.validate_blackboard_state(graph_data)
            
            # 阶段4: 右脑创作验证
            blog_draft = await self.validate_right_brain_creation(knowledge_markdown)
            
            print(f"\n🎉 [验证大成功] ag引擎从吃草到出餐的全自动流水线测试 100% 通过！")
            print(f"\n============== 最终可供 WordPress 发布的内容预览 ==============\n")
            preview = blog_draft[:300] + "..." if len(blog_draft) > 300 else blog_draft
            print(preview)
            print("\n" + "="*70 + "\n")
            
            return True
            
        except AssertionError as e:
            print(f"\n❌ [验证失败] 断言错误: {e}")
            return False
        except Exception as e:
            print(f"\n❌ [验证失败] 在测试流程中发生致命错误: {e}")
            import traceback
            print(traceback.format_exc())
            return False
        finally:
            # 清理测试数据（可选，当前保留用于调试）
            # await self.cleanup_test_data()
            pass


async def main():
    """主函数"""
    validator = DualBrainValidator()
    success = await validator.run_validation()
    
    if success:
        print("🟢 所有验证检查点通过！双脑引擎健康运行。")
        sys.exit(0)
    else:
        print("🔴 验证失败！请检查双脑引擎配置。")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())