"""
GitHub 趋势感知器 (GitHub Trending Sensor)
用于自动采集最新的AI技术趋势并更新知识图谱
"""
import os
import json
import asyncio
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class GitHubTrendingSensor:
    """GitHub 趋势感知器 - 专门用于采集最新AI技术趋势"""
    
    def __init__(self, blackboard=None):
        from brain.config import BrainConfig
        self.config = BrainConfig()
        self.blackboard = blackboard
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DavidAgent-GithubTrendingSensor/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        self.api_base = "https://api.github.com"
    
    async def _make_request(self, client: httpx.AsyncClient, url: str, **kwargs) -> dict:
        """统一的API请求方法，包含错误处理和限流保护"""
        try:
            response = await client.get(url, headers=self.headers, **kwargs)
            
            # 处理速率限制
            if response.status_code == 403:
                rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', '0'))
                if rate_limit_remaining == 0:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', '0'))
                    reset_datetime = datetime.fromtimestamp(reset_time, tz=timezone.utc)
                    raise Exception(f"GitHub API速率限制已达到，重置时间: {reset_datetime}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {}
            raise Exception(f"GitHub API请求失败: {e}")
        except Exception as e:
            raise Exception(f"网络请求异常: {e}")
    
    async def _fetch_readme(self, client: httpx.AsyncClient, owner: str, repo: str) -> str:
        """异步获取并解码仓库的README.md"""
        try:
            readme_url = f"{self.api_base}/repos/{owner}/{repo}/readme"
            readme_data = await self._make_request(client, readme_url)
            
            if not readme_data or 'content' not in readme_data:
                return ""
            
            import base64
            content = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # 清理Markdown格式，保留核心文本
            cleaned_content = self._clean_markdown(content)
            return cleaned_content[:2000]  # 限制长度避免过长
            
        except Exception as e:
            print(f"获取README失败 ({owner}/{repo}): {e}")
            return ""
    
    def _clean_markdown(self, text: str) -> str:
        """清理Markdown文本，移除不必要的格式标记"""
        if not text:
            return ""
        
        import re
        # 移除代码块
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`[^`]*`', '', text)
        
        # 移除图片和链接
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        
        # 移除标题标记
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # 移除列表标记
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 清理多余空白行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    async def fetch_ai_trending_repos(self, 
                                    limit: int = 5,
                                    hours: int = 24) -> List[Dict]:
        """
        获取指定时间窗口内的AI相关技术趋势
        
        Args:
            limit: 返回的项目数量限制
            hours: 时间窗口（小时），默认24小时
            
        Returns:
            符合统一数据契约的Payload列表
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 计算时间窗口
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                since_str = since.strftime('%Y-%m-%d')
                
                # 构建搜索查询 - AI相关关键词
                ai_keywords = ["ai", "ml", "machine-learning", "deep-learning", "llm", "large-language-model", "neural", "artificial-intelligence"]
                query = f"created:>{since_str} {' '.join([f'topic:{kw}' for kw in ai_keywords[:3]])}"  # 使用前3个关键词避免查询过长
                
                search_url = f"{self.api_base}/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": limit
                }
                
                # 如果没有结果，尝试更宽泛的查询
                search_result = await self._make_request(client, search_url, params=params)
                repositories = search_result.get('items', [])[:limit]
                
                if not repositories:
                    # 尝试Python语言过滤
                    query = f"created:>{since_str} language:python"
                    params["q"] = query
                    search_result = await self._make_request(client, search_url, params=params)
                    repositories = search_result.get('items', [])[:limit]
                
                if not repositories:
                    print(f"未找到过去{hours}小时内创建的AI相关项目")
                    return []
                
                # 并发获取所有仓库的README
                readme_tasks = []
                for repo in repositories:
                    owner = repo['owner']['login']
                    name = repo['name']
                    task = self._fetch_readme(client, owner, name)
                    readme_tasks.append(task)
                
                readme_contents = await asyncio.gather(*readme_tasks, return_exceptions=True)
                
                # 组装标准Payload
                payloads = []
                for i, repo in enumerate(repositories):
                    # 处理README获取异常
                    if isinstance(readme_contents[i], Exception):
                        readme_text = ""
                        print(f"README获取异常: {readme_contents[i]}")
                    else:
                        readme_text = readme_contents[i]
                    
                    # 构建core_text
                    core_text = f"【项目名称】: {repo['name']}\n"
                    core_text += f"【简介】: {repo.get('description', '无描述')}\n"
                    if readme_text:
                        core_text += f"【核心README】: {readme_text}"
                    
                    payload = {
                        "source_type": "github_trending",
                        "source_id": f"repo_{repo['id']}",
                        "author": repo['owner']['login'],
                        "timestamp": repo['created_at'],
                        "core_text": core_text.strip(),
                        "original_url": repo['html_url']
                    }
                    payloads.append(payload)
                
                print(f"成功获取{len(payloads)}个GitHub AI趋势项目")
                return payloads
                
            except Exception as e:
                print(f"获取GitHub AI趋势失败: {e}")
                return []
    
    async def ingest_to_blackboard(self, limit: int = 5, hours: int = 24):
        """抓取AI趋势并推送到黑板持久化"""
        trending_repos = await self.fetch_ai_trending_repos(limit=limit, hours=hours)
        
        if not trending_repos or not self.blackboard:
            return
        
        from brain.memory.episodic_memory import get_episodic_memory_db
        db = get_episodic_memory_db()
        
        for repo_data in trending_repos:
            text_content = repo_data['core_text']
            if not text_content:
                print(f"⏭️ 跳过无内容仓库: {repo_data['original_url']}")
                continue
            
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            
            # 检查去重 (如果内容没变就跳过分析)
            if db.check_duplicate(content_hash):
                print(f"⏭️ 跳过重复内容体系 (Hash: {content_hash[:8]})")
                continue
            
            signal_id = f"gh_trend_{repo_data['source_id']}_{content_hash[:4]}"
            
            # 构造统一信号格式
            signal_data = {
                'signal_id': signal_id,
                'content_hash': content_hash,
                'handle': repo_data['original_url'],
                'author_name': repo_data['author'],
                'timestamp': repo_data['timestamp'],
                'likes': 0,  # GitHub趋势不直接提供likes
                'retweets': 0,  # GitHub趋势不直接提供retweets
                'raw_text': text_content,
                'raw_json': json.dumps(repo_data, ensure_ascii=False),
                'signal_type': 'github_trending'
            }
            
            # 保存原始信号
            db.save_raw_signal(signal_data)
            
            # 推送黑板触发分析
            self.blackboard.update('topic_id', signal_id, 'SENSOR_GH_TRENDING')
            self.blackboard.update('raw_source', signal_data['raw_text'], 'SENSOR_GH_TRENDING')
            self.blackboard.update('workflow_status', 'START', 'SYSTEM')
            
            print(f"📡 [感知器-GitHub-Trending] 已注入 AI 趋势信号点: {signal_id}")

# 使用示例
async def main():
    """测试函数"""
    sensor = GitHubTrendingSensor()
    await sensor.ingest_to_blackboard(limit=3, hours=48)

if __name__ == "__main__":
    asyncio.run(main())