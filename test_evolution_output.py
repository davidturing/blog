"""
测试科技达人演进报告输出格式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensors.tech_blogger_output import TechBloggerOutput
from datetime import datetime


def test_output_format():
    """测试输出格式是否符合要求"""
    print("🧪 测试科技达人演进报告输出格式...")
    
    # 创建测试数据
    test_data = {
        "start_time": "2026-03-15T01:00:00",
        "sources": {
            "github": 15,
            "rss": 8,
            "social": 12,
            "docs": 5,
            "qa": 10
        },
        "new_technologies": [
            {
                "title": "OpenClaw Agent Framework v2.0",
                "source": "github",
                "similarity_score": 0.35
            },
            {
                "title": "MCP Protocol Standardization",
                "source": "arxiv",
                "similarity_score": 0.42
            }
        ],
        "distilled_knowledge": [
            {
                "title": "Agent Self-Improvement via Reflection",
                "key_insights": [
                    "使用强化学习进行自我反思和改进",
                    "多智能体协作提升整体系统能力",
                    "实时知识蒸馏减少认知延迟"
                ]
            }
        ],
        "validation_results": {
            "validated_skills": 8,
            "failed_validations": 3
        },
        "storage_stats": {
            "skillbank_entries": 8,
            "reasoning_entries": 3
        },
        "resource_usage": {
            "bandwidth_mb": 45.2,
            "entropy_reduction": 6.0,
            "memory_mb": 1200
        },
        "summary": "今日成功发现 2 项新技术，验证 8 个有效技能，认知熵降低 6.0%，流量使用 45.2MB。系统持续进化中！"
    }
    
    # 测试输出
    output_handler = TechBloggerOutput()
    filename = output_handler.generate_evolution_filename(datetime(2026, 3, 15, 1, 0))
    
    print(f"✅ 生成的文件名: {filename}")
    expected_filename = "DavidAgent自主演进20260315_0100.md"
    if filename == expected_filename:
        print("✅ 文件名格式正确")
    else:
        print(f"❌ 文件名格式错误，期望: {expected_filename}")
        return False
        
    # 测试内容格式
    content = output_handler.format_evolution_content(test_data)
    print("✅ 内容格式生成成功")
    
    # 检查关键部分
    required_sections = [
        "# DavidAgent 自主演进报告",
        "## 📊 抓取数据源与总量",
        "## 🔍 认知熵识别到的新技术/热点", 
        "## 💡 蒸馏后的核心知识",
        "## ✅ 验证结果",
        "## 📦 存入 SkillBank / ReasoningBank 数量",
        "## 📈 流量使用、认知熵变化",
        "## 🎯 今日演进总结"
    ]
    
    for section in required_sections:
        if section in content:
            print(f"✅ 找到必需章节: {section}")
        else:
            print(f"❌ 缺少必需章节: {section}")
            return False
            
    print("🎉 所有输出格式测试通过！")
    return True


if __name__ == "__main__":
    success = test_output_format()
    sys.exit(0 if success else 1)