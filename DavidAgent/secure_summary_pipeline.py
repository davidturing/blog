#!/usr/bin/env python3
"""
安全的摘要提取 Pipeline - 严格的内容过滤 + 主题验证
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from content_filter_rules import ContentFilter
from semantic_filter import SemanticFilter
from brain.left_brain.experience_distiller import get_experience_distiller


class SecureSummaryPipeline:
    """安全的摘要提取管道"""
    
    def __init__(self):
        self.content_filter = ContentFilter()
        self.semantic_filter = SemanticFilter()
        self.distiller = get_experience_distiller()
    
    async def process_tweet_safely(self, tweet_data: dict) -> dict:
        """
        安全处理推文：过滤 → 验证 → 摘要提取
        
        Args:
            tweet_data: 推文数据字典
            
        Returns:
            处理结果字典，包含是否通过过滤、摘要内容等
        """
        result = {
            'original_tweet': tweet_data,
            'passed_filter': False,
            'filter_reason': '',
            'summary': None,
            'keywords_matched': [],
            'semantic_score': 0.0
        }
        
        # 步骤 1: 基础内容过滤
        filter_result = self.content_filter.check_content(tweet_data)
        if not filter_result['allowed']:
            result['filter_reason'] = f"基础过滤失败: {filter_result['reason']}"
            return result
        
        # 步骤 2: 语义相似度验证
        semantic_result = self.semantic_filter.analyze_semantic_relevance(tweet_data)
        if semantic_result['score'] < 0.7:  # 阈值可配置
            result['filter_reason'] = f"语义相关性不足: {semantic_result['score']:.2f} < 0.7"
            return result
        
        # 步骤 3: 提取摘要（只有通过过滤的内容才进行摘要）
        try:
            summary = await self._extract_summary(tweet_data)
            result.update({
                'passed_filter': True,
                'summary': summary,
                'keywords_matched': filter_result['matched_keywords'],
                'semantic_score': semantic_result['score']
            })
        except Exception as e:
            result['filter_reason'] = f"摘要提取失败: {str(e)}"
        
        return result
    
    async def _extract_summary(self, tweet_data: dict) -> dict:
        """提取推文摘要"""
        # 这里调用左脑的摘要功能
        # 实际实现会使用 Gemini API 进行摘要和翻译
        text = tweet_data.get('text', '')
        author = tweet_data.get('author', 'Unknown')
        username = tweet_data.get('username', 'unknown')
        
        # 构建摘要 prompt
        prompt = f"""
任务: 将以下推文翻译成中文并提取核心观点。

输出格式:
TRANSLATION: [中文翻译]
KEY_POINT: [核心洞察]

推文作者: @{username}
推文内容: {text}
"""
        
        # 调用左脑进行摘要（简化版本）
        # 实际会调用 Gemini API
        return {
            'translation': f"[模拟翻译] {text}",
            'key_point': f"[模拟核心观点] 这是一条关于AI技术的推文",
            'author': author,
            'username': username
        }


# 全局安全摘要管道实例
_SECURE_SUMMARY_PIPELINE = None

def get_secure_summary_pipeline() -> SecureSummaryPipeline:
    """获取全局安全摘要管道实例"""
    global _SECURE_SUMMARY_PIPELINE
    if _SECURE_SUMMARY_PIPELINE is None:
        _SECURE_SUMMARY_PIPELINE = SecureSummaryPipeline()
    return _SECURE_SUMMARY_PIPELINE