"""
SkillRL管理器
"""

import os
import json
from typing import Dict, Any, List

class SkillRLManager:
    """SkillRL管理器，负责递归技能增强强化学习相关操作"""
    
    def __init__(self, base_path: str = "/Users/zhaoqinhuang/david_project/SkillRL"):
        self.base_path = base_path
        self.skills_path = os.path.join(base_path, "skills")
        self.experience_path = os.path.join(base_path, "experience")
        
        # 确保目录存在
        os.makedirs(self.skills_path, exist_ok=True)
        os.makedirs(self.experience_path, exist_ok=True)
    
    def save_successful_strategy(self, strategy_name: str, strategy_info: Dict[str, Any]):
        """保存成功策略到技能库"""
        skill_file = os.path.join(self.skills_path, f"{strategy_name}.json")
        with open(skill_file, 'w', encoding='utf-8') as f:
            json.dump(strategy_info, f, ensure_ascii=False, indent=2)
    
    def save_failure_case(self, strategy_name: str, failure_info: Dict[str, Any]):
        """保存失败案例到经验库"""
        failure_file = os.path.join(self.experience_path, f"{strategy_name}_failure.json")
        with open(failure_file, 'w', encoding='utf-8') as f:
            json.dump(failure_info, f, ensure_ascii=False, indent=2)
    
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """获取所有技能"""
        skills = []
        for filename in os.listdir(self.skills_path):
            if filename.endswith('.json'):
                with open(os.path.join(self.skills_path, filename), 'r', encoding='utf-8') as f:
                    skills.append(json.load(f))
        return skills