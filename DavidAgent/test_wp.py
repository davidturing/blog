import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv(dotenv_path=project_root / ".env")

from brain.executor.wordpress_executor import WordPressExecutor
from brain.memory.blackboard import BrainBlackboard

async def main():
    print("🚀 Testing WordPress Executor...")
    blackboard = BrainBlackboard()
    motor = WordPressExecutor(blackboard)
    print(f"Target URL: {motor.wp_url}")
    print(f"Auth User: {motor.wp_username}")
    
    try:
        res = await motor._push_to_wordpress("Test Auto Publish", "This is a direct API push test.")
        print("✅ SUCCESS!")
        print(res)
    except Exception as e:
        print(f"❌ FAILED:")
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
