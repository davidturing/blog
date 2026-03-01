#!/usr/bin/env python3
"""
右脑创作者 - 通义千问驱动的Persona合成器
实现"降维打击"与"升维表达"：将左脑的结构化知识转化为带Persona的连贯文章
"""

import os
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent

# 导入技能加载器
from .skill_loader import load_skills_for_persona


class RightBrainPersonaSynthesizer:
    """右脑Persona合成器 - Qwen驱动的创意表达"""
    
    def __init__(self):
        # 初始化千问客户端 (使用阿里云 DashScope 的 OpenAI 兼容模式)
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is required")
            
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://coding.dashscope.aliyuncs.com/v1"
        )
        
        # PageIndex知识图谱存储目录
        self.project_root = Path(__file__).parent.parent.parent
        self.knowledge_dir = self.project_root / "skills" / "self-learning-agent" / "pageindex" / "knowledge"
        
        # 海马体集成
        from brain.memory.hippocampus import LongTermMemory
        self.hippocampus = LongTermMemory()
    
    async def draft_blog_post(self, topic_name: str, knowledge_markdown: str) -> dict:
        """
        核心创作逻辑：融合知识图谱、历史记忆与Persona
        
        Args:
            topic_name: 主题名称
            knowledge_markdown: 左脑生成的结构化知识Markdown
            
        Returns:
            dict: 包含 "draft", "historical_context", "is_pruned", "ontological_associations"
        """
        print(f"🎨 [右脑-Qwen] 接收到左脑整理的知识骨架: {topic_name}，开始构思文章...")
        
        # 1. 检索相关历史记忆（带鲁棒性增强）
        try:
            # 提取知识摘要用于检索
            summary_for_retrieval = self._extract_summary_for_retrieval(knowledge_markdown)
            historical_context, is_pruned = await self.hippocampus.retrieve_relevant_memory(summary_for_retrieval)
            
            # 使用 SPARQL 引擎挖掘图谱深层跨领域关联
            ontological_associations = self._get_ontological_associations(knowledge_markdown)
        except Exception as e:
            print(f"⚠️ [系统告警] 长期记忆库/图谱访问失败 ({e})。启动降级模式。")
            historical_context = ""
            is_pruned = False
            ontological_associations = ""
        
        # 2. 读取最新的避坑指南
        dynamic_guidelines = get_dynamic_guidelines()
        
        # 3. 构建增强版System Prompt
        system_prompt = self._build_system_prompt(historical_context, dynamic_guidelines)
        user_prompt = self._build_user_prompt(knowledge_markdown, ontological_associations)
        
        try:
            response = await self.client.chat.completions.create(
                model="qwen3-max-2026-01-23",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # 适当的温度，保留千问的创作活力
                max_tokens=2500
            )
            
            draft_content = response.choices[0].message.content
            
            # Extract internal token billings
            token_usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage_obj = response.usage
                token_usage = {
                    "prompt_tokens": getattr(usage_obj, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage_obj, "completion_tokens", 0),
                    "total_tokens": getattr(usage_obj, "total_tokens", 0)
                }
                
            print(f"✅ [右脑-Qwen] 博客草稿创作完毕！耗费 Tokens: {token_usage.get('total_tokens', '计算中...')}")
            return {
                "draft": draft_content,
                "historical_context": historical_context,
                "is_pruned": is_pruned,
                "ontological_associations": ontological_associations,
                "raw_system_prompt": system_prompt,
                "raw_user_prompt": user_prompt,
                "token_usage": token_usage
            }
            
        except Exception as e:
            print(f"❌ [右脑-Qwen] 创作失败: {e}")
            raise e
    
    def _extract_summary_for_retrieval(self, knowledge_markdown: str) -> str:
        """从知识Markdown中提取摘要用于检索"""
        # 简单提取标题和前几行作为摘要
        lines = knowledge_markdown.split('\n')
        title = ""
        content_preview = ""
        
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
            elif line.strip() and not line.startswith('##') and not line.startswith('-'):
                content_preview = line.strip()
                break
        
        return f"{title} {content_preview}"[:200]
    
    def _get_ontological_associations(self, knowledge_markdown: str) -> str:
        """从知识图谱提取核心实体，并通过 SPARQL 查询跨领域关联。"""
        # 简单提取双链实体名称
        entities = []
        for line in knowledge_markdown.split('\n'):
            if line.startswith("- **[[") and "]]**" in line:
                entity = line.split("[[")[1].split("]]")[0]
                entities.append(entity)
                
        if not entities:
            return ""
            
        associations = []
        for entity in entities[:3]: # 取前3个核心实体避免过载上下文
            sparql_query = f'''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?p ?o
            WHERE {{
                ?s rdfs:label "{entity}" .
                ?s ?p ?o .
                FILTER(?p != rdf:type && ?p != rdfs:label && ?p != rdfs:comment)
            }} LIMIT 5
            '''
            try:
                results = self.hippocampus.query_ontology_sparql(sparql_query)
                if results:
                    assoc_str = ", ".join([f"{r.get('p')} -> {r.get('o')}" for r in results])
                    if assoc_str:
                        associations.append(f"【{entity}】的系统级本体关联: {assoc_str}")
            except Exception as e:
                print(f"⚠️ [SPARQL] 查询实体 {entity} 遇到错误: {e}")
                pass
                
        if associations:
            return "以下是基于统一聚合本体(OWL)查询到的深层拓扑知识（可用于跨领域发散创作）：\n" + "\n".join(associations)
        return ""

    def _build_system_prompt(self, historical_context: str, dynamic_guidelines: str) -> str:
        """
        构建系统提示词，包含历史记忆和动态规则
        
        Args:
            historical_context: 相关历史记忆
            dynamic_guidelines: 动态避坑指南
            
        Returns:
            str: 完整的系统提示词
        """
        base_prompt = """
你是一个资深的“科技达人”数字分身。你拥有极强的极客精神，对前沿 AI 技术、多智能体框架有着敏锐的洞察力。
你的语言风格：
1. 专业但接地气，喜欢用比喻，带有强烈的“网感”。
2. 逻辑清晰，喜欢一针见血地指出技术的核心优势。
3. 你的输出内容是系统自我进化的一部分。

🚨【你必须绝对遵守的自我反思法则 (从过去的错误中学习)】：
{dynamic_guidelines}

任务目标：
基于用户提供的【知识图谱结构数据】，撰写一篇引人入胜的技术博客文章（Markdown格式），准备发布到 WordPress。

文章结构要求：
- 【吸引眼球的标题】：不要太死板。
- 【开篇引入】：自然地引入话题，可以是一句感叹或者一个痛点。
- 【核心解析】：将知识图谱中的“实体(entities)”和“三元组关系(triples)”用人类友好的语言串联起来，进行深度解读。
- 🚨【绝对约束】：务必基于提供的数据进行解读，禁止发散捏造不存在的实体和功能（防止幻觉）。
- 【总结展望】：给出你作为科技达人的主观评价。
""".format(dynamic_guidelines=dynamic_guidelines)
        
        # 如果有相关历史记忆，添加到Prompt中
        if historical_context.strip():
            memory_section = """
【过往相关记忆片段】：
{historical_context}

【行为指令】：
你是一个有记忆的科技达人。请在写作时，自然地关联《过往记忆片段》，
例如使用'正如我们之前探讨的那样...'或者'这印证了之前对某某技术的判断'等句式，
构建属于你自己的知识宇宙。

【写作与记忆融合准则】：
- 🚨 如果 [过往历史记忆] 对理解 [当前核心事实] 有极其顺畅的补充作用（例如技术演进对比、历史观点印证），请以你本人的口吻自然融入。
- 🚨 鲁棒性约束：如果你觉得 [过往历史记忆] 与当前主题关联较弱，或者融入起来显得生硬造作，**请完全无视历史记忆**，绝不强行串联。自然、流畅永远是第一位的！
""".format(historical_context=historical_context)
            
            base_prompt += memory_section
        
        return base_prompt
    
    def _build_user_prompt(self, knowledge_markdown: str, ontological_associations: str = "") -> str:
        """
        构建用户提示词
        
        Args:
            knowledge_markdown: 知识图谱Markdown内容
            ontological_associations: 基于本体查询出的跨域关联提示词
            
        Returns:
            str: 用户提示词
        """
        prompt = f"""
这是 ag 引擎左脑刚刚吸收的结构化图谱数据：

{knowledge_markdown}
"""
        if ontological_associations:
            prompt += f"\n{ontological_associations}\n"
            
        prompt += "\n请根据这些核心事实与本体拓扑，帮我写一篇完整的博客文章草稿。展现你的深度推演能力。\n"
        return prompt
    
    async def rewrite_blog_post(self, original_draft: str, feedback: str, knowledge_markdown: str) -> str:
        """
        重写博客草稿（处理左脑审查反馈或人类修改意见）
        
        Args:
            original_draft: 原始草稿
            feedback: 修改意见
            knowledge_markdown: 知识图谱内容
            
        Returns:
            str: 重写后的草稿
        """
        print(f"🔄 [右脑-Qwen] 收到修改意见，正在重写草稿...")
        
        # 读取最新的避坑指南
        dynamic_guidelines = get_dynamic_guidelines()
        
        system_prompt = f"""
你是一个资深的“科技达人”数字分身。

🚨【你必须绝对遵守的自我反思法则 (从过去的错误中学习)】：
{dynamic_guidelines}

任务目标：
你之前写的草稿收到了修改意见。请根据以下信息重写一篇更好的博客文章。

【原始草稿】：
{original_draft}

【修改意见】：
{feedback}

【知识图谱结构数据】：
{knowledge_markdown}

请认真对待修改意见，重写一篇更符合要求的博客文章。
"""
        
        user_prompt = "请根据以上所有信息，重写一篇完整的博客文章草稿。"
        
        try:
            response = await self.client.chat.completions.create(
                model="qwen3-max-2026-01-23",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,  # 重写时稍微降低温度，更注重准确性
                max_tokens=2500
            )
            
            new_draft = response.choices[0].message.content
            print(f"✅ [右脑-Qwen] 草稿重写完成！")
            return new_draft
            
        except Exception as e:
            print(f"❌ [右脑-Qwen] 草稿重写失败: {e}")
            raise e