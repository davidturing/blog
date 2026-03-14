"""
认知熵过滤核心 - 基于 KL 散度的信息增益计算

实现认知熵过滤算法，只允许高信息增益的内容进入 LLM 蒸馏流程。
"""

import numpy as np
from typing import List, Dict, Any, Optional
import logging
from scipy.stats import entropy
import hashlib


class CognitiveEntropyFilter:
    """认知熵过滤器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化认知熵过滤器
        
        Args:
            config: 配置字典，包含认知阈值等参数
        """
        self.logger = logging.getLogger("CognitiveEntropyFilter")
        self.cognitive_threshold = config.get("cognitive_threshold", 0.65)
        self.max_fetch_per_cycle = config.get("max_fetch_per_cycle", 5)
        
        # 初始化已见内容缓存（用于去重）
        self.seen_content_hashes = set()
        
    def calculate_information_gain(self, content: str, reference_distribution: Optional[np.ndarray] = None) -> float:
        """计算内容的信息增益（基于 KL 散度）
        
        Args:
            content: 待评估的内容文本
            reference_distribution: 参考分布（可选，用于计算 KL 散度）
            
        Returns:
            信息增益分数 (0-1)
        """
        if not content or len(content.strip()) < 10:
            return 0.0
            
        # 生成内容哈希用于去重
        content_hash = self._hash_content(content)
        if content_hash in self.seen_content_hashes:
            self.logger.debug("内容已存在，跳过重复项")
            return 0.0
            
        # 简化的信息增益计算
        # 在实际实现中，这里会使用更复杂的 NLP 模型和向量相似度计算
        info_gain = self._estimate_information_gain_simple(content, reference_distribution)
        
        # 如果信息增益足够高，记录该内容
        if info_gain > self.cognitive_threshold:
            self.seen_content_hashes.add(content_hash)
            
        return info_gain
        
    def _hash_content(self, content: str) -> str:
        """生成内容的哈希值用于去重
        
        Args:
            content: 内容文本
            
        Returns:
            哈希字符串
        """
        # 使用 SHA256 哈希
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
    def _estimate_information_gain_simple(self, content: str, reference_distribution: Optional[np.ndarray]) -> float:
        """简化版信息增益估算
        
        Args:
            content: 内容文本
            reference_distribution: 参考分布
            
        Returns:
            估算的信息增益分数
        """
        # 这里是简化的实现
        # 在生产环境中，应该使用：
        # 1. 向量化内容
        # 2. 计算与现有知识库的相似度
        # 3. 基于相似度反推信息增益
        
        content_lower = content.lower()
        
        # 关键词权重（模拟信息密度）
        high_value_keywords = [
            'novel', 'breakthrough', 'innovative', 'efficient', 'scalable',
            'architecture', 'framework', 'protocol', 'algorithm', 'system',
            'implementation', 'benchmark', 'performance', 'optimization'
        ]
        
        keyword_score = sum(1 for keyword in high_value_keywords if keyword in content_lower)
        keyword_density = min(keyword_score / len(high_value_keywords), 1.0)
        
        # 长度因子（太短或太长都可能信息密度低）
        length_factor = min(len(content) / 1000, 1.0) if len(content) > 100 else 0.1
        
        # 综合评分
        info_gain = (keyword_density * 0.7 + length_factor * 0.3)
        
        return info_gain
        
    def filter_content_batch(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量过滤内容，只保留高信息增益的内容
        
        Args:
            contents: 内容列表，每个内容是字典格式
            
        Returns:
            过滤后的高价值内容列表
        """
        filtered_contents = []
        
        for content_item in contents:
            content_text = content_item.get("content", "")
            info_gain = self.calculate_information_gain(content_text)
            
            if info_gain > self.cognitive_threshold:
                content_item["information_gain"] = info_gain
                filtered_contents.append(content_item)
                
            # 限制每轮获取数量
            if len(filtered_contents) >= self.max_fetch_per_cycle:
                break
                
        self.logger.info(f"过滤前: {len(contents)} 项, 过滤后: {len(filtered_contents)} 项")
        return filtered_contents
        
    def update_reference_distribution(self, new_knowledge: List[str]):
        """更新参考分布（在实际系统中会定期调用）
        
        Args:
            new_knowledge: 新知识列表
        """
        # 在实际实现中，这里会更新向量数据库中的参考分布
        # 目前是占位实现
        pass