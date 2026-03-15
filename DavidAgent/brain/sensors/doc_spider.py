import os
import requests
import polars as pl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Set, List, Dict

class DocSpider:
    """
    DavidAgent 的官方文档本体重构器
    核心职责：递归爬取官方文档，提取结构化知识，构建技术本体。
    """

    def __init__(self, memory_dir: str):
        self.memory_dir = memory_dir
        self.cache_file = os.path.join(self.memory_dir, "doc_visited_urls.parquet")
        
        # 初始化 Polars 访问记录
        self.visited_urls = self._init_polars_cache()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "DavidAgent/v2.1 (Technical Research Bot)"})

    def _init_polars_cache(self) -> pl.DataFrame:
        if os.path.exists(self.cache_file):
            return pl.read_parquet(self.cache_file)
        return pl.DataFrame(schema={"url": pl.Utf8, "title": pl.Utf8, "scanned_at": pl.Utf8})

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """确保不爬出当前文档域名，避开无关链接"""
        parsed = urlparse(url)
        return parsed.netloc == base_domain and not parsed.fragment

    def crawl(self, start_url: str, max_depth: int = 2):
        """
        开始递归爬取
        :param start_url: 文档入口地址 (如 https://docs.polars.rs/python/user-guide/)
        :param max_depth: 爬取深度，防止在大型文档中迷路
        """
        base_domain = urlparse(start_url).netloc
        queue = [(start_url, 0)]
        results = []

        while queue:
            url, depth = queue.pop(0)
            
            # 1. 检查是否已访问或超过深度
            if depth > max_depth or url in self.visited_urls["url"].to_list():
                continue

            print(f"🕸️ 正在深度 {depth} 爬取: {url}")
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code != 200: continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 2. 提取核心内容 (针对技术文档优化)
                title = soup.title.string if soup.title else "Untitled"
                # 尝试抓取文档主体内容 (通常在 <article> 或 <main> 标签中)
                main_content = soup.find(['article', 'main', 'div.content'])
                text_content = main_content.get_text(separator='\n') if main_content else ""

                results.append({
                    "url": url,
                    "title": title,
                    "depth": depth,
                    "content_preview": text_content[:1000] # 截取部分喂给左脑
                })

                # 3. 记录已访问
                self._mark_as_visited(url, title)

                # 4. 提取页面内的链接，加入队列
                for link in soup.find_all('a', href=True):
                    full_link = urljoin(url, link['href'])
                    if self.is_valid_url(full_link, base_domain):
                        queue.append((full_link, depth + 1))

            except Exception as e:
                print(f"❌ 爬取 {url} 失败: {e}")

        return results

    def _mark_as_visited(self, url: str, title: str):
        new_row = pl.DataFrame({
            "url": [url],
            "title": [title],
            "scanned_at": [datetime.now().isoformat()]
        })
        self.visited_urls = pl.concat([self.visited_urls, new_row])
        self.visited_urls.write_parquet(self.cache_file)

# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":
    spider = DocSpider(memory_dir="../../hippocampus/episodic/")
    
    # 示例：爬取 Polars 官方文档的 API 概览
    target_docs = "https://docs.polars.rs/api/python/stable/reference/index.html"
    
    print(f"🚀 DavidAgent 启动本体重构任务...")
    doc_assets = spider.crawl(target_docs, max_depth=1) # 测试时设为 1 层
    
    print(f"\n✅ 任务完成，共重构 {len(doc_assets)} 个知识节点。")
    for asset in doc_assets:
        print(f"📍 节点: {asset['title']} ({asset['url']})")