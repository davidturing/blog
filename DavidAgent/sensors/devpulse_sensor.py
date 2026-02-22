"""
开发者脉搏感知器 (DevPulse Sensor)
用于聚合顶级技术资讯，特别是AI辅助编程和LLM架构方向的最新动态
"""
import os
import json
import asyncio
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urlparse

import httpx
import feedparser
from bs4 import BeautifulSoup

class DevPulseSensor:
    """开发者脉搏感知器 - 专门用于捕捉AI编程和LLM工具链的最新动态"""
    
    def __init__(self, blackboard=None, db_path="devpulse_cache.db"):
        from brain.config import BrainConfig
        self.config = BrainConfig()
        self.blackboard = blackboard
        self.db_path = db_path
        self._init_cache_db()
        
        # 技术关键词过滤器
        self.tech_keywords = [
            "AI", "LLM", "Agent", "Cursor", "Copilot", "Code", "Python", "React",
            "LangChain", "Devin", "GitHub", "OpenAI", "Anthropic", "HuggingFace",
            "大模型", "人工智能", "机器学习", "深度学习", "神经网络", "编码", "编程"
        ]
        
        # Hacker News API配置
        self.hn_api_base = "https://hacker-news.firebaseio.com/v0"
        
        # RSS订阅源列表
        self.rss_feeds = [
            "https://huggingface.co/blog/feed.xml",
            "https://openai.com/blog/rss/",
            "https://blog.anthropic.com/rss/",
            # 可以添加更多顶级开发者博客
        ]
        
        # HTTP客户端配置
        self.headers = {
            "User-Agent": "DavidAgent-DevPulseSensor/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    
    def _init_cache_db(self):
        """初始化缓存数据库用于去重"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_items (
                source_id TEXT PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _is_already_processed(self, source_id: str) -> bool:
        """检查是否已经处理过该source_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_items WHERE source_id = ?", (source_id,))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def _mark_as_processed(self, source_id: str):
        """标记为已处理"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO processed_items (source_id) VALUES (?)", (source_id,))
        conn.commit()
        conn.close()
    
    async def _fetch_with_retry(self, client: httpx.AsyncClient, url: str, max_retries=3) -> Optional[str]:
        """带重试机制的HTTP请求"""
        for attempt in range(max_retries):
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ [DevPulse] 获取 {url} 失败，已重试{max_retries}次: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    async def _extract_article_content(self, client: httpx.AsyncClient, url: str) -> str:
        """从网页URL提取正文内容"""
        try:
            html_content = await self._fetch_with_retry(client, url)
            if not html_content:
                return ""
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 尝试找到主要内容区域
            main_content = None
            for selector in ['article', 'main', '.post-content', '.entry-content', '.content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.body
            
            if not main_content:
                return ""
            
            # 提取文本并清理
            text = main_content.get_text(separator=' ', strip=True)
            
            # 清理多余空白
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            return cleaned_text[:5000]  # 限制长度避免过长
            
        except Exception as e:
            print(f"❌ [DevPulse] 提取文章内容失败 ({url}): {e}")
            return ""
    
    def _contains_tech_keywords(self, text: str) -> bool:
        """检查文本是否包含技术关键词"""
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in self.tech_keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    async def fetch_hacker_news_tech_posts(self, limit: int = 10) -> List[Dict]:
        """
        获取Hacker News中的技术相关帖子
        
        Args:
            limit: 返回的帖子数量限制
            
        Returns:
            符合统一数据契约的Payload列表
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 获取热门帖子ID
                top_stories_url = f"{self.hn_api_base}/topstories.json"
                top_stories_response = await self._fetch_with_retry(client, top_stories_url)
                if not top_stories_response:
                    return []
                
                top_stories = json.loads(top_stories_response)[:limit * 3]  # 获取更多候选
                
                # 并发获取帖子详情
                item_tasks = []
                for item_id in top_stories:
                    item_url = f"{self.hn_api_base}/item/{item_id}.json"
                    task = self._fetch_with_retry(client, item_url)
                    item_tasks.append(task)
                
                item_responses = await asyncio.gather(*item_tasks, return_exceptions=True)
                
                # 过滤技术相关帖子
                tech_posts = []
                for i, response in enumerate(item_responses):
                    if isinstance(response, Exception) or not response:
                        continue
                    
                    try:
                        item_data = json.loads(response)
                        title = item_data.get('title', '')
                        url = item_data.get('url', '')
                        
                        # 检查是否包含技术关键词
                        if self._contains_tech_keywords(title) and url:
                            # 检查是否已处理
                            source_id = f"hn_{item_data['id']}"
                            if self._is_already_processed(source_id):
                                continue
                            
                            # 提取文章内容
                            content = await self._extract_article_content(client, url)
                            
                            # 构建core_text
                            core_text = f"【标题】: {title}\n"
                            if content:
                                core_text += f"【正文提取】: {content}"
                            else:
                                core_text += "【正文提取】: 无法提取正文内容"
                            
                            payload = {
                                "source_type": "tech_news",
                                "source_id": source_id,
                                "author": item_data.get('by', 'unknown'),
                                "timestamp": datetime.fromtimestamp(item_data.get('time', 0), tz=timezone.utc).isoformat(),
                                "core_text": core_text.strip(),
                                "original_url": url
                            }
                            tech_posts.append(payload)
                            
                            # 标记为已处理
                            self._mark_as_processed(source_id)
                            
                            if len(tech_posts) >= limit:
                                break
                                
                    except Exception as e:
                        print(f"❌ [DevPulse] 处理HN帖子失败: {e}")
                        continue
                
                print(f"✅ [DevPulse] 成功获取 {len(tech_posts)} 个Hacker News技术帖子")
                return tech_posts
                
            except Exception as e:
                print(f"❌ [DevPulse] 获取Hacker News失败: {e}")
                return []
    
    async def fetch_rss_tech_articles(self, limit_per_feed: int = 3) -> List[Dict]:
        """
        获取RSS订阅源中的技术文章
        
        Args:
            limit_per_feed: 每个订阅源返回的文章数量限制
            
        Returns:
            符合统一数据契约的Payload列表
        """
        all_articles = []
        
        for feed_url in self.rss_feeds:
            try:
                # 解析RSS
                feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    continue
                
                # 处理每个文章
                articles_from_feed = []
                for entry in feed.entries[:limit_per_feed]:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    
                    # 检查是否包含技术关键词
                    if not self._contains_tech_keywords(title) and not self._contains_tech_keywords(entry.get('summary', '')):
                        continue
                    
                    # 生成source_id（使用URL哈希）
                    url_hash = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
                    source_id = f"rss_{url_hash}"
                    
                    # 检查是否已处理
                    if self._is_already_processed(source_id):
                        continue
                    
                    # 获取文章内容
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    # 如果RSS内容不够详细，尝试抓取原文
                    if len(content) < 500 and link:
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            content = await self._extract_article_content(client, link)
                    
                    # 构建core_text
                    core_text = f"【标题】: {title}\n"
                    if content:
                        core_text += f"【正文提取】: {content}"
                    else:
                        core_text += "【正文提取】: 无法提取正文内容"
                    
                    # 获取作者信息
                    author = "unknown"
                    if hasattr(entry, 'author'):
                        author = entry.author
                    elif hasattr(feed, 'author'):
                        author = feed.author
                    
                    # 获取发布时间
                    timestamp = datetime.now(timezone.utc).isoformat()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        timestamp = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                    
                    payload = {
                        "source_type": "tech_news",
                        "source_id": source_id,
                        "author": author,
                        "timestamp": timestamp,
                        "core_text": core_text.strip(),
                        "original_url": link
                    }
                    articles_from_feed.append(payload)
                    
                    # 标记为已处理
                    self._mark_as_processed(source_id)
                
                all_articles.extend(articles_from_feed)
                print(f"✅ [DevPulse] 从 {feed_url} 获取 {len(articles_from_feed)} 篇技术文章")
                
            except Exception as e:
                print(f"❌ [DevPulse] 处理RSS源 {feed_url} 失败: {e}")
                continue
        
        return all_articles
    
    async def ingest_to_blackboard(self, hn_limit: int = 5, rss_limit_per_feed: int = 2):
        """抓取技术资讯并推送到黑板持久化"""
        print("📡 [DevPulse-Sensor] 开始抓取开发者脉搏...")
        
        # 并发抓取HN和RSS
        hn_posts = await self.fetch_hacker_news_tech_posts(limit=hn_limit)
        rss_articles = await self.fetch_rss_tech_articles(limit_per_feed=rss_limit_per_feed)
        
        all_payloads = hn_posts + rss_articles
        
        if not all_payloads or not self.blackboard:
            print("⏭️ [DevPulse-Sensor] 未发现新的技术资讯或黑板不可用")
            return
        
        from brain.memory.episodic_memory import get_episodic_memory_db
        db = get_episodic_memory_db()
        
        for payload in all_payloads:
            text_content = payload['core_text']
            if not text_content:
                print(f"⏭️ 跳过无内容资讯: {payload['original_url']}")
                continue
            
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            
            # 检查全局去重
            if db.check_duplicate(content_hash):
                print(f"⏭️ 跳过重复内容体系 (Hash: {content_hash[:8]})")
                continue
            
            signal_id = f"devpulse_{payload['source_id']}_{content_hash[:4]}"
            
            # 构造统一信号格式
            signal_data = {
                'signal_id': signal_id,
                'content_hash': content_hash,
                'handle': payload['original_url'],
                'author_name': payload['author'],
                'timestamp': payload['timestamp'],
                'likes': 0,
                'retweets': 0,
                'raw_text': text_content,
                'raw_json': json.dumps(payload, ensure_ascii=False),
                'signal_type': 'tech_news'
            }
            
            # 保存原始信号
            db.save_raw_signal(signal_data)
            
            # 推送黑板触发分析
            self.blackboard.update('topic_id', signal_id, 'SENSOR_DEVPULSE')
            self.blackboard.update('raw_source', signal_data['raw_text'], 'SENSOR_DEVPULSE')
            self.blackboard.update('workflow_status', 'START', 'SYSTEM')
            
            print(f"📡 [DevPulse-Sensor] 已注入技术资讯信号点: {signal_id}")
        
        print(f"✅ [DevPulse-Sensor] 完成抓取，共处理 {len(all_payloads)} 条技术资讯")

# 使用示例
async def main():
    """测试函数"""
    sensor = DevPulseSensor()
    await sensor.ingest_to_blackboard(hn_limit=3, rss_limit_per_feed=1)

if __name__ == "__main__":
    asyncio.run(main())