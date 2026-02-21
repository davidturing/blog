import subprocess
import sys
import time
import os
import signal
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def run_services():
    print("=" * 60)
    print("🚀 启动 DavidAgent 仿生双脑全量服务...")
    print("=" * 60)

    # 定义要启动的服务
    services = [
        {"name": "Core Engine", "cmd": [sys.executable, "brain/app.py"]},
        {"name": "AG Worker", "cmd": [sys.executable, "ag_worker.py"]},
        {"name": "Dashboard", "cmd": [sys.executable, "-m", "streamlit", "run", "brain/dashboard.py"]}
    ]

    processes = []
    
    # 启动所有服务
    for service in services:
        print(f"🔄 正在启动 {service['name']}...")
        process = subprocess.Popen(
            service["cmd"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=os.environ.copy()
        )
        processes.append((service["name"], process))
        # 给一定缓冲时间，避免日志全部黏在一起
        time.sleep(2)
        
    print("=" * 60)
    print("✅ 所有服务启动命令已下发。")
    print("   - 按下 Ctrl+C 可以停止所有服务。")
    print("=" * 60)

    def signal_handler(sig, frame):
        print("\n🛑 收到终止信号，正在优雅关闭所有服务...")
        for name, p in processes:
            print(f"关闭 {name} (PID: {p.pid})...")
            p.terminate()
            
        # 等待进程退出
        for name, p in processes:
            try:
                p.wait(timeout=5)
                print(f"✅ {name} 已退出。")
            except subprocess.TimeoutExpired:
                print(f"⚠️ {name} 未能在一小段时间内退出，强制 kill。")
                p.kill()
        
        print("👋 DavidAgent 服务已全部安全关闭。")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # 持续运行并检查子进程状态
        while True:
            for name, p in processes:
                if p.poll() is not None:
                    print(f"❌ {name} 异常退出 (Return code: {p.returncode})。")
                    # 如果任何服务挂了，根据需求可以决定是否杀掉其他服务，这里选择提示
            time.sleep(5)
    except Exception as e:
        print(f"发生异常: {e}")
        signal_handler(None, None)

if __name__ == "__main__":
    run_services()
