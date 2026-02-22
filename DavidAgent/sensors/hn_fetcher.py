"""
Hacker News 智能嗅探器 (HN Fetcher)
用于从Hacker News API获取热门技术帖子并进行语义过滤
"""
import asyncio
import json
import hashlib
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

class HNFetcher:
    """Hacker News 智能嗅探器"""
    
    def __init__(self, keywords: List[str] = None):
        """
        初始化HN抓取器
        
        Args:
            keywords: 技术关键词列表，用于语义过滤
        """
        self.keywords = keywords or [
            "AI", "LLM", "Agent", "Cursor", "Copilot", "Code", "Python", 
            "React", "JavaScript", "TypeScript", "Machine Learning", 
            "Deep Learning", "Neural", "OpenAI", "Anthropic", "Gemini",
            "LangChain", "Devin", "GitHub", "Programming", "Developer"
        ]
        self.hn_api_base = "https://hacker-news.firebaseio.com/v0"
        self.headers = {
            "User-Agent": "DavidAgent-DevPulseSensor/1.0"
        }
    
    async def _make_request(self, client: httpx.AsyncClient, url: str, **kwargs) -> dict:
        """统一的API请求方法"""
        try:
            response = await client.get(url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"HN API请求失败: {e}")
            return {}
    
    def _contains_keywords(self, text: str) -> bool:
        """
        检查文本是否包含技术关键词
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 是否包含关键词
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def _extract_domain(self, url: str) -> str:
        """提取URL的域名"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "unknown"
    
    def _clean_text(self, text: str) -> str:
        """清理和格式化文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # 限制长度
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        return text
    
    async def _extract_article_content(self, client: httpx.AsyncClient, url: str) -> str:
        """
        提取文章正文内容
        
        Args:
            client: 异步HTTP客户端
            url: 文章URL
            
        Returns:
            str: 提取的正文内容
        """
        try:
            response = await client.get(url, headers=self.headers, timeout=15.0)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 尝试找到主要内容
            content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '.post-body',
                '.article-body'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text() for elem in elements])
                    break
            
            # 如果没有找到特定内容，使用整个body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text()
            
            return self._clean_text(content)
            
        except Exception as e:
            print(f"文章内容提取失败 ({url}): {e}")
            return ""
    
    async def fetch_top_stories(self, limit: int = 30) -> List[Dict]:
        """
        获取HN热门帖子并进行语义过滤
        
        Args:
            limit: 获取的帖子数量限制
            
        Returns:
            List[Dict]: 符合条件的帖子列表
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 获取热门帖子ID列表
                top_stories_url = f"{self.hn_api_base}/topstories.json"
                story_ids = await self._make_request(client, top_stories_url)
                
                if not story_ids:
                    print("未能获取HN热门帖子ID")
                    return []
                
                # 获取前limit个帖子的详细信息
                stories = []
                for story_id in story_ids[:limit]:
                    story_url = f"{self.hn_api_base}/item/{story_id}.json"
                    story_data = await self._make_request(client, story_url)
                    
                    if not story_data:
                        continue
                    
                    # 检查是否为故事类型（非评论）
                    if story_data.get('type') != 'story':
                        continue
                    
                    # 语义过滤：检查标题是否包含技术关键词
                    title = story_data.get('title', '')
                    if not self._contains_keywords(title):
                        continue
                    
                    # 获取URL
                    url = story_data.get('url')
                    if not url:
                        continue
                    
                    # 提取文章正文
                    content = await self._extract_article_content(client, url)
                    if not content:
                        # 如果无法提取正文，使用标题作为内容
                        content = title
                    
                    # 构建帖子信息
                    story_info = {
                        'id': story_id,
                        'title': title,
                        'url': url,
                        'author': story_data.get('by', 'unknown'),
                        'score': story_data.get('score', 0),
                        'time': story_data.get('time', 0),
                        'domain': self._extract_domain(url),
                        'content': content
                    }
                    
                    stories.append(story_info)
                    print(f"✅ HN命中: {title} (Score: {story_info['score']})")
                
                print(f"HN智能嗅探完成，共找到 {len(stories)} 个技术相关帖子")
                return stories
                
            except Exception as e:
                print(f"HN抓取失败: {e}")
                return []
    
    async def fetch_story_comments(self, client: httpx.AsyncClient, story_id: int, limit: int = 5) -> List[str]:
        """
        获取帖子的高赞评论
        
        Args:
            client: 异步HTTP客户端
            story_id: 帖子ID
            limit: 评论数量限制
            
        Returns:
            List[str]: 评论内容列表
        """
        try:
            story_url = f"{self.hn_api_base}/item/{story_id}.json"
            story_data = await self._make_request(client, story_url)
            
            if not story_data or 'kids' not in story_data:
                return []
            
            comments = []
            comment_ids = story_data['kids'][:limit]
            
            for comment_id in comment_ids:
                comment_url = f"{self.hn_api_base}/item/{comment_id}.json"
                comment_data = await self._make_request(client, comment_url)
                
                if comment_data and comment_data.get('type') == 'comment':
                    text = comment_data.get('text', '')
                    if text:
                        # 清理HTML标签
                        clean_text = BeautifulSoup(text, 'html.parser').get_text()
                        comments.append(clean_text)
            
            return comments
            
        except Exception as e:
            print(f"获取HN评论失败: {e}")
            return []

# 测试函数
async def main():
    """测试HN抓取器"""
    fetcher = HNFetcher()
    stories = await fetcher.fetch_top_stories(limit=10)
    
    for story in stories[:3]:
        print(f"\n标题: {story['title']}")
        print(f"URL: {story['url']}")
        print(f"作者: {story['author']}")
        print(f"分数: {story['score']}")
        print(f"域名: {story['domain']}")
        print(f"内容预览: {story['content'][:200]}...")

if __name__ == "__main__":
    asyncio.run(main())