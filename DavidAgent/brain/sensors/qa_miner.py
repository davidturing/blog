"""
StackOverflow 异常补丁采集器 - 实战问题与解决方案挖掘
"""

import logging
from typing import List, Dict, Any
from datetime import datetime


class QAMiner:
    """StackOverflow 异常补丁采集器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 QA 采集器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger("QAMiner")
        self.config = config
        self.qa_tags = config.get("qa_tags", [])
        self.serpapi_key = self._load_serpapi_key()
        
    def _load_serpapi_key(self) -> Optional[str]:
        """从凭据文件加载 SERP API key"""
        try:
            credentials_path = ".credentials/api_keys.env"
            if os.path.exists(credentials_path):
                with open(credentials_path, "r") as f:
                    for line in f:
                        if line.strip().startswith("SERPAPI_KEY="):
                            return line.strip().split("=", 1)[1].strip('"\'')
        except Exception as e:
            self.logger.warning(f"无法加载 SERP API key: {e}")
        return None
        
    def search_qa_posts(self) -> List[Dict[str, Any]]:
        """搜索 QA 帖子（模拟实现）
        
        Returns:
            帖子列表
        """
        self.logger.info("开始搜索 StackOverflow 高价值问题...")
        
        # 模拟搜索结果（实际实现会调用 StackExchange API 或 SERP API）
        qa_posts = [
            {
                "id": "7001234",
                "title": "How to optimize Polars DataFrame operations for large datasets?",
                "question": "I'm working with 10GB+ CSV files and Polars is running out of memory. What are the best practices for memory-efficient operations?",
                "answer": "Use lazy evaluation with .lazy() and .collect() only when needed. Also consider using scan_csv() instead of read_csv() for streaming processing. For very large datasets, partition your data and process in chunks.",
                "tags": ["python", "polars", "dataframe", "memory-optimization"],
                "score": 45,
                "accepted_answer": True
            },
            {
                "id": "7001235",
                "title": "OpenClaw Agent Framework: How to implement custom MCP tools?",
                "question": "I want to create custom tools for my OpenClaw agents using the MCP protocol. What's the correct way to register and implement them?",
                "answer": "Create a class that inherits from MCPTool base class, implement the execute() method, then register it with agent.register_tool(). Make sure to handle both sync and async execution patterns as per MCP specification.",
                "tags": ["openclaw", "ai-agent", "mcp", "tool-integration"],
                "score": 32,
                "accepted_answer": True
            },
            {
                "id": "7001236", 
                "title": "Best practices for AutoGen multi-agent conversation management?",
                "question": "When using Microsoft AutoGen with multiple agents, how do I prevent infinite loops and manage conversation flow effectively?",
                "answer": "Use the GroupChat manager with max_rounds parameter. Implement custom termination conditions in your agent logic. Also consider using the sequential chat pattern instead of group chat for complex workflows.",
                "tags": ["autogen", "multi-agent", "llm", "conversation-management"],
                "score": 28,
                "accepted_answer": True
            }
        ]
        
        # 过滤包含相关标签的帖子
        filtered_posts = []
        qa_tags_set = set(self.qa_tags)
        
        for post in qa_posts:
            post_tags_set = set(post["tags"])
            if qa_tags_set.intersection(post_tags_set):
                filtered_posts.append(post)
                
        max_fetch = self.config.get("max_fetch_per_cycle", 5)
        return filtered_posts[:max_fetch]
        
    def extract_insights(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从 QA 帖子中提取洞察
        
        Args:
            posts: 帖子列表
            
        Returns:
            提取的洞察列表
        """
        insights = []
        
        for post in posts:
            # 合并问题和答案
            full_content = f"Question: {post['question']}\n\nAnswer: {post['answer']}"
            
            insight = {
                "source": "qa",
                "title": f"QA: {post['title']}",
                "content": full_content,
                "metadata": {
                    "platform": "stackoverflow",
                    "post_id": post["id"],
                    "tags": post["tags"],
                    "score": post["score"],
                    "has_accepted_answer": post["accepted_answer"],
                    "url": f"https://stackoverflow.com/questions/{post['id']}"
                },
                "timestamp": datetime.now().isoformat()
            }
            insights.append(insight)
            
        return insights
        
    def run_discovery(self) -> List[Dict[str, Any]]:
        """运行完整的 QA 采集流程
        
        Returns:
            提取的洞察列表
        """
        try:
            # 搜索 QA 帖子
            posts = self.search_qa_posts()
            
            if not posts:
                self.logger.info("未发现相关 QA 内容")
                return []
                
            # 提取洞察
            insights = self.extract_insights(posts)
            
            self.logger.info(f"QA 采集完成，获得 {len(insights)} 项洞察")
            return insights
            
        except Exception as e:
            self.logger.error(f"QA 采集失败: {e}")
            return []