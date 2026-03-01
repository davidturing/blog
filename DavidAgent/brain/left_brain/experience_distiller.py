"""
经验蒸馏器 (Experience Distiller)
基于《SkillRL》论文实现的技能提取模块
将失败草稿、驳回意见和最终定稿蒸馏为结构化技能规则
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from brain.left_brain.left_brain import LeftBrainGemini


class ExperienceDistiller:
    """经验蒸馏器 - 将试错轨迹压缩为肌肉记忆"""
    
    def __init__(self):
        self.left_brain = LeftBrainGemini()
    
    async def distill_experience(self, 
                              failed_draft: str,
                              review_feedback: str, 
                              final_draft: str,
                              persona: str) -> List[Dict[str, Any]]:
        """
        执行经验蒸馏，从失败到成功的完整轨迹中提取技能规则
        
        Args:
            failed_draft: 右脑的第一版失败草稿
            review_feedback: 左脑的驳回意见
            final_draft: 最终通过的定稿
            persona: 适用的角色分身 (如 'corporate_cdo', 'tech_enthusiast')
            
        Returns:
            List[Dict]: 提取的技能规则列表
        """
        if not all([failed_draft, review_feedback, final_draft]):
            print("⚠️ [经验蒸馏] 缺少必要输入，跳过蒸馏")
            return []
        
        # 构建蒸馏 Prompt
        distillation_prompt = f"""
【左脑反思指令】：
作为系统的法官，请对比最初的失败草稿与最终的成功定稿。
提取出 1-2 条通用或针对特定角色（{persona}）的"避坑指南"或"高光技巧"。

**失败草稿**：
{failed_draft}

**驳回意见**：
{review_feedback}

**最终定稿**：
{final_draft}

请输出极其凝练的 JSON 格式数组，每个元素包含：
- persona: 适用分身（'{persona}' 或 'ALL'代表通用）
- skill_type: 'anti_pattern' (避坑) 或 'best_practice' (最佳实践)  
- rule: 具体的技能规则描述（自然语言）

示例输出：
[
    {{
        "persona": "{persona}",
        "skill_type": "anti_pattern", 
        "rule": "汇报数据治理时，不要罗列底层组件库的名字，必须转化为业务视角的 SLA 和 ROI。"
    }},
    {{
        "persona": "ALL",
        "skill_type": "best_practice",
        "rule": "技术文章必须包含可复现的代码示例和实际应用场景。"
    }}
]

只输出 JSON 数组，不要任何其他文字。
"""
        
        try:
            # 调用左脑进行蒸馏
            response = await asyncio.to_thread(
                self.left_brain.model.generate_content,
                distillation_prompt
            )
            distilled_skills_json = response.text
            
            # 解析 JSON
            skills = json.loads(distilled_skills_json)
            
            # 验证和清理技能
            validated_skills = []
            for skill in skills:
                if self._validate_skill(skill, persona):
                    validated_skills.append(skill)
                else:
                    print(f"⚠️ [经验蒸馏] 无效技能被过滤: {skill}")
            
            print(f"✅ [经验蒸馏] 成功提取 {len(validated_skills)} 条技能规则")
            return validated_skills
            
        except json.JSONDecodeError as e:
            print(f"❌ [经验蒸馏] JSON 解析失败: {e}")
            return []
        except Exception as e:
            print(f"❌ [经验蒸馏] 蒸馏过程异常: {e}")
            return []
    
    def _validate_skill(self, skill: Dict[str, Any], expected_persona: str) -> bool:
        """验证技能规则的有效性"""
        required_fields = ['persona', 'skill_type', 'rule']
        if not all(field in skill for field in required_fields):
            return False
        
        if skill['persona'] not in [expected_persona, 'ALL']:
            return False
            
        if skill['skill_type'] not in ['anti_pattern', 'best_practice']:
            return False
            
        if not isinstance(skill['rule'], str) or len(skill['rule'].strip()) < 10:
            return False
            
        return True
    
    async def distill_from_blackboard(self, blackboard_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从黑板状态中提取必要的信息并执行经验蒸馏
        
        Args:
            blackboard_state: 黑板的完整状态快照
            
        Returns:
            List[Dict]: 提取的技能规则
        """
        # 从黑板状态中提取必要信息
        failed_draft = blackboard_state.get('draft_content')
        review_feedback = blackboard_state.get('review_feedback') 
        final_draft = blackboard_state.get('published_content', '')  # 假设发布后会存储
        
        # 获取当前 persona（需要从系统配置或其他地方获取）
        persona = self._get_current_persona(blackboard_state)
        
        return await self.distill_experience(
            failed_draft=failed_draft,
            review_feedback=review_feedback,
            final_draft=final_draft,
            persona=persona
        )
    
    def _get_current_persona(self, blackboard_state: Dict[str, Any]) -> str:
        """从黑板状态或系统配置中获取当前 persona"""
        # 这里需要根据实际的 persona 管理逻辑来实现
        # 暂时返回默认值，后续需要完善
        topic_id = blackboard_state.get('topic_id', '')
        if 'tech' in topic_id.lower() or 'ai' in topic_id.lower():
            return 'tech_enthusiast'
        else:
            return 'corporate_cdo'


# 全局经验蒸馏器实例
_EXPERIENCE_DISTILLER = None

def get_experience_distiller() -> ExperienceDistiller:
    """获取全局经验蒸馏器实例"""
    global _EXPERIENCE_DISTILLER
    if _EXPERIENCE_DISTILLER is None:
        _EXPERIENCE_DISTILLER = ExperienceDistiller()
    return _EXPERIENCE_DISTILLER