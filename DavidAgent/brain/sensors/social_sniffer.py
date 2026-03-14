"""
X/Twitter 趋势嗅探器 - 社交媒体热点发现
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime


class SocialSniffer:
    """X/Twitter 趋势嗅探器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化社交嗅探器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger("SocialSniffer")
        self.config = config
        self.keywords = config.get("social_keywords", [])
        self.x_bearer_token = self._load_x_token()
        
    def _load_x_token(self) -> Optional[str]:
        """从凭据文件加载 X API Bearer Token"""
        try:
            credentials_path = ".credentials/api_keys.env"
            if os.path.exists(credentials_path):
                with open(credentials_path, "r") as f:
                    for line in f:
                        if line.strip().startswith("X_API_BEARER_TOKEN="):
                            return line.strip().split("=", 1)[1].strip('"\'')
        except Exception as e:
            self.logger.warning(f"无法加载 X API token: {e}")
        return None
        
    def search_trending_posts(self) -> List[Dict[str, Any]]:
        """搜索趋势帖子（模拟实现）
        
        Returns:
            帖子列表
        """
        self.logger.info("开始搜索社交媒体趋势...")
        
        # 模拟搜索结果（实际实现会调用 X API）
        # 在生产环境中，这里会使用 Twitter/X API v2
        trending_posts = [
            {
                "id": "1234567890",
                "text": "Just released Polars 1.0! Blazingly fast DataFrame operations with 10x performance improvement over pandas. #Polars #DataScience",
                "author": "@polars_dev",
                "created_at": "2026-03-15T06:30:00Z",
                "metrics": {"likes": 1250, "retweets": 320, "replies": 89}
            },
            {
                "id": "1234567891", 
                "text": "AutoGen framework now supports MCP protocol for standardized tool calling across AI platforms. Game changer for multi-agent systems! #AutoGen #AI #MCP",
                "author": "@microsoft_ai",
                "created_at": "2026-03-15T05:45:00Z",
                "metrics": {"likes": 2100, "retweets": 560, "replies": 145}
            },
            {
                "id": "1234567892",
                "text": "Gemini 3 Pro Image (Nano Banana Pro) just dropped! Incredible image generation quality with 4K output and advanced prompt understanding. #Gemini #AI #ImageGeneration",
                "author": "@google_ai",
                "created_at": "2026-03-15T04:20:00Z", 
                "metrics": {"likes": 3500, "retweets": 890, "replies": 230}
            }
        ]
        
        # 过滤包含关键词的帖子
        filtered_posts = []
        keywords_lower = [kw.lower() for kw in self.keywords]
        
        for post in trending_posts:
            post_text_lower = post["text"].lower()
            if any(keyword in post_text_lower for keyword in keywords_lower):
                filtered_posts.append(post)
                
        max_fetch = self.config.get("max_fetch_per_cycle", 5)
        return filtered_posts[:max_fetch]
        
    def extract_insights(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从帖子中提取洞察
        
        Args:
            posts: 帖子列表
            
        Returns:
            提取的洞察列表
        """
        insights = []
        
        for post in posts:
            insight = {
                "source": "social",
                "title": f"Social Trend: {post['author']}",
                "content": post["text"],
                "metadata": {
                    "platform": "twitter",
                    "author": post["author"],
                    "post_id": post["id"],
                    "engagement": post["metrics"],
                    "url": f"https://twitter.com/{post['author'].replace('@', '')}/status/{post['id']}"
                },
                "timestamp": datetime.now().isoformat()
            }
            insights.append(insight)
            
        return insights
        
    def run_discovery(self) -> List[Dict[str, Any]]:
        """运行完整的社交趋势发现流程
        
        Returns:
            提取的洞察列表
        """
        try:
            # 搜索趋势帖子
            posts = self.search_trending_posts()
            
            if not posts:
                self.logger.info("未发现相关社交趋势")
                return []
                
            # 提取洞察
            insights = self.extract_insights(posts)
            
            self.logger.info(f"社交嗅探完成，获得 {len(insights)} 项洞察")
            return insights
            
        except Exception as e:
            self.logger.error(f"社交嗅探失败: {e}")
            return []