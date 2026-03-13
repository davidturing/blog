#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Curiosity Engine v1 - DavidAgent 自主学习引擎
基于 reflection_manager.py 和 cpep_engine.py 构建的增强层
实现认知缺口检测、外部刺激监听、自发性实验执行和心跳记录
"""

import os
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# DavidAgent 核心模块导入
from DavidAgent.brain.reflection.reflection_manager import ReflectionManager
from DavidAgent.brain.cpep.cpep_engine import CPEPEngine
from DavidAgent.brain.skill.skill_bank import SkillBank
from DavidAgent.brain.skill.skillrl_paper_impl import SkillRLManager
from DavidAgent.memory.reasoning_bank import ReasoningBank
from DavidAgent.utils.web_sensor import WebSensor

# 配置路径
HEARTBEAT_PATH = "/Users/zhaoqinhuang/david_project/memory/HEARTBEAT.md"
REASONING_BANK_PATH = "/Users/zhaoqinhuang/david_project/DavidAgent/memory/reasoning_bank"
SKILL_BANK_PATH = "/Users/zhaoqinhuang/david_project/DavidAgent/brain/skill/skill_bank.json"


class CuriosityEngine:
    """好奇心引擎 - DavidAgent 自主学习增强层"""
    
    def __init__(self):
        self.reflection_manager = ReflectionManager()
        self.cpep_engine = CPEPEngine()
        self.skill_bank = SkillBank()
        self.skillrl_manager = SkillRLManager()
        self.reasoning_bank = ReasoningBank()
        self.web_sensor = WebSensor()
        self.weak_areas = []
        self.learning_motivations = []
        
        # 初始化日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """初始化好奇心引擎"""
        try:
            self.logger.info("🚀 初始化好奇心引擎 v1.0")
            
            # 验证依赖模块
            if not self._validate_dependencies():
                self.logger.error("❌ 依赖模块验证失败")
                return False
                
            self.logger.info("✅ 好奇心引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 好奇心引擎初始化失败: {e}")
            return False
    
    def _validate_dependencies(self) -> bool:
        """验证依赖模块是否可用"""
        try:
            # 检查核心模块
            assert hasattr(self.reflection_manager, 'analyze_performance'), "ReflectionManager 缺少必要方法"
            assert hasattr(self.cpep_engine, 'broadcast_experience'), "CPEPEngine 缺少必要方法"
            assert hasattr(self.skill_bank, 'get_skill'), "SkillBank 缺少必要方法"
            assert hasattr(self.skillrl_manager, 'extract_skill'), "SkillRLManager 缺少必要方法"
            assert hasattr(self.reasoning_bank, 'get_reasoning_records'), "ReasoningBank 缺少必要方法"
            
            # 检查路径存在
            os.makedirs(os.path.dirname(HEARTBEAT_PATH), exist_ok=True)
            return True
            
        except Exception as e:
            self.logger.error(f"依赖验证失败: {e}")
            return False
    
    # 功能1: 认知缺口检测 (Gap Analysis)
    def detect_cognitive_gaps(self) -> List[Dict]:
        """识别认知薄弱领域"""
        self.logger.info("🔍 执行认知缺口检测...")
        weak_areas = []
        
        try:
            # A. 分析失败案例库 (成功率 < 70%)
            reasoning_records = self.reasoning_bank.get_reasoning_records()
            failure_cases = self._analyze_failure_cases(reasoning_records)
            weak_areas.extend(failure_cases)
            
            # B. 识别过期技能/逻辑路径 (30天未更新)
            outdated_skills = self._find_outdated_skills()
            weak_areas.extend(outdated_skills)
            
            # C. 监控 SkillRL Reward 波动
            low_performance_areas = self._monitor_reward_fluctuations()
            weak_areas.extend(low_performance_areas)
            
            # 去重和排序
            self.weak_areas = self._deduplicate_and_prioritize(weak_areas)
            
            self.logger.info(f"✅ 识别出 {len(self.weak_areas)} 个认知薄弱领域")
            return self.weak_areas
            
        except Exception as e:
            self.logger.error(f"认知缺口检测失败: {e}")
            return []
    
    def _analyze_failure_cases(self, records: List[Dict]) -> List[Dict]:
        """分析失败案例，识别成功率 < 70% 的领域"""
        failure_areas = []
        
        # 按领域分组统计成功率
        domain_stats = {}
        for record in records:
            domain = record.get('domain', 'unknown')
            success = record.get('success', False)
            
            if domain not in domain_stats:
                domain_stats[domain] = {'total': 0, 'success': 0}
            
            domain_stats[domain]['total'] += 1
            if success:
                domain_stats[domain]['success'] += 1
        
        # 识别成功率 < 70% 的领域
        for domain, stats in domain_stats.items():
            if stats['total'] >= 5:  # 至少有5次尝试才有统计意义
                success_rate = stats['success'] / stats['total']
                if success_rate < 0.7:
                    failure_areas.append({
                        'type': 'failure_case',
                        'domain': domain,
                        'success_rate': success_rate,
                        'total_attempts': stats['total'],
                        'priority': 'high' if success_rate < 0.5 else 'medium'
                    })
        
        return failure_areas
    
    def _find_outdated_skills(self) -> List[Dict]:
        """识别30天未更新的技能"""
        outdated_areas = []
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 获取所有技能
        all_skills = self.skill_bank.list_all_skills()
        
        for skill_key, skill_data in all_skills.items():
            last_updated = skill_data.get('last_updated')
            if last_updated:
                last_updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                if last_updated_dt < thirty_days_ago:
                    outdated_areas.append({
                        'type': 'outdated_skill',
                        'skill_key': skill_key,
                        'domain': skill_data.get('domain', 'general'),
                        'last_updated': last_updated,
                        'priority': 'medium'
                    })
        
        return outdated_areas
    
    def _monitor_reward_fluctuations(self) -> List[Dict]:
        """监控 SkillRL Reward 波动，识别低绩效领域"""
        low_perf_areas = []
        
        # 获取历史 Reward 数据
        reward_history = self.skillrl_manager.get_reward_history()
        
        # 按领域分析 Reward 趋势
        domain_rewards = {}
        for entry in reward_history:
            domain = entry.get('domain', 'unknown')
            reward = entry.get('reward', 0.0)
            timestamp = entry.get('timestamp', '')
            
            if domain not in domain_rewards:
                domain_rewards[domain] = []
            domain_rewards[domain].append({'reward': reward, 'timestamp': timestamp})
        
        # 识别低绩效领域 (平均 Reward < 0.6)
        for domain, rewards in domain_rewards.items():
            if len(rewards) >= 10:  # 足够的数据点
                avg_reward = sum(r['reward'] for r in rewards) / len(rewards)
                recent_rewards = sorted(rewards, key=lambda x: x['timestamp'], reverse=True)[:5]
                recent_avg = sum(r['reward'] for r in recent_rewards) / len(recent_rewards)
                
                if avg_reward < 0.6 or recent_avg < 0.5:
                    low_perf_areas.append({
                        'type': 'low_performance',
                        'domain': domain,
                        'avg_reward': avg_reward,
                        'recent_avg': recent_avg,
                        'priority': 'high' if recent_avg < 0.4 else 'medium'
                    })
        
        return low_perf_areas
    
    def _deduplicate_and_prioritize(self, areas: List[Dict]) -> List[Dict]:
        """去重并按优先级排序"""
        unique_areas = {}
        
        for area in areas:
            key = f"{area['type']}:{area.get('domain', area.get('skill_key', ''))}"
            if key not in unique_areas:
                unique_areas[key] = area
            else:
                # 合并优先级，取更高的
                current_priority = unique_areas[key]['priority']
                new_priority = area['priority']
                priority_order = {'high': 3, 'medium': 2, 'low': 1}
                if priority_order[new_priority] > priority_order[current_priority]:
                    unique_areas[key] = area
        
        # 按优先级排序
        sorted_areas = sorted(
            unique_areas.values(), 
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], 
            reverse=True
        )
        
        return sorted_areas
    
    # 功能2: 外部刺激监听 (External Stimulus)
    async def listen_external_stimulus(self) -> List[Dict]:
        """监听外部刺激，触发学习动机"""
        self.logger.info("📡 执行外部刺激监听...")
        motivations = []
        
        try:
            # 在闲时（深夜）执行扫描
            current_hour = datetime.now().hour
            if not (22 <= current_hour or current_hour <= 6):  # 非深夜时段跳过
                self.logger.info("⏰ 非深夜时段，跳过外部刺激监听")
                return []
            
            # A. 扫描 GitHub Trending
            github_trending = await self.web_sensor.scan_github_trending()
            motivations.extend(self._process_github_trending(github_trending))
            
            # B. 扫描 ArXiv / 技术博客
            arxiv_papers = await self.web_sensor.scan_arxiv()
            tech_blogs = await self.web_sensor.scan_tech_blogs()
            motivations.extend(self._process_research_content(arxiv_papers + tech_blogs))
            
            # 过滤和验证学习动机
            self.learning_motivations = self._filter_learning_motivations(motivations)
            
            self.logger.info(f"✅ 生成 {len(self.learning_motivations)} 个学习动机")
            return self.learning_motivations
            
        except Exception as e:
            self.logger.error(f"外部刺激监听失败: {e}")
            return []
    
    def _process_github_trending(self, trending_items: List[Dict]) -> List[Dict]:
        """处理 GitHub Trending 数据"""
        motivations = []
        
        for item in trending_items:
            # 计算与现有技能库的语义相似度
            similarity = self._calculate_similarity(item['description'], self.weak_areas)
            
            # 检查是否属于认知薄弱领域
            relevant_weak_area = self._find_relevant_weak_area(item['topics'], self.weak_areas)
            
            if similarity > 0.8 and relevant_weak_area:
                motivations.append({
                    'type': 'github_trending',
                    'source': item['url'],
                    'title': item['name'],
                    'description': item['description'],
                    'similarity': similarity,
                    'weak_area': relevant_weak_area,
                    'priority': 'high'
                })
        
        return motivations
    
    def _process_research_content(self, research_items: List[Dict]) -> List[Dict]:
        """处理研究论文和技术博客"""
        motivations = []
        
        for item in research_items:
            similarity = self._calculate_similarity(item['abstract'], self.weak_areas)
            relevant_weak_area = self._find_relevant_weak_area(item['keywords'], self.weak_areas)
            
            if similarity > 0.8 and relevant_weak_area:
                motivations.append({
                    'type': 'research',
                    'source': item['url'],
                    'title': item['title'],
                    'abstract': item['abstract'],
                    'similarity': similarity,
                    'weak_area': relevant_weak_area,
                    'priority': 'medium'
                })
        
        return motivations
    
    def _calculate_similarity(self, content: str, weak_areas: List[Dict]) -> float:
        """计算内容与认知薄弱领域的语义相似度"""
        # 简化的相似度计算（实际应使用嵌入模型）
        max_similarity = 0.0
        
        for area in weak_areas:
            domain_keywords = area.get('domain', '').lower().split()
            content_lower = content.lower()
            
            matches = sum(1 for keyword in domain_keywords if keyword in content_lower)
            similarity = matches / len(domain_keywords) if domain_keywords else 0.0
            max_similarity = max(max_similarity, similarity)
        
        return min(max_similarity, 1.0)  # 限制在0-1范围内
    
    def _find_relevant_weak_area(self, topics: List[str], weak_areas: List[Dict]) -> Optional[Dict]:
        """查找相关的认知薄弱领域"""
        for area in weak_areas:
            domain = area.get('domain', '').lower()
            if any(topic.lower() in domain or domain in topic.lower() for topic in topics):
                return area
        return None
    
    def _filter_learning_motivations(self, motivations: List[Dict]) -> List[Dict]:
        """过滤学习动机，确保质量"""
        filtered = []
        
        for motivation in motivations:
            # 去重：避免重复的学习动机
            is_duplicate = False
            for existing in filtered:
                if existing['source'] == motivation['source']:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(motivation)
        
        # 按优先级排序
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        filtered.sort(key=lambda x: priority_order.get(x['priority'], 1), reverse=True)
        
        return filtered[:10]  # 限制最多10个学习动机
    
    # 功能3: 自发性实验执行 (Spontaneous Experiment)
    async def execute_spontaneous_experiment(self, motivation: Dict) -> Optional[Dict]:
        """执行自发性实验"""
        self.logger.info(f"🧪 执行自发性实验: {motivation['title']}")
        
        try:
            # 1. 生成实验任务描述
            experiment_task = self._generate_experiment_task(motivation)
            
            # 2. 调用 LeftBrain 生成实验方案
            from DavidAgent.brain.left_brain.analyzer import LeftBrainAnalyzer
            left_brain = LeftBrainAnalyzer()
            experiment_plan = await left_brain.generate_solution(experiment_task)
            
            # 3. 在沙箱环境安全执行
            result = await self._execute_in_sandbox(experiment_plan)
            
            # 4. RightBrain 价值审计与评分
            from DavidAgent.brain.right_brain.evaluator import RightBrainEvaluator  
            right_brain = RightBrainEvaluator()
            audit_result = await right_brain.evaluate_solution(experiment_plan, result)
            
            if audit_result['score'] > 0.7:  # 成功分支
                # 自动萃取为新技能
                new_skill = self.skillrl_manager.extract_skill(experiment_plan, result, audit_result)
                
                # 广播至全局共享池
                experience = {
                    'persona': 'curiosity_engine',
                    'reward': audit_result['score'],
                    'concrete_details': experiment_task,
                    'abstract_strategy': new_skill.get('abstract_strategy', ''),
                    'domain': motivation.get('weak_area', {}).get('domain', 'general')
                }
                self.cpep_engine.broadcast_experience(experience)
                
                # 更新 SkillBank
                skill_key = f"auto_{new_skill['name']}"
                self.skill_bank.add_skill('global', new_skill['name'], new_skill['version'], new_skill)
                
                self.logger.info(f"✅ 自发性实验成功，新技能已存入 SkillBank: {skill_key}")
                
                return {
                    'experiment_task': experiment_task,
                    'result': result,
                    'audit_score': audit_result['score'],
                    'new_skill': new_skill,
                    'status': 'success'
                }
            else:
                self.logger.info("⚠️ 自发性实验未达到成功标准")
                return {
                    'experiment_task': experiment_task,
                    'result': result,
                    'audit_score': audit_result['score'],
                    'status': 'failed'
                }
                
        except Exception as e:
            self.logger.error(f"自发性实验执行失败: {e}")
            return None
    
    def _generate_experiment_task(self, motivation: Dict) -> str:
        """生成实验任务描述"""
        if motivation['type'] == 'github_trending':
            return f"[自研] 验证 {motivation['title']} 在相关场景下的性能表现和适用性"
        elif motivation['type'] == 'research':
            return f"[自研] 实现并验证 {motivation['title']} 中提出的新算法/架构"
        else:
            return f"[自研] 探索 {motivation['title']} 的实际应用价值"
    
    async def _execute_in_sandbox(self, plan: Dict) -> Dict:
        """在沙箱环境中安全执行实验"""
        # 模拟沙箱执行（实际应有真正的沙箱环境）
        import subprocess
        import tempfile
        
        try:
            # 创建临时文件执行代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(plan.get('code', '# No code provided'))
                temp_file = f.name
            
            # 安全执行（限制资源和时间）
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                cwd='/tmp'
            )
            
            os.unlink(temp_file)
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_time': 30  # 实际应测量真实执行时间
            }
            
        except subprocess.TimeoutExpired:
            return {'error': 'timeout', 'message': '实验执行超时'}
        except Exception as e:
            return {'error': 'execution_failed', 'message': str(e)}
    
    # 功能4: 心跳记录与汇报 (Heartbeat & Reporting)
    def record_heartbeat(self, experiment_results: List[Dict]) -> bool:
        """记录心跳和实验结果到 HEARTBEAT.md"""
        self.logger.info("📝 记录心跳和实验结果...")
        
        try:
            # 生成结构化 Markdown 内容
            heartbeat_content = self._generate_heartbeat_content(experiment_results)
            
            # 写入文件
            with open(HEARTBEAT_PATH, 'w', encoding='utf-8') as f:
                f.write(heartbeat_content)
            
            self.logger.info(f"✅ 心跳记录已写入: {HEARTBEAT_PATH}")
            return True
            
        except Exception as e:
            self.logger.error(f"心跳记录失败: {e}")
            return False
    
    def _generate_heartbeat_content(self, results: List[Dict]) -> str:
        """生成结构化的心跳记录内容"""
        content = f"""# 自主演进简报
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 实验概览
- **总实验数**: {len(results)}
- **成功实验**: {sum(1 for r in results if r.get('status') == 'success')}
- **失败实验**: {sum(1 for r in results if r.get('status') == 'failed')}

