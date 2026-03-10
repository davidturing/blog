"""
语义相似度过滤器
使用嵌入向量计算内容与科技达人主题的相似度
"""

import os
import json
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

class SemanticContentFilter:
    """语义内容过滤器"""
    
    def __init__(self):
        # 使用轻量级的嵌入模型
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 科技达人主题锚点
        self.tech_anchor_texts = [
            "AI Agent development and architecture",
            "Large Language Models and their applications", 
            "Vibe Coding and generative programming",
            "Multi-agent systems and coordination",
            "Machine learning research and breakthroughs",
            "Open source AI projects and frameworks",
            "Agentic AI and autonomous systems",
            "AI infrastructure and deployment",
            "Technical analysis of AI papers",
            "Software engineering for AI systems"
        ]
        
        # 预计算锚点嵌入
        self.anchor_embeddings = self.model.encode(self.tech_anchor_texts)
    
    def calculate_relevance_score(self, content: str) -> float:
        """
        计算内容与科技主题的相关性分数
        
        Args:
            content: 待评估的内容
            
        Returns:
            float: 相关性分数 (0.0 - 1.0)
        """
        if not content.strip():
            return 0.0
            
        # 计算内容嵌入
        content_embedding = self.model.encode([content])
        
        # 计算与所有锚点的最大相似度
        similarities = []
        for anchor_emb in self.anchor_embeddings:
            similarity = self._cosine_similarity(content_embedding[0], anchor_emb)
            similarities.append(similarity)
            
        max_similarity = max(similarities) if similarities else 0.0
        return max_similarity
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """计算余弦相似度"""
        import numpy as np
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    def is_relevant_content(self, content: str, threshold: float = 0.65) -> bool:
        """
        判断内容是否相关
        
        Args:
            content: 待判断的内容
            threshold: 相关性阈值
            
        Returns:
            bool: 是否相关
        """
        score = self.calculate_relevance_score(content)
        return score >= threshold

# 全局语义过滤器实例
_SEMANTIC_FILTER = None

def get_semantic_filter() -> SemanticContentFilter:
    """获取全局语义过滤器实例"""
    global _SEMANTIC_FILTER
    if _SEMANTIC_FILTER is None:
        _SEMANTIC_FILTER = SemanticContentFilter()
    return _SEMANTIC_FILTER