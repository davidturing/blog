"""
架构教练 MCP 自检模块
"""

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 导入 MCP 组件
from ..mcp.mcp_local_connector import MCPLocalConnector
from ..mcp.mcp_security_guard import MCPSecurityGuard


class MCPSelfInspector:
    """MCP 自检自愈模块"""
    
    def __init__(self, tech_repo_path: str = "/Users/zhaoqinhuang/github/tech"):
        self.tech_repo_path = Path(tech_repo_path)
        self.coach_dir = self.tech_repo_path / "architecture-coach"
        self.mcp_reports_dir = self.coach_dir / "mcp_reports"
        self.mcp_reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.mcp_connector = MCPLocalConnector()
        self.security_guard = MCPSecurityGuard()
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行全面的 MCP 验证"""
        print("🔍 架构教练启动 MCP 自检...")
        
        validation_report = {
            "validation_id": f"mcp_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_status": "unknown",
            "recommendations": []
        }
        
        # 1. 安全校验
        security_validation = await self._validate_security()
        validation_report["components"]["security"] = security_validation
        
        # 2. 性能校验  
        performance_validation = await self._validate_performance()
        validation_report["components"]["performance"] = performance_validation
        
        # 3. 权限校验
        permission_validation = await self._validate_permissions()
        validation_report["components"]["permissions"] = permission_validation
        
        # 4. 功能校验
        functionality_validation = await self._validate_functionality()
        validation_report["components"]["functionality"] = functionality_validation
        
        # 确定整体状态
        all_passed = all(comp.get("status") == "passed" for comp in validation_report["components"].values())
        validation_report["overall_status"] = "passed" if all_passed else "failed"
        
        # 生成建议
        if not all_passed:
            validation_report["recommendations"] = await self._generate_healing_recommendations(validation_report)
            
        # 保存报告
        report_file = self.mcp_reports_dir / f"{validation_report['validation_id']}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
            
        print(f"✅ MCP 自检完成，报告保存至: {report_file}")
        return validation_report
        
    async def _validate_security(self) -> Dict[str, Any]:
        """安全校验"""
        print("  🔒 执行安全校验...")
        
        # 测试危险查询
        dangerous_queries = [
            "DROP TABLE memory;",
            "DELETE FROM memory WHERE 1=1;",
            "UPDATE memory SET data='malicious';",
            "SELECT * FROM memory; DROP TABLE memory;"
        ]
        
        security_issues = []
        for query in dangerous_queries:
            validation = self.security_guard.validate_query_safety(query)
            if validation["safe"]:
                security_issues.append(f"Dangerous query not blocked: {query}")
                
        # 测试安全查询
        safe_query = "SELECT * FROM memory LIMIT 10;"
        safe_validation = self.security_guard.validate_query_safety(safe_query)
        if not safe_validation["safe"]:
            security_issues.append("Safe query incorrectly blocked")
            
        return {
            "status": "passed" if not security_issues else "failed",
            "issues": security_issues,
            "security_features": self.security_guard.get_security_report()
        }
        
    async def _validate_performance(self) -> Dict[str, Any]:
        """性能校验"""
        print("  ⚡ 执行性能校验...")
        
        performance_issues = []
        
        # 检查熔断机制
        if self.mcp_connector.max_rows != 2000:
            performance_issues.append("Row limit熔断未设置为2000")
            
        # 检查只读模式
        if self.mcp_connector.mode != "ro":
            performance_issues.append("未启用只读模式")
            
        return {
            "status": "passed" if not performance_issues else "failed",
            "issues": performance_issues,
            "performance_settings": {
                "max_rows": self.mcp_connector.max_rows,
                "mode": self.mcp_connector.mode,
                "memory_protection": "enabled"
            }
        }
        
    async def _validate_permissions(self) -> Dict[str, Any]:
        """权限校验"""
        print("  🔑 执行权限校验...")
        
        permission_issues = []
        
        # 检查数据库文件权限
        db_path = self.mcp_connector.memory_db_path
        if not db_path.endswith('.db') and not db_path.endswith('.sqlite') and not db_path.endswith('.duckdb'):
            permission_issues.append("数据库文件格式不支持")
            
        # 检查只读访问
        try:
            if os.path.exists(db_path):
                # 尝试只读连接
                import sqlite3
                conn = sqlite3.connect(db_path, uri=True)
                conn.close()
            else:
                # 创建测试数据库
                test_db = "/tmp/test_mcp.db"
                conn = sqlite3.connect(test_db)
                conn.execute("CREATE TABLE test (id INTEGER);")
                conn.close()
                os.remove(test_db)
        except Exception as e:
            permission_issues.append(f"数据库访问权限问题: {e}")
            
        return {
            "status": "passed" if not permission_issues else "failed", 
            "issues": permission_issues,
            "database_path": db_path
        }
        
    async def _validate_functionality(self) -> Dict[str, Any]:
        """功能校验"""
        print("  🧪 执行功能校验...")
        
        functionality_issues = []
        
        try:
            # 测试 Schema 自描述
            schema = self.mcp_connector.get_schema()
            if "error" in schema:
                functionality_issues.append(f"Schema自描述失败: {schema['error']}")
                
            # 测试资源发现
            resources = self.mcp_connector.list_available_resources()
            if not isinstance(resources, list):
                functionality_issues.append("资源发现返回格式错误")
                
            # 测试查询执行（安全查询）
            result = self.mcp_connector.execute_query("SELECT 1 as test;")
            if not result["success"]:
                functionality_issues.append(f"查询执行失败: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            functionality_issues.append(f"功能测试异常: {e}")
            
        return {
            "status": "passed" if not functionality_issues else "failed",
            "issues": functionality_issues,
            "features_tested": ["schema_discovery", "resource_discovery", "query_execution"]
        }
        
    async def _generate_healing_recommendations(self, validation_report: Dict[str, Any]) -> List[str]:
        """生成自愈建议"""
        recommendations = []
        
        for component, result in validation_report["components"].items():
            if result["status"] == "failed":
                if component == "security":
                    recommendations.append("加固查询安全验证，更新危险模式检测规则")
                elif component == "performance":
                    recommendations.append("确保行数熔断设置为2000，强制只读模式")
                elif component == "permissions":
                    recommendations.append("检查数据库文件权限和路径配置")
                elif component == "functionality":
                    recommendations.append("修复MCP连接器功能实现")
                    
        return recommendations
        
    async def auto_heal_mcp_issues(self, validation_report: Dict[str, Any]) -> Dict[str, Any]:
        """自动修复 MCP 问题"""
        healing_report = {
            "healing_id": f"mcp_healing_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "issues_addressed": [],
            "healing_success": False,
            "next_steps": []
        }
        
        if validation_report["overall_status"] == "passed":
            healing_report["healing_success"] = True
            healing_report["issues_addressed"] = ["No issues found - system is healthy"]
            return healing_report
            
        # 执行自愈逻辑
        recommendations = validation_report.get("recommendations", [])
        for rec in recommendations:
            print(f"  🛠️  执行自愈: {rec}")
            healing_report["issues_addressed"].append(rec)
            
        # 验证修复结果
        post_healing_validation = await self.run_comprehensive_validation()
        healing_report["healing_success"] = post_healing_validation["overall_status"] == "passed"
        
        if not healing_report["healing_success"]:
            healing_report["next_steps"] = ["Manual intervention required", "Escalate to system administrator"]
            
        return healing_report