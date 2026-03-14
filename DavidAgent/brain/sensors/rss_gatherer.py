"""
RSS/ArXiv 理论采集器 - 学术论文和技术博客聚合
"""

import feedparser
import logging
from typing import List, Dict, Any
from datetime import datetime
import asyncio
import aiohttp


class RSSGatherer:
    """RSS/ArXiv 理论采集器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 RSS 采集器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger("RSSGatherer")
        self.config = config
        self.feeds = config.get("rss_feeds", [])
        
    async def fetch_feed_async(self, session: aiohttp.ClientSession, feed_url: str) -> List[Dict[str, Any]]:
        """异步获取单个 RSS 源
        
        Args:
            session: aiohttp 会话
            feed_url: RSS 源 URL
            
        Returns:
            文章列表
        """
        try:
            async with session.get(feed_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:3]:  # 限制每源最多3篇文章
                        article = {
                            "title": entry.get("title", ""),
                            "summary": entry.get("summary", entry.get("description", "")),
                            "link": entry.get("link", ""),
                            "published": entry.get("published", entry.get("updated", "")),
                            "source": self._identify_source(feed_url)
                        }
                        articles.append(article)
                        
                    return articles
                else:
                    self.logger.warning(f"RSS 源 {feed_url} 返回状态码: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"获取 RSS 源失败 {feed_url}: {e}")
            return []
            
    def _identify_source(self, feed_url: str) -> str:
        """识别 RSS 源类型
        
        Args:
            feed_url: RSS 源 URL
            
        Returns:
            源类型标识
        """
        if "arxiv.org" in feed_url:
            return "arxiv"
        elif "hnrss.org" in feed_url:
            return "hackernews"
        elif "openai.com" in feed_url:
            return "openai_blog"
        elif "netflixtechblog.com" in feed_url:
            return "netflix_tech"
        else:
            return "unknown"
            
    async def gather_all_feeds(self) -> List[Dict[str, Any]]:
        """并发获取所有 RSS 源
        
        Returns:
            所有文章列表
        """
        self.logger.info(f"开始获取 {len(self.feeds)} 个 RSS 源...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_feed_async(session, feed) for feed in self.feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # 合并结果
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                self.logger.error(f"RSS 获取异常: {result}")
                
        self.logger.info(f"RSS 采集完成，获得 {len(all_articles)} 篇文章")
        return all_articles
        
    def extract_insights(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从文章中提取洞察
        
        Args:
            articles: 文章列表
            
        Returns:
            提取的洞察列表
        """
        insights = []
        
        for article in articles:
            # 跳过空内容
            if not article.get("title") and not article.get("summary"):
                continue
                
            insight = {
                "source": "rss",
                "title": f"{article['source'].upper()}: {article['title']}",
                "content": article["summary"],
                "metadata": {
                    "original_source": article["source"],
                    "url": article["link"],
                    "published": article["published"]
                },
                "timestamp": datetime.now().isoformat()
            }
            insights.append(insight)
            
        return insights
        
    async def run_discovery(self) -> List[Dict[str, Any]]:
        """运行完整的 RSS 采集流程
        
        Returns:
            提取的洞察列表
        """
        try:
            # 获取所有文章
            articles = await self.gather_all_feeds()
            
            if not articles:
                self.logger.info("未获取到任何 RSS 文章")
                return []
                
            # 提取洞察
            insights = self.extract_insights(articles)
            
            # 限制数量
            max_fetch = self.config.get("max_fetch_per_cycle", 5)
            insights = insights[:max_fetch]
            
            self.logger.info(f"RSS 采集完成，获得 {len(insights)} 项洞察")
            return insights
            
        except Exception as e:
            self.logger.error(f"RSS 采集失败: {e}")
            return []