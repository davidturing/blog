import os
import json
import requests
import polars as pl
from datetime import datetime, timedelta
from typing import List, Dict, Any

class GitHubWatcher:
    """
    DavidAgent 的外部视觉神经 (GitHub 探测器)
    核心职责：精准检索、极速去重、认知熵过滤、移交双脑
    """
    
    def __init__(self, credentials_path: str, memory_dir: str):
        self.api_url = "https://api.github.com"
        self.memory_dir = memory_dir
        self.cache_file = os.path.join(self.memory_dir, "github_seen_repos.parquet")
        
        # 1. 动态加载凭据 (零信任架构)
        self.token = self._load_github_token(credentials_path)
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # 2. 初始化 Polars 高速缓存 (利用 M4 内存优化)
        self.seen_repos = self._init_polars_cache()

    def _load_github_token(self, path: str) -> str:
        """从凭据中心读取 Token"""
        if not os.path.exists(path):
            print("⚠️ 警告：未发现 GitHub Token，将以受限模式运行 (每小时 60 次请求)")
            return ""
        with open(path, 'r') as f:
            # 假设简单的 K=V 解析，实际按你的 credential_manager 逻辑走
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.strip().split("=")[1]
        return ""

    def _init_polars_cache(self) -> pl.DataFrame:
        """加载已探索过的 Repo，防止认知近亲繁殖和重复计算"""
        if os.path.exists(self.cache_file):
            return pl.read_parquet(self.cache_file)
        # 初始化空的 DataFrame
        schema = {"repo_id": pl.Int64, "full_name": pl.Utf8, "scanned_at": pl.Utf8}
        return pl.DataFrame(schema=schema)

    def search_new_tech(self, topics: List[str], days_back: int = 7) -> List[Dict]:
        """基于关键词和时间窗口进行狩猎"""
        target_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        new_discoveries = []

        for topic in topics:
            query = f"topic:{topic} created:>{target_date} sort:stars-desc"
            print(f"🔍 正在扫描领域: {topic} (Query: {query})")
            
            response = requests.get(
                f"{self.api_url}/search/repositories",
                headers=self.headers,
                params={"q": query, "per_page": 5}  # 严格限制数量，保护 Token 预算
            )
            
            if response.status_code != 200:
                print(f"❌ API 请求失败: {response.status_code}")
                continue
                
            repos = response.json().get("items", [])
            for repo in repos:
                # Polars 极速去重 (O(1) 级别的哈希检查)
                if repo["id"] not in self.seen_repos["repo_id"].to_list():
                    new_discoveries.append({
                        "repo_id": repo["id"],
                        "full_name": repo["full_name"],
                        "description": repo["description"],
                        "stars": repo["stargazers_count"],
                        "url": repo["html_url"]
                    })
        
        return new_discoveries

    def fetch_readme(self, repo_full_name: str) -> str:
        """抽取核心文档，准备喂给左脑"""
        response = requests.get(
            f"{self.api_url}/repos/{repo_full_name}/readme",
            headers=self.headers
        )
        if response.status_code == 200:
            import base64
            content = response.json().get("content", "")
            return base64.b64decode(content).decode('utf-8', errors='ignore')
        return ""

    def mark_as_seen(self, repo_id: int, full_name: str):
        """将处理过的 Repo 压入 Polars 缓存并刷入磁盘"""
        new_row = pl.DataFrame({
            "repo_id": [repo_id],
            "full_name": [full_name],
            "scanned_at": [datetime.now().isoformat()]
        })
        self.seen_repos = pl.concat([self.seen_repos, new_row])
        self.seen_repos.write_parquet(self.cache_file)
        print(f"💾 已将 {full_name} 记入认知黑名单，避免重复学习。")

# ==========================================
# 独立测试与演进触发入口
# ==========================================
if __name__ == "__main__":
    watcher = GitHubWatcher(
        credentials_path="../../.credentials/api_keys.env",
        memory_dir="../../hippocampus/episodic/"
    )
    
    # 注入好奇心引擎分配的课题
    focus_topics = ["polars", "wasm", "multi-agent"]
    
    print("🚀 启动 GitHub 认知缺口探测引擎...")
    raw_repos = watcher.search_new_tech(focus_topics, days_back=3)
    
    for repo in raw_repos:
        print(f"🎯 锁定目标: {repo['full_name']} (🌟 {repo['stars']})")
        readme_text = watcher.fetch_readme(repo['full_name'])
        
        if len(readme_text) > 500:
            # 这里的伪代码展示了如何与双脑联动
            print(f"🧠 移交左脑进行 SOP 蒸馏... (文档长度: {len(readme_text)} 字符)")
            # 假设: new_skill = left_brain.distill(readme_text)
            # 假设: curiosity_engine.sandbox_test(new_skill)
            
            # 无论成功失败，记入缓存，避免明天重复抓取
            watcher.mark_as_seen(repo['repo_id'], repo['full_name'])