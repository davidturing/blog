#!/usr/bin/env python3
"""
Twitter Insight Pipeline V2 - 全域重构版
- 动态热词库自动扩展
- 真实 AI 摘要与观点提炼
- 好奇心引擎评分系统
- 智能排序输出
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# Load env
from dotenv import load_dotenv
load_dotenv()

# AI Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==================== 动态热词库 ====================
class AIKeywordEngine:
    """AI 全域热词库 - 自动扩展、动态更新"""
    
    def __init__(self):
        # 核心热词（永久）
        self.core_keywords = [
            "AI", "Artificial Intelligence", "LLM", "Large Language Model",
            "AGI", "GPT", "OpenAI", "Gemini", "Claude", "Qwen", "GLM",
            "Agent", "AI Agent", "RAG", "GraphRAG", "MCP", "Vibe Coding",
            "Transformer", "Deep Learning", "Machine Learning", "Neural Network"
        ]
        
        # 动态热词（可扩展）
        self.dynamic_keywords = [
            "CodeLlama", "CodeX", "Sora", "DALL-E", "Midjourney",
            "A100", "H100", "CUDA", "TPU", "GPU",
            "Scaling Law", "Alignment", "Fine-tuning", "RLHF", "DPO",
            "AWS", "GCP", "Azure", "Cloud AI", "Edge AI",
            "Multi-agent", "Autonomous Agent", "ReAct", "CoT",
            "Inference", "Training", "Pre-training", "Post-training"
        ]
        
        # 新兴热词池（从最近推文中发现）
        self.emerging_keywords = []
        
        # 搜索权重
        self.keyword_weights = {kw: 1.0 for kw in self.core_keywords}
    
    def get_search_query(self, limit=15):
        """生成动态搜索查询"""
        # 组合核心词 + 动态词
        all_keywords = self.core_keywords[:10] + self.dynamic_keywords[:5]
        
        # 构建 OR 查询
        keyword_parts = [f'"{kw}"' for kw in all_keywords[:limit]]
        query = f"({' OR '.join(keyword_parts)}) lang:en min_faves:50"
        
        return query
    
    def discover_new_keywords(self, tweet_texts):
        """从推文中发现新兴热词"""
        # 常见 AI 相关新词模式
        new_word_patterns = [
            "AI2", "xAI", "DeepSeek", "Mistral", "Llama 3", "GPT-5",
            "Claude 3", "Gemini 2", "Qwen 2", "Grok",
            "O1", "O3", "Reasoning", "Chain of Thought",
            "World Model", "Embodied AI", "Robotics AI"
        ]
        
        for text in tweet_texts:
            text_lower = text.lower()
            for pattern in new_word_patterns:
                if pattern.lower() in text_lower and pattern not in self.dynamic_keywords:
                    self.emerging_keywords.append(pattern)
                    self.dynamic_keywords.append(pattern)
                    print(f"  🔍 发现新热词: {pattern}")
        
        # 去重
        self.emerging_keywords = list(set(self.emerging_keywords))
        self.dynamic_keywords = list(set(self.dynamic_keywords))


# ==================== 好奇心引擎 ====================
class CuriosityEngine:
    """好奇心引擎 - 评估推文价值"""
    
    def __init__(self, gemini_key=None):
        self.gemini_key = gemini_key or GEMINI_API_KEY
    
    def evaluate(self, tweet_data):
        """评估单条推文的好奇心价值"""
        text = tweet_data.get('text', '')
        like_count = tweet_data.get('likeCount', 0)
        retweet_count = tweet_data.get('retweetCount', 0)
        reply_count = tweet_data.get('replyCount', 0)
        
        # 基础指标计算
        engagement_score = min(10, (like_count + retweet_count * 2 + reply_count * 3) / 100)
        
        # AI 内容评估
        ai_analysis = self._ai_evaluate(text) if self.gemini_key else {}
        
        # 综合评分
        info_value = ai_analysis.get('info_value', 5)
        timeliness = ai_analysis.get('timeliness', 5)
        industry_impact = ai_analysis.get('industry_impact', 5)
        
        # 加权总分
        total_score = (
            engagement_score * 0.2 +
            info_value * 0.3 +
            timeliness * 0.25 +
            industry_impact * 0.25
        )
        
        return {
            'total_score': round(total_score, 1),
            'info_value': info_value,
            'timeliness': timeliness,
            'industry_impact': industry_impact,
            'worth_attention': total_score >= 6.0,
            'reason': ai_analysis.get('reason', '基于互动数据评估')
        }
    
    def _ai_evaluate(self, text):
        """使用 AI 评估内容价值"""
        if not self.gemini_key:
            return {}
        
        prompt = f"""评估这条 AI/科技推文的价值（输出 JSON）：

推文内容：
{text[:500]}

输出格式（仅 JSON，无其他内容）：
{{
    "info_value": 1-10,
    "timeliness": 1-10,
    "industry_impact": 1-10,
    "reason": "简短理由"
}}"""
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                raw = data["candidates"][0]["content"]["parts"][0]["text"]
                # 提取 JSON
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]
                return json.loads(raw.strip())
        except Exception as e:
            print(f"  ⚠️ AI 评估失败: {e}")
        
        return {}


# ==================== AI 摘要引擎 ====================
class SummaryEngine:
    """AI 摘要引擎 - 深度提炼观点"""
    
    def __init__(self, gemini_key=None):
        self.gemini_key = gemini_key or GEMINI_API_KEY
    
    def summarize(self, text, author=""):
        """生成核心观点和深度解读"""
        if not self.gemini_key:
            return {
                'key_point': 'AI 摘要服务暂不可用',
                'deep_insight': '请检查 GEMINI_API_KEY 配置'
            }
        
        prompt = f"""你是一位资深 AI 科技博主。请深度分析这条推文：

作者: @{author}
内容: {text[:1000]}

输出格式（严格遵守）：
核心观点：[一句话精准总结核心信息，不超过30字]
深度解读：[一句话行业趋势/技术影响判断，不超过50字]

要求：
1. 核心观点要精准、有价值、不是废话
2. 深度解读要有前瞻性、体现专业洞察
3. 不用"这是一条关于..."这种开头
4. 直接输出内容，不要加序号"""
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                raw = data["candidates"][0]["content"]["parts"][0]["text"]
                
                # 解析输出
                key_point = ""
                deep_insight = ""
                
                for line in raw.split('\n'):
                    line = line.strip()
                    if line.startswith('核心观点') or line.startswith('核心观点：'):
                        key_point = line.split('：', 1)[-1].strip() if '：' in line else line.split(':', 1)[-1].strip()
                    elif line.startswith('深度解读') or line.startswith('深度解读：'):
                        deep_insight = line.split('：', 1)[-1].strip() if '：' in line else line.split(':', 1)[-1].strip()
                
                return {
                    'key_point': key_point or raw[:50],
                    'deep_insight': deep_insight or ''
                }
        except Exception as e:
            print(f"  ⚠️ AI 摘要失败: {e}")
        
        return {
            'key_point': '摘要生成失败',
            'deep_insight': ''
        }


# ==================== 主流程 ====================
class TwitterInsightPipeline:
    """Twitter 每日精选 Pipeline V2"""
    
    def __init__(self):
        self.keyword_engine = AIKeywordEngine()
        self.curiosity_engine = CuriosityEngine()
        self.summary_engine = SummaryEngine()
    
    def search_tweets(self, count=10):
        """使用 bird CLI 搜索推文"""
        query = self.keyword_engine.get_search_query()
        print(f"🔍 搜索查询: {query[:80]}...")
        
        try:
            result = subprocess.run([
                "bird", "search",
                query,
                "--count", str(count),
                "--json"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                tweets = json.loads(result.stdout)
                print(f"✅ 获取 {len(tweets)} 条推文")
                return tweets
            else:
                print(f"❌ Bird 搜索失败: {result.stderr}")
                return []
        except Exception as e:
            print(f"❌ 搜索异常: {e}")
            return []
    
    def parse_tweet(self, tweet):
        """正确解析推文数据"""
        # ✅ 修复：正确获取作者信息
        author = tweet.get('author', {})
        username = author.get('username', 'unknown')
        display_name = author.get('name', 'Unknown')
        
        return {
            'id': tweet.get('id', ''),
            'text': tweet.get('text', ''),
            'username': username,
            'display_name': display_name,
            'likeCount': tweet.get('likeCount', 0),
            'retweetCount': tweet.get('retweetCount', 0),
            'replyCount': tweet.get('replyCount', 0),
            'createdAt': tweet.get('createdAt', ''),
            'url': f"https://twitter.com/{username}/status/{tweet.get('id', '')}"
        }
    
    def process_tweets(self, tweets, top_n=5):
        """处理推文：评估、摘要、排序"""
        processed = []
        texts = [t.get('text', '') for t in tweets]
        
        # 发现新热词
        self.keyword_engine.discover_new_keywords(texts)
        
        for tweet in tweets:
            parsed = self.parse_tweet(tweet)
            
            # 好奇心评估
            print(f"  📊 评估 @{parsed['username']}...")
            curiosity = self.curiosity_engine.evaluate(tweet)
            
            # AI 摘要
            print(f"  🤖 摘要 @{parsed['username']}...")
            summary = self.summary_engine.summarize(parsed['text'], parsed['username'])
            
            processed.append({
                **parsed,
                'curiosity': curiosity,
                'summary': summary
            })
            
            time.sleep(0.5)  # 避免 rate limit
        
        # 按好奇心评分排序
        processed.sort(key=lambda x: x['curiosity']['total_score'], reverse=True)
        
        return processed[:top_n]
    
    def generate_output(self, tweets):
        """生成 Markdown 输出"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        md = f"# Twitter 每日精选 ({date_str})\n\n"
        md += f"> 由 DavidAgent 好奇心引擎精选，共 {len(tweets)} 条高质量 AI 资讯\n\n"
        md += "---\n\n"
        
        for i, tweet in enumerate(tweets, 1):
            c = tweet['curiosity']
            s = tweet['summary']
            
            md += f"## {i}. @{tweet['username']} ({tweet['display_name']})\n\n"
            md += f"**推文原文**：\n> {tweet['text'][:300]}{'...' if len(tweet['text']) > 300 else ''}\n\n"
            md += f"**核心观点**：{s['key_point']}\n\n"
            
            if s['deep_insight']:
                md += f"**深度解读**：{s['deep_insight']}\n\n"
            
            md += f"**好奇心引擎评估**：\n"
            md += f"- 📊 综合评分：**{c['total_score']}/10**\n"
            md += f"- 💡 信息价值：{c['info_value']}/10\n"
            md += f"- ⏰ 时效性：{c['timeliness']}/10\n"
            md += f"- 🌐 行业影响：{c['industry_impact']}/10\n"
            md += f"- {'🔥 **值得重点关注**' if c['worth_attention'] else '📌 一般关注'}\n\n"
            md += f"[查看原文]({tweet['url']})\n\n"
            md += "---\n\n"
        
        return md
    
    def run(self):
        """执行完整流程"""
        print("🚀 Twitter Insight Pipeline V2 启动...\n")
        
        # 1. 搜索推文
        tweets = self.search_tweets(count=10)
        
        if not tweets:
            print("❌ 未获取到推文")
            return None
        
        # 2. 处理推文
        print("\n📝 处理推文中...\n")
        processed = self.process_tweets(tweets, top_n=5)
        
        # 3. 生成输出
        print("\n📄 生成报告...\n")
        output = self.generate_output(processed)
        
        # 4. 保存文件
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 保存到本地 memory
        memory_path = Path(__file__).parent.parent.parent / "memory" / f"twitter_insight_{date_str}.md"
        memory_path.parent.mkdir(exist_ok=True)
        memory_path.write_text(output)
        print(f"✅ 已保存到: {memory_path}")
        
        # 保存到 GitHub tech 仓库
        tech_path = Path("/Users/zhaoqinhuang/github/tech/twitter-summary") / f"twitter_summary_{date_str}.md"
        tech_path.parent.mkdir(exist_ok=True)
        tech_path.write_text(output)
        print(f"✅ 已保存到: {tech_path}")
        
        return output


if __name__ == "__main__":
    pipeline = TwitterInsightPipeline()
    output = pipeline.run()
    
    if output:
        print("\n" + "="*60)
        print(output)
        print("="*60)
