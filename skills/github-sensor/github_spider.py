#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Spider - DavidAgent 感知器技能组件

架构定位：为DavidAgent仿生双脑架构的感知层（Sensors）提供GitHub硬核技术信息源
数据信噪比：极高（相比社交媒体高出几个数量级）
集成方式：异步技能组件，支持定时任务和事件触发

作者：G老师架构指导 + OpenClaw AI助手
"""

import asyncio
import base64
import os
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class GithubSpider:
    """
    GitHub感知器核心类
    
    功能：
    1. 技术趋势获取 (Trending Fetcher)
    2. 自动解卷与脱水 (Readme Unrolling)  
    3. 防爆盾与鉴权 (Resilience & Auth)
    """
    
    def __init__(self, token: str = None):
        """
        初始化GitHub感知器
        
        Args:
            token: GitHub Personal Access Token，用于提升API速率限制
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DavidAgent-GithubSpider/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        # GitHub API基础URL
        self.api_base = "https://api.github.com"
        
        # API限流处理
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
        
    async def _make_request(self, client: httpx.AsyncClient, url: str, **kwargs) -> dict:
        """
        统一的API请求方法，包含错误处理和限流保护
        
        Args:
            client: 异步HTTP客户端
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            API响应JSON数据
            
        Raises:
            Exception: API请求失败或限流异常
        """
        try:
            response = await client.get(url, headers=self.headers, **kwargs)
            
            # 更新速率限制信息
            if 'X-RateLimit-Remaining' in response.headers:
                self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
                self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            # 处理速率限制
            if response.status_code == 403 and self.rate_limit_remaining == 0:
                reset_time = datetime.fromtimestamp(self.rate_limit_reset, tz=timezone.utc)
                raise Exception(f"GitHub API速率限制已达到，重置时间: {reset_time}")
            
            # 处理其他错误
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # 仓库可能没有README，平滑降级
                return {}
            raise Exception(f"GitHub API请求失败: {e}")
        except Exception as e:
            raise Exception(f"网络请求异常: {e}")
    
    async def _fetch_readme(self, client: httpx.AsyncClient, owner: str, repo: str) -> str:
        """
        异步获取并解码仓库的README.md
        
        Args:
            client: 异步HTTP客户端
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            README内容（纯文本），如果获取失败返回空字符串
        """
        try:
            # 首先尝试获取README
            readme_url = f"{self.api_base}/repos/{owner}/{repo}/readme"
            readme_data = await self._make_request(client, readme_url)
            
            if not readme_data or 'content' not in readme_data:
                return ""
            
            # 解码Base64内容
            content = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # 清理Markdown格式，保留核心文本
            cleaned_content = self._clean_markdown(content)
            return cleaned_content[:2000]  # 限制长度避免过长
            
        except Exception as e:
            print(f"获取README失败 ({owner}/{repo}): {e}")
            return ""
    
    def _clean_markdown(self, text: str) -> str:
        """
        清理Markdown文本，移除不必要的格式标记
        
        Args:
            text: 原始Markdown文本
            
        Returns:
            清理后的纯文本
        """
        if not text:
            return ""
        
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
    
    async def fetch_daily_trending(self, 
                                 limit: int = 5,
                                 hours: int = 24,
                                 language: str = "python") -> List[Dict]:
        """
        核心方法：获取指定时间窗口内的技术趋势
        
        Args:
            limit: 返回的项目数量限制
            hours: 时间窗口（小时），默认24小时
            language: 编程语言过滤，默认Python
            
        Returns:
            符合统一数据契约的Payload列表
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 计算时间窗口
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                since_str = since.strftime('%Y-%m-%d')
                
                # 构建搜索查询
                query = f"created:>{since_str}"
                if language:
                    query += f" language:{language}"
                
                search_url = f"{self.api_base}/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": limit
                }
                
                # 获取热门仓库
                search_result = await self._make_request(client, search_url, params=params)
                repositories = search_result.get('items', [])[:limit]
                
                if not repositories:
                    print(f"未找到过去{hours}小时内创建的{language}项目")
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
                
                print(f"成功获取{len(payloads)}个GitHub趋势项目")
                return payloads
                
            except Exception as e:
                print(f"获取GitHub趋势失败: {e}")
                return []
    
    async def fetch_discussions(self, 
                               owner: str, 
                               repo: str, 
                               limit: int = 5) -> List[Dict]:
        """
        获取仓库Discussions中的深度技术讨论（使用GraphQL API）
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称  
            limit: 返回的讨论数量限制
            
        Returns:
            符合统一数据契约的Payload列表
        """
        # TODO: 实现GraphQL API调用获取Discussions
        # 这需要更复杂的GraphQL查询构建
        print("Discussions功能待实现（需要GraphQL API支持）")
        return []
    
    async def fetch_user_events(self, username: str, limit: int = 10) -> List[Dict]:
        """
        获取用户公开事件（监控KOL动态）
        
        Args:
            username: GitHub用户名
            limit: 返回的事件数量限制
            
        Returns:
            符合统一数据契约的Payload列表
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                events_url = f"{self.api_base}/users/{username}/events/public"
                events = await self._make_request(client, events_url)
                
                payloads = []
                for event in events[:limit]:
                    if event['type'] == 'WatchEvent':  # Star事件
                        repo_info = event['repo']
                        payload = {
                            "source_type": "github_event",
                            "source_id": f"event_{event['id']}",
                            "author": username,
                            "timestamp": event['created_at'],
                            "core_text": f"【KOL动态】: {username} Star了项目 {repo_info['name']}",
                            "original_url": f"https://github.com/{repo_info['name']}"
                        }
                        payloads.append(payload)
                
                return payloads
                
            except Exception as e:
                print(f"获取用户事件失败: {e}")
                return []


# 使用示例和测试函数
async def main():
    """测试函数"""
    spider = GithubSpider()
    
    print("=== 测试GitHub趋势获取 ===")
    trending_payloads = await spider.fetch_daily_trending(limit=3, hours=48, language="python")
    
    for payload in trending_payloads:
        print(f"\n项目: {payload['author']}/{payload['source_id']}")
        print(f"URL: {payload['original_url']}")
        print(f"摘要: {payload['core_text'][:200]}...")
    
    print(f"\n=== 完成测试，共获取{len(trending_payloads)}个项目 ===")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())