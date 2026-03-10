import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv(dotenv_path=project_root / ".env")

from brain.app import AGEngine
from brain.memory.episodic_memory import get_episodic_memory_db

async def run_local_e2e():
    db = get_episodic_memory_db()
    
    # 抽取刚才发进去的原始数据
    tweet_id = "x_2024885969250394191"
    cursor = db.conn.cursor()
    cursor.execute("SELECT raw_text FROM raw_signals WHERE signal_id=?", (tweet_id,))
    row = cursor.fetchone()
    
    if not row:
        print("未找到该推文数据。")
        return
        
    raw_text = row[0]
    print("="*50)
    print("🚀 [Foreground Test] Starting AGEngine synchronously for target X URL...")
    print("="*50)
    
    # 清理该信号的 PageIndex 历史残留，确保干净环境
    import glob
    pageindex_dir = str(project_root / "skills" / "self-learning-agent" / "pageindex" / "knowledge")
    safe_id = "".join(c if c.isalnum() else "_" for c in ("test_" + tweet_id))
    stale = glob.glob(os.path.join(pageindex_dir, f"{safe_id}_*.md"))
    if stale:
        for f in stale:
            os.remove(f)
        print(f"🧹 [清理] 已移除 {len(stale)} 个历史图谱残留文件")
    
    engine = AGEngine()
    
    # 覆写 blackboard 行为以提供阻塞式控制
    async def log_state(snapshot):
        status = snapshot.get("workflow_status")
        print(f"🚥 [State Update]: {status}")
        
    engine.blackboard.subscribe_global(log_state)
    
    # 手动触发 + 追踪起点
    engine.blackboard.append_trace('PERCEPTION', f'感知到信号: {tweet_id}', {
        'raw_text_preview': raw_text[:200]
    })
    engine.blackboard.update('topic_id', "test_" + tweet_id, 'SYSTEM_WORKER')
    engine.blackboard.update('raw_source', raw_text, 'SYSTEM_WORKER')
    
    # 阻塞等待完成
    try:
        await asyncio.wait_for(engine.wait_for_completion(timeout_seconds=300), timeout=305)
    except Exception as e:
        print(f"❌ Timed out or exception: {e}")
        
    final_status = await engine.blackboard.read('workflow_status')
    print(f"🏁 Final Status: {final_status}")

if __name__ == "__main__":
    asyncio.run(run_local_e2e())
