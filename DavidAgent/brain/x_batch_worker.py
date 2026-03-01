
import asyncio
import random
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.sensors.x_spider import XSpider
from brain.memory.blackboard import get_blackboard
from brain.memory.episodic_memory import get_episodic_memory_db

async def run_batch_crawl():
    print(f"🚀 [批量采集] 后台进程启动 (PID: {os.getpid()})")
    
    db = get_episodic_memory_db()
    blackboard = get_blackboard()
    spider = XSpider(blackboard=blackboard)
    
    task_name = "x_batch_crawl"
    
    # 1. 标记运行中
    db.set_task_status(task_name, "running", progress="正在初始化账号列表...")
    
    try:
        # 2. 读取账号库
        status_info = db.get_task_status(task_name)
        with open(spider.config.x_accounts_json, 'r') as f:
            all_accounts = json.load(f)
            handles = [a['handle'] for a in all_accounts if 'handle' in a]
        
        # 3. 随机选择 10 个 (如果总数不足 10 则全选)
        target_count = min(10, len(handles))
        selected_handles = random.sample(handles, target_count)
        print(f"🎯 [批量采集] 本次采样对象: {selected_handles}")
        
        # 获取最新的 UI 配置(保留延迟设置)
        config_dict = {}
        try:
            curr_raw = status_info.get('config')
            if curr_raw:
                config_dict = json.loads(curr_raw)
                if not isinstance(config_dict, dict):
                    config_dict = {}
        except:
            pass
            
        config_dict['targets'] = selected_handles
        
        db.set_task_status(task_name, "running", 
                          progress=f"已选定 {target_count} 个采样账号",
                          config=json.dumps(config_dict, ensure_ascii=False))
        
        # 4. 循环采集
        for i, handle in enumerate(selected_handles):
            # 检查是否要求停止
            status_info = db.get_task_status(task_name)
            if status_info['status'] == 'stopping':
                print(f"🛑 [批量采集] 收到停止指令，安全退出...")
                break
            
            progress_msg = f"正在采集第 {i+1}/{target_count} 个账号: @{handle}"
            db.set_task_status(task_name, "running", progress=progress_msg)
            
            # 执行采集
            await spider.ingest_to_blackboard(handle, count=1)
            
            # 采集后随机休眠 (模拟阅读)
            # 热读取最新设置
            try:
                curr_config = json.loads(status_info.get('config') or "{}")
                if not isinstance(curr_config, dict):
                    curr_config = {}
            except:
                curr_config = {}
                
            req_min = curr_config.get('req_min_sleep', 5)
            req_max = curr_config.get('req_max_sleep', 15)
            account_min = curr_config.get('account_min_sleep', 30)
            account_max = curr_config.get('account_max_sleep', 120)

            jitter_post = random.uniform(req_min, req_max)
            print(f"⏳ [批量采集] @{handle} 采集完成，单次请求后休眠 {jitter_post:.1f}s...")
            await asyncio.sleep(jitter_post)
            
            if i < target_count - 1:
                jitter_account = random.uniform(account_min, account_max)
                print(f"⏳ [批量采集] 准备切换账号，模拟步态休眠 {jitter_account:.1f}s...")
                # 分段休眠以便能实时响应停止指令
                for _ in range(int(jitter_account)):
                    await asyncio.sleep(1)
                    if db.get_task_status(task_name)['status'] == 'stopping':
                        break
            else:
                print(f"✅ [批量采集] 完成本次采样任务。")
        
    except Exception as e:
        print(f"❌ [批量采集] 运行异常: {e}")
    finally:
        # 5. 标记结束
        db.set_task_status(task_name, "idle", progress="任务已完成或手动停止")
        print(f"👋 [批量采集] 进程结束。")

if __name__ == "__main__":
    asyncio.run(run_batch_crawl())
