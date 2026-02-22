#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Worker - 自动采集AI资讯并更新知识图谱
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from DavidAgent.sensors.github_trending_sensor import GitHubTrendingSensor
from brain.memory.episodic_memory import get_episodic_memory_db
from brain.global_graph import SystemicKnowledgeGraph
from brain.blackboard import Blackboard

class GitHubTrendingWorker:
    """GitHub趋势工作器，负责定期采集和更新知识图谱"""
    
    def __init__(self):
        self.sensor = GitHubTrendingSensor()
        self.db = get_episodic_memory_db()
        self.graph = SystemicKnowledgeGraph()
        self.blackboard = Blackboard()
        
    async def collect_and_update(self, limit: int = 5, hours: int = 24, language: str = "python"):
        """
        采集GitHub趋势并更新知识图谱
        
        Args:
            limit: 采集项目数量限制
            hours: 时间窗口（小时）
            language: 编程语言过滤
        """
        print(f"🚀 开始采集最新的{language} AI项目...")
        
        # 1. 采集GitHub趋势数据
        trending_payloads = await self.sensor.fetch_daily_trending(
            limit=limit, 
            hours=hours, 
            language=language
        )
        
        if not trending_payloads:
            print("❌ 未获取到任何趋势数据")
            return
        
        print(f"✅ 成功获取 {len(trending_payloads)} 个AI项目")
        
        # 2. 处理每个项目并更新知识图谱
        for payload in trending_payloads:
            await self._process_and_update(payload)
        
        print("🎉 GitHub趋势数据已成功更新到知识图谱！")
        
    async def _process_and_update(self, payload: dict):
        """处理单个项目并更新知识图谱"""
        try:
            # 检查是否已存在（去重）
            content_hash = self._generate_content_hash(payload['core_text'])
            if self.db.check_duplicate(content_hash):
                print(f"⏭️ 跳过重复内容: {payload['source_id']}")
                return
            
            # 构造信号数据
            signal_data = {
                'signal_id': payload['source_id'],
                'content_hash': content_hash,
                'handle': f"{payload['author']}/{payload['source_id'].replace('repo_', '')}",
                'author_name': payload['author'],
                'timestamp': payload['timestamp'],
                'likes': 0,  # GitHub没有直接的likes，可以用stars替代
                'retweets': 0,  # GitHub没有retweets
                'raw_text': payload['core_text'],
                'raw_json': str(payload),
                'signal_type': 'github_trending'
            }
            
            # 保存原始信号
            self.db.save_raw_signal(signal_data)
            
            # 更新黑板触发分析
            self.blackboard.update('topic_id', payload['source_id'], 'SENSOR_GH_TRENDING')
            self.blackboard.update('raw_source', payload['core_text'], 'SENSOR_GH_TRENDING')
            self.blackboard.update('workflow_status', 'START', 'SYSTEM')
            
            # 直接更新知识图谱（模拟左脑处理后的结果）
            await self._update_knowledge_graph(payload)
            
            print(f"✅ 已处理项目: {payload['author']}/{payload['source_id']}")
            
        except Exception as e:
            print(f"❌ 处理项目失败: {e}")
    
    def _generate_content_hash(self, content: str) -> str:
        """生成内容哈希用于去重"""
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def _update_knowledge_graph(self, payload: dict):
        """直接更新知识图谱（简化版，实际应该通过左脑处理）"""
        from brain.left_brain.schemas import GraphData, Entity, Triple
        
        # 提取项目信息
        project_name = payload['core_text'].split('\n')[0].replace('【项目名称】: ', '')
        description = payload['core_text'].split('\n')[1].replace('【简介】: ', '')
        
        # 创建简化的知识图谱数据
        graph_data = GraphData(
            summary=f"GitHub热门AI项目: {project_name}",
            entities=[
                Entity(name=project_name, type="SoftwareProject", definition=description),
                Entity(name=payload['author'], type="Organization", definition=f"GitHub用户: {payload['author']}"),
                Entity(name="GitHub", type="Platform", definition="开源代码托管平台")
            ],
            triples=[
                Triple(subject=project_name, predicate="developedBy", object_=payload['author']),
                Triple(subject=project_name, predicate="hostedOn", object_="GitHub"),
                Triple(subject=payload['author'], predicate="hasProject", object_=project_name)
            ]
        )
        
        # 摄入到全局知识图谱
        await self.graph.ingest_graph_data(graph_data, payload['source_id'])
    
    async def run_scheduled_task(self):
        """运行定时任务"""
        while True:
            try:
                # 每6小时运行一次
                await self.collect_and_update(limit=5, hours=6, language="python")
                
                # 等待6小时
                await asyncio.sleep(6 * 3600)
                
            except KeyboardInterrupt:
                print("🛑 收到中断信号，停止GitHub趋势工作器")
                break
            except Exception as e:
                print(f"❌ 定时任务出错: {e}")
                # 等待1小时后重试
                await asyncio.sleep(3600)

async def main():
    """主函数"""
    worker = GitHubTrendingWorker()
    
    # 立即运行一次
    await worker.collect_and_update(limit=5, hours=24, language="python")
    
    # 如果需要持续运行，取消下面的注释
    # await worker.run_scheduled_task()

if __name__ == "__main__":
    asyncio.run(main())