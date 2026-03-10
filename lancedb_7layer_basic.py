#!/usr/bin/env python3
"""
LanceDB 7层混合检索 - 基础实现
使用现有的 SQLite 数据库和 Google Generative AI
"""

import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

# 使用 Google Generative AI 进行文本嵌入
try:
    import google.genai as genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    print("Warning: google-generativeai not available")

class Simple7LayerRetriever:
    def __init__(self, db_path: str = "david_agent_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def get_embedding(self, text: str):
        """获取文本嵌入向量（简化版，使用关键词提取代替）"""
        if not GOOGLE_GENAI_AVAILABLE:
            # 简化版：返回关键词列表
            words = re.findall(r'\b\w+\b', text.lower())
            return list(set(words))  # 去重
        else:
            # TODO: 实际的嵌入生成
            words = re.findall(r'\b\w+\b', text.lower())
            return list(set(words))
    
    def layer1_vector_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """第1层：向量检索（简化为关键词匹配）"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        results = []
        
        # 搜索 raw_signals 表
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM raw_signals ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        for row in rows[:top_k * 2]:  # 获取更多候选
            content_words = set(re.findall(r'\b\w+\b', (row['raw_text'] or '').lower()))
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / len(query_words)
                results.append({
                    'id': row['signal_id'],
                    'content': row['raw_text'],
                    'timestamp': row['timestamp'],
                    'score': score,
                    'source': 'raw_signals'
                })
        
        # 搜索 trace_logs 表
        cursor.execute("SELECT * FROM trace_logs ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        for row in rows[:top_k * 2]:
            content_parts = [
                row['raw_source'] or '',
                row['left_brain_graph'] or '',
                row['right_brain_draft'] or '',
                row['review_feedback'] or ''
            ]
            full_content = ' '.join(content_parts)
            content_words = set(re.findall(r'\b\w+\b', full_content.lower()))
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / len(query_words)
                results.append({
                    'id': row['task_id'],
                    'content': full_content,
                    'timestamp': row['timestamp'],
                    'score': score,
                    'source': 'trace_logs'
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def layer2_bm25_keywords(self, results: List[Dict], query: str) -> List[Dict]:
        """第2层：BM25 关键词检索（简化版）"""
        # 提取查询中的技术术语、命令、配置项
        tech_terms = re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', query)
        important_terms = [term for term in tech_terms if len(term) > 2]
        
        for result in results:
            content = result['content'] or ''
            term_matches = 0
            for term in important_terms:
                if term.lower() in content.lower():
                    term_matches += 1
            
            # 提升包含技术术语的结果分数
            if term_matches > 0:
                boost = term_matches * 0.1
                result['score'] = min(1.0, result['score'] + boost)
        
        return results
    
    def layer3_mmr_dedup(self, results: List[Dict], diversity_threshold: float = 0.8) -> List[Dict]:
        """第3层：MMR 多样性去重（简化版）"""
        if len(results) <= 1:
            return results
        
        unique_results = []
        seen_contents = set()
        
        for result in results:
            content_hash = hash(result['content'][:100])  # 只看前100字符
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def layer4_metadata_filter(self, results: List[Dict]) -> List[Dict]:
        """第4层：元数据过滤（只保留已解决问题）"""
        # 在当前数据库结构中，我们假设所有记录都是有效的
        # 实际应用中可以根据特定字段过滤
        return results
    
    def layer5_time_decay(self, results: List[Dict]) -> List[Dict]:
        """第5层：时间衰减加权"""
        now = datetime.now()
        
        for result in results:
            try:
                timestamp = datetime.strptime(result['timestamp'], '%Y-%m-%d %H:%M:%S')
                days_diff = (now - timestamp).days
                decay_factor = math.exp(-0.01 * days_diff)
                result['score'] *= decay_factor
            except:
                # 如果时间解析失败，保持原分数
                pass
        
        return results
    
    def layer6_preference_weight(self, results: List[Dict]) -> List[Dict]:
        """第6层：用户偏好加权"""
        code_patterns = [
            r'\bpython\b', r'\bjavascript\b', r'\bjava\b', r'\bgo\b', r'\brust\b',
            r'\bdef\s+\w+', r'\bfunction\s+\w+', r'\bclass\s+\w+',
            r'\bimport\b', r'\bfrom\s+\w+\s+import\b',
            r'\$\s+\w+', r'\bcommand:\s+', r'\bconfig:\s+'
        ]
        
        for result in results:
            content = result['content'] or ''
            code_score = 0
            
            for pattern in code_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    code_score += 0.1
            
            # 技术方案和架构说明加分
            if any(keyword in content.lower() for keyword in ['architecture', 'design', 'solution', 'implementation']):
                code_score += 0.15
            
            result['score'] = min(1.0, result['score'] + code_score)
        
        return results
    
    def layer7_rerank(self, results: List[Dict], top_k: int = 3) -> List[Dict]:
        """第7层：交叉编码器重排序（简化版）"""
        # 按分数排序并返回 top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def search(self, query: str) -> List[Dict]:
        """执行完整的7层检索"""
        print(f"🔍 执行7层混合检索: {query}")
        
        # 第1层：向量检索
        results = self.layer1_vector_search(query)
        print(f"第1层结果: {len(results)} 条")
        
        if not results:
            return []
        
        # 第2层：BM25 关键词检索
        results = self.layer2_bm25_keywords(results, query)
        print(f"第2层完成")
        
        # 第3层：MMR 去重
        results = self.layer3_mmr_dedup(results)
        print(f"第3层去重后: {len(results)} 条")
        
        # 第4层：元数据过滤
        results = self.layer4_metadata_filter(results)
        print(f"第4层过滤后: {len(results)} 条")
        
        # 第5层：时间衰减
        results = self.layer5_time_decay(results)
        print(f"第5层时间衰减完成")
        
        # 第6层：用户偏好加权
        results = self.layer6_preference_weight(results)
        print(f"第6层偏好加权完成")
        
        # 第7层：重排序
        results = self.layer7_rerank(results)
        print(f"第7层重排序后: {len(results)} 条")
        
        return results

def main():
    """测试函数"""
    retriever = Simple7LayerRetriever()
    
    # 测试查询
    test_queries = [
        "WordPress 发布博客",
        "DAMA-DMBOK2 教程",
        "LanceDB 向量检索",
        "Google Gemini API"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"查询: {query}")
        print(f"{'='*50}")
        
        results = retriever.search(query)
        
        if results:
            print("【记忆召回·已解决】")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. 相关度: {result['score']:.3f}")
                print(f"   内容: {result['content'][:200]}...")
                print(f"   时间: {result['timestamp']}")
                print(f"   来源: {result['source']}")
        else:
            print("无相关历史记忆")

if __name__ == "__main__":
    main()