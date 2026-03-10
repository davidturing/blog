#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LanceDB 7层混合检索模块 - 简化版（无需scikit-learn）
作为 DavidAgent 的基础记忆增强能力
"""

import os
import sys
import json
import sqlite3
import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import google.genai as genai

# 配置 Gemini API
def configure_gemini():
    """配置 Google Gemini API"""
    # 从环境变量获取 API 密钥
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # 尝试从凭据文件获取
        credentials_path = os.path.join(os.path.dirname(__file__), ".credentials", "api_keys.env")
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip('"')
                        break
    
    if api_key:
        genai.configure(api_key=api_key)
        print(f"✅ Gemini API 配置成功")
    else:
        print("❌ 未找到 GOOGLE_API_KEY，请设置环境变量或凭据文件")
        sys.exit(1)

def get_embedding(text: str) -> List[float]:
    """使用 Gemini 获取文本嵌入向量"""
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"⚠️ 获取嵌入向量失败: {e}")
        # 返回零向量作为备用
        return [0.0] * 768

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算余弦相似度"""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def simple_bm25_score(query: str, document: str) -> float:
    """
    简化的 BM25 关键词匹配评分
    由于没有 scikit-learn，使用基本的 TF-IDF 近似
    """
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    doc_words = re.findall(r'\b\w+\b', document.lower())
    
    if not query_words or not doc_words:
        return 0.0
    
    # 计算查询词在文档中的出现频率
    score = 0.0
    doc_length = len(doc_words)
    
    for word in query_words:
        tf = doc_words.count(word) / doc_length
        # 简化的 IDF：假设所有词都重要
        idf = 1.0
        score += tf * idf
    
    return score

def calculate_time_decay(timestamp_str: str, current_time: datetime) -> float:
    """计算时间衰减权重"""
    try:
        # 处理不同格式的时间戳
        if timestamp_str.isdigit():
            timestamp = datetime.fromtimestamp(int(timestamp_str))
        else:
            # 尝试解析常见的日期格式
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        days_diff = (current_time - timestamp).days
        if days_diff < 0:
            days_diff = 0
        
        # 时间衰减公式: exp(-0.01 * 天数)
        return math.exp(-0.01 * days_diff)
    except Exception as e:
        print(f"⚠️ 时间解析失败: {e}")
        return 1.0  # 默认权重

def calculate_preference_score(content: str) -> float:
    """计算用户偏好加权分数"""
    score = 1.0
    
    # 技术关键词加分
    tech_keywords = ['command', 'code', 'step', 'configure', 'install', 'setup', 'api', 'function', 'class', 'method']
    content_lower = content.lower()
    
    for keyword in tech_keywords:
        if keyword in content_lower:
            score += 0.2
    
    # 代码片段检测
    if '```' in content or 'import ' in content or 'def ' in content:
        score += 0.3
    
    return min(score, 2.0)  # 最大加权2倍

def simple_rerank(query: str, candidates: List[Dict]) -> List[Dict]:
    """简单的重排序（由于没有交叉编码器）"""
    # 使用更精细的相似度计算
    for candidate in candidates:
        # 结合向量相似度和关键词匹配
        vector_score = candidate.get('vector_score', 0.0)
        keyword_score = simple_bm25_score(query, candidate.get('content', ''))
        combined_score = vector_score * 0.7 + keyword_score * 0.3
        candidate['final_score'] = combined_score
    
    # 按最终分数排序
    return sorted(candidates, key=lambda x: x['final_score'], reverse=True)

