#!/usr/bin/env python3
"""
DavidAgent 2.0 SkillRL 架构测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.app import AGEngine
from brain.memory.skill_bank import SkillBank


async def test_skillrl_workflow():
    """测试完整的 SkillRL 工作流"""
    print("=" * 60)
    print("🧪 测试 DavidAgent 2.0 SkillRL 架构")
    print("=" * 60)
    
    # 1. 初始化技能库
    skill_bank = SkillBank()
    print("✅ 技能库初始化完成")
    
    # 2. 创建测试数据
    test_data = {
        'topic_id': 'test_skillrl_001',
        'raw_source': '测试推文内容：AI Agent 架构的最新进展',
        'extracted_graph': {
            'entities': ['AI Agent', 'SkillRL', 'Multi-Agent'],
            'triples': [
                ('AI Agent', 'uses', 'SkillRL'),
                ('SkillRL', 'enables', 'Multi-Agent')
            ]
        },
        'draft_content': '这是右脑生成的初稿，包含一些错误...',
        'review_feedback': '左脑的审查意见：需要更准确地描述 SkillRL 的作用',
        'final_draft': '这是修正后的最终稿，准确描述了 SkillRL 的价值'
    }
    
    # 3. 模拟经验蒸馏
    from brain.left_brain.experience_distiller import ExperienceDistiller
    distiller = ExperienceDistiller()
    
    distilled_skills = await distiller.distill_experience(
        persona='tech_enthusiast',
        failed_draft=test_data['draft_content'],
        review_feedback=test_data['review_feedback'],
        final_draft=test_data['final_draft']
    )
    
    print(f"✅ 经验蒸馏完成，提取出 {len(distilled_skills)} 条技能")
    for i, skill in enumerate(distilled_skills, 1):
        print(f"   {i}. {skill['rule']}")
        
        # 4. 保存技能到技能库
        skill_bank.add_skill(
            skill_id=f"test_{i:03d}",
            persona=skill['persona'],
            skill_type=skill['skill_type'],
            rule_description=skill['rule']
        )
    
    # 5. 测试技能加载
    from brain.right_brain.skill_loader import load_skills_for_persona
    loaded_skills = load_skills_for_persona('tech_enthusiast', limit=5)
    print(f"\n✅ 技能加载测试完成，加载了 {len(loaded_skills)} 条技能")
    
    # 6. 测试突触修剪
    from synaptic_pruning import prune_unused_skills
    pruned_count = await prune_unused_skills(days_threshold=0, min_usage=0, success_rate_threshold=0.0)
    print(f"✅ 突触修剪测试完成，清理了 {pruned_count} 条技能")
    
    print("\n🎉 DavidAgent 2.0 SkillRL 架构测试全部通过！")


if __name__ == "__main__":
    asyncio.run(test_skillrl_workflow())