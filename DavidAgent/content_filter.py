"""
AI 内容过滤器 - 确保只处理与 AI/技术相关的内容
"""

import re
from typing import List, Dict

class AIContentFilter:
    """AI 内容过滤器"""
    
    def __init__(self):
        # AI/技术相关关键词
        self.ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'large language model', 'gpt', 'gemini',
            'claude', 'openai', 'anthropic', 'google ai', 'microsoft ai',
            'agent', 'multi-agent', 'autonomous', 'automation', 'robotics',
            'computer vision', 'nlp', 'natural language', 'generative',
            'diffusion', 'transformer', 'attention', 'embedding', 'vector',
            'rag', 'retrieval', 'fine-tuning', 'prompt', 'inference',
            'training', 'dataset', 'algorithm', 'framework', 'library',
            'python', 'javascript', 'coding', 'programming', 'software',
            'cloud', 'api', 'model', 'architecture', 'system', 'design',
            'engineering', 'developer', 'tech', 'technology', 'innovation',
            'research', 'paper', 'arxiv', 'github', 'open source',
            'vibe coding', 'agentic', 'dama', 'data governance',
            'skillrl', 'recursive', 'evolution', 'reinforcement learning'
        ]
        
        # 非 AI 相关的排除关键词（如体育、娱乐等）
        self.exclude_keywords = [
            'football', 'soccer', 'basketball', 'tennis', 'baseball',
            'cricket', 'rugby', 'hockey', 'golf', 'boxing', 'mma',
            'wrestling', 'olympics', 'world cup', 'champions league',
            'premier league', 'la liga', 'serie a', 'bundesliga',
            'music', 'movie', 'film', 'celebrity', 'entertainment',
            'fashion', 'beauty', 'cooking', 'recipe', 'food', 'travel',
            'politics', 'election', 'government', 'war', 'conflict',
            'weather', 'climate', 'environment', 'health', 'medical',
            'finance', 'stock', 'crypto', 'bitcoin', 'ethereum'
        ]
        
        # 转换为小写以便匹配
        self.ai_keywords_lower = [kw.lower() for kw in self.ai_keywords]
        self.exclude_keywords_lower = [kw.lower() for kw in self.exclude_keywords]
    
    def is_ai_related(self, text: str) -> bool:
        """
        判断文本是否与 AI/技术相关
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 是否与 AI 相关
        """
        if not text:
            return False
            
        text_lower = text.lower()
        
        # 检查是否包含排除关键词（如果有，直接返回 False）
        for exclude_kw in self.exclude_keywords_lower:
            if exclude_kw in text_lower:
                print(f"❌ 内容过滤: 检测到排除关键词 '{exclude_kw}'，跳过处理")
                return False
        
        # 检查是否包含 AI 关键词
        ai_score = 0
        for ai_kw in self.ai_keywords_lower:
            if ai_kw in text_lower:
                ai_score += 1
                
        # 如果 AI 关键词数量 >= 1，则认为是 AI 相关
        if ai_score >= 1:
            print(f"✅ 内容过滤: 检测到 {ai_score} 个 AI 关键词，通过过滤")
            return True
        else:
            print(f"❌ 内容过滤: 未检测到足够的 AI 关键词（得分: {ai_score}），跳过处理")
            return False
    
    def filter_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """
        过滤推文列表，只保留 AI 相关的内容
        
        Args:
            tweets: 推文列表
            
        Returns:
            List[Dict]: 过滤后的推文列表
        """
        filtered_tweets = []
        for tweet in tweets:
            text = tweet.get('text', '')
            if self.is_ai_related(text):
                filtered_tweets.append(tweet)
            else:
                print(f"❌ 跳过非 AI 相关推文: {text[:100]}...")
                
        return filtered_tweets

# 全局过滤器实例
_AI_CONTENT_FILTER = None

def get_ai_content_filter() -> AIContentFilter:
    """获取全局 AI 内容过滤器实例"""
    global _AI_CONTENT_FILTER
    if _AI_CONTENT_FILTER is None:
        _AI_CONTENT_FILTER = AIContentFilter()
    return _AI_CONTENT_FILTER