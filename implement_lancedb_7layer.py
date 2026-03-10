#!/usr/bin/env python3
"""
LanceDB 7层混合检索模块实现
基于 Google Gemini 生成的代码框架
"""

import os
import math
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import lancedb
import numpy as np
from google.genai import embedding
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LanceDB7LayerRetriever:
    def __init__(self, db_path: str = "/Users/zhaoqinhuang/david_project/lancedb"):
        """初始化7层混合检索器"""
        self.db = lancedb.connect(db_path)
        self.table = None
        self._load_table()
        
    def _load_table(self):
        """加载现有的LanceDB表"""
        try:
            self.table = self.db.open_table("memory")
        except Exception as e:
            print(f"警告: 无法加载现有记忆表: {e}")
            # 创建新表的schema
            schema = {
                "id": "string",
                "content": "string", 
                "embedding": "vector(768)",
                "timestamp": "datetime64[ms]",
                "solved": "bool",
                "metadata": "string"
            }
            self.table = self.db.create_table("memory", schema=schema, mode="overwrite")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """使用Google Gemini生成文本嵌入"""
        try:
            result = embedding.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"嵌入生成失败: {e}")
            # 返回零向量作为后备
            return [0.0] * 768
    
    def layer1_vector_search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """第1层：向量检索 - 召回top20最相似记忆"""
        query_embedding = self._generate_embedding(query)
        results = self.table.search(query_embedding).limit(top_k).to_pandas()
        return results.to_dict('records')
    
    def layer2_bm25_keyword_search(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """第2层：BM25关键词检索 - 提升技术术语权重"""
        # 提取技术关键词（命令、配置项、技术术语）
        tech_keywords = self._extract_tech_keywords(query)
        
        scored_candidates = []
        for candidate in candidates:
            content = candidate['content']
            score = 0
            
            # 基础关键词匹配
            for keyword in tech_keywords:
                if keyword.lower() in content.lower():
                    score += 2  # 技术术语权重更高
            
            # 普通关键词匹配
            query_words = query.lower().split()
            for word in query_words:
                if len(word) > 2 and word in content.lower():
                    score += 1
            
            candidate['bm25_score'] = score
            scored_candidates.append(candidate)
        
        # 按BM25分数排序
        scored_candidates.sort(key=lambda x: x['bm25_score'], reverse=True)
        return scored_candidates
    
    def _extract_tech_keywords(self, text: str) -> List[str]:
        """提取技术关键词"""
        keywords = []
        
        # 命令模式
        cmd_pattern = r'\b[a-z]+(?:\s+[a-z0-9\-_]+)*\b'
        commands = re.findall(cmd_pattern, text)
        keywords.extend([cmd for cmd in commands if len(cmd.split()) <= 3])
        
        # 配置项模式
        config_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*\s*[:=]\s*[^,\s]+'
        configs = re.findall(config_pattern, text)
        keywords.extend(configs)
        
        # 技术术语（已知的技术词汇）
        tech_terms = ['lancedb', 'gemini', 'embedding', 'vector', 'retrieval', 'memory', 'database', 'python', 'api']
        for term in tech_terms:
            if term in text.lower():
                keywords.append(term)
        
        return list(set(keywords))
    
    def layer3_mmr_deduplication(self, candidates: List[Dict[str, Any]], diversity_lambda: float = 0.7) -> List[Dict[str, Any]]:
        """第3层：MMR多样性去重"""
        if len(candidates) <= 3:
            return candidates
        
        selected = [candidates[0]]  # 选择第一个（最高分）
        remaining = candidates[1:]
        
        while len(selected) < min(10, len(candidates)) and remaining:
            best_score = -1
            best_candidate = None
            
            for candidate in remaining:
                # 计算与已选项目的最大相似度
                max_sim = 0
                for selected_item in selected:
                    sim = self._calculate_similarity(candidate['content'], selected_item['content'])
                    max_sim = max(max_sim, sim)
                
                # MMR公式: lambda * relevance - (1-lambda) * max_similarity
                relevance = candidate.get('bm25_score', 0) + candidate.get('_distance', 0)
                mmr_score = diversity_lambda * relevance - (1 - diversity_lambda) * max_sim
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break
        
        return selected
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        try:
            vectorizer = TfidfVectorizer().fit([text1, text2])
            tfidf_matrix = vectorizer.transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def layer4_metadata_filter(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """第4层：元数据过滤 - 只保留已解决的问题"""
        filtered = []
        for candidate in candidates:
            # 检查是否标记为已解决
            if candidate.get('solved', False):
                filtered.append(candidate)
            else:
                # 尝试从内容中推断是否为解决方案
                content = candidate['content'].lower()
                solution_indicators = ['解决了', '完成', '成功', '已修复', '方案', '步骤', '命令', '代码']
                if any(indicator in content for indicator in solution_indicators):
                    filtered.append(candidate)
        
        return filtered
    
    def layer5_time_decay_weighting(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """第5层：时间衰减加权"""
        now = datetime.now()
        weighted_candidates = []
        
        for candidate in candidates:
            # 计算天数差
            try:
                timestamp = candidate.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif hasattr(timestamp, 'timestamp'):
                    timestamp = datetime.fromtimestamp(timestamp.timestamp())
                
                days_diff = (now - timestamp).days
                time_weight = math.exp(-0.01 * days_diff)
                
                # 应用时间权重
                base_score = candidate.get('bm25_score', 1)
                candidate['time_weighted_score'] = base_score * time_weight
                weighted_candidates.append(candidate)
            except Exception as e:
                candidate['time_weighted_score'] = candidate.get('bm25_score', 1)
                weighted_candidates.append(candidate)
        
        # 按时间加权分数排序
        weighted_candidates.sort(key=lambda x: x['time_weighted_score'], reverse=True)
        return weighted_candidates
    
    def layer6_preference_weighting(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """第6层：用户偏好加权"""
        weighted_candidates = []
        
        for candidate in candidates:
            content = candidate['content']
            preference_score = candidate.get('time_weighted_score', 1)
            
            # 对包含命令、步骤、代码的记忆加分
            if any(pattern in content for pattern in ['```', '命令', '步骤', '运行', '执行', '安装']):
                preference_score *= 1.5
            
            # 对技术方案、架构说明额外加权
            if any(pattern in content.lower() for pattern in ['架构', '方案', '设计', '实现', '模块', '系统']):
                preference_score *= 1.3
            
            candidate['preference_weighted_score'] = preference_score
            weighted_candidates.append(candidate)
        
        # 按偏好加权分数排序
        weighted_candidates.sort(key=lambda x: x['preference_weighted_score'], reverse=True)
        return weighted_candidates
    
    def layer7_cross_encoder_rerank(self, candidates: List[Dict[str, Any]], query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """第7层：交叉编码器重排序 - 使用小模型精排"""
        # 由于我们使用Gemini，这里模拟交叉编码器的行为
        # 实际上可以调用更小的模型进行精排
        
        scored_candidates = []
        for candidate in candidates[:10]:  # 只处理top10
            # 计算查询和内容的相关性
            relevance = self._calculate_query_relevance(query, candidate['content'])
            final_score = candidate.get('preference_weighted_score', 1) * relevance
            candidate['final_score'] = final_score
            scored_candidates.append(candidate)
        
        # 按最终分数排序并返回top3
        scored_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        return scored_candidates[:top_k]
    
    def _calculate_query_relevance(self, query: str, content: str) -> float:
        """计算查询与内容的相关性"""
        # 简单的相关性计算
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        relevance = overlap / len(query_words)
        
        # 添加语义相关性（如果可能）
        try:
            query_emb = self._generate_embedding(query)
            content_emb = self._generate_embedding(content)
            semantic_sim = np.dot(query_emb, content_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(content_emb))
            return (relevance + semantic_sim) / 2
        except:
            return relevance
    
    def retrieve(self, query: str) -> Dict[str, Any]:
        """执行完整的7层混合检索"""
        try:
            # 第1层：向量检索
            candidates = self.layer1_vector_search(query)
            if not candidates:
                return {"status": "no_memory", "message": "无相关历史"}
            
            # 第2层：BM25关键词检索
            candidates = self.layer2_bm25_keyword_search(query, candidates)
            
            # 第3层：MMR去重
            candidates = self.layer3_mmr_deduplication(candidates)
            
            # 第4层：元数据过滤
            candidates = self.layer4_metadata_filter(candidates)
            if not candidates:
                return {"status": "no_solved_memory", "message": "无相关已解决历史"}
            
            # 第5层：时间衰减加权
            candidates = self.layer5_time_decay_weighting(candidates)
            
            # 第6层：用户偏好加权
            candidates = self.layer6_preference_weighting(candidates)
            
            # 第7层：交叉编码器重排
            final_results = self.layer7_cross_encoder_rerank(candidates, query)
            
            return {
                "status": "success",
                "results": final_results,
                "message": "【记忆召回·已解决】"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"检索失败: {str(e)}"}

# 使用示例
if __name__ == "__main__":
    retriever = LanceDB7LayerRetriever()
    result = retriever.retrieve("如何实现LanceDB 7层混合检索？")
    print(json.dumps(result, indent=2, default=str))