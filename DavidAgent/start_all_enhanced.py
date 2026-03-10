#!/usr/bin/env python3
"""
增强版 DavidAgent 启动脚本 - 带完整错误处理和日志记录
"""

import subprocess
import sys
import time
import os
import signal
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 配置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"davidagent_pipeline_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 加载环境变量
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def run_services():
    logger.info("=" * 60)
    logger.info("🚀 启动 DavidAgent 仿生双脑全量服务...")
    logger.info("=" * 60)

    # 定义要启动的服务
    services = [
        {"name": "Core Engine", "cmd": [sys.executable, "brain/app.py"]},
        {"name": "AG Worker", "cmd": [sys.executable, "ag_worker.py"]},
        {"name": "Dashboard", "cmd": [sys.executable, "-m", "streamlit", "run", "brain/dashboard.py"]}
    ]

    processes = []
    
    # 启动所有服务
    for service in services:
        logger.info(f"🔄 正在启动 {service['name']}...")
        try:
            process = subprocess.Popen(
                service["cmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy(),
                cwd=Path(__file__).parent
            )
            processes.append((service["name"], process))
            # 给一定缓冲时间，避免日志全部黏在一起
            time.sleep(2)
            logger.info(f"✅ {service['name']} 启动成功 (PID: {process.pid})")
        except Exception as e:
            logger.error(f"❌ {service['name']} 启动失败: {e}")
            continue
        
    if not processes:
        logger.error("❌ 所有服务启动失败！")
        return False
        
    logger.info("=" * 60)
    logger.info("✅ 所有服务启动命令已下发。")
    logger.info("   - 监控服务运行状态...")
    logger.info("=" * 60)

    def signal_handler(sig, frame):
        logger.info("\n🛑 收到终止信号，正在优雅关闭所有服务...")
        for name, p in processes:
            logger.info(f"关闭 {name} (PID: {p.pid})...")
            p.terminate()
            
        # 等待进程退出
        for name, p in processes:
            try:
                p.wait(timeout=5)
                logger.info(f"✅ {name} 已退出。")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ {name} 未能在一小段时间内退出，强制 kill。")
                p.kill()
        
        logger.info("👋 DavidAgent 服务已全部安全关闭。")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 持续运行并检查子进程状态
        start_time = time.time()
        max_runtime = 3600  # 最大运行时间1小时
        
        while True:
            # 检查是否超时
            if time.time() - start_time > max_runtime:
                logger.warning(f"⏰ 达到最大运行时间 {max_runtime} 秒，准备退出...")
                break
                
            all_finished = True
            for name, p in processes:
                if p.poll() is None:
                    all_finished = False
                else:
                    stdout, stderr = p.communicate()
                    if p.returncode != 0:
                        logger.error(f"❌ {name} 异常退出 (Return code: {p.returncode})")
                        if stderr:
                            logger.error(f"   stderr: {stderr.decode('utf-8', errors='ignore')}")
                    else:
                        logger.info(f"✅ {name} 正常完成")
                        if stdout:
                            logger.info(f"   stdout: {stdout.decode('utf-8', errors='ignore')[:500]}...")
            
            if all_finished:
                logger.info("✅ 所有服务已完成，pipeline执行成功！")
                return True
                
            time.sleep(10)
            
    except Exception as e:
        logger.error(f"发生异常: {e}")
        signal_handler(None, None)
        return False

if __name__ == "__main__":
    success = run_services()
    if success:
        logger.info("🎉 DavidAgent pipeline 执行成功！")
        sys.exit(0)
    else:
        logger.error("💥 DavidAgent pipeline 执行失败！")
        sys.exit(1)