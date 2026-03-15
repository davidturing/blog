#!/usr/bin/env python3
"""
测试数字分身 MCP 全域记忆协同
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "brain" / "mcp"))
sys.path.insert(0, str(Path(__file__).parent / "brain" / "coach"))

from mcp_unified_router import MCPUnifiedRouter


async def test_digital_persona_collaboration():
    """测试数字分身协同"""
    print("🧪 测试数字分身 MCP 全域记忆协同...")
    
    # 创建 MCP 统一路由器
    router = MCPUnifiedRouter()
    
    # 注册所有数字分身
    personas_to_register = [
        ("科技达人", "tech_blogger"),
        ("首席数据官", "chief_data_officer"),
        ("推荐系统老师", "recommendation_system_teacher"),
        ("芯片数据专家", "chip_data_expert"),
        ("家庭助理", "home_assistant"),
        ("大数据专家", "big_data_expert"),
        ("摄影师（GLM）", "photographer_glm"),
        ("数字化转型专家（GLM）", "digital_transformation_expert_glm"),
        ("Vibe Coding 老师", "vibe_coding_teacher"),
        ("Agent 自进化老师", "agent_self_improvement_teacher"),
        ("多智能体老师", "multi_agent_teacher"),
        ("Agentic AI 老师", "agentic_ai_teacher"),
        ("架构教练", "architecture_coach"),
        ("MCP 标准化中枢", "mcp_standardization_hub")
    ]
    
    print("\n1. 注册数字分身到 MCP 网络...")
    registered_count = 0
    for persona_name, persona_id in personas_to_register:
        success = await router.register_digital_persona(persona_name, persona_id)
        if success:
            registered_count += 1
            
    print(f"✅ 成功注册 {registered_count}/{len(personas_to_register)} 个数字分身")
    
    # 测试记忆共享连通性
    print("\n2. 测试记忆共享连通性...")
    test_queries = [
        ("tech_blogger", "SELECT COUNT(*) as total FROM memory WHERE source = 'github'"),
        ("chip_data_expert", "SELECT COUNT(*) as total FROM memory WHERE source = 'rss'"),
        ("photographer_glm", "SELECT COUNT(*) as total FROM memory WHERE source = 'social'")
    ]
    
    connectivity_results = []
    for persona_id, query in test_queries:
        result = await router.query_memory(persona_id, query)
        connectivity_results.append({
            "persona": persona_id,
            "success": result["success"],
            "error": result.get("error")
        })
        
    successful_connections = sum(1 for r in connectivity_results if r["success"])
    print(f"✅ 记忆共享连通性: {successful_connections}/{len(test_queries)} 个分身连接成功")
    
    # 架构教练安全校验
    print("\n3. 架构教练安全校验...")
    inspector = router.architecture_coach
    validation_report = await inspector.run_comprehensive_validation()
    
    safety_passed = validation_report["overall_status"] == "passed"
    print(f"✅ 安全校验结果: {'通过' if safety_passed else '失败'}")
    
    # 协同演示：跨经验查询
    print("\n4. 协同演示：跨领域经验关联分析...")
    collaboration_result = await router.run_cross_domain_analysis(
        "芯片数据专家", 
        "大数据专家", 
        "性能优化"
    )
    
    collaboration_success = "error" not in collaboration_result
    print(f"✅ 协同演示结果: {'成功' if collaboration_success else '失败'}")
    
    if collaboration_success:
        print(f"   - 洞察: {', '.join(collaboration_result['insights'])}")
        print(f"   - 关联: {', '.join(collaboration_result['correlations'])}")
    
    # 获取最终状态报告
    print("\n5. 生成协同状态报告...")
    status_report = await router.get_collaboration_status()
    
    print(f"\n📊 数字分身 MCP 接入状态:")
    print(f"   - 总分身数: {status_report['total_personas']}")
    print(f"   - 总查询数: {status_report['total_queries']}")
    print(f"   - 安全特性: {', '.join(status_report['safety_features'])}")
    
    # 验证内存占用
    memory_usage = "unknown"
    try:
        import psutil
        process = psutil.Process()
        memory_usage = f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
    except:
        pass
        
    print(f"   - 内存占用: {memory_usage} (目标: <100MB)")
    
    # 返回综合结果
    all_tests_passed = (
        registered_count == len(personas_to_register) and
        successful_connections == len(test_queries) and
        safety_passed and
        collaboration_success
    )
    
    return {
        "mcp_access_status": f"{registered_count}/{len(personas_to_register)} 分身接入",
        "memory_connectivity": f"{successful_connections}/{len(test_queries)} 连接成功",
        "safety_validation": "通过" if safety_passed else "失败",
        "collaboration_demo": "成功" if collaboration_success else "失败",
        "memory_usage": memory_usage,
        "overall_status": "成功" if all_tests_passed else "部分失败"
    }


if __name__ == "__main__":
    results = asyncio.run(test_digital_persona_collaboration())
    
    print("\n" + "="*60)
    print("🎯 数字分身 MCP 全域记忆协同测试结果")
    print("="*60)
    print(f"• 数字分身MCP接入状态: {results['mcp_access_status']}")
    print(f"• 记忆共享连通性测试结果: {results['memory_connectivity']}")
    print(f"• 架构教练安全校验结论: {results['safety_validation']}")
    print(f"• 协同演示示例: {results['collaboration_demo']}")
    print(f"• 内存占用: {results['memory_usage']}")
    print(f"• 总体状态: {results['overall_status']}")
    
    if results['overall_status'] == '成功':
        print("\n🎉 数字分身 MCP 全域记忆协同部署完成！")
    else:
        print("\n⚠️  部分测试未通过，需要进一步调试")