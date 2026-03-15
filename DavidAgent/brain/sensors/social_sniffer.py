import os
import praw
import tweepy
import polars as pl
from datetime import datetime
from typing import List, Dict

class SocialSniffer:
 """
 DavidAgent 的社交雷达 (X & Reddit 嗅探器)
 核心职责：捕捉技术圈突发 Bug、框架崩溃报警及大牛的最新吐槽。
 """

 def __init__(self, credentials_path: str, memory_dir: str):
 self.memory_dir = memory_dir
 self.cache_file = os.path.join(self.memory_dir, "social_seen_posts.parquet")
 
 # 1. 凭据加载 (包含 Reddit 和 X 的 API Keys)
 self.creds = self._load_credentials(credentials_path)
 
 # 2. 初始化客户端
 self.reddit = self._init_reddit()
 self.x_client = self._init_x()

 # 3. 初始化高速缓存
 self.seen_posts = self._init_polars_cache()

 def _load_credentials(self, path: str) -> Dict:
 """从凭据中心读取社交媒体 API 密钥"""
 # 实际逻辑应调用你的 credential_manager.py
 # 这里模拟读取逻辑
 creds = {}
 if os.path.exists(path):
 with open(path, 'r') as f:
 for line in f:
 if "=" in line:
 k, v = line.strip().split("=")
 creds[k] = v
 return creds

 def _init_reddit(self):
 try:
 return praw.Reddit(
 client_id=self.creds.get("REDDIT_CLIENT_ID"),
 client_secret=self.creds.get("REDDIT_CLIENT_SECRET"),
 user_agent="DavidAgent:v2.1 (by /u/davidturing)"
 )
 except: return None

 def _init_x(self):
 try:
 return tweepy.Client(bearer_token=self.creds.get("X_BEARER_TOKEN"))
 except: return None

 def _init_polars_cache(self) -> pl.DataFrame:
 if os.path.exists(self.cache_file):
 return pl.read_parquet(self.cache_file)
 return pl.DataFrame(schema={"post_id": pl.Utf8, "platform": pl.Utf8, "scanned_at": pl.Utf8})

 def sniff_reddit(self, subreddits: List[str] = ["programming", "rust", "dataengineering"], limit: int = 10):
 """在 Reddit 挖掘高热度技术帖"""
 if not self.reddit: return []
 
 discoveries = []
 for sub_name in subreddits:
 print(f"探针已进入 r/{sub_name}...")
 subreddit = self.reddit.subreddit(sub_name)
 # 获取最近的热帖
 for submission in subreddit.hot(limit=limit):
 if submission.id not in self.seen_posts["post_id"].to_list():
 # 只有包含特定负面/警示词的才会被视为“瓜”
 is_urgent = any(word in submission.title.lower() for word in ["bug", "issue", "broken", "critical", "outage", "warning"])
 
 discoveries.append({
 "post_id": submission.id,
 "platform": "reddit",
 "title": submission.title,
 "url": submission.url,
 "score": submission.score,
 "is_urgent": is_urgent,
 "content": submission.selftext[:500]
 })
 return discoveries

 def sniff_x(self, queries: List[str] = ["Polars bug", "LangGraph issue", "DuckDB crash"], limit: int = 5):
 """在 X 上追踪技术关键词"""
 if not self.x_client: return []
 
 discoveries = []
 for q in queries:
 print(f"正在 X 检索关键词: {q}...")
 # 搜索最近推文 (仅演示逻辑，需 API 权限)
 tweets = self.x_client.search_recent_tweets(query=q, max_results=limit)
 if tweets.data:
 for tweet in tweets.data:
 if str(tweet.id) not in self.seen_posts["post_id"].to_list():
 discoveries.append({
 "post_id": str(tweet.id),
 "platform": "x",
 "title": tweet.text[:100],
 "url": f"https://x.com/user/status/{tweet.id}",
 "score": 0, # X API V2 基础版获取点赞数较复杂，暂设 0
 "is_urgent": True,
 "content": tweet.text
 })
 return discoveries

 def mark_as_seen(self, post_id: str, platform: str):
 """持久化缓存"""
 new_row = pl.DataFrame({
 "post_id": [post_id],
 "platform": [platform],
 "scanned_at": [datetime.now().isoformat()]
 })
 self.seen_posts = pl.concat([self.seen_posts, new_row])
 self.seen_posts.write_parquet(self.cache_file)

# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":
 sniffer = SocialSniffer(
 credentials_path="../../.credentials/api_keys.env",
 memory_dir="../../hippocampus/episodic/"
 )
 
 print("🕵️‍♂️ DavidAgent 正在潜入社交媒体...")
 reddit_news = sniffer.sniff_reddit()
 
 for news in reddit_news:
 prefix = "🚨 [紧急]" if news['is_urgent'] else "ℹ️ [趋势]"
 print(f"{prefix} 来自 {news['platform']}: {news['title']}")
 sniffer.mark_as_seen(news['post_id'], news['platform'])