"""
感知器官 (Sensors) - GitHub 仓库爬虫
支持批量抓取开源仓库 README 与元数据并推送到黑板
"""
import os
import json
import asyncio
import urllib.request
import base64
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

class GitHubSensor:
    """GitHub 仓库网络探测插件"""
    
    def __init__(self, blackboard=None):
        from brain.config import BrainConfig
        self.config = BrainConfig()
        self.blackboard = blackboard
        
    async def fetch_repo_data(self, owner: str, repo: str) -> Optional[Dict]:
        """通过 GitHub API 抓取仓库元信息与 README 内容"""
        print(f"📡 [感知器-GitHub] 正在分析代码仓库 {owner}/{repo}...")
        
        headers = {'User-Agent': 'DavidAgent-Sensor/1.0'}
        # Optional: Append exact GITHUB_TOKEN if rate limited
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers['Authorization'] = f"token {github_token}"
            
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        readme_url = f"{repo_url}/readme"
        
        try:
            # 获取元数据
            repo_req = urllib.request.Request(repo_url, headers=headers)
            with urllib.request.urlopen(repo_req) as response:
                repo_data = json.loads(response.read().decode('utf-8'))
                
            # 获取 README
            readme_req = urllib.request.Request(readme_url, headers=headers)
            with urllib.request.urlopen(readme_req) as response:
                readme_data = json.loads(response.read().decode('utf-8'))
                
            # 解码 Base64 README 内容
            content_decoded = ""
            if readme_data.get('encoding') == 'base64':
                content_decoded = base64.b64decode(readme_data['content']).decode('utf-8')
            
            repo_data['_readme_content'] = content_decoded
            print(f"✅ [感知器-GitHub] 成功获取 {owner}/{repo} (Stars: {repo_data.get('stargazers_count')})")
            return repo_data
            
        except urllib.error.HTTPError as e:
            print(f"❌ [感知器-GitHub] API 限流或不存在 {owner}/{repo}: {e}")
            return None
        except Exception as e:
            print(f"❌ [感知器-GitHub] 抓取异常 ({owner}/{repo}): {e}")
            return None

    async def ingest_to_blackboard(self, owner: str, repo: str):
        """抓取并推送到黑板持久化"""
        repo_data = await self.fetch_repo_data(owner, repo)
        if not repo_data or not self.blackboard:
            return
            
        from brain.memory.episodic_memory import get_episodic_memory_db
        db = get_episodic_memory_db()
        
        text_content = repo_data.get('_readme_content', '')
        if not text_content:
            print(f"⏭️ [感知器-GitHub] 过滤无 README 仓库: {owner}/{repo}")
            return
            
        content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
        
        # 检查去重 (如果 README 没变就跳过分析)
        if db.check_duplicate(content_hash):
            print(f"⏭️ [感知器-GitHub] 跳过重复内容体系 (Hash: {content_hash[:8]})")
            return
            
        signal_id = f"gh_{repo_data['id']}_{content_hash[:4]}"
        
        # 构造统一信号格式
        signal_data = {
            'signal_id': signal_id,
            'content_hash': content_hash,
            'handle': f"{owner}/{repo}",
            'author_name': repo_data['owner']['login'],
            'timestamp': repo_data.get('updated_at', datetime.now().isoformat()),
            'likes': repo_data.get('stargazers_count', 0),
            'retweets': repo_data.get('forks_count', 0),
            'raw_text': f"Repository: {owner}/{repo}\nDescription: {repo_data.get('description', '')}\n\n{text_content}",
            'raw_json': json.dumps(repo_data, ensure_ascii=False),
            'signal_type': 'github_repo'
        }
        
        # 保存原始信号
        db.save_raw_signal(signal_data)
        
        # 推送黑板触发分析
        self.blackboard.update('topic_id', signal_id, 'SENSOR_GH')
        self.blackboard.update('raw_source', signal_data['raw_text'], 'SENSOR_GH')
        self.blackboard.update('workflow_status', 'START', 'SYSTEM')
        
        print(f"📡 [感知器-GitHub] 已注入 Github 信号点: {signal_id}")