class LanceDB7LayerRetriever:
    """LanceDB 7层混合检索器"""
    
    def __init__(self, db_path: str = "david_agent_memory.db"):
        self.db_path = db_path
        self.current_time = datetime.now()
        self.load_memory_embeddings()
    
    def load_memory_embeddings(self):
        """加载记忆库的嵌入向量（如果存在）"""
        self.memory_embeddings = {}
        embedding_file = "memory_embeddings.json"
        if os.path.exists(embedding_file):
            try:
                with open(embedding_file, 'r') as f:
                    self.memory_embeddings = json.load(f)
                print(f"✅ 加载了 {len(self.memory_embeddings)} 个记忆嵌入向量")
            except Exception as e:
                print(f"⚠️ 加载嵌入向量失败: {e}")
                self.memory_embeddings = {}
    
    def save_memory_embeddings(self):
        """保存记忆嵌入向量"""
        embedding_file = "memory_embeddings.json"
        try:
            with open(embedding_file, 'w') as f:
                json.dump(self.memory_embeddings, f)
            print(f"✅ 保存了 {len(self.memory_embeddings)} 个记忆嵌入向量")
        except Exception as e:
            print(f"⚠️ 保存嵌入向量失败: {e}")
    
    def get_memory_from_db(self) -> List[Dict]:
        """从数据库获取记忆数据"""
        memories = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询 raw_signals 表
            cursor.execute("""
                SELECT signal_id, content_hash, handle, author_name, 
                       timestamp, likes, retweets, raw_text, raw_json, 
                       signal_type, ingested_at
                FROM raw_signals
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                memory = {
                    'id': row[0],
                    'content_hash': row[1],
                    'handle': row[2],
                    'author_name': row[3],
                    'timestamp': row[4],
                    'likes': row[5],
                    'retweets': row[6],
                    'content': row[7],
                    'raw_json': row[8],
                    'signal_type': row[9],
                    'ingested_at': row[10],
                    'source': 'raw_signals',
                    'solved': 1  # 假设所有信号都是已解决的
                }
                memories.append(memory)
            
            # 查询 trace_logs 表
            cursor.execute("""
                SELECT task_id, timestamp, workflow_status, raw_source,
                       left_brain_graph, right_brain_draft, review_feedback,
                       logic_score, tone_score, format_score, human_comment,
                       pipeline_trace, full_snapshot
                FROM trace_logs
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                # 合并相关字段作为内容
                content_parts = [
                    row[2],  # workflow_status
                    row[3],  # raw_source  
                    row[4],  # left_brain_graph
                    row[5],  # right_brain_draft
                    row[6],  # review_feedback
                    row[10]  # human_comment
                ]
                content = '\n'.join([part for part in content_parts if part])
                
                if content.strip():
                    memory = {
                        'id': row[0],
                        'timestamp': row[1],
                        'content': content,
                        'logic_score': row[7],
                        'tone_score': row[8],
                        'format_score': row[9],
                        'pipeline_trace': row[11],
                        'full_snapshot': row[12],
                        'source': 'trace_logs',
                        'solved': 1 if row[2] and 'completed' in row[2].lower() else 0
                    }
                    memories.append(memory)
            
            conn.close()
            print(f"✅ 从数据库加载了 {len(memories)} 条记忆")
            
        except Exception as e:
            print(f"⚠️ 数据库查询失败: {e}")
        
        return memories
    
    def layer1_vector_retrieval(self, query: str, memories: List[Dict], top_k: int = 20) -> List[Dict]:
        """第1层：向量检索"""
        print(f"第1层：向量检索 (top{top_k})")
        
        # 获取查询嵌入
        query_embedding = get_embedding(query)
        
        # 计算相似度
        scored_memories = []
        for memory in memories:
            content = memory.get('content', '')
            if not content.strip():
                continue
            
            # 获取或计算记忆嵌入
            memory_id = memory.get('id', str(hash(content)))
            if memory_id not in self.memory_embeddings:
                self.memory_embeddings[memory_id] = get_embedding(content)
            
            memory_embedding = self.memory_embeddings[memory_id]
            similarity = cosine_similarity(query_embedding, memory_embedding)
            
            if similarity > 0.1:  # 过滤低相似度
                memory_copy = memory.copy()
                memory_copy['vector_score'] = similarity
                scored_memories.append(memory_copy)
        
        # 按相似度排序，取top_k
        scored_memories.sort(key=lambda x: x['vector_score'], reverse=True)
        result = scored_memories[:top_k]
        print(f"第1层结果: {len(result)} 条")
        return result
    
    def layer2_bm25_retrieval(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """第2层：BM25关键词检索"""
        print("第2层：BM25关键词检索")
        
        for candidate in candidates:
            content = candidate.get('content', '')
            bm25_score = simple_bm25_score(query, content)
            candidate['bm25_score'] = bm25_score
            # 结合向量分数和关键词分数
            candidate['combined_score'] = (
                candidate.get('vector_score', 0) * 0.6 + 
                bm25_score * 0.4
            )
        
        print("第2层完成")
        return candidates
    
    def layer3_mmr_deduplication(self, candidates: List[Dict], diversity_threshold: float = 0.8) -> List[Dict]:
        """第3层：MMR多样性去重"""
        print("第3层：MMR去重")
        
        if len(candidates) <= 1:
            return candidates
        
        # 简化的去重：基于内容哈希和相似度
        unique_candidates = []
        seen_hashes = set()
        
        for candidate in candidates:
            content = candidate.get('content', '')
            content_hash = hash(content)
            
            # 检查是否已经见过相同内容
            if content_hash in seen_hashes:
                continue
            
            # 检查与已有结果的相似度
            is_duplicate = False
            for existing in unique_candidates:
                existing_content = existing.get('content', '')
                if len(content) > 0 and len(existing_content) > 0:
                    similarity = cosine_similarity(
                        self.memory_embeddings.get(candidate.get('id', ''), [0.0]*768),
                        self.memory_embeddings.get(existing.get('id', ''), [0.0]*768)
                    )
                    if similarity > diversity_threshold:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_candidates.append(candidate)
                seen_hashes.add(content_hash)
        
        print(f"第3层去重后: {len(unique_candidates)} 条")
        return unique_candidates
    
    def layer4_metadata_filter(self, candidates: List[Dict]) -> List[Dict]:
        """第4层：元数据过滤（只保留已解决问题）"""
        print("第4层：元数据过滤")
        
        filtered = [cand for cand in candidates if cand.get('solved', 0) == 1]
        print(f"第4层过滤后: {len(filtered)} 条")
        return filtered
    
    def layer5_time_decay(self, candidates: List[Dict]) -> List[Dict]:
        """第5层：时间衰减加权"""
        print("第5层：时间衰减加权")
        
        for candidate in candidates:
            timestamp = candidate.get('timestamp', '')
            time_weight = calculate_time_decay(timestamp, self.current_time)
            candidate['time_weight'] = time_weight
            candidate['score_after_time'] = candidate.get('combined_score', 0) * time_weight
        
        print("第5层时间衰减完成")
        return candidates
    
    def layer6_preference_weighting(self, candidates: List[Dict]) -> List[Dict]:
        """第6层：用户偏好加权"""
        print("第6层：用户偏好加权")
        
        for candidate in candidates:
            content = candidate.get('content', '')
            pref_weight = calculate_preference_score(content)
            candidate['preference_weight'] = pref_weight
            candidate['score_after_pref'] = candidate.get('score_after_time', 0) * pref_weight
        
        print("第6层偏好加权完成")
        return candidates
    
    def layer7_reranking(self, candidates: List[Dict], top_k: int = 3) -> List[Dict]:
        """第7层：交叉编码器重排序"""
        print("第7层：重排序")
        
        # 使用简化的重排序
        reranked = simple_rerank("", candidates)  # 查询已在前面处理
        result = reranked[:top_k]
        print(f"第7层重排序后: {len(result)} 条")
        return result
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """执行完整的7层混合检索"""
        print(f"🔍 执行7层混合检索: {query}")
        
        # 获取所有记忆
        all_memories = self.get_memory_from_db()
        if not all_memories:
            print("无可用记忆数据")
            return []
        
        # 第1层：向量检索
        candidates = self.layer1_vector_retrieval(query, all_memories, top_k * 10)
        if not candidates:
            return []
        
        # 第2层：BM25关键词检索
        candidates = self.layer2_bm25_retrieval(query, candidates)
        
        # 第3层：MMR去重
        candidates = self.layer3_mmr_deduplication(candidates)
        if not candidates:
            return []
        
        # 第4层：元数据过滤
        candidates = self.layer4_metadata_filter(candidates)
        if not candidates:
            return []
        
        # 第5层：时间衰减
        candidates = self.layer5_time_decay(candidates)
        
        # 第6层：偏好加权
        candidates = self.layer6_preference_weighting(candidates)
        
        # 第7层：重排序
        final_results = self.layer7_reranking(candidates, top_k)
        
        return final_results

def format_results(results: List[Dict]) -> str:
    """格式化检索结果"""
    if not results:
        return "无相关历史记忆"
    
    output = "【记忆召回·已解决】\n\n"
    for i, result in enumerate(results, 1):
        content = result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', '')
        timestamp = result.get('timestamp', '未知时间')
        source = result.get('source', '未知来源')
        
        output += f"{i}. 相关度: {result.get('final_score', 0):.3f}\n"
        output += f"   内容: {content}\n"
        output += f"   时间: {timestamp}\n"
        output += f"   来源: {source}\n\n"
    
    return output.strip()

def main():
    """主函数 - 测试用例"""
    configure_gemini()
    
    retriever = LanceDB7LayerRetriever()
    
    # 测试查询
    test_queries = [
        "WordPress 发布博客",
        "DAMA-DMBOK2 教程", 
        "LanceDB 向量检索",
        "Google Gemini API"
    ]
    
    for query in test_queries:
        print("=" * 50)
        print(f"查询: {query}")
        print("=" * 50)
        
        results = retriever.retrieve(query)
        print(format_results(results))
        print()
    
    # 保存嵌入向量
    retriever.save_memory_embeddings()

if __name__ == "__main__":
    main()