"""
MCP 安全卫士 - 由架构教练自动管理
"""

import re
import json
from typing import Dict, List, Any
from datetime import datetime


class MCPSecurityGuard:
    """MCP 安全卫士"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'(?:\b|_)drop\b',
            r'(?:\b|_)delete\b', 
            r'(?:\b|_)update\b',
            r'(?:\b|_)insert\b',
            r'(?:\b|_)alter\b',
            r'(?:\b|_)create\b',
            r'(?:\b|_)truncate\b',
            r'(?:\b|_)exec\b',
            r'(?:\b|_)execute\b',
            r';.*;',
            r'--.*',
            r'/\*.*\*/'
        ]
        
        self.whitelisted_functions = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'LIMIT', 'OFFSET',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT', 'AS', 'AND', 'OR', 'NOT',
            'LIKE', 'IN', 'BETWEEN', 'IS NULL', 'IS NOT NULL'
        ]
        
    def validate_query_safety(self, query: str) -> Dict[str, Any]:
        """验证查询安全性"""
        validation = {
            "safe": True,
            "issues": [],
            "severity": "low",
            "timestamp": datetime.now().isoformat()
        }
        
        query_upper = query.upper().strip()
        
        # 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                validation["safe"] = False
                validation["issues"].append(f"Dangerous pattern detected: {pattern}")
                validation["severity"] = "critical"
                
        # 检查是否以 SELECT 开头（基本安全要求）
        if not query_upper.startswith('SELECT'):
            validation["safe"] = False
            validation["issues"].append("Query must start with SELECT")
            validation["severity"] = "high"
            
        return validation
        
    def sanitize_query(self, query: str) -> str:
        """清理查询（移除注释等）"""
        # 移除单行注释
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        # 移除多行注释
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        # 移除多余空白
        query = ' '.join(query.split())
        return query.strip()
        
    def get_security_report(self) -> Dict[str, Any]:
        """获取安全报告"""
        return {
            "security_level": "high",
            "features": ["read_only_mode", "query_validation", "row_limit_melting", "schema_validation"],
            "dangerous_patterns_blocked": len(self.dangerous_patterns),
            "last_updated": datetime.now().isoformat()
        }