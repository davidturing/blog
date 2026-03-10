import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 强制加载 .env 
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)
print(f"✅ Loaded .env from {env_path}. GEMINI_API_KEY exists: {'GEMINI_API_KEY' in os.environ}")

from brain.app import AGEngine

async def run_worker():
    print("=" * 50)
    print("⚙️ DavidAgent 后台驻留守护进程 (ag_worker) 启动中...")
    print("=" * 50)
    
    engine = AGEngine()
    print("✅ 引擎与神经黑板已挂载，处于监听模式...")
    
    # 保持主循环活跃，监听黑板事件
    try:
        while True:
            try:
                cursor = engine.blackboard.episodic_memory.cursor
                cursor.execute("SELECT task_id, raw_source FROM trace_logs WHERE workflow_status = 'START' ORDER BY timestamp ASC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    task_id, raw_source = row
                    print(f"📦 [ag_worker] 发现新推文信号 {task_id}，开始注入图谱提取引擎...")
                    cursor.execute("UPDATE trace_logs SET workflow_status = 'INGESTING' WHERE task_id = ?", (task_id,))
                    engine.blackboard.episodic_memory.conn.commit()
                    
                    # 注入黑板触发 LeftBrainAnalyzer 
                    engine.blackboard.update('topic_id', task_id, 'SYSTEM_WORKER')
                    engine.blackboard.update('raw_source', raw_source, 'SYSTEM_WORKER')
            except Exception as e:
                print(f"⚠️ [ag_worker] 轮询异常: {e}")
                
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("🛑 收到终止信号，ag_worker 退出。")

if __name__ == "__main__":
    asyncio.run(run_worker())
