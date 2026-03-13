"""
SkillBank - SkillRL 的存储增强层

作为 SkillRL 体系的存储后端，提供：
- 命名空间管理 ({persona_id}::{skill_name}::v{version})
- 分身隔离（同名技能不会互相覆盖）
- 灰度状态管理（incubating/stable/deprecated）
- 与 digital_personas.json 的持久化集成

SkillRL 调用此模块来存储和检索技能，而不是直接操作 JSON 文件。
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

class SkillBank:
    """SkillRL 的存储增强层"""
    
    def __init__(self, personas_file: str = "DavidAgent/digital_personas.json"):
        self.personas_file = personas_file
        self._load_personas()
    
    def _load_personas(self):
        """加载数字分身配置"""
        if os.path.exists(self.personas_file):
            with open(self.personas_file, 'r', encoding='utf-8') as f:
                self.personas = json.load(f)
        else:
            self.personas = {}
    
    def _save_personas(self):
        """保存数字分身配置"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.personas_file), exist_ok=True)
        
        with open(self.personas_file, 'w', encoding='utf-8') as f:
            json.dump(self.personas, f, ensure_ascii=False, indent=2)
    
    def _validate_namespace(self, namespace: str) -> Dict[str, str]:
        """
        验证并解析命名空间格式
        支持格式：
        - {persona_id}::{skill_name}::v{version}
        - global::skill_name::v{version}
        """
        pattern = r'^(?P<persona>[^:]+)::(?P<skill>[^:]+)::v(?P<version>\d+\.\d+)$'
        match = re.match(pattern, namespace)
        
        if not match:
            raise ValueError(f"Invalid namespace format: {namespace}. Expected format: persona::skill_name::vX.X")
        
        return {
            'persona_id': match.group('persona'),
            'skill_name': match.group('skill'),
            'version': f"v{match.group('version')}"
        }
    
    def store_skill(self, namespace: str, skill_data: Dict[str, Any]) -> bool:
        """
        存储技能到指定命名空间
        
        Args:
            namespace: 命名空间字符串 (persona::skill_name::vX.X)
            skill_data: 技能数据字典
            
        Returns:
            bool: 是否成功存储
        """
        try:
            parsed = self._validate_namespace(namespace)
            persona_id = parsed['persona_id']
            skill_name = parsed['skill_name']
            version = parsed['version']
            
            # 检查是否存在冲突
            if self.skill_exists(namespace):
                existing_skill = self.get_skill(namespace)
                if existing_skill.get('status') == 'stable':
                    # stable 技能不能被覆盖
                    raise ValueError(f"Cannot overwrite stable skill: {namespace}")
                elif existing_skill.get('code') == skill_data.get('code'):
                    # 代码相同，可能是重复存储，跳过
                    return False
            
            # 确保分身存在
            if persona_id != 'global' and persona_id not in self.personas:
                raise ValueError(f"Persona {persona_id} not found in digital_personas.json")
            
            # 初始化技能结构
            if persona_id == 'global':
                # 全局技能需要特殊处理
                if 'global_skills' not in self.personas:
                    self.personas['global_skills'] = {}
                target_dict = self.personas['global_skills']
            else:
                # 分身技能
                if 'skills' not in self.personas[persona_id]:
                    self.personas[persona_id]['skills'] = {}
                target_dict = self.personas[persona_id]['skills']
            
            # 存储技能
            target_dict[skill_name] = {
                'version': version,
                'status': skill_data.get('status', 'incubating'),
                'reward': skill_data.get('reward', 0.0),
                'test_count': skill_data.get('test_count', 0),
                'code': skill_data.get('code', ''),
                'created_at': skill_data.get('created_at', ''),
                'last_used': skill_data.get('last_used', '')
            }
            
            self._save_personas()
            return True
            
        except Exception as e:
            print(f"Error storing skill {namespace}: {e}")
            return False
    
    def get_skill(self, namespace: str) -> Optional[Dict[str, Any]]:
        """
        获取指定命名空间的技能
        
        Args:
            namespace: 命名空间字符串
            
        Returns:
            Dict or None: 技能数据或 None
        """
        try:
            parsed = self._validate_namespace(namespace)
            persona_id = parsed['persona_id']
            skill_name = parsed['skill_name']
            
            if persona_id == 'global':
                if 'global_skills' in self.personas and skill_name in self.personas['global_skills']:
                    return self.personas['global_skills'][skill_name]
            else:
                if (persona_id in self.personas and 
                    'skills' in self.personas[persona_id] and 
                    skill_name in self.personas[persona_id]['skills']):
                    return self.personas[persona_id]['skills'][skill_name]
            
            return None
            
        except Exception as e:
            print(f"Error getting skill {namespace}: {e}")
            return None
    
    def skill_exists(self, namespace: str) -> bool:
        """检查技能是否存在"""
        return self.get_skill(namespace) is not None
    
    def list_skills(self, persona_id: Optional[str] = None) -> List[str]:
        """
        列出所有技能的命名空间
        
        Args:
            persona_id: 可选，指定分身ID来过滤
            
        Returns:
            List[str]: 命名空间列表
        """
        namespaces = []
        
        # 添加全局技能
        if persona_id is None or persona_id == 'global':
            if 'global_skills' in self.personas:
                for skill_name in self.personas['global_skills']:
                    namespaces.append(f"global::{skill_name}::{self.personas['global_skills'][skill_name]['version']}")
        
        # 添加分身技能
        for pid, persona_data in self.personas.items():
            if pid == 'global_skills':
                continue
                
            if persona_id is not None and pid != persona_id:
                continue
                
            if 'skills' in persona_data:
                for skill_name, skill_data in persona_data['skills'].items():
                    namespaces.append(f"{pid}::{skill_name}::{skill_data['version']}")
        
        return namespaces
    
    def promote_to_global(self, source_namespace: str, owner_authorized: bool = False) -> bool:
        """
        将分身技能提升为全局技能（需要 OwnerMemoryManager 授权）
        
        Args:
            source_namespace: 源技能命名空间
            owner_authorized: 是否已获得 OwnerMemoryManager 授权
            
        Returns:
            bool: 是否成功提升
        """
        if not owner_authorized:
            raise PermissionError("OwnerMemoryManager authorization required to promote skills to global")
        
        skill_data = self.get_skill(source_namespace)
        if not skill_data:
            return False
        
        # 解析源命名空间
        parsed = self._validate_namespace(source_namespace)
        skill_name = parsed['skill_name']
        version = parsed['version']
        
        # 创建全局命名空间
        global_namespace = f"global::{skill_name}::{version}"
        
        # 存储为全局技能
        return self.store_skill(global_namespace, skill_data)
    
    def update_skill_status(self, namespace: str, new_status: str) -> bool:
        """
        更新技能状态
        
        Args:
            namespace: 技能命名空间
            new_status: 新状态 (incubating/stable/deprecated)
            
        Returns:
            bool: 是否成功更新
        """
        if new_status not in ['incubating', 'stable', 'deprecated']:
            raise ValueError(f"Invalid status: {new_status}")
        
        skill_data = self.get_skill(namespace)
        if not skill_data:
            return False
        
        skill_data['status'] = new_status
        return self.store_skill(namespace, skill_data)


# SkillRL 调用接口
def skill_bank_store(persona_id: str, skill_name: str, version: str, skill_data: Dict[str, Any]) -> bool:
    """
    SkillRL 调用的存储接口
    
    Args:
        persona_id: 分身ID
        skill_name: 技能名称  
        version: 版本号 (如 "1.0")
        skill_data: 技能数据
        
    Returns:
        bool: 是否成功存储
    """
    bank = SkillBank()
    namespace = f"{persona_id}::{skill_name}::v{version}"
    return bank.store_skill(namespace, skill_data)


def skill_bank_get(persona_id: str, skill_name: str, version: str) -> Optional[Dict[str, Any]]:
    """
    SkillRL 调用的获取接口
    """
    bank = SkillBank()
    namespace = f"{persona_id}::{skill_name}::v{version}"
    return bank.get_skill(namespace)


def skill_bank_list(persona_id: Optional[str] = None) -> List[str]:
    """
    SkillRL 调用的列表接口
    """
    bank = SkillBank()
    return bank.list_skills(persona_id)