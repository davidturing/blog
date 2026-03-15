"""
MCP 统一路由器 - 数字分身全域记忆协同中枢
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入 MCP 组件
from .mcp_local_connector import MCPLocalConnector
from ..coach.mcp_self_inspector import MCPSelfInspector


class MCPUnifiedRouter:
    """MCP 统一路由器"""
    
    def __init__(self):
        self.memory_db_path = "/Users/zhaoqinhuang/david_project/DavidAgent/hippocampus/memory.db"
        self.mcp_connector = MCPLocalConnector(self.memory_db_path)
        self.architecture_coach = MCPSelfInspector()
        self.connected_personas = {}
        self.query_history = []
        
    async def register_digital_persona(self, persona_name: str, persona_id: str) -> bool:
        """注册数字分身到 MCP 路由器"""
        try:
            # 验证分身权限
            validation_result = await self._validate_persona_permissions(persona_name, persona_id)
            if not validation_result["authorized"]:
                print(f"❌ 分身 {persona_name} 未通过权限验证")
                return False
                
            # 注册分身
            self.connected_personas[persona_id] = {
                "name": persona_name,
                "id": persona_id,
                "registered_at": datetime.now().isoformat(),
                "query_count": 0,
                "last_query": None
            }
            
            print(f"✅ 分身 {persona_name} 已成功接入 MCP 全域记忆协同网络")
            return True
            
        except Exception as e:
            print(f"❌ 分身 {persona_name} 注册失败: {e}")
            return False
            
    async def _validate_persona_permissions(self, persona_name: str, persona_id: str) -> Dict[str, Any]:
        """验证分身权限"""
        # 基于 MEMORY.md 中的分身映射表验证
        valid_personas = {
            "tech_blogger": "科技达人",
            "chief_data_officer": "首席数据官", 
            "recommendation_system_teacher": "推荐系统老师",
            "chip_data_expert": "芯片数据专家",
            "home_assistant": "家庭助理",
            "big_data_expert": "大数据专家",
            "photographer_glm": "摄影师（GLM）",
            "digital_transformation_expert_glm": "数字化转型专家（GLM）",
            "vibe_coding_teacher": "Vibe Coding 老师",
            "agent_self_improvement_teacher": "Agent 自进化老师",
            "multi_agent_teacher": "多智能体老师",
            "agentic_ai_teacher": "Agentic AI 老师",
            "architecture_coach": "架构教练",
            "mcp_standardization_hub": "MCP 标准化中枢"
        }
        
        is_valid = persona_id in valid_personas and valid_personas[persona_id] == persona_name
        
        return {
            "authorized": is_valid,
            "validation_time": datetime.now().isoformat(),
            "persona_id": persona_id,
            "persona_name": persona_name
        }
        
    async def query_memory(self, persona_id: str, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """分身查询记忆库"""
        result = {
            "success": False,
            "data": [],
            "error": None,
            "persona_id": persona_id,
            "query_time": datetime.now().isoformat()
        }
        
        # 验证分身是否已注册
        if persona_id not in self.connected_personas:
            result["error"] = f"分身 {persona_id} 未注册到 MCP 网络"
            return result
            
        # 架构教练安全校验
        security_validation = await self._run_security_validation(query)
        if not security_validation["safe"]:
            result["error"] = f"查询被架构教练拦截: {security_validation['issues']}"
            return result
            
        # 执行查询
        query_result = self.mcp_connector.execute_query(query, params)
        
        # 应用熔断机制
        if query_result["row_count"] > 2000:
            result["error"] = "查询结果超过内存熔断阈值 (2000行)"
            return result
            
        # 记录查询历史
        self._log_query(persona_id, query, query_result)
        
        # 更新分身统计
        self.connected_personas[persona_id]["query_count"] += 1
        self.connected_personas[persona_id]["last_query"] = query
        
        result["success"] = query_result["success"]
        result["data"] = query_result["data"]
        result["row_count"] = query_result["row_count"]
        result["truncated"] = query_result["truncated"]
        
        return result
        
    async def _run_security_validation(self, query: str) -> Dict[str, Any]:
        """运行安全验证"""
        # 使用架构教练的安全卫士
        from .mcp_security_guard import MCPSecurityGuard
        security_guard = MCPSecurityGuard()
        return security_guard.validate_query_safety(query)
        
    def _log_query(self, persona_id: str, query: str, result: Dict[str, Any]):
        """记录查询日志"""
        log_entry = {
            "persona_id": persona_id,
            "query": query,
            "success": result["success"],
            "row_count": result.get("row_count", 0),
            "timestamp": datetime.now().isoformat()
        }
        self.query_history.append(log_entry)
        
        # 限制日志大小
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-500:]
            
    async def get_collaboration_status(self) -> Dict[str, Any]:
        """获取协同状态报告"""
        status = {
            "total_personas": len(self.connected_personas),
            "connected_personas": list(self.connected_personas.keys()),
            "total_queries": sum(p["query_count"] for p in self.connected_personas.values()),
            "memory_db_path": self.memory_db_path,
            "safety_features": ["read_only", "row_limit_melting", "query_validation", "persona_authorization"],
            "last_updated": datetime.now().isoformat()
        }
        return status
        
    async def run_cross_domain_analysis(self, source_persona: str, target_persona: str, analysis_topic: str) -> Dict[str, Any]:
        """执行跨领域经验关联分析"""
        analysis_result = {
            "source_persona": source_persona,
            "target_persona": target_persona,
            "analysis_topic": analysis_topic,
            "insights": [],
            "correlations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 查询源分身相关经验
            source_query = f"SELECT content FROM memory WHERE persona = '{source_persona}' AND topic LIKE '%{analysis_topic}%' LIMIT 10"
            source_result = await self.query_memory(source_persona, source_query)
            
            # 查询目标分身相关经验  
            target_query = f"SELECT content FROM memory WHERE persona = '{target_persona}' AND topic LIKE '%{analysis_topic}%' LIMIT 10"
            target_result = await self.query_memory(target_persona, target_query)
            
            if source_result["success"] and target_result["success"]:
                analysis_result["insights"] = [
                    f"{source_persona} 经验: {len(source_result['data'])} 条相关记录",
                    f"{target_persona} 经验: {len(target_result['data'])} 条相关记录"
                ]
                analysis_result["correlations"] = ["发现跨领域经验关联机会"]
                
        except Exception as e:
            analysis_result["error"] = str(e)
            
        return analysis_result