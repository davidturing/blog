#!/usr/bin/env python3
"""
突触修剪 (Synaptic Pruning) - DavidAgent 2.0 的遗忘机制
基于《SkillRL》论文实现的技能库自动优化
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from brain.memory.skill_bank import get_skill_bank


def prune_unused_skills():
    """清理僵尸技能（长时间未激活且使用次数少的技能）"""
    skill_bank = get_skill_bank()
    
    # 清理30天未激活且使用次数少于3次的技能
    deleted_count = skill_bank.prune_zombie_skills(days_threshold=30, min_usage=3)
    
    # 清理使用10次以上但成功率低于30%的技能
    low_success_count = skill_bank.prune_low_success_skills(min_usage=10, success_rate_threshold=0.3)
    
    # 合并语义重复的技能（简化版本）
    duplicate_count = skill_bank.merge_duplicate_skills()
    
    total_pruned = deleted_count + low_success_count + duplicate_count
    
    if total_pruned > 0:
        print(f"✅ [突触修剪] 总共清理了 {total_pruned} 个无效技能")
    else:
        print("✅ [突触修剪] 无需清理，技能库状态良好")
    
    return total_pruned


def main():
    """主函数 - 用于定时任务调用"""
    print(f"🌙 [突触修剪] DavidAgent 深度睡眠期开始，执行技能库优化...")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        prune_unused_skills()
        print("✨ [突触修剪] 技能库优化完成！")
    except Exception as e:
        print(f"❌ [突触修剪] 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()