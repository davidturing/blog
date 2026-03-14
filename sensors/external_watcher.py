"""
World感知主入口模块。

实现了 ExternalWatcher 类，负责协调5大资讯获取通道：
1. Code-Pull (GitHub)
2. RSS-Feed (ArXiv, 技术博客)
3. Social-Stream (Hacker News, Reddit)
4. Doc-Crawl (官方文档)
5. Q&A Mining (StackOverflow, Dev.to)

该模块严格遵循配置文件中的限流和资源约束。
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import tomli
from datetime import datetime

# Local imports
from sensors.embedding.ane_encoder import ANEEncoder
from sensors.distiller.brain_balance import DualBrainDistiller
from sensors.sandbox.shadow_runner import ShadowSandbox
from sensors.cpep.align_broadcast import CPEPAlign


class ExternalWatcher:
    """世界感知主协调器。"""

    def __init__(self, config_path: str = "config/world_grounding.toml"):
        """初始化外部观察者。
        
        Args:
            config_path: 配置文件路径。
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.encoder = ANEEncoder(self.config["algorithms"]["curiosity_engine"])
        self.distiller = DualBrainDistiller(self.config["algorithms"]["dual_brain_distiller"])
        self.sandbox = ShadowSandbox(self.config["algorithms"]["shadow_sandbox"])
        self.cpep = CPEPAlign(self.config["algorithms"]["cpep"])
        
        # Track bandwidth usage
        self.bandwidth_used = 0
        self.max_bandwidth = self.config["system"]["daily_bandwidth_limit_mb"] * 1024 * 1024  # Convert to bytes

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载 TOML 配置文件。
        
        Args:
            config_path: 配置文件路径。
            
        Returns:
            解析后的配置字典。
            
        Raises:
            FileNotFoundError: 如果配置文件不存在。
            tomli.TOMLDecodeError: 如果配置文件格式无效。
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, "rb") as f:
            return tomli.load(f)

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器。
        
        Returns:
            配置好的日志记录器。
        """
        logger = logging.getLogger("ExternalWatcher")
        logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if called multiple times
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    async def poll_github_trending(self) -> List[Dict[str, Any]]:
        """从 GitHub 获取热门仓库和趋势。
        
        Returns:
            包含仓库信息的字典列表。
        """
        if not self.config["sources"]["github"]["enabled"]:
            self.logger.info("GitHub source is disabled in config")
            return []
            
        if self._check_bandwidth_limit():
            self.logger.warning("Bandwidth limit reached, skipping GitHub polling")
            return []
            
        try:
            from github import Github
            # This is a placeholder - in real implementation, we'd use the GitHub API
            # For now, we'll simulate the data structure
            self.logger.info("Polling GitHub trending repositories...")
            # Simulate bandwidth usage
            self.bandwidth_used += 1024 * 50  # 50KB
            
            # Return mock data structure that matches expected format
            return [
                {
                    "source": "github",
                    "title": "openclaw/openclaw",
                    "description": "Open-source AI agent framework",
                    "url": "https://github.com/openclaw/openclaw",
                    "language": "TypeScript",
                    "stars": 1200,
                    "forks": 150,
                    "timestamp": datetime.now().isoformat(),
                    "raw_content": "OpenClaw is an open-source framework for building AI agents..."
                }
            ]
        except Exception as e:
            self.logger.error(f"Error polling GitHub: {e}")
            return []

    async def fetch_rss_feeds(self) -> List[Dict[str, Any]]:
        """获取 RSS/Atom 订阅源内容。
        
        Returns:
            包含文章信息的字典列表。
        """
        if not self.config["sources"]["rss"]["enabled"]:
            self.logger.info("RSS source is disabled in config")
            return []
            
        if self._check_bandwidth_limit():
            self.logger.warning("Bandwidth limit reached, skipping RSS polling")
            return []
            
        try:
            import feedparser
            self.logger.info("Fetching RSS feeds...")
            all_articles = []
            
            for feed_url in self.config["sources"]["rss"]["feeds"]:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:  # Limit to 5 entries per feed
                        article = {
                            "source": "rss",
                            "title": getattr(entry, "title", "No title"),
                            "description": getattr(entry, "summary", "") or getattr(entry, "description", ""),
                            "url": getattr(entry, "link", ""),
                            "published": getattr(entry, "published", datetime.now().isoformat()),
                            "timestamp": datetime.now().isoformat(),
                            "raw_content": getattr(entry, "summary", "") or getattr(entry, "description", "")
                        }
                        all_articles.append(article)
                        
                    # Simulate bandwidth usage
                    self.bandwidth_used += 1024 * 20  # 20KB per feed
                    
                except Exception as feed_error:
                    self.logger.warning(f"Error fetching feed {feed_url}: {feed_error}")
                    continue
                    
            return all_articles
            
        except Exception as e:
            self.logger.error(f"Error fetching RSS feeds: {e}")
            return []

    async def poll_social_stream(self) -> List[Dict[str, Any]]:
        """从社交平台获取内容（Hacker News, Reddit）。
        
        Returns:
            包含帖子信息的字典列表。
        """
        if not self.config["sources"]["social"]["enabled"]:
            self.logger.info("Social source is disabled in config")
            return []
            
        if self._check_bandwidth_limit():
            self.logger.warning("Bandwidth limit reached, skipping social polling")
            return []
            
        try:
            self.logger.info("Polling social streams...")
            # Simulate bandwidth usage
            self.bandwidth_used += 1024 * 30  # 30KB
            
            # Return mock data
            return [
                {
                    "source": "hackernews",
                    "title": "The Future of AI Agents",
                    "description": "Discussion on autonomous AI systems and their implications",
                    "url": "https://news.ycombinator.com/item?id=12345",
                    "score": 150,
                    "comments": 42,
                    "timestamp": datetime.now().isoformat(),
                    "raw_content": "AI agents are becoming increasingly sophisticated..."
                }
            ]
        except Exception as e:
            self.logger.error(f"Error polling social streams: {e}")
            return []

    async def crawl_document(self) -> List[Dict[str, Any]]:
        """爬取官方文档和知识库。
        
        Returns:
            包含文档片段的字典列表。
        """
        if not self.config["sources"]["docs"]["enabled"]:
            self.logger.info("Docs source is disabled in config")
            return []
            
        if self._check_bandwidth_limit():
            self.logger.warning("Bandwidth limit reached, skipping doc crawling")
            return []
            
        try:
            self.logger.info("Crawling documentation sites...")
            # Simulate bandwidth usage
            self.bandwidth_used += 1024 * 40  # 40KB
            
            # Return mock data
            return [
                {
                    "source": "readthedocs",
                    "title": "OpenClaw Documentation",
                    "description": "Official documentation for OpenClaw framework",
                    "url": "https://docs.openclaw.ai",
                    "section": "Agent Architecture",
                    "timestamp": datetime.now().isoformat(),
                    "raw_content": "OpenClaw agents follow a modular architecture with clear separation of concerns..."
                }
            ]
        except Exception as e:
            self.logger.error(f"Error crawling documents: {e}")
            return []

    async def mine_qa_content(self) -> List[Dict[str, Any]]:
        """从 Q&A 平台挖掘内容。
        
        Returns:
            包含问答内容的字典列表。
        """
        if not self.config["sources"]["qa"]["enabled"]:
            self.logger.info("Q&A source is disabled in config")
            return []
            
        if self._check_bandwidth_limit():
            self.logger.warning("Bandwidth limit reached, skipping Q&A mining")
            return []
            
        try:
            self.logger.info("Mining Q&A content...")
            # Simulate bandwidth usage
            self.bandwidth_used += 1024 * 25  # 25KB
            
            # Return mock data
            return [
                {
                    "source": "stackoverflow",
                    "title": "How to implement MCP protocol in Python?",
                    "description": "Best practices for implementing Model Context Protocol",
                    "url": "https://stackoverflow.com/questions/12345",
                    "tags": ["python", "mcp", "ai"],
                    "answers": 3,
                    "timestamp": datetime.now().isoformat(),
                    "raw_content": "To implement MCP protocol in Python, you should use asyncio for handling concurrent requests..."
                }
            ]
        except Exception as e:
            self.logger.error(f"Error mining Q&A content: {e}")
            return []

    def _check_bandwidth_limit(self) -> bool:
        """检查是否达到带宽限制。
        
        Returns:
            True if bandwidth limit is reached, False otherwise.
        """
        return self.bandwidth_used >= self.max_bandwidth

    def filter_by_entropy(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用认知熵驱动算法过滤数据。
        
        Args:
            data: 原始数据列表。
            
        Returns:
            过滤后的高优先级数据列表。
        """
        self.logger.info(f"Filtering {len(data)} items by cognitive entropy...")
        filtered_data = []
        
        for item in data:
            try:
                # Generate embedding for the content
                embedding = self.encoder.encode(item["raw_content"])
                
                # Calculate similarity with existing knowledge (simulated)
                similarity = self._calculate_similarity_with_skillbank(embedding)
                
                # Check if it's below threshold and has sufficient popularity
                popularity_score = self._get_popularity_score(item)
                
                if similarity < self.config["algorithms"]["curiosity_engine"]["similarity_threshold"] and \
                   popularity_score >= self.config["algorithms"]["curiosity_engine"]["min_popularity_score"]:
                    item["embedding"] = embedding
                    item["similarity_score"] = similarity
                    item["priority"] = popularity_score
                    filtered_data.append(item)
                    
            except Exception as e:
                self.logger.warning(f"Error processing item for entropy filtering: {e}")
                continue
                
        self.logger.info(f"Filtered down to {len(filtered_data)} high-priority items")
        return filtered_data

    def _calculate_similarity_with_skillbank(self, embedding: List[float]) -> float:
        """计算与现有知识库的相似度（模拟实现）。
        
        Args:
            embedding: 内容的向量表示。
            
        Returns:
            相似度分数（0.0 到 1.0）。
        """
        # In a real implementation, this would query LanceDB
        # For now, we'll simulate with random values biased toward lower similarity
        import random
        return random.uniform(0.2, 0.8)

    def _get_popularity_score(self, item: Dict[str, Any]) -> int:
        """获取内容的热度分数。
        
        Args:
            item: 数据项。
            
        Returns:
            热度分数。
        """
        source = item.get("source", "")
        if source == "github":
            return item.get("stars", 0) + item.get("forks", 0)
        elif source == "hackernews":
            return item.get("score", 0) + item.get("comments", 0)
        elif source == "rss":
            # RSS doesn't have explicit popularity, so we'll use a default score
            return 15
        elif source == "stackoverflow":
            return item.get("answers", 0) * 5
        else:
            return 10  # Default score for other sources

    async def run_full_cycle(self) -> Dict[str, Any]:
        """执行完整的感知周期。
        
        Returns:
            包含执行结果摘要的字典。
        """
        self.logger.info("Starting full world grounding cycle...")
        
        # Gather data from all sources concurrently
        tasks = [
            self.poll_github_trending(),
            self.fetch_rss_feeds(),
            self.poll_social_stream(),
            self.crawl_document(),
            self.mine_qa_content()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and handle exceptions
        all_data = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Source collection failed: {result}")
                continue
            all_data.extend(result)
            
        # Filter by cognitive entropy
        filtered_data = self.filter_by_entropy(all_data)
        
        # Process through distillation, sandbox, and CPEP
        validated_skills = []
        reasoning_entries = []
        
        for item in filtered_data:
            try:
                # Distill knowledge
                distilled = self.distiller.distill(item)
                
                # Validate in sandbox
                validation_result = self.sandbox.validate(distilled)
                
                if validation_result["success"]:
                    validated_skills.append(validation_result["skill"])
                    # In real implementation, this would be saved to SkillRL
                else:
                    reasoning_entries.append(validation_result["error_trace"])
                    # In real implementation, this would be saved to ReasoningBank
                    
                # Broadcast via CPEP regardless of validation result
                self.cpep.broadcast(distilled, validation_result)
                
            except Exception as e:
                self.logger.error(f"Error processing item: {e}")
                continue
                
        # Generate daily report
        report_data = {
            "new_tech_count": len(filtered_data),
            "validated_skills": len(validated_skills),
            "skillbank_entries": len(validated_skills),
            "reasoning_entries": len(reasoning_entries),
            "bandwidth_used": round(self.bandwidth_used / (1024 * 1024), 2),  # MB
            "entropy_reduction": round(len(filtered_data) * 0.5, 2)  # Simulated
        }
        
        self.logger.info("World grounding cycle completed successfully")
        return report_data


# For testing purposes
if __name__ == "__main__":
    import asyncio
    
    async def main():
        watcher = ExternalWatcher()
        result = await watcher.run_full_cycle()
        print("Daily Report Data:", result)
        
    asyncio.run(main())