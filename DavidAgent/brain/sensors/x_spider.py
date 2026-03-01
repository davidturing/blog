"""
感知器官 (Sensors) - X 网站爬虫
基于 bird 命令行工具，支持批量抓取并推送到黑板
"""
import os
import json
import asyncio
import subprocess
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

class XSpider:
    """X 网站感知探测器"""
    
    def __init__(self, blackboard=None):
        from brain.config import BrainConfig
        self.config = BrainConfig()
        self.blackboard = blackboard
        # 默认数据存储位置
        self.data_dir = os.path.join(os.getcwd(), "brain/sensors/data")
        os.makedirs(self.data_dir, exist_ok=True)
        
    async def fetch_tweets_by_handle(self, handle: str, count: int = 5) -> List[Dict]:
        """抓取指定账号的最新推文"""
        import tempfile
        print(f"📡 [感知器-X] 正在探测账号 @{handle}...")
        cmd = ["bird", "search", f"from:{handle}", "-n", str(count), "--json-full"]
        
        try:
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=tmp,
                    stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await process.communicate()
                
                if process.returncode != 0:
                    print(f"❌ [感知器-X] Bird 搜索失败: {stderr.decode()}")
                    return []
                
                tmp.seek(0)
                result = tmp.read().decode('utf-8', errors='ignore').strip()
                
            # 鲁棒解析 JSON
            start_idx = result.find('[')
            end_idx = result.rfind(']')
            if start_idx != -1 and end_idx != -1:
                tweets = json.loads(result[start_idx:end_idx+1])
            else:
                tweets = json.loads(result)
            
            print(f"✅ [感知器-X] 成功获取 @{handle} 的 {len(tweets)} 条详细推文")
            return tweets
        except Exception as e:
            print(f"❌ [感知器-X] 异常 (@{handle}): {e}")
            return []
            
    async def fetch_tweet_by_id(self, tweet_id: str) -> List[Dict]:
        """抓取特定 ID 的推文/文章"""
        import tempfile
        print(f"📡 [感知器-X] 正在抓取特定 ID: {tweet_id}...")
        cmd = ["bird", "read", tweet_id, "--json-full"]
        try:
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=tmp,
                    stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await process.communicate()
                
                if process.returncode != 0:
                    print(f"❌ [感知器-X] Bird 读取失败: {stderr.decode()}")
                    return []
                
                tmp.seek(0)
                result = tmp.read().decode('utf-8', errors='ignore').strip()
            
            # 鲁棒解析 JSON
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx+1]
                print(f"📊 [感知器-X] 原始数据长度: {len(result)}, JSON 截取长度: {len(json_str)}")
                tweet = json.loads(json_str)
            else:
                tweet = json.loads(result)
            
            return [tweet]
        except Exception as e:
            print(f"❌ [感知器-X] 抓取异常: {e}")
            return []

    async def ingest_to_blackboard(self, handle: str, count: int = 5, tweet_ids: Optional[List[str]] = None):
        """
        抓取并推送到黑板 (支持通过 handle 抓取最新或指定 ID)
        """
        if tweet_ids:
            tweets = []
            for tid in tweet_ids:
                tweets.extend(await self.fetch_tweet_by_id(tid))
        else:
            tweets = await self.fetch_tweets_by_handle(handle, count)
        
        if not tweets or not self.blackboard:
            return
            
        from brain.memory.episodic_memory import get_episodic_memory_db
        db = get_episodic_memory_db()
        
        for tweet in tweets:
            try:
                # bird search --json-full 返回的是标准化的推文对象，且带有 _raw 原始数据
                # 1. 基础信息提取 (优先使用标准化字段)
                raw_data = tweet.get('_raw', tweet) # 如果没有 _raw，则认为本身就是原始数据
                legacy_tweet = raw_data.get('legacy', {})
                user_res = raw_data.get('core', {}).get('user_results', {}).get('result', {})
                legacy_user = user_res.get('legacy', {})
                
                tweet_id = tweet.get('id') or tweet.get('id_str') or legacy_tweet.get('id_str')
                in_reply_to = tweet.get('inReplyToStatusId') or legacy_tweet.get('in_reply_to_status_id_str')
                
                # 2. 过滤回复 (Replies)
                if in_reply_to:
                    print(f"⏭️ [感知器-X] 过滤回复内容: {tweet_id}")
                    continue
                
                # 3. 提取文本及识别文章类型
                # X Articles / Note Tweets
                note_tweet = raw_data.get('note_tweet', {})
                note_text = note_tweet.get('note_tweet_results', {}).get('result', {}).get('text')
                
                text = note_text or tweet.get('text') or legacy_tweet.get('full_text') or ""
                
                # 文章识别逻辑强化
                is_article = False
                # 如果是 NoteTweet 或文本超长，通常就是 Article
                if note_tweet or len(text) > 280:
                    is_article = True
                    
                if not is_article:
                    print(f"⏭️ [感知器-X] 过滤非文章内容 (短 POST): {tweet_id}")
                    continue
                
                # 生成内容 Hash 用于去重
                content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                
                # 检查去重
                if db.check_duplicate(content_hash):
                    print(f"⏭️ [感知器-X] 跳过重复内容 (Hash: {content_hash[:8]})")
                    continue
                
                # 构造信号数据
                signal_data = {
                    'signal_id': f"x_{tweet_id}",
                    'content_hash': content_hash,
                    'handle': handle,
                    'author_name': legacy_user.get('name') or tweet.get('author', {}).get('name', handle),
                    'timestamp': tweet.get('createdAt') or legacy_tweet.get('created_at'),
                    'likes': tweet.get('likeCount') or legacy_tweet.get('favorite_count', 0),
                    'retweets': tweet.get('retweetCount') or legacy_tweet.get('retweet_count', 0),
                    'raw_text': text,
                    'raw_json': json.dumps(tweet, ensure_ascii=False),
                    'signal_type': 'article' if is_article else 'tweet'
                }
                
                # 1. 永久保存原始信号到 SQLite (raw_signals 表)
                db.save_raw_signal(signal_data)
                
                # 2. 推送到黑板触发下游 (Left/Right Brain)
                if self.blackboard:
                    self.blackboard.update('topic_id', signal_id := signal_data['signal_id'], 'SENSOR_X')
                    self.blackboard.update('raw_source', text, 'SENSOR_X')
                    self.blackboard.update('workflow_status', 'START', 'SYSTEM')
                
                type_label = "📄 文章" if is_article else "🐦 推文"
                print(f"📡 [感知器-X] 已摄入新信号 ({type_label}): {signal_data['signal_id']}")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"❌ [感知器-X] 解析推文失败: {e}")
                import traceback
                traceback.print_exc()
                continue
            
    async def batch_ingest(self, count_per_handle: int = 1):
        """
        批量抓取任务包 - 从 JSON 配置文件读取账号 (默认抓取 1 条推文)
        """
        accounts = []
        if os.path.exists(self.config.x_accounts_json):
            try:
                with open(self.config.x_accounts_json, 'r') as f:
                    accounts_data = json.load(f)
                    accounts = [a['handle'] for a in accounts_data if 'handle' in a]
            except Exception as e:
                print(f"⚠️ [感知器-X] 读取账号 JSON 失败: {e}")
        
        # 如果 JSON 为空，降级使用 config.py 的硬编码列表
        if not accounts:
            accounts = self.config.x_target_accounts
            
        print(f"🚀 [感知器-X] 开始执行批量探测任务: {accounts}")
        for handle in accounts:
            await self.ingest_to_blackboard(handle, count_per_handle)
            # 账号间休息，降低被风控风险
            await asyncio.sleep(10)