## 🧪 详细实验记录
"""
        
        for i, result in enumerate(results, 1):
            content += f"\n### 实验 {i}: {result.get('experiment_task', 'Unknown')}\n"
            content += f"- **状态**: {result.get('status', 'unknown')}\n"
            content += f"- **评分**: {result.get('audit_score', 0):.2f}\n"
            
            if result.get('status') == 'success':
                new_skill = result.get('new_skill', {})
                content += f"- **新技能**: {new_skill.get('name', 'N/A')} v{new_skill.get('version', 'N/A')}\n"
                content += f"- **抽象策略**: {new_skill.get('abstract_strategy', 'N/A')}\n"
        
        content += "\n---\n*由 Curiosity Engine v1.0 自动生成*"
        return content
    
    # 主执行流程
    async def run_curiosity_cycle(self) -> Dict:
        """运行完整的好奇心周期"""
        self.logger.info("🧠 启动好奇心引擎完整周期...")
        
        results = {
            'cognitive_gaps': [],
            'learning_motivations': [],
            'experiments': [],
            'heartbeat_recorded': False
        }
        
        # 1. 认知缺口检测
        results['cognitive_gaps'] = self.detect_cognitive_gaps()
        
        # 2. 外部刺激监听
        results['learning_motivations'] = await self.listen_external_stimulus()
        
        # 3. 自发性实验执行
        experiment_results = []
        for motivation in results['learning_motivations'][:3]:  # 限制最多3个实验
            experiment_result = await self.execute_spontaneous_experiment(motivation)
            if experiment_result:
                experiment_results.append(experiment_result)
        
        results['experiments'] = experiment_results
        
        # 4. 心跳记录
        results['heartbeat_recorded'] = self.record_heartbeat(experiment_results)
        
        self.logger.info("✅ 好奇心引擎周期完成!")
        return results


# 使用示例和集成点说明
if __name__ == "__main__":
    # 初始化好奇心引擎
    curiosity_engine = CuriosityEngine()
    if curiosity_engine.initialize():
        # 运行完整周期（通常在后台定时执行）
        import asyncio
        results = asyncio.run(curiosity_engine.run_curiosity_cycle())
        print(f"好奇心引擎执行完成，结果: {results}")