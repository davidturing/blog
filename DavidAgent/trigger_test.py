import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv(dotenv_path=project_root / ".env")

from brain.sensors.x_spider import XSpider
from brain.memory.blackboard import BrainBlackboard
from brain.memory.episodic_memory import get_episodic_memory_db

async def trigger():
    db = get_episodic_memory_db()
    bb = BrainBlackboard()  # Blackboard handles DB internally
    spider = XSpider(blackboard=bb)
    
    tweet_id = "2024885969250394191"
    print(f"🚀 Pushing Tweet {tweet_id} into the Pipeline...")
    
    await spider.ingest_to_blackboard(handle="", tweet_ids=[tweet_id])
    print("✅ Done pushing to Blackboard. The ag_worker daemon will pick it up automatically!")

if __name__ == "__main__":
    asyncio.run(trigger())
