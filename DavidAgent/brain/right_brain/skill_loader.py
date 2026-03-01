"""
右脑技能加载器 - 动态从 SkillBank 加载相关技能
"""

from typing import List, Dict
from brain.memory.skill_bank import get_skill_bank


def load_skills_for_persona(persona: str, limit: int = 5) -> List[Dict]:
    """
    为指定 persona 加载相关技能
    
    Args:
        persona: 数字分身标识 (如 'tech_enthusiast', 'corporate_cdo')
        limit: 返回技能数量限制
        
    Returns:
        技能列表，按成功率降序排列
    """
    skill_bank = get_skill_bank()
    skills = skill_bank.get_skills_for_persona(persona, limit)
    return skills

def format_skills_for_prompt(skills: List[Dict]) -> str:
    """
    将技能格式化为 Prompt 可读的字符串
    
    Args:
        skills: 技能列表
        
    Returns:
        格式化的技能字符串
    """
    if not skills:
        return ""
        
    formatted_skills = []
    for i, skill in enumerate(skills, 1):
        usage_count = skill.get('usage_count', 0)
        success_count = skill.get('success_count', 0)
        success_rate = success_count / usage_count if usage_count > 0 else 0
        formatted_skills.append(
            f"{i}. {skill['rule_description']} "
            f"(成功应用 {usage_count} 次，成功率 {success_rate:.1%})"
        )
    
    return "\n".join(formatted_skills)

def update_skill_usage(skill_id: str, success: bool):
    """
    更新技能使用统计
    
    Args:
        skill_id: 技能ID
        success: 是否成功通过左脑审核
    """
    skill_bank = get_skill_bank()
    skill_bank.increment_usage(skill_id)
    if success:
        skill_bank.increment_success(skill_id)