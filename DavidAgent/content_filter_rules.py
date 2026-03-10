"""
科技达人数字分身内容过滤规则
确保只处理与AI/技术相关的专业内容
"""

import re
from typing import List, Tuple

class TechEnthusiastContentFilter:
    """科技达人内容过滤器"""
    
    def __init__(self):
        # AI/技术相关关键词（必须包含至少一个）
        self.tech_keywords = [
            # AI 基础
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'large language model', 'foundation model',
            'generative ai', 'genai', 'transformer', 'diffusion model',
            
            # 大模型和框架
            'gpt', 'gemini', 'claude', 'llama', 'mistral', 'qwen', 'bailian',
            'openai', 'anthropic', 'google deepmind', 'meta ai', 'hugging face',
            
            # AI Agent 相关
            'ai agent', 'multi-agent', 'agentic', 'agent framework', 'autonomous agent',
            'vibe coding', 'prompt engineering', 'reinforcement learning', 'rlhf',
            
            # 技术开发
            'open source', 'github', 'api', 'framework', 'library', 'toolkit',
            'developer', 'programming', 'coding', 'software engineering',
            'cloud computing', 'distributed system', 'microservice',
            
            # 中文关键词
            '人工智能', '机器学习', '深度学习', '大模型', '语言模型', '生成式',
            '智能体', '多智能体', '开源', '框架', '开发者', '编程', '云计算'
        ]
        
        # 禁止的主题关键词（如果包含则直接拒绝）
        self.banned_topics = [
            # 体育
            'football', 'soccer', 'basketball', 'tennis', 'olympic', 'world cup',
            'champion', 'player', 'team', 'match', 'game', 'score', 'goal',
            '足球', '篮球', '网球', '奥运会', '世界杯', '冠军', '球员', '球队',
            
            # 娱乐
            'movie', 'film', 'actor', 'actress', 'celebrity', 'entertainment',
            'music', 'song', 'album', 'concert', '明星', '电影', '音乐', '演唱会',
            
            # 政治
            'politics', 'election', 'government', 'president', 'prime minister',
            'political', 'vote', 'democracy', '政', '选举', '政府', '总统',
            
            # 社会新闻
            'accident', 'crime', 'disaster', 'war', 'conflict', '事故', '犯罪',
            '灾难', '战争', '冲突'
        ]
    
    def is_tech_related(self, text: str) -> bool:
        """
        判断文本是否与AI/技术相关
        
        Args:
            text: 待检测的文本
            
        Returns:
            bool: 是否为技术相关内容
        """
        if not text:
            return False
            
        text_lower = text.lower()
        
        # 检查是否包含禁止主题
        for banned_word in self.banned_topics:
            if banned_word.lower() in text_lower:
                print(f"❌ 内容过滤: 检测到禁止主题 '{banned_word}'，拒绝处理")
                return False
        
        # 检查是否包含技术关键词
        tech_count = 0
        for keyword in self.tech_keywords:
            if keyword.lower() in text_lower:
                tech_count += 1
                if tech_count >= 1:  # 至少包含1个技术关键词
                    return True
        
        print(f"❌ 内容过滤: 未检测到技术相关关键词，拒绝处理")
        return False
    
    def filter_content(self, content_data: dict) -> Tuple[bool, str]:
        """
        过滤内容数据
        
        Args:
            content_data: 包含 'text', 'author', 'url' 等字段的字典
            
        Returns:
            Tuple[bool, str]: (是否通过过滤, 过滤结果说明)
        """
        text = content_data.get('text', '')
        author = content_data.get('author', '')
        url = content_data.get('url', '')
        
        # 主要内容过滤
        if not self.is_tech_related(text):
            return False, "内容不包含AI/技术相关关键词"
        
        # URL 过滤（可选）
        if any(banned in url.lower() for banned in ['sports', 'entertainment', 'news']):
            return False, "URL 包含非技术领域关键词"
            
        return True, "内容通过过滤，符合科技达人专业领域"

# 全局过滤器实例
_CONTENT_FILTER = None

def get_content_filter() -> TechEnthusiastContentFilter:
    """获取全局内容过滤器实例"""
    global _CONTENT_FILTER
    if _CONTENT_FILTER is None:
        _CONTENT_FILTER = TechEnthusiastContentFilter()
    return _CONTENT_FILTER