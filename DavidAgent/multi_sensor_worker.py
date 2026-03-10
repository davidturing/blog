import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

from brain.app import AGEngine
from brain.sensors.rss_sensor import RSSSensor
from brain.sensors.github_sensor import GitHubSensor

async def run_multi_sensors():
    print("=" * 60)
    print("🌐 [Multi-Sensor] 多源知识感知阵列 (RSS & GitHub) 启动...")
    print("=" * 60)
    
    # 初始化核心引擎以挂载黑板
    engine = AGEngine()
    rss_sensor = RSSSensor(blackboard=engine.blackboard)
    gh_sensor = GitHubSensor(blackboard=engine.blackboard)
    
    # 静态抓取目标 (后续可提取到 config.py)
    rss_targets = [
        "https://news.ycombinator.com/rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    ]
    gh_targets = [
        ("hwchase17", "langchain"),
        ("google", "gemini-cookbook")
    ]
    
    # 抓取 RSS 源
    for url in rss_targets:
        try:
            await rss_sensor.ingest_to_blackboard(url)
        except Exception as e:
            print(f"⚠️ RSS 探测异常 ({url}): {e}")
            
        await asyncio.sleep(3)
        
    # 抓取 GitHub 源
    for owner, repo in gh_targets:
        try:
            await gh_sensor.ingest_to_blackboard(owner, repo)
        except Exception as e:
            print(f"⚠️ GitHub 探测异常 ({owner}/{repo}): {e}")
            
        await asyncio.sleep(3)
        
    print("✅ [Multi-Sensor] 周期探测完成。等待后台 LeftBrain 处理黑板事件。")

if __name__ == "__main__":
    asyncio.run(run_multi_sensors())
