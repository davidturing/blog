#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS Reader - DevPulse-Sensor的RSS订阅源模块

功能：
- 解析标准RSS/Atom订阅源
- 定时拉取指定科技博客
- 获取最新文章正文并提取核心内容
- 支持去重和防抖机制

作者：G老师架构指导 + OpenClaw AI助手
"""

import asyncio
import feedparser
import hashlib
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


class RSSReader:
    """RSS订阅源读取器"""
    
    def __init__(self, db_path: str = "devpulse_cache.db"):
        """
        初始化RSS读取器
        
        Args:
            db_path: 缓存数据库路径，用于去重
        """
        self.db_path = db_path
        self._init_cache_db()
        
        # 预设的高质量技术博客RSS源
        self.default_feeds = [
            # HuggingFace官方博客
            "https://huggingface.co/blog/feed.xml",
            # OpenAI官方博客
            "https://openai.com/blog/rss/",
            # Anthropic官方博客  
            "https://www.anthropic.com/news/rss.xml",
            # Google AI博客
            "https://ai.googleblog.com/feeds/posts/default?alt=rss",
            # GitHub Blog
            "https://github.blog/feed/",
            # Hacker News (虽然主要用HN API，但也可以作为RSS源)
            "https://news.ycombinator.com/rss",
            # 知名开发者博客（示例）
            "https://karpathy.ai/rss.xml",  # Andrej Karpathy
            "https://www.oreilly.com/radar/feed/index.xml",  # O'Reilly Radar
        ]
        
        self.headers = {
            "User-Agent": "DavidAgent-DevPulseSensor/1.0 (+https://github.com/davidturing/tech)"
        }
    
    def _init_cache_db(self):
        """初始化缓存数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_cache (
                source_id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                author TEXT,
                published_at TEXT,
                content_hash TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _is_duplicate(self, source_id: str, content_hash: str) -> bool:
        """检查是否为重复内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM rss_cache WHERE source_id = ? OR content_hash = ?",
            (source_id, content_hash)
        )
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def _save_to_cache(self, source_id: str, title: str, url: str, 
                      author: str, published_at: str, content_hash: str):
        """保存到缓存数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO rss_cache 
            (source_id, title, url, author, published_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source_id, title, url, author, published_at, content_hash))
        conn.commit()
        conn.close()
    
    def _clean_html_content(self, html_content: str) -> str:
        """清理HTML内容，提取纯文本"""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取文本
            text = soup.get_text()
            
            # 清理多余空白
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 限制长度
            return text[:3000]
            
        except Exception as e:
            print(f"HTML清理失败: {e}")
            return html_content[:3000] if html_content else ""
    
    async def _fetch_article_content(self, client: httpx.AsyncClient, url: str) -> str:
        """异步获取文章正文内容"""
        try:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            
            # 尝试使用newspaper3k风格的内容提取
            content = self._clean_html_content(response.text)
            return content
            
        except Exception as e:
            print(f"获取文章内容失败 ({url}): {e}")
            return ""
    
    async def fetch_feed(self, feed_url: str, 
                        keywords: List[str] = None,
                        limit: int = 5) -> List[Dict]:
        """
        获取单个RSS源的最新文章
        
        Args:
            feed_url: RSS源URL
            keywords: 关键词过滤列表
            limit: 返回文章数量限制
            
        Returns:
            符合统一数据契约的Payload列表
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 获取RSS源
                response = await client.get(feed_url, headers=self.headers)
                response.raise_for_status()
                
                # 解析RSS
                feed = feedparser.parse(response.text)
                
                if not feed.entries:
                    print(f"RSS源无条目: {feed_url}")
                    return []
                
                payloads = []
                entries_processed = 0
                
                for entry in feed.entries[:limit * 2]:  # 多获取一些用于关键词过滤
                    if entries_processed >= limit:
                        break
                    
                    # 提取基本信息
                    title = getattr(entry, 'title', '')
                    link = getattr(entry, 'link', '')
                    author = getattr(entry, 'author', 'Unknown')
                    published = getattr(entry, 'published', '')
                    
                    # 时间处理
                    try:
                        if published:
                            # 尝试多种时间格式
                            pub_time = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
                        else:
                            pub_time = datetime.now(timezone.utc)
                    except:
                        pub_time = datetime.now(timezone.utc)
                    
                    # 关键词过滤
                    if keywords:
                        content_for_filter = f"{title} {getattr(entry, 'summary', '')}".lower()
                        if not any(keyword.lower() in content_for_filter for keyword in keywords):
                            continue
                    
                    # 生成唯一ID
                    source_id = f"rss_{hashlib.md5(link.encode()).hexdigest()[:16]}"
                    
                    # 获取文章正文
                    content = await self._fetch_article_content(client, link)
                    
                    if not content:
                        # 如果无法获取正文，使用摘要
                        content = getattr(entry, 'summary', '')
                    
                    # 内容哈希用于去重
                    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    
                    # 检查重复
                    if self._is_duplicate(source_id, content_hash):
                        print(f"跳过重复RSS文章: {title}")
                        continue
                    
                    # 构建core_text
                    core_text = f"【标题】: {title}\n【正文提取】: {content}"
                    
                    payload = {
                        "source_type": "tech_news",
                        "source_id": source_id,
                        "author": author,
                        "timestamp": pub_time.isoformat(),
                        "core_text": core_text.strip(),
                        "original_url": link
                    }
                    
                    payloads.append(payload)
                    entries_processed += 1
                    
                    # 保存到缓存
                    self._save_to_cache(source_id, title, link, author, 
                                      pub_time.isoformat(), content_hash)
                
                print(f"RSS源 {feed_url} 获取到 {len(payloads)} 篇新文章")
                return payloads
                
            except Exception as e:
                print(f"RSS源抓取失败 ({feed_url}): {e}")
                return []
    
    async def fetch_all_feeds(self, 
                             custom_feeds: List[str] = None,
                             keywords: List[str] = None,
                             limit_per_feed: int = 3) -> List[Dict]:
        """
        获取所有RSS源的最新文章
        
        Args:
            custom_feeds: 自定义RSS源列表
            keywords: 关键词过滤列表
            limit_per_feed: 每个源返回文章数量限制
            
        Returns:
            符合统一数据契约的Payload列表
        """
        feeds = custom_feeds or self.default_feeds
        all_payloads = []
        
        # 并发获取所有RSS源
        tasks = []
        for feed_url in feeds:
            task = self.fetch_feed(feed_url, keywords, limit_per_feed)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                print(f"RSS抓取异常: {result}")
                continue
            all_payloads.extend(result)
        
        return all_payloads


# 使用示例
async def main():
    """测试函数"""
    reader = RSSReader()
    
    # AI相关关键词
    ai_keywords = ["AI", "LLM", "Agent", "Cursor", "Copilot", "Code", "Python", "React"]
    
    print("🚀 测试RSS Reader...")
    payloads = await reader.fetch_all_feeds(keywords=ai_keywords, limit_per_feed=2)
    
    print(f"\n✅ 获取到 {len(payloads)} 篇AI相关技术文章:")
    for i, payload in enumerate(payloads[:3], 1):  # 只显示前3篇
        print(f"\n【文章 {i}】")
        print(f"   标题: {payload['core_text'].split('【标题】: ')[1].split('【正文提取】:')[0]}")
        print(f"   作者: {payload['author']}")
        print(f"   URL: {payload['original_url']}")
        print(f"   预览: {payload['core_text'][:200]}...")


if __name__ == "__main__":
    asyncio.run(main())