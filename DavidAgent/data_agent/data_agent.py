#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Agent - DavidAgent的前额叶皮层 (Prefrontal Cortex)

架构定位：交互式数据智能体，负责与人类长官进行自然语言对话
核心功能：
1. 意图路由 (Intent Routing) - 判断查询类型
2. NL2SQL引擎 - 处理运维指标查询  
3. GraphRAG引擎 - 处理知识洞察查询
4. 安全防护 - 只读权限，SQL注入防护

作者：G老师架构指导 + OpenClaw AI助手
"""

import os
import re
import json
import sqlite3
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib

# 导入Gemini客户端（假设使用Google GenAI SDK）
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    print("⚠️  Google GenAI SDK未安装，将使用模拟模式")

class DataAgent:
    """
    Data Agent核心类 - DavidAgent的前额叶皮层
    
    负责接收人类自然语言查询，智能路由到对应的数据源，
    并返回人类友好的洞察报告。
    """
    
    def __init__(self, 
                 db_path: str = "david_agent_memory.db",
                 pageindex_dir: str = "skills/self-learning-agent/pageindex/knowledge",
                 model_name: str = "gemini-3.1-pro"):
        """
        初始化Data Agent
        
        Args:
            db_path: SQLite数据库路径
            pageindex_dir: PageIndex知识库目录路径  
            model_name: 使用的大模型名称
        """
        self.db_path = db_path
        self.pageindex_dir = Path(pageindex_dir)
        self.model_name = model_name
        
        # 验证路径存在
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
        if not self.pageindex_dir.exists():
            raise FileNotFoundError(f"PageIndex目录不存在: {self.pageindex_dir}")
        
        # 初始化Gemini客户端（如果可用）
        self.client = None
        if HAS_GENAI:
            try:
                self.client = genai.Client()
            except Exception as e:
                print(f"⚠️  Gemini客户端初始化失败: {e}")
                self.client = None
        
        print(f"🧠 [DataAgent] 已初始化 - 数据库: {db_path}, 知识库: {pageindex_dir}")
    
    # ================= 工具箱 (Tools) =================
    
    async def _tool_query_operational_sql(self, natural_language_query: str) -> str:
        """
        工具 A：处理所有关于系统运行状态、成本消耗、抓取日志的查询。
        实现逻辑：将 NL 转化为 SQL -> 在 SQLite 中执行 -> 返回结果的 JSON 字符串。
        
        Args:
            natural_language_query: 自然语言查询
            
        Returns:
            JSON格式的查询结果字符串
        """
        print(f"📊 [DataAgent] 路由命中 -> Text-to-SQL 引擎: {natural_language_query}")
        
        # 这里应该调用大模型生成SQL，但为了演示先使用模拟逻辑
        # 实际实现中会使用Gemini的Function Calling能力
        sql_query = await self._generate_sql_from_nl(natural_language_query)
        
        if not sql_query:
            return json.dumps({"error": "无法生成有效的SQL查询"})
        
        # 执行SQL查询（只读模式）
        try:
            result = await self._execute_safe_sql(sql_query)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            # 尝试自修复（最多3次）
            for attempt in range(3):
                print(f"🔄 [DataAgent] SQL执行失败，尝试自修复 (第{attempt+1}次): {e}")
                repaired_sql = await self._repair_sql_query(sql_query, str(e))
                if repaired_sql:
                    try:
                        result = await self._execute_safe_sql(repaired_sql)
                        return json.dumps(result, ensure_ascii=False)
                    except Exception as repair_error:
                        if attempt == 2:  # 最后一次尝试
                            return json.dumps({"error": f"SQL自修复失败: {repair_error}"})
                        continue
                else:
                    break
            
            return json.dumps({"error": f"SQL执行失败: {e}"})
    
    async def _tool_query_knowledge_graph(self, natural_language_query: str) -> str:
        """
        工具 B：处理所有关于技术知识、框架对比、架构演进的查询。
        实现逻辑：对 PageIndex 和 ChromaDB 进行检索 -> 提取上下文 -> 返回知识片段的字符串。
        
        Args:
            natural_language_query: 自然语言查询
            
        Returns:
            知识检索结果字符串
        """
        print(f"🧠 [DataAgent] 路由命中 -> GraphRAG 引擎: {natural_language_query}")
        
        # 1. 向量检索（ChromaDB）- 这里简化为文件搜索
        vector_results = await self._vector_search(natural_language_query)
        
        # 2. 图谱遍历（PageIndex双链）  
        graph_results = await self._graph_traversal(natural_language_query)
        
        # 3. 综合建构
        combined_result = self._synthesize_knowledge(vector_results, graph_results, natural_language_query)
        
        return combined_result
    
    # ================= 核心实现方法 =================
    
    async def _generate_sql_from_nl(self, nl_query: str) -> Optional[str]:
        """
        将自然语言查询转换为SQL查询
        
        Args:
            nl_query: 自然语言查询
            
        Returns:
            生成的SQL查询字符串，或None如果失败
        """
        if self.client and HAS_GENAI:
            # 使用Gemini Function Calling生成SQL
            # 这里是简化版本，实际需要完整的Function Calling实现
            system_prompt = """
            你是一个SQL专家，专门处理DavidAgent系统的运维查询。
            数据库表结构：
            - trace_logs: task_id, timestamp, workflow_status, raw_source, left_brain_graph, right_brain_draft, logic_score, tone_score, format_score, full_snapshot
            - raw_signals: signal_id, content_hash, handle, author_name, timestamp, likes, retweets, raw_text, raw_json, signal_type
            - consolidation_logs: id, source_id, status, processed_at, error_message
            - system_tasks: task_id, task_type, status, created_at, completed_at, result
            
            请根据用户的问题生成准确的SQL查询。只返回SQL语句，不要包含任何解释。
            """
            
            try:
                response = await self.client.generate_content(
                    model=self.model_name,
                    prompt=f"{system_prompt}\n\n用户问题: {nl_query}",
                    max_tokens=200
                )
                sql = response.text.strip()
                # 验证SQL安全性
                if self._is_safe_sql(sql):
                    return sql
                else:
                    print("❌ [DataAgent] 生成的SQL不安全，已拒绝执行")
                    return None
            except Exception as e:
                print(f"❌ [DataAgent] SQL生成失败: {e}")
                return None
        else:
            # 模拟模式 - 基于关键词匹配
            return self._simulate_sql_generation(nl_query)
    
    def _simulate_sql_generation(self, nl_query: str) -> Optional[str]:
        """
        模拟SQL生成（用于开发和测试）
        """
        nl_query_lower = nl_query.lower()
        
        if "github" in nl_query_lower and ("token" in nl_query_lower or "耗" in nl_query_lower):
            return """
            SELECT DATE(timestamp) as date, 
                   SUM(CASE WHEN raw_source LIKE '%token%' THEN 1 ELSE 0 END) as token_count,
                   COUNT(*) as total_tasks
            FROM trace_logs 
            WHERE timestamp >= datetime('now', '-7 days')
            AND raw_source LIKE '%github%'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            """
        elif "错误" in nl_query_lower or "报错" in nl_query_lower:
            return """
            SELECT DATE(timestamp) as date, 
                   COUNT(*) as error_count
            FROM trace_logs 
            WHERE timestamp >= datetime('now', '-7 days')
            AND workflow_status = 'ERROR'
            GROUP BY DATE(timestamp)
            ORDER BY error_count DESC
            LIMIT 1
            """
        elif "抓取" in nl_query_lower or "trending" in nl_query_lower:
            return """
            SELECT signal_type, COUNT(*) as count
            FROM raw_signals 
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY signal_type
            """
        else:
            return """
            SELECT COUNT(*) as total_records,
                   COUNT(DISTINCT signal_type) as signal_types
            FROM raw_signals
            """
    
    async def _execute_safe_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        安全执行SQL查询（只读模式）
        
        Args:
            sql_query: 要执行的SQL查询
            
        Returns:
            查询结果列表
        """
        # 再次验证SQL安全性
        if not self._is_safe_sql(sql_query):
            raise ValueError("SQL查询包含不安全的操作")
        
        # 连接到数据库（只读模式）
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append(dict(row))
            
            return result
        finally:
            conn.close()
    
    def _is_safe_sql(self, sql: str) -> bool:
        """
        验证SQL查询是否安全（只读）
        
        Args:
            sql: SQL查询字符串
            
        Returns:
            True如果安全，False如果不安全
        """
        unsafe_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b',
            r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bEXEC\b'
        ]
        
        sql_upper = sql.upper()
        for pattern in unsafe_patterns:
            if re.search(pattern, sql_upper):
                return False
        
        return True
    
    async def _repair_sql_query(self, original_sql: str, error_message: str) -> Optional[str]:
        """
        修复SQL查询（自修复机制）
        
        Args:
            original_sql: 原始SQL查询
            error_message: 错误信息
            
        Returns:
            修复后的SQL查询，或None如果无法修复
        """
        if self.client and HAS_GENAI:
            repair_prompt = f"""
            原始SQL查询: {original_sql}
            错误信息: {error_message}
            
            请修复这个SQL查询，确保它能正确执行。只返回修复后的SQL语句。
            """
            
            try:
                response = await self.client.generate_content(
                    model=self.model_name,
                    prompt=repair_prompt,
                    max_tokens=200
                )
                repaired_sql = response.text.strip()
                if self._is_safe_sql(repaired_sql):
                    return repaired_sql
            except Exception as e:
                print(f"❌ [DataAgent] SQL修复失败: {e}")
        
        return None
    
    async def _vector_search(self, query: str) -> List[Dict[str, Any]]:
        """
        向量检索（简化版 - 文件内容搜索）
        
        Args:
            query: 查询字符串
            
        Returns:
            检索结果列表
        """
        results = []
        query_keywords = set(re.findall(r'\w+', query.lower()))
        
        # 搜索PageIndex中的Markdown文件
        for md_file in self.pageindex_dir.glob("**/*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 计算关键词匹配度
                content_words = set(re.findall(r'\w+', content.lower()))
                match_score = len(query_keywords & content_words) / len(query_keywords) if query_keywords else 0
                
                if match_score > 0.1:  # 阈值
                    results.append({
                        'file': str(md_file),
                        'content': content[:500],  # 截断
                        'score': match_score
                    })
            except Exception as e:
                print(f"⚠️  文件读取失败 {md_file}: {e}")
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]  # 返回前5个结果
    
    async def _graph_traversal(self, query: str) -> List[Dict[str, Any]]:
        """
        图谱遍历（双链Markdown解析）
        
        Args:
            query: 查询字符串
            
        Returns:
            图谱遍历结果列表
        """
        results = []
        query_lower = query.lower()
        
        # 查找包含相关标签的文件
        for md_file in self.pageindex_dir.glob("**/*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含双链语法 [[...]]
                double_brackets = re.findall(r'\[\[(.*?)\]\]', content)
                if double_brackets:
                    # 检查是否与查询相关
                    relevant_links = []
                    for link in double_brackets:
                        if query_lower in link.lower() or link.lower() in query_lower:
                            relevant_links.append(link)
                    
                    if relevant_links:
                        results.append({
                            'file': str(md_file),
                            'links': relevant_links,
                            'context': self._extract_context_around_links(content, relevant_links)
                        })
            except Exception as e:
                print(f"⚠️  图谱遍历失败 {md_file}: {e}")
        
        return results
    
    def _extract_context_around_links(self, content: str, links: List[str]) -> str:
        """
        提取链接周围的上下文
        """
        context_parts = []
        for link in links:
            pattern = rf'\[\[{re.escape(link)}\]\]'
            matches = list(re.finditer(pattern, content))
            if matches:
                match = matches[0]
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context_parts.append(content[start:end])
        
        return " ".join(context_parts)[:300]
    
    def _synthesize_knowledge(self, vector_results: List[Dict], graph_results: List[Dict], query: str) -> str:
        """
        综合建构知识回答
        """
        if not vector_results and not graph_results:
            return "在知识库中未找到相关信息。"
        
        synthesis = f"🔍 **基于您的查询 '{query}'，我找到了以下信息：**\n\n"
        
        if vector_results:
            synthesis += "### 📚 相关文档摘要\n"
            for i, result in enumerate(vector_results[:3], 1):
                synthesis += f"{i}. **文件**: {Path(result['file']).name}\n"
                synthesis += f"   **内容**: {result['content']}...\n\n"
        
        if graph_results:
            synthesis += "### 🔗 知识图谱关联\n"
            for i, result in enumerate(graph_results[:3], 1):
                synthesis += f"{i}. **文件**: {Path(result['file']).name}\n"
                synthesis += f"   **关联概念**: {', '.join(result['links'])}\n"
                synthesis += f"   **上下文**: {result['context']}...\n\n"
        
        synthesis += "💡 **建议**: 这些信息基于DavidAgent的历史学习记录，可能需要结合最新资料进行验证。"
        
        return synthesis
    
    # ================= 交互入口 =================
    
    async def process_human_query(self, query: str) -> str:
        """
        核心入口：接收人类提问，利用大模型的 Function Calling 自动路由，并生成最终回复。
        
        Args:
            query: 人类的自然语言查询
            
        Returns:
            人类友好的回答字符串
        """
        print(f"👤 [人类长官]: {query}")
        
        # 判断查询类型（简化版 - 基于关键词）
        query_lower = query.lower()
        is_operational = any(keyword in query_lower for keyword in [
            'token', '耗', '错误', '报错', '日志', '状态', '数量', '统计', '多少', '几次'
        ])
        
        if is_operational:
            # 运维指标查询
            sql_result = await self._tool_query_operational_sql(query)
            try:
                result_data = json.loads(sql_result)
                if 'error' in result_data:
                    return f"❌ 查询执行失败: {result_data['error']}"
                else:
                    return self._format_sql_result_for_human(result_data, query)
            except json.JSONDecodeError:
                return f"📊 查询结果: {sql_result}"
        else:
            # 知识洞察查询  
            knowledge_result = await self._tool_query_knowledge_graph(query)
            return knowledge_result
    
    def _format_sql_result_for_human(self, result_data: List[Dict], original_query: str) -> str:
        """
        将SQL查询结果格式化为人类友好的回答
        """
        if not result_data:
            return "🔍 未找到相关数据。"
        
        # 根据原始查询类型生成不同格式的回答
        query_lower = original_query.lower()
        
        if "token" in query_lower or "耗" in query_lower:
            total_tokens = sum(row.get('token_count', 0) for row in result_data)
            return f"📈 **GitHub Trending Token消耗统计**:\n过去一周共消耗约 {total_tokens:,} tokens。\n详细数据: {json.dumps(result_data, indent=2, ensure_ascii=False)}"
        
        elif "错误" in query_lower or "报错" in query_lower:
            if result_data:
                worst_day = result_data[0]
                return f"🚨 **错误最多的日期**: {worst_day.get('date', '未知')}，共 {worst_day.get('error_count', 0)} 次错误。"
            else:
                return "✅ 过去一周没有发现错误。"
        
        else:
            # 通用格式
            return f"📊 **查询结果**:\n```json\n{json.dumps(result_data, indent=2, ensure_ascii=False)}\n```"


# 使用示例和测试函数
async def main():
    """测试函数"""
    try:
        agent = DataAgent()
        
        # 测试运维查询
        print("=== 测试运维查询 ===")
        operational_query = "过去一周，我们抓取 GitHub Trending 耗费了多少 Token？"
        result = await agent.process_human_query(operational_query)
        print(f"🤖 [DataAgent回答]:\n{result}\n")
        
        # 测试知识查询  
        print("=== 测试知识查询 ===")
        knowledge_query = "根据我们最近的学习，业界对 Node.js 跑大模型底层的态度是什么？"
        result = await agent.process_human_query(knowledge_query)
        print(f"🤖 [DataAgent回答]:\n{result}\n")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())