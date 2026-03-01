#!/usr/bin/env python3
"""
主动引擎 - 图谱涌现与主动深度思考
每周五晚上自动触发，让DavidAgent从"打工人"变成"行业分析师"
"""

import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent


class WeeklySynthesisEngine:
    """每周图谱涌现引擎"""
    
    def __init__(self):
        self.db_path = project_root / "brain" / "memory" / "david_agent_memory.db"
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    async def trigger_graph_emergence(self):
        """触发每周图谱涌现机制"""
        print("🌌 [主动引擎] 触发每周图谱涌现机制，DavidAgent 正在进行深度思考...")
        
        # 1. 提取过去7天内左脑成功提取的所有高质量知识图谱
        weekly_graphs = await self._extract_weekly_graphs()
        
        if len(weekly_graphs) < 3:
            print("😴 [主动引擎] 本周吸收的知识太少（不足3篇），无法产生高质量涌现，取消创作。")
            return
        
        # 2. 聚合所有的实体和三元组（消除孤岛，建立全局图谱）
        aggregated_entities, aggregated_triples = self._aggregate_knowledge_graphs(weekly_graphs)
        
        print(f"📊 [主动引擎] 本周共吸收 {len(aggregated_entities)} 个独立实体，建立 {len(aggregated_triples)} 条知识链接。")
        
        # 3. 唤醒右脑（千问），让它作为"行业分析大佬"俯瞰这些数据
        deep_article = await self._generate_deep_insight(aggregated_entities, aggregated_triples)
        
        if deep_article:
            # 4. 落盘并准备发布
            await self._save_weekly_insight(deep_article)
            print("🎉 [主动引擎] 周报已生成。去看看 DavidAgent 发现了什么你没注意到的行业规律吧！")
    
    async def _extract_weekly_graphs(self):
        """提取过去7天的知识图谱"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            cursor.execute('''
                SELECT left_brain_graph 
                FROM trace_logs 
                WHERE timestamp > ? AND left_brain_graph IS NOT NULL AND left_brain_graph != ''
            ''', (seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),))
            
            weekly_graphs = cursor.fetchall()
            conn.close()
            return weekly_graphs
            
        except Exception as e:
            print(f"❌ [主动引擎] 数据库查询失败: {e}")
            return []
    
    def _aggregate_knowledge_graphs(self, weekly_graphs):
        """聚合知识图谱"""
        aggregated_entities = set()
        aggregated_triples = []
        
        for row in weekly_graphs:
            try:
                graph_data = json.loads(row[0])
                # 提取实体
                for entity in graph_data.get('entities', []):
                    entity_str = f"{entity['name']} ({entity['type']})"
                    aggregated_entities.add(entity_str)
                
                # 提取三元组
                for triple in graph_data.get('triples', []):
                    triple_str = f"{triple['subject']} -> {triple['predicate']} -> {triple['object']}"
                    aggregated_triples.append(triple_str)
                    
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"⚠️ [主动引擎] 图谱解析错误: {e}")
                continue
        
        return list(aggregated_entities), aggregated_triples
    
    async def _generate_deep_insight(self, entities, triples):
        """生成深度洞察文章"""
        system_prompt = """
你是一个拥有上帝视角的顶级 AI 行业分析师兼科技达人。

【输入数据说明】：
下面是你在这个星期内，通过全网阅读提取出来的所有【核心实体】和【关联三元组】的汇总。
这就像是一地散落的珍珠。

【主动创作任务】：
1. 图谱涌现：不要像报流水账一样罗列它们。请在这些碎片中寻找"隐藏的趋势"或"底层逻辑的共性"。
2. 深度长文：将你发现的趋势，撰写成一篇深度的每周技术总结博客（Markdown格式）。
3. 标题示例：《从本周的碎片知识中，我看到了大模型框架的三个暗流》等。
4. 语气：高屋建瓴，洞察敏锐。
5. 长度：800-1200字，包含具体的技术细节和趋势分析。
"""
        
        user_prompt = f"""【本周实体词云】:
{', '.join(entities)}

【本周逻辑连接网】:
{'\n'.join(triples)}

请开始你的深度创作："""
        
        try:
            response = await self.client.chat.completions.create(
                model="qwen-coder-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # 极高的温度，鼓励大模型"脑洞大开"寻找隐藏联系
                max_tokens=3000
            )
            
            deep_article = response.choices[0].message.content
            print("✅ [主动引擎] 深度长文创作完毕！")
            return deep_article
            
        except Exception as e:
            print(f"❌ [主动引擎] 图谱涌现失败: {e}")
            return None
    
    async def _save_weekly_insight(self, article_content):
        """保存周报"""
        try:
            # 创建输出目录
            output_dir = project_root / "brain" / "outputs" / "weekly_insights"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            filename = f"weekly_insight_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = output_dir / filename
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(article_content)
            
            print(f"💾 [主动引擎] 周报已保存: {filepath}")
            
            # 这里也可以直接调用WordPress执行器发布
            # await self._publish_to_wordpress(article_content)
            
        except Exception as e:
            print(f"❌ [主动引擎] 保存周报失败: {e}")


async def main():
    """主函数"""
    try:
        engine = WeeklySynthesisEngine()
        await engine.trigger_graph_emergence()
    except Exception as e:
        print(f"❌ [主动引擎] 主函数执行失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())