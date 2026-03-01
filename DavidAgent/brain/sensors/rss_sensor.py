"""
感知器官 (Sensors) - RSS 订阅爬虫
支持批量抓取新闻/博客 RSS feeds 并推送到黑板
"""
import json
import asyncio
import urllib.request
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

class RSSSensor:
    """RSS 订阅流态感知插件"""
    
    def __init__(self, blackboard=None):
        from brain.config import BrainConfig
        self.config = BrainConfig()
        self.blackboard = blackboard
        
    async def fetch_feed(self, feed_url: str) -> List[Dict]:
        """通过基础 urllib 抓取并解析 RSS XML 树"""
        print(f"📡 [感知器-RSS] 正在订阅解析 {feed_url}...")
        headers = {'User-Agent': 'DavidAgent-Sensor/1.0'}
        
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            items = []
            
            # 简单处理常见的 RSS 2.0 / Atom 标签结构
            for item in root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                title = item.find('title')
                title_txt = title.text if title is not None else ""
                
                desc = item.find('description') or item.find('{http://www.w3.org/2005/Atom}content') or item.find('{http://www.w3.org/2005/Atom}summary')
                desc_txt = desc.text if desc is not None else ""
                
                link = item.find('link')
                link_txt = link.text if link is not None else (link.get('href') if link is not None else "")
                
                pub_date = item.find('pubDate') or item.find('{http://www.w3.org/2005/Atom}published')
                pub_date_txt = pub_date.text if pub_date is not None else datetime.now().isoformat()
                
                if title_txt or desc_txt:
                    items.append({
                        'title': title_txt,
                        'description': desc_txt,
                        'link': link_txt,
                        'pubDate': pub_date_txt,
                        'source_feed': feed_url
                    })
                    
            print(f"✅ [感知器-RSS] 成功从 {feed_url} 抓取 {len(items)} 条内容区块")
            return items
            
        except Exception as e:
            print(f"❌ [感知器-RSS] 解析异常 ({feed_url}): {e}")
            return []

    async def ingest_to_blackboard(self, feed_url: str):
        """抓取流并按项推送到黑板持久化"""
        articles = await self.fetch_feed(feed_url)
        if not articles or not self.blackboard:
            return
            
        from brain.memory.episodic_memory import get_episodic_memory_db
        db = get_episodic_memory_db()
        
        for article in articles:
            text_content = f"{article.get('title', '')}\n\n{article.get('description', '')}"
            
            # 如果内容过短则抛弃
            if len(text_content.strip()) < 50:
                continue
                
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            
            # 检查去重
            if db.check_duplicate(content_hash):
                continue
                
            signal_id = f"rss_{content_hash[:10]}"
            
            # 构造统一信号格式
            signal_data = {
                'signal_id': signal_id,
                'content_hash': content_hash,
                'handle': feed_url,
                'author_name': 'RSS Feed',
                'timestamp': article.get('pubDate', datetime.now().isoformat()),
                'likes': 0,
                'retweets': 0,
                'raw_text': text_content,
                'raw_json': json.dumps(article, ensure_ascii=False),
                'signal_type': 'rss_article'
            }
            
            # 保存原始信号
            db.save_raw_signal(signal_data)
            
            # 推送黑板触发分析
            self.blackboard.update('topic_id', signal_id, 'SENSOR_RSS')
            self.blackboard.update('raw_source', signal_data['raw_text'], 'SENSOR_RSS')
            self.blackboard.update('workflow_status', 'START', 'SYSTEM')
            
            print(f"📡 [感知器-RSS] 注入新闻信号: {signal_id} ({article.get('title')[:20]}...)")
            await asyncio.sleep(1) # 节流缓冲
