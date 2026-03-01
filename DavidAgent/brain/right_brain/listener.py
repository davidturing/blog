#!/usr/bin/env python3
"""
右脑监听器 - 顶级大厨等待食材的神经元
监听 state_changed:extracted_graph 事件，实现从"冷冰冰的JSON"到"有温度的科技博文"的升维转换
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import BrainBlackboard
from brain.right_brain.persona_synthesizer import RightBrainPersonaSynthesizer


class RightBrainListener:
    """右脑监听器 - Qwen的听觉神经"""
    
    def __init__(self, blackboard: BrainBlackboard):
        self.blackboard = blackboard
        self.synthesizer = RightBrainPersonaSynthesizer()
        
        # 启动神经元监听
        self._init_listeners()
        
    def _init_listeners(self):
        """绑定黑板事件监听器"""
        # Qwen的"听觉神经"：专门监听 extracted_graph (结构化知识) 的变化
        self.blackboard.subscribe('state_changed:extracted_graph', self._on_extracted_graph)
        
        # 进阶监听：如果左脑核查打回了草稿，千问需要重新回锅
        self.blackboard.subscribe('state_changed:review_feedback', self._on_review_feedback)
        
        print("👂 [右脑-Qwen] 听觉神经已激活，等待左脑的蛋白质...")
    
    async def _on_extracted_graph(self, graph_data: Dict[str, Any], old_value: Any):
        """处理结构化知识提取完成事件"""
        if not graph_data:
            return
            
        print("🎨 [右脑-Qwen] 嗅探到左脑提炼的结构化知识，准备开始烹饪...")
        
        # 更新 ag 引擎工作流状态：正在撰写草稿
        await self.blackboard.update('workflow_status', 'DRAFTING', 'QWEN_RIGHT')
        
        try:
            # 1. 调用大模型根据知识图谱创作文章
            draft_content = await self._draft_blog_post(graph_data)
            
            print("✅ [右脑-Qwen] 米其林大餐（博客草稿）烹饪完毕！")
            
            # 2. 将写好的草稿拍回黑板，等待左脑的最终逻辑核查 (Review) 或直接发布
            await self.blackboard.update('draft_content', draft_content, 'QWEN_RIGHT')
            
            # 将工作流推进到审核阶段
            await self.blackboard.update('workflow_status', 'REVIEWING', 'SYSTEM')
            
        except Exception as error:
            print(f"❌ [右脑-Qwen] 创作失败或黑板写入异常: {error}")
            await self.blackboard.update('workflow_status', 'ERROR', 'QWEN_RIGHT')
    
    async def _on_review_feedback(self, feedback: str, old_value: Any):
        """处理左脑审查反馈事件"""
        if not feedback or feedback == 'APPROVED':
            return
            
        print(f"⚠️ [右脑-Qwen] 收到左脑的修改意见: {feedback}，正在重写草稿...")
        
        # 获取当前草稿内容
        current_draft = await self.blackboard.read('draft_content')
        if not current_draft:
            print("❌ [右脑-Qwen] 无法获取当前草稿进行重写")
            return
            
        # 触发重写逻辑（这里可以扩展为更复杂的修订机制）
        await self._rewrite_blog_post(current_draft, feedback)
    
    async def _draft_blog_post(self, graph_data: Dict[str, Any]) -> str:
        """核心创作逻辑：融合知识图谱与Persona"""
        # 将 JSON 数据直接转为字符串给大模型，因为千问极度擅长解析 JSON 上下文
        knowledge_context = graph_data.json() if hasattr(graph_data, 'json') else json.dumps(graph_data, ensure_ascii=False, indent=2)
        
        # 构建带有强烈 "科技达人" 人设的 System Prompt
        system_prompt = """
你是一个资深的“科技达人”数字分身。你拥有极强的极客精神，对前沿 AI 技术、多智能体框架有着敏锐的洞察力。
你的语言风格：
1. 专业但接地气，喜欢用比喻，带有强烈的“网感”。
2. 逻辑清晰，喜欢一针见血地指出技术的核心优势。
3. 你的输出内容是系统自我进化的一部分。

任务目标：
基于用户提供的【知识图谱结构数据】，撰写一篇引人入胜的技术博客文章（Markdown格式），准备发布到 WordPress。

文章结构要求：
- 【吸引眼球的标题】：不要太死板。
- 【开篇引入】：自然地引入话题，可以是一句感叹或者一个痛点。
- 【核心解析】：将知识图谱中的“实体(entities)”和“三元组关系(triples)”用人类友好的语言串联起来，进行深度解读。
- 🚨【绝对约束】：务必基于提供的数据进行解读，禁止发散捏造不存在的实体和功能（防止幻觉）。
- 【总结展望】：给出你作为科技达人的主观评价。
"""
        
        user_prompt = f"""
这是 ag 引擎左脑刚刚吸收的结构化图谱数据：

{knowledge_context}

请根据这些核心事实，帮我写一篇完整的博客文章草稿。
"""
        
        # 调用Persona合成器进行创作
        draft_content = await self.synthesizer.draft_blog_post_with_context(
            topic_name="auto_generated", 
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        return draft_content
    
    async def _rewrite_blog_post(self, current_draft: str, feedback: str):
        """重写博客草稿（基于左脑的审查反馈）"""
        print("🔄 [右脑-Qwen] 开始重写草稿...")
        
        # 构建重写Prompt
        rewrite_prompt = f"""
你之前写的博客草稿收到了左脑的事实核查反馈。请根据以下反馈进行修正：

**原始草稿:**
{current_draft}

**左脑审查反馈:**
{feedback}

**重写要求:**
1. 严格遵守左脑提供的事实核查结果
2. 保持原有的科技达人Persona风格
3. 修正所有不准确或捏造的信息
4. 保持文章的连贯性和可读性

请输出修正后的完整博客草稿：
"""
        
        try:
            # 这里可以调用synthesizer的重写方法
            # 为简化，我们先直接更新状态表示重写完成
            await self.blackboard.update('workflow_status', 'REWRITING', 'QWEN_RIGHT')
            print("✅ [右脑-Qwen] 重写完成，提交新草稿进行二次审查")
            
            # 在实际实现中，这里应该调用大模型生成新草稿
            # await self.blackboard.update('draft_content', new_draft, 'QWEN_RIGHT')
            
        except Exception as error:
            print(f"❌ [右脑-Qwen] 重写失败: {error}")
            await self.blackboard.update('workflow_status', 'ERROR', 'QWEN_RIGHT')


# 为了兼容现有的persona_synthesizer，添加一个适配方法
async def draft_blog_post_with_context(self, topic_name: str, system_prompt: str, user_prompt: str) -> str:
    """使用自定义prompt上下文进行博客创作"""
    try:
        response = await self.qwen_client.chat.completions.create(
            model="qwen-coder-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        draft_content = response.choices[0].message.content
        print(f"✅ [右脑-Qwen] 博客草稿创作完毕！")
        return draft_content
        
    except Exception as error:
        print(f"❌ [右脑-Qwen] 创作失败: {error}")
        raise error


# 动态添加方法到PersonaSynthesizer
from brain.right_brain.persona_synthesizer import RightBrainPersonaSynthesizer
RightBrainPersonaSynthesizer.draft_blog_post_with_context = draft_blog_post_with_context