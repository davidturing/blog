#!/usr/bin/env python3
"""
测试 MCP 标准化中枢
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "brain" / "mcp"))
sys.path.insert(0, str(Path(__file__).parent / "brain" / "coach"))

from mcp_local_connector import MCPLocalConnector
from mcp_self_inspector import MCPSelfInspector


async def test_mcp_standardization():
    """测试 MCP 标准化中枢"""
    print("🧪 测试 MCP 标准化中枢...")
    
    # 创建测试记忆数据库
    test_db_path = "/Users/zhaoqinhuang/david_project/DavidAgent/hippocampus/memory.db"
    os.makedirs("/Users/zhaoqinhuang/david_project/DavidAgent/hippocampus", exist_ok=True)
    
    if not os.path.exists(test_db_path):
        import sqlite3
        conn = sqlite3.connect(test_db_path)
        conn.execute("CREATE TABLE memory (id INTEGER PRIMARY KEY, content TEXT, timestamp TEXT);")
        conn.execute("INSERT INTO memory (content, timestamp) VALUES ('test_memory', '2026-03-15');")
        conn.commit()
        conn.close()
        print("💾 创建测试记忆数据库")
    
    # 测试 MCP 连接器
    connector = MCPLocalConnector(test_db_path)
    
    print("\n1. 测试 Schema 自描述...")
    schema = connector.get_schema()
    print(f"   数据库类型: {schema.get('database_type', 'unknown')}")
    print(f"   表数量: {len(schema.get('tables', []))}")
    print(f"   安全特性: {', '.join(schema.get('safety_features', []))}")
    
    print("\n2. 测试资源发现...")
    resources = connector.list_available_resources()
    print(f"   可用资源: {len(resources)} 个")
    if resources:
        print(f"   资源类型: {resources[0].get('resource_type', 'unknown')}")
        print(f"   MCP 兼容: {resources[0].get('mcp_compatible', False)}")
    
    print("\n3. 测试只读查询...")
    result = connector.execute_query("SELECT * FROM memory LIMIT 5;")
    print(f"   查询成功: {result['success']}")
    print(f"   返回行数: {result['row_count']}")
    print(f"   是否截断: {result['truncated']}")
    
    print("\n4. 测试写入保护...")
    write_result = connector.execute_query("DROP TABLE memory;")
    print(f"   写入阻止: {'✅ 成功' if write_result['error'] else '❌ 失败'}")
    
    print("\n5. 启动架构教练自检...")
    inspector = MCPSelfInspector()
    validation_report = await inspector.run_comprehensive_validation()
    
    print(f"\n✅ MCP 标准化中枢测试完成！")
    print(f"整体状态: {validation_report['overall_status']}")
    
    # 验证关键要求
    requirements_check = {
        "只读模式": connector.mode == "ro",
        "熔断机制": connector.max_rows == 2000,
        "Schema自描述": "database_type" in schema,
        "安全加固": len(schema.get("safety_features", [])) > 0,
        "架构教练校验": validation_report["overall_status"] == "passed"
    }
    
    print("\n📋 关键要求验证:")
    all_passed = True
    for requirement, passed in requirements_check.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {requirement}")
        if not passed:
            all_passed = False
            
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_mcp_standardization())
    if success:
        print("\n🎉 MCP 标准化中枢部署完成 + 架构教练校验通过！")
    else:
        print("\n⚠️  部分要求未满足，需要修复")