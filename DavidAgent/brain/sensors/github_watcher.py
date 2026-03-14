"""
GitHub 技术演进探测器 - 高价值仓库发现与分析
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import polars as pl
from pathlib import Path


class GitHubWatcher:
    """GitHub 技术演进探测器"""
    
    def __init__(self, config: Dict[str, Any], github_token: Optional[str] = None):
        """初始化 GitHub 探测器
        
        Args:
            config: 配置字典
            github_token: GitHub API token（可选）
        """
        self.logger = logging.getLogger("GitHubWatcher")
        self.config = config
        self.github_token = github_token or self._load_github_token()
        
        # 缓存文件路径
        self.cache_dir = Path("DavidAgent/hippocampus/episodic")
        self.cache_file = self.cache_dir / "github_seen_repos.parquet"
        self._ensure_cache_dir()
        
        # 加载现有缓存
        self.seen_repos = self._load_cache()
        
    def _load_github_token(self) -> Optional[str]:
        """从凭据文件加载 GitHub token"""
        try:
            credentials_path = ".credentials/api_keys.env"
            if os.path.exists(credentials_path):
                with open(credentials_path, "r") as f:
                    for line in f:
                        if line.strip().startswith("GITHUB_TOKEN="):
                            return line.strip().split("=", 1)[1].strip('"\'')
        except Exception as e:
            self.logger.warning(f"无法加载 GitHub token: {e}")
        return None
        
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_cache(self) -> set:
        """加载已见仓库缓存"""
        if self.cache_file.exists():
            try:
                df = pl.read_parquet(self.cache_file)
                return set(df["repo_id"].to_list())
            except Exception as e:
                self.logger.warning(f"无法加载缓存: {e}")
        return set()
        
    def _save_cache(self, new_repos: List[Dict[str, Any]]):
        """保存新发现的仓库到缓存"""
        if not new_repos:
            return
            
        # 创建 DataFrame
        repo_ids = [repo["full_name"] for repo in new_repos]
        timestamps = [datetime.now().isoformat() for _ in new_repos]
        
        df = pl.DataFrame({
            "repo_id": repo_ids,
            "discovered_at": timestamps
        })
        
        # 如果缓存文件存在，追加到现有数据
        if self.cache_file.exists():
            existing_df = pl.read_parquet(self.cache_file)
            df = pl.concat([existing_df, df])
            
        # 去重并保存
        df = df.unique(subset=["repo_id"])
        df.write_parquet(self.cache_file)
        self.logger.info(f"缓存已更新，共 {len(df)} 个仓库")
        
    def search_trending_repos(self) -> List[Dict[str, Any]]:
        """搜索高价值 GitHub 仓库
        
        Returns:
            仓库信息列表
        """
        self.logger.info("开始搜索 GitHub 高价值仓库...")
        
        # 获取配置的主题
        topics = self.config.get("github_topics", [])
        if not topics:
            self.logger.warning("未配置 GitHub 主题，使用默认主题")
            topics = ["ai", "machine-learning", "python", "rust"]
            
        # 模拟搜索结果（实际实现会调用 GitHub API）
        # 在生产环境中，这里会使用 PyGithub 或直接调用 GitHub Search API
        trending_repos = self._simulate_github_search(topics)
        
        # 过滤已见仓库
        new_repos = []
        for repo in trending_repos:
            repo_id = repo["full_name"]
            if repo_id not in self.seen_repos:
                new_repos.append(repo)
                
        self.logger.info(f"发现 {len(new_repos)} 个新仓库")
        
        # 保存新仓库到缓存
        if new_repos:
            self._save_cache(new_repos)
            self.seen_repos.update([repo["full_name"] for repo in new_repos])
            
        return new_repos
        
    def _simulate_github_search(self, topics: List[str]) -> List[Dict[str, Any]]:
        """模拟 GitHub 搜索（实际实现会调用真实 API）
        
        Args:
            topics: 搜索主题列表
            
        Returns:
            仓库信息列表
        """
        # 这里是模拟数据
        # 在实际实现中，会调用 GitHub Search API
        simulated_repos = [
            {
                "full_name": "openclaw/openclaw",
                "description": "Next-generation AI agent framework with MCP protocol support",
                "stars": 1250,
                "created_at": "2026-03-14T10:00:00Z",
                "updated_at": "2026-03-15T08:00:00Z",
                "language": "Python",
                "topics": ["ai-agent", "mcp", "framework"],
                "readme_content": "# OpenClaw Agent Framework\nNext-generation AI agent framework with standardized MCP protocol integration for seamless tool calling across platforms."
            },
            {
                "full_name": "polars-rs/polars",
                "description": "Blazingly fast DataFrame library for Rust and Python",
                "stars": 25000,
                "created_at": "2023-01-01T00:00:00Z", 
                "updated_at": "2026-03-15T07:00:00Z",
                "language": "Rust",
                "topics": ["dataframe", "rust", "python", "performance"],
                "readme_content": "# Polars\nBlazingly fast DataFrame library built on Apache Arrow memory format with lazy evaluation and query optimization."
            },
            {
                "full_name": "microsoft/autogen",
                "description": "Framework for enabling next-generation LLM applications",
                "stars": 18000,
                "created_at": "2023-08-01T00:00:00Z",
                "updated_at": "2026-03-15T06:00:00Z", 
                "language": "Python",
                "topics": ["llm", "agent", "framework", "multi-agent"],
                "readme_content": "# AutoGen\nFramework for enabling next-generation LLM applications via multi-agent conversations and tool integration."
            }
        ]
        
        return simulated_repos[:self.config.get("max_fetch_per_cycle", 5)]
        
    def extract_repo_insights(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从仓库中提取洞察（用于左脑蒸馏）
        
        Args:
            repos: 仓库信息列表
            
        Returns:
            提取的洞察列表
        """
        insights = []
        
        for repo in repos:
            insight = {
                "source": "github",
                "title": f"GitHub: {repo['full_name']}",
                "content": repo.get("readme_content", repo.get("description", "")),
                "metadata": {
                    "repo_name": repo["full_name"],
                    "stars": repo.get("stars", 0),
                    "language": repo.get("language", "unknown"),
                    "topics": repo.get("topics", []),
                    "url": f"https://github.com/{repo['full_name']}"
                },
                "timestamp": datetime.now().isoformat()
            }
            insights.append(insight)
            
        return insights
        
    def run_discovery(self) -> List[Dict[str, Any]]:
        """运行完整的 GitHub 发现流程
        
        Returns:
            提取的洞察列表
        """
        try:
            # 搜索新仓库
            new_repos = self.search_trending_repos()
            
            if not new_repos:
                self.logger.info("未发现新的高价值仓库")
                return []
                
            # 提取洞察
            insights = self.extract_repo_insights(new_repos)
            
            self.logger.info(f"GitHub 探测完成，获得 {len(insights)} 项洞察")
            return insights
            
        except Exception as e:
            self.logger.error(f"GitHub 探测失败: {e}")
            return []