#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPEP (Cross-Persona Experience Protocol) - 跨分身经验共享引擎
核心定位：所有数字分身的"胼胝体（Corpus Callosum）"
功能：经验跨分身共享、全局避坑、技能自动转发、群体智能协同
"""

import os
import json
import asyncio
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

# 导入现有模块
from DavidAgent.brain.skill_bank import SkillBank
from DavidAgent.brain.reasoning_bank import ReasoningBank
from DavidAgent.memory.owner_memory_manager import OwnerMemoryManager
from DavidAgent.controller import LeftBrainAnalyzer


class CPEPEngine:
    """CPEP 跨分身经验共享引擎"""
    
    def __init__(self):
        self.shared_experiences_path = Path("DavidAgent/hippocampus/logical/shared_experiences.md")
        self.shared_experiences_path.parent.mkdir(parents=True, exist_ok=True)
        self.skill_bank = SkillBank()
        self.reasoning_bank = ReasoningBank()
        self.left_brain = LeftBrainAnalyzer()
        self.owner_memory = OwnerMemoryManager()
        
        # 初始化共享经验池文件
        if not self.shared_experiences_path.exists():
            self.shared_experiences_path.write_text("# Shared Experiences Pool\n\n")
            
        # 经验缓存（内存中）
        self.experience_cache: Dict[str, Dict] = {}
        self._cache_lock = threading.Lock()
        
    def broadcast_experience(self, 
                          persona_id: str, 
                          experience: Dict[str, Any], 
                          reward: float) -> bool:
        """
        广播高分经验到共享池
        
        Args:
            persona_id: 分身ID
            experience: 经验数据（包含技能、推理路径等）
            reward: 奖励分数
            
        Returns:
            bool: 广播是否成功
        """
        if reward <= 0.85:
            return False
            
        try:
            # 1. 左脑抽象化处理
            abstracted_experience = self._abstract_experience(experience)
            
            # 2. 生成经验哈希（用于去重）
            exp_hash = self._generate_experience_hash(abstracted_experience)
            
            # 3. 写入共享经验池
            with self._cache_lock:
                if exp_hash not in self.experience_cache:
                    self.experience_cache[exp_hash] = {
                        'persona_id': persona_id,
                        'timestamp': datetime.now().isoformat(),
                        'reward': reward,
                        'abstracted_experience': abstracted_experience,
                        'hash': exp_hash
                    }
                    
                    # 异步写入共享池文件
                    asyncio.create_task(self._async_write_to_shared_pool(
                        exp_hash, 
                        self.experience_cache[exp_hash]
                    ))
                    
            return True
            
        except Exception as e:
            print(f"CPEP broadcast error: {e}")
            return False
    
    def request_synergy(self, 
                       current_persona: str, 
                       task_context: Dict[str, Any],
                       similarity_threshold: float = 0.85) -> List[Dict]:
        """
        请求其他分身的相关经验
        
        Args:
            current_persona: 当前分身ID
            task_context: 当前任务上下文
            similarity_threshold: 相似度阈值
            
        Returns:
            List[Dict]: 相关经验列表
        """
        relevant_experiences = []
        
        try:
            # 1. 计算任务上下文的特征向量
            task_features = self._extract_task_features(task_context)
            
            # 2. 检索相关经验
            with self._cache_lock:
                for exp_hash, experience in self.experience_cache.items():
                    if experience['persona_id'] == current_persona:
                        continue  # 跳过自己的经验
                        
                    # 计算相似度
                    similarity = self._calculate_similarity(
                        task_features, 
                        experience['abstracted_experience']
                    )
                    
                    if similarity >= similarity_threshold:
                        # 3. 注入经验到上下文
                        formatted_experience = {
                            'source': f"[CPEP_EXPERIENCE] 来自 {experience['persona_id']} 分身",
                            'content': experience['abstracted_experience'],
                            'similarity': similarity,
                            'reward': experience['reward']
                        }
                        relevant_experiences.append(formatted_experience)
                        
            # 4. 按相似度排序（降序）
            relevant_experiences.sort(key=lambda x: x['similarity'], reverse=True)
            
            return relevant_experiences[:3]  # 最多返回3个最相关经验
            
        except Exception as e:
            print(f"CPEP synergy request error: {e}")
            return []
    
    def synchronize_globals(self) -> List[str]:
        """
        同步全局技能
        
        Returns:
            List[str]: 新晋升的全局技能列表
        """
        new_global_skills = []
        
        try:
            # 1. 查找跨分身通用高分技能
            cross_persona_skills = self._find_cross_persona_high_score_skills()
            
            for skill_key, skill_data in cross_persona_skills.items():
                # 2. 晋升为全局技能
                global_skill_key = f"global::{skill_data['skill_name']}::v{skill_data['version']}"
                
                # 3. 通过 OwnerMemoryManager 授权
                if self.owner_memory.authorize_global_skill(skill_key):
                    # 4. 写入全局技能区
                    success = self.skill_bank.promote_to_global(
                        skill_key, 
                        self.owner_memory.get_authorization_token()
                    )
                    
                    if success:
                        new_global_skills.append(global_skill_key)
                        
        except Exception as e:
            print(f"CPEP global synchronization error: {e}")
            
        return new_global_skills
    
    def _abstract_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """左脑抽象化：将具体内容抽象成通用策略"""
        try:
            # 使用左脑分析器进行抽象
            abstracted = self.left_brain.abstract_concrete_details(experience)
            
            # 确保抽象后的经验符合三层次结构
            return self._structure_experience_by_levels(abstracted)
            
        except Exception as e:
            # 如果抽象失败，使用基础抽象策略
            return self._basic_abstraction(experience)
    
    def _basic_abstraction(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """基础抽象策略"""
        abstracted = {}
        
        # L1: 原子技能
        if 'skills' in experience:
            abstracted['L1_skills'] = []
            for skill in experience['skills']:
                # 抽象具体技术细节
                abstract_skill = self._abstract_skill(skill)
                abstracted['L1_skills'].append(abstract_skill)
        
        # L2: 推理路径
        if 'reasoning_path' in experience:
            abstracted['L2_reasoning'] = self._abstract_reasoning_path(
                experience['reasoning_path']
            )
        
        # L3: 元认知
        if 'meta_cognition' in experience:
            abstracted['L3_meta_cognition'] = self._abstract_meta_cognition(
                experience['meta_cognition']
            )
            
        return abstracted
    
    def _abstract_skill(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """抽象原子技能"""
        # 移除具体实现细节，保留通用模式
        abstract_skill = {
            'pattern': skill.get('pattern', 'unknown'),
            'category': self._categorize_skill(skill),
            'optimization_strategy': skill.get('optimization_strategy', 'general')
        }
        return abstract_skill
    
    def _categorize_skill(self, skill: Dict[str, Any]) -> str:
        """技能分类"""
        code = skill.get('code', '').lower()
        
        if 'polars' in code or 'lazy' in code:
            return 'high_performance_computing'
        elif 'io' in code or 'file' in code:
            return 'low_latency_io'
        elif 'batch' in code or 'vectorized' in code:
            return 'batch_processing_optimization'
        elif 'cache' in code or 'memory' in code:
            return 'memory_efficiency'
        else:
            return 'general_optimization'
    
    def _abstract_reasoning_path(self, reasoning_path: List[str]) -> List[str]:
        """抽象推理路径"""
        # 移除具体问题细节，保留通用推理模式
        abstracted_path = []
        for step in reasoning_path:
            if 'specific' in step.lower() or 'concrete' in step.lower():
                continue
            abstracted_path.append(step)
        return abstracted_path
    
    def _abstract_meta_cognition(self, meta_cognition: Dict[str, Any]) -> Dict[str, Any]:
        """抽象元认知"""
        return {
            'learning_pattern': meta_cognition.get('learning_pattern', 'adaptive'),
            'error_handling': meta_cognition.get('error_handling', 'robust'),
            'optimization_focus': meta_cognition.get('optimization_focus', 'efficiency')
        }
    
    def _structure_experience_by_levels(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """按三层次结构化经验"""
        structured = {}
        
        # L1: 原子技能 → SkillBank
        if 'skills' in experience:
            structured['L1_skills'] = experience['skills']
            
        # L2: 推理路径 → ReasoningBank  
        if 'reasoning_path' in experience:
            structured['L2_reasoning'] = experience['reasoning_path']
            
        # L3: 元认知 → Memory Alpha
        if 'meta_cognition' in experience:
            structured['L3_meta_cognition'] = experience['meta_cognition']
            
        return structured
    
    def _generate_experience_hash(self, experience: Dict[str, Any]) -> str:
        """生成经验哈希（用于去重）"""
        exp_str = json.dumps(experience, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(exp_str.encode('utf-8')).hexdigest()
    
    def _extract_task_features(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """提取任务特征向量"""
        features = {
            'domain': task_context.get('domain', 'general'),
            'complexity': task_context.get('complexity', 'medium'),
            'data_size': task_context.get('data_size', 'small'),
            'optimization_needs': task_context.get('optimization_needs', [])
        }
        return features
    
    def _calculate_similarity(self, 
                            task_features: Dict[str, Any], 
                            experience: Dict[str, Any]) -> float:
        """计算任务与经验的相似度"""
        # 简单的相似度计算（实际可使用更复杂的向量相似度）
        score = 0.0
        total_weight = 0
        
        # 领域匹配
        if task_features.get('domain') == experience.get('domain'):
            score += 0.4
        total_weight += 0.4
        
        # 复杂度匹配
        if task_features.get('complexity') == experience.get('complexity'):
            score += 0.3
        total_weight += 0.3
        
        # 优化需求匹配
        task_opt = set(task_features.get('optimization_needs', []))
        exp_opt = set(experience.get('optimization_needs', []))
        if task_opt & exp_opt:
            score += 0.3 * len(task_opt & exp_opt) / max(len(task_opt), len(exp_opt))
        total_weight += 0.3
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _find_cross_persona_high_score_skills(self) -> Dict[str, Dict]:
        """查找跨分身通用高分技能"""
        cross_skills = {}
        
        # 从 SkillBank 获取所有分身的技能
        all_skills = self.skill_bank.list_all_skills()
        
        # 按技能名称分组
        skill_groups = {}
        for skill_key, skill_data in all_skills.items():
            if '::' in skill_key:
                parts = skill_key.split('::')
                if len(parts) >= 3:
                    skill_name = parts[1]
                    if skill_name not in skill_groups:
                        skill_groups[skill_name] = []
                    skill_groups[skill_name].append((skill_key, skill_data))
        
        # 找出被多个分身使用的高分技能
        for skill_name, skills in skill_groups.items():
            if len(skills) >= 2:  # 至少2个分身使用
                high_score_skills = [
                    (key, data) for key, data in skills 
                    if data.get('reward', 0) > 0.85
                ]
                if high_score_skills:
                    # 选择奖励分数最高的
                    best_skill = max(high_score_skills, key=lambda x: x[1].get('reward', 0))
                    cross_skills[best_skill[0]] = {
                        'skill_name': skill_name,
                        'version': best_skill[1].get('version', 'v1.0'),
                        'reward': best_skill[1].get('reward', 0)
                    }
        
        return cross_skills
    
    async def _async_write_to_shared_pool(self, 
                                        exp_hash: str, 
                                        experience: Dict[str, Any]):
        """异步写入共享经验池"""
        try:
            experience_entry = f"""
## Experience: {exp_hash}
- **Source Persona**: {experience['persona_id']}
- **Timestamp**: {experience['timestamp']}
- **Reward**: {experience['reward']:.2f}
- **Abstracted Experience**:
```json
{json.dumps(experience['abstracted_experience'], indent=2, ensure_ascii=False)}
```

---
"""
            
            # 异步写入文件
            with open(self.shared_experiences_path, 'a', encoding='utf-8') as f:
                f.write(experience_entry)
                
        except Exception as e:
            print(f"Async write to shared pool error: {e}")
    
    def cross_persona_reflexion_alignment(self, 
                                        current_persona: str,
                                        potential_error: Dict[str, Any]) -> Optional[Dict]:
        """
        跨分身纠错（Reflexion 对齐）
        如果当前分身要犯的错误，其他分身已经解决，则注入避坑规则
        """
        try:
            # 从 ReasoningBank 查找相关的避坑规则
            error_signature = self._generate_error_signature(potential_error)
            avoidance_rules = self.reasoning_bank.get_avoidance_rules(error_signature)
            
            if avoidance_rules:
                # 检查是否有其他分身已经解决了这个问题
                for rule in avoidance_rules:
                    if rule.get('source_persona') != current_persona:
                        return {
                            'intercepted': True,
                            'avoidance_rule': rule,
                            'reference_sop': rule.get('reference_sop', ''),
                            'source_persona': rule.get('source_persona')
                        }
                        
            return None
            
        except Exception as e:
            print(f"Cross-persona reflexion alignment error: {e}")
            return None
    
    def _generate_error_signature(self, error: Dict[str, Any]) -> str:
        """生成错误签名"""
        error_str = f"{error.get('type', '')}:{error.get('context', '')}"
        return hashlib.md5(error_str.encode('utf-8')).hexdigest()


# 全局 CPEP 引擎实例
_cpep_engine_instance = None
_cpep_lock = threading.Lock()

def get_cpep_engine() -> CPEPEngine:
    """获取全局 CPEP 引擎实例"""
    global _cpep_engine_instance
    with _cpep_lock:
        if _cpep_engine_instance is None:
            _cpep_engine_instance = CPEPEngine()
        return _cpep_engine_instance


# 便捷函数
def broadcast_experience(persona_id: str, experience: Dict[str, Any], reward: float) -> bool:
    """广播经验的便捷函数"""
    return get_cpep_engine().broadcast_experience(persona_id, experience, reward)


def request_synergy(current_persona: str, task_context: Dict[str, Any]) -> List[Dict]:
    """请求协同经验的便捷函数"""
    return get_cpep_engine().request_synergy(current_persona, task_context)


def synchronize_globals() -> List[str]:
    """同步全局技能的便捷函数"""
    return get_cpep_engine().synchronize_globals()


def cross_persona_reflexion_alignment(current_persona: str, potential_error: Dict[str, Any]) -> Optional[Dict]:
    """跨分身纠错的便捷函数"""
    return get_cpep_engine().cross_persona_reflexion_alignment(current_persona, potential_error)