import os
import polars as pl
from github import Github
from datetime import datetime, timedelta
from typing import List, Dict

class IssueExplorer:
    """
    DavidAgent 的风险预警与补丁采集器 (GitHub Issues & Discussions 版)
    核心职责：监控核心依赖库的 Bug 报告与修复方案，提取避坑经验，防止认知污染。
    """

    def __init__(self, credentials_path: str, memory_dir: str):
        self.memory_dir = memory_dir
        self.cache_file = os.path.join(self.memory_dir, "github_seen_issues.parquet")
        
        # 1. 动态加载凭据
        self.token = self._load_token(credentials_path)
        self.gh = Github(self.token) if self.token else None
        
        # 2. 初始化 Polars 高速缓存 (针对 M4 内存优化)
        self.seen_issues = self._init_polars_cache()

    def _load_token(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN="):
                        return line.strip().split("=")[1]
        return ""

    def _init_polars_cache(self) -> pl.DataFrame:
        if os.path.exists(self.cache_file):
            return pl.read_parquet(self.cache_file)
        # 记录 Issue ID, 仓库名和最后更新时间
        schema = {"issue_id": pl.Int64, "repo": pl.Utf8, "updated_at": pl.Utf8}
        return pl.DataFrame(schema=schema)

    def explore_issues(self, repo_names: List[str], label_filter: str = "bug") -> List[Dict]:
        """
        探测核心库的 Issues
        :param repo_names: 监控的仓库列表，例如 ["pola-rs/polars"]
        :param label_filter: 关注的标签，通常是 'bug' 或 'critical'
        """
        if not self.gh:
            print("❌ 未发现有效 GITHUB_TOKEN，Issue 探针无法启动。")
            return []
        
        discoveries = []
        # 只看最近 7 天的动态，确保时效性
        since = datetime.now() - timedelta(days=7)

        for repo_name in repo_names:
            print(f"🔍 正在探测仓库 Issues: {repo_name}...")
            try:
                repo = self.gh.get_repo(repo_name)
                # 获取最近更新的、带有特定标签的 Issue
                issues = repo.get_issues(state='all', labels=[label_filter], since=since)
                
                for issue in issues[:10]: # 每次只看最核心的前 10 个
                    if issue.id not in self.seen_issues["issue_id"].to_list():
                        # 提取讨论精髓：Issue 主体 + 前 3 条高价值评论
                        comments = [c.body for c in issue.get_comments()[:3]]
                        
                        discoveries.append({
                            "issue_id": issue.id,
                            "repo": repo_name,
                            "title": issue.title,
                            "state": issue.state, # open 或 closed
                            "url": issue.html_url,
                            "body": issue.body[:1200] if issue.body else "",
                            "discussion_summary": "\n---\n".join(comments)
                        })
            except Exception as e:
                print(f"❌ 探测 {repo_name} 失败: {e}")

        return discoveries

    def mark_as_seen(self, issue_id: int, repo: str):
        """记录已处理的 Issue，避免重复干扰"""
        new_row = pl.DataFrame({
            "issue_id": [issue_id],
            "repo": [repo],
            "updated_at": [datetime.now().isoformat()]
        })
        self.seen_issues = pl.concat([self.seen_issues, new_row])
        self.seen_issues.write_parquet(self.cache_file)

# ==========================================
# 独立测试入口
# ==========================================
if __name__ == "__main__":
    explorer = IssueExplorer(
        credentials_path="../../.credentials/api_keys.env",
        memory_dir="../../hippocampus/episodic/"
    )
    
    # 监控 DavidAgent 的生命线库
    core_dependencies = ["pola-rs/polars", "microsoft/autogen", "langchain-ai/langchain"]
    
    print("🚀 DavidAgent 正在扫描核心依赖的“地雷区”...")
    bugs = explorer.explore_issues(core_dependencies)
    
    for bug in bugs:
        status = "🔴 [活跃]" if bug['state'] == 'open' else "🟢 [已修补]"
        print(f"{status} {bug['repo']}: {bug['title']}")
        print(f"   详情链接: {bug['url']}\n")
        
        # 无论是否处理，标记为已读，确保系统熵值稳定
        explorer.mark_as_seen(bug['issue_id'], bug['repo'])