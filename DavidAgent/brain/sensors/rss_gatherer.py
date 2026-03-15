import os
import feedparser
import polars as pl
from datetime import datetime
from typing import List, Dict

class RSSGatherer:
    """
    DavidAgent 的理论基石采集器 (RSS & ArXiv 探测器)
    核心职责：抓取前沿论文与顶级技术博客，提取摘要，供给右脑进行元认知升级。
    """
    
    def __init__(self, memory_dir: str):
        self.memory_dir = memory_dir
        self.cache_file = os.path.join(self.memory_dir, "rss_seen_articles.parquet")
        
        # 默认的高质量资讯源
        self.feeds = {
            "ArXiv_AI": "http://export.arxiv.org/rss/cs.AI",
            "ArXiv_CL": "http://export.arxiv.org/rss/cs.CL",
            "HackerNews": "https://hnrss.org/frontpage?points=100",
            "OpenAI_Blog": "https://openai.com/blog/rss.xml"
        }
        
        # 初始化 Polars 高速缓存
        self.seen_articles = self._init_polars_cache()

    def _init_polars_cache(self) -> pl.DataFrame:
        """加载已阅读的文章记录，防止重复总结"""
        if os.path.exists(self.cache_file):
            return pl.read_parquet(self.cache_file)
        schema = {"article_id": pl.Utf8, "title": pl.Utf8, "source": pl.Utf8, "scanned_at": pl.Utf8}
        return pl.DataFrame(schema=schema)

    def fetch_new_articles(self, max_per_feed: int = 5) -> List[Dict]:
        """遍历所有 RSS 源，抓取最新文章"""
        new_discoveries = []
        seen_ids = self.seen_articles["article_id"].to_list() if not self.seen_articles.is_empty() else []

        for source_name, feed_url in self.feeds.items():
            print(f"📡 正在解析资讯源: {source_name}...")
            try:
                parsed_feed = feedparser.parse(feed_url)
            except Exception as e:
                print(f"❌ 无法解析 {source_name}: {e}")
                continue
                
            for entry in parsed_feed.entries[:max_per_feed]:
                article_id = entry.get("id", entry.get("link", ""))
                
                if article_id not in seen_ids:
                    summary = entry.get("summary", "")
                    clean_summary = summary.replace("<p>", "").replace("</p>", "").strip()
                    
                    new_discoveries.append({
                        "article_id": article_id,
                        "title": entry.get("title", ""),
                        "source": source_name,
                        "link": entry.get("link", ""),
                        "published": entry.get("published", datetime.now().isoformat()),
                        "summary": clean_summary[:1000]
                    })
        
        return new_discoveries

    def mark_as_seen(self, article_id: str, title: str, source: str):
        """将已处理的文章写入 Polars 缓存并固化到磁盘"""
        new_row = pl.DataFrame({
            "article_id": [article_id],
            "title": [title],
            "source": [source],
            "scanned_at": [datetime.now().isoformat()]
        })
        self.seen_articles = pl.concat([self.seen_articles, new_row])
        self.seen_articles.write_parquet(self.cache_file)
        print(f"💾 已将文献《{title[:20]}...》标记为已读。")

# 独立测试入口
if __name__ == "__main__":
    gatherer = RSSGatherer(memory_dir="../../hippocampus/episodic/")
    
    print("🚀 启动 RSS 理论采集引擎...")
    raw_articles = gatherer.fetch_new_articles(max_per_feed=3)
    
    if not raw_articles:
         print("✅ 当前所有订阅源均无更新，或已被完全消化。")
         
    for article in raw_articles:
        print(f"🎯 捕获新知: [{article['source']}] {article['title']}")
        print(f"   摘要预览: {article['summary'][:100]}...\n")
        
        gatherer.mark_as_seen(article['article_id'], article['title'], article['source'])