#!/usr/bin/env python3
"""
测试内容过滤器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试足球内容（应该被拒绝）
football_content = """
#加纳 罚丢点球后就不配进半决赛了！
评论者认为，由于加纳队罚失了关键点球，他们因此不配晋级半决赛。
"""

# 测试AI内容（应该被接受）
ai_content = """
《SkillRL》论文提出了一种新的AI Agent记忆机制，通过经验蒸馏将原始轨迹转化为结构化技能。
这种方法实现了10-20%的Token压缩率，让7B模型能击败GPT-4o。
"""

def test_filter():
    from content_filter_rules import is_content_relevant
    
    print("测试足球内容:")
    result1 = is_content_relevant(football_content)
    print(f"结果: {result1}")
    
    print("\n测试AI内容:")
    result2 = is_content_relevant(ai_content)  
    print(f"结果: {result2}")
    
    return result1, result2

if __name__ == "__main__":
    test_filter()