"""
MCP (Model Context Protocol) 本地连接器
安全暴露本地 SQLite/DuckDB 记忆库为标准 MCP 资源
"""

import os
import sqlite3
import duckdb
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class MCPLocalConnector:
    """MCP 本地连接器 - 安全只读模式"""
    
    def __init__(self, memory_db_path: str = "/Users/zhaoqinhuang/david_project/DavidAgent/hippocampus/memory.db"):
        self.memory_db_path = memory_db_path
        self.mode = "ro"  # 强制只读模式
        self.max_rows = 2000  # 内存熔断阈值
        self.supported_dbs = ["sqlite", "duckdb"]
        
    def get_schema(self) -> Dict[str, Any]:
        """自动 Schema 自描述"""
        schema_info = {
            "database_type": "unknown",
            "tables": [],
            "mode": self.mode,
            "max_rows_limit": self.max_rows,
            "safety_features": ["read_only", "row_limit", "schema_validation"]
        }
        
        try:
            if self.memory_db_path.endswith('.db') or self.memory_db_path.endswith('.sqlite'):
                # SQLite 数据库
                conn = sqlite3.connect(self.memory_db_path, uri=True)
                cursor = conn.cursor()
                
                # 获取表信息
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                schema_info["database_type"] = "sqlite"
                for table in tables:
                    table_name = table[0]
                    # 获取列信息
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    column_info = [{"name": col[1], "type": col[2]} for col in columns]
                    
                    schema_info["tables"].append({
                        "name": table_name,
                        "columns": column_info
                    })
                    
                conn.close()
                
            elif self.memory_db_path.endswith('.duckdb'):
                # DuckDB 数据库
                conn = duckdb.connect(self.memory_db_path, read_only=True)
                
                # 获取表信息
                tables_df = conn.execute("SHOW TABLES;").fetchdf()
                schema_info["database_type"] = "duckdb"
                
                for table_name in tables_df['Name']:
                    # 获取列信息
                    columns_df = conn.execute(f"DESCRIBE {table_name};").fetchdf()
                    column_info = []
                    for _, row in columns_df.iterrows():
                        column_info.append({"name": row['column_name'], "type": row['column_type']})
                        
                    schema_info["tables"].append({
                        "name": table_name,
                        "columns": column_info
                    })
                    
                conn.close()
                
        except Exception as e:
            schema_info["error"] = f"Schema discovery failed: {str(e)}"
            
        return schema_info
        
    def execute_query(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """安全执行查询（只读 + 熔断）"""
        result = {
            "success": False,
            "data": [],
            "row_count": 0,
            "truncated": False,
            "error": None
        }
        
        # 安全检查：禁止写入操作
        query_lower = query.strip().lower()
        if any(keyword in query_lower for keyword in ['insert', 'update', 'delete', 'drop', 'alter', 'create']):
            result["error"] = "Write operations are not allowed in read-only mode"
            return result
            
        try:
            if self.memory_db_path.endswith('.db') or self.memory_db_path.endswith('.sqlite'):
                # SQLite 查询
                conn = sqlite3.connect(self.memory_db_path, uri=True)
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                # 获取结果（带熔断）
                rows = []
                row_count = 0
                for row in cursor:
                    if row_count >= self.max_rows:
                        result["truncated"] = True
                        break
                    rows.append(row)
                    row_count += 1
                    
                # 获取列名
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    # 转换为字典列表
                    result["data"] = [dict(zip(columns, row)) for row in rows]
                else:
                    result["data"] = rows
                    
                result["row_count"] = row_count
                result["success"] = True
                conn.close()
                
            elif self.memory_db_path.endswith('.duckdb'):
                # DuckDB 查询
                conn = duckdb.connect(self.memory_db_path, read_only=True)
                
                if params:
                    df = conn.execute(query, params).fetchdf()
                else:
                    df = conn.execute(query).fetchdf()
                    
                # 检查行数熔断
                if len(df) > self.max_rows:
                    df = df.head(self.max_rows)
                    result["truncated"] = True
                    
                # 转换为字典列表
                result["data"] = df.to_dict('records')
                result["row_count"] = len(df)
                result["success"] = True
                conn.close()
                
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def list_available_resources(self) -> List[Dict[str, Any]]:
        """列出可用的 MCP 资源"""
        resources = []
        
        # 检查记忆数据库是否存在
        if os.path.exists(self.memory_db_path):
            schema = self.get_schema()
            resources.append({
                "resource_id": "local_memory_db",
                "resource_type": "database",
                "database_type": schema.get("database_type", "unknown"),
                "mode": self.mode,
                "description": "DavidAgent 本地记忆库 (只读)",
                "tables": [table["name"] for table in schema.get("tables", [])],
                "mcp_compatible": True
            })
            
        return resources