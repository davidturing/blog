"""
Data Agent - SQL查询工具
用于处理运维指标和系统运行状态的自然语言查询
"""
import sqlite3
import re
import json
from typing import Dict, Any, List
import asyncio

class SQLTool:
    """SQL查询工具 - 安全的Text-to-SQL引擎"""
    
    def __init__(self, db_path: str = "david_agent_memory.db"):
        self.db_path = db_path
        self.readonly_keywords = [
            'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 
            'LIMIT', 'OFFSET', 'JOIN', 'INNER JOIN', 'LEFT JOIN',
            'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT'
        ]
        self.dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
            'TRUNCATE', 'REPLACE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE'
        ]
    
    def _validate_sql_safety(self, sql: str) -> bool:
        """
        验证SQL语句的安全性，确保只读操作
        
        Args:
            sql: 要验证的SQL语句
            
        Returns:
            bool: 是否安全
        """
        sql_upper = sql.upper().strip()
        
        # 检查是否以SELECT开头
        if not sql_upper.startswith('SELECT'):
            return False
        
        # 检查危险关键词
        for keyword in self.dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        # 检查是否只包含安全关键词
        words = re.findall(r'\b\w+\b', sql_upper)
        for word in words:
            if word not in self.readonly_keywords and not word.isdigit():
                # 允许表名、列名等标识符
                if word in ['trace_logs', 'raw_signals', 'consolidation_logs', 'system_tasks']:
                    continue
                if word in ['task_id', 'timestamp', 'workflow_status', 'raw_source', 'source_type',
                           'logic_score', 'tone_score', 'format_score', 'human_comment', 'full_snapshot']:
                    continue
                # 其他单词需要进一步验证
                if len(word) > 1 and not word.replace('_', '').replace('-', '').isalnum():
                    return False
        
        return True
    
    def _execute_safe_query(self, sql: str, max_rows: int = 100) -> List[Dict[str, Any]]:
        """
        执行安全的SQL查询
        
        Args:
            sql: SQL查询语句
            max_rows: 最大返回行数
            
        Returns:
            查询结果列表
        """
        if not self._validate_sql_safety(sql):
            raise ValueError("SQL查询不安全，只允许只读操作")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 添加LIMIT保护
            if 'LIMIT' not in sql.upper():
                sql_with_limit = f"{sql} LIMIT {max_rows}"
            else:
                sql_with_limit = sql
            
            cursor.execute(sql_with_limit)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append(dict(row))
            
            conn.close()
            return result
            
        except Exception as e:
            raise ValueError(f"SQL执行错误: {str(e)}")
    
    async def text_to_sql(self, natural_language_query: str, schema_info: str = None) -> str:
        """
        将自然语言转换为SQL查询（模拟实现，实际应调用LLM）
        
        Args:
            natural_language_query: 自然语言查询
            schema_info: 数据库schema信息
            
        Returns:
            SQL查询语句
        """
        # 这里应该是调用LLM的逻辑，现在先用规则匹配
        query_lower = natural_language_query.lower()
        
        if 'token' in query_lower or '消耗' in query_lower:
            if 'github' in query_lower or 'trending' in query_lower:
                return "SELECT DATE(timestamp) as date, COUNT(*) as count, SUM(CASE WHEN workflow_status = 'ERROR' THEN 1 ELSE 0 END) as error_count FROM trace_logs WHERE source_type = 'github_trending' GROUP BY DATE(timestamp) ORDER BY date DESC"
            else:
                return "SELECT DATE(timestamp) as date, COUNT(*) as count FROM trace_logs GROUP BY DATE(timestamp) ORDER BY date DESC"
        
        elif '错误' in query_lower or '报错' in query_lower or '死信' in query_lower:
            return "SELECT DATE(timestamp) as date, COUNT(*) as error_count FROM trace_logs WHERE workflow_status = 'ERROR' GROUP BY DATE(timestamp) ORDER BY error_count DESC LIMIT 7"
        
        elif '抓取' in query_lower or '数量' in query_lower:
            return "SELECT source_type, COUNT(*) as count FROM trace_logs GROUP BY source_type ORDER BY count DESC"
        
        elif '最近' in query_lower or '最新' in query_lower:
            return "SELECT task_id, timestamp, source_type, workflow_status FROM trace_logs ORDER BY timestamp DESC LIMIT 10"
        
        else:
            # 默认查询
            return "SELECT DATE(timestamp) as date, COUNT(*) as daily_count FROM trace_logs GROUP BY DATE(timestamp) ORDER BY date DESC LIMIT 7"
    
    async def process_query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        处理自然语言查询，返回结构化结果
        
        Args:
            natural_language_query: 自然语言查询
            
        Returns:
            结构化结果
        """
        try:
            # 1. 获取数据库schema信息
            schema_info = self._get_db_schema()
            
            # 2. 转换为SQL
            sql_query = await self.text_to_sql(natural_language_query, schema_info)
            
            # 3. 执行查询
            results = self._execute_safe_query(sql_query)
            
            # 4. 返回结果
            return {
                'status': 'success',
                'query': natural_language_query,
                'sql': sql_query,
                'results': results,
                'result_count': len(results)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query': natural_language_query,
                'error': str(e),
                'results': [],
                'result_count': 0
            }
    
    def _get_db_schema(self) -> str:
        """获取数据库schema信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema_info = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                column_info = []
                for col in columns:
                    column_info.append(f"{col[1]} ({col[2]})")
                
                schema_info.append(f"Table: {table_name}\nColumns: {', '.join(column_info)}")
            
            conn.close()
            return '\n\n'.join(schema_info)
            
        except Exception as e:
            return f"Error getting schema: {str(e)}"

# 测试函数
async def main():
    """测试SQL工具"""
    tool = SQLTool()
    
    test_queries = [
        "过去一周，我们抓取 GitHub Trending 耗费了多少 Token？",
        "哪天报错（死信任务）最多？",
        "最近的抓取任务有哪些？"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        result = await tool.process_query(query)
        print(f"📊 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())