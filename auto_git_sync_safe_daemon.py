#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 安全 Git 自动同步守护进程
【严格遵守安全协议】
1. 强制屏蔽密钥、数据库、环境配置。
2. 后台静默运行，文件变动自动提交并推送到私有仓库。
3. 纯标准库实现，无三方依赖。
"""

import os
import time
import subprocess
from datetime import datetime

# ================================
# 配置区
# ================================
PROJECT_ROOT = "/Users/zhaoqinhuang/david_project"
SYNC_INTERVAL = 60  # 每 60 秒检查一次变动

# 允许自动添加的安全文件扩展名白名单（严格限制）
SAFE_EXTENSIONS = {
    ".py", ".json", ".md", ".txt", ".csv", ".html", ".sh"
}

# ================================

def run_cmd(cmd):
    """执行 Shell 命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, cwd=PROJECT_ROOT, shell=True, 
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def get_changed_files():
    """获取所有已修改和新增的文件（跳过 gitignore 的内容）"""
    success, output = run_cmd("git ls-files --modified --others --exclude-standard")
    if success and output.strip():
        return [f.strip() for f in output.strip().split('\n') if f.strip()]
    return []

def is_safe_file(filepath):
    """双重安全校验：扩展名白名单 + 敏感词黑名单"""
    # 1. 扩展名校验
    ext = os.path.splitext(filepath)[1].lower()
    # 特别允许 .gitignore 本身
    if ext not in SAFE_EXTENSIONS and not filepath.endswith('.gitignore'):
        return False
    
    # 2. 危险关键词硬编码拦截（最后一道防线）
    lower_path = filepath.lower()
    
    # 直接毙掉危险文件后缀或路径
    if lower_path.endswith('.env') or lower_path.endswith('.key') or "credentials" in lower_path:
        return False
    
    # 毙掉本地数据库扩展名
    if lower_path.endswith('.db') or lower_path.endswith('.sqlite') or lower_path.endswith('.lancedb'):
        return False

    return True

def git_sync():
    """执行完整的同步流程"""
    changed_files = get_changed_files()
    if not changed_files:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    added_files = []
    for f in changed_files:
        if is_safe_file(f):
            run_cmd(f'git add "{f}"')
            added_files.append(f)
            
    if not added_files:
        # print(f"[{timestamp}] 变动文件被拦截策略屏蔽，无安全内容可同步。")
        return
        
    print(f"\n[{timestamp}] 检测到 {len(added_files)} 个安全变动文件，开始同步...")
    
    # 提交
    commit_msg = f"Auto-sync (Safe): DavidAgent backup {timestamp}"
    success, output = run_cmd(f'git commit -m "{commit_msg}"')
    
    if success:
        # 推送
        push_success, push_output = run_cmd("git push origin main")
        if push_success:
            print(f"[{timestamp}] ✅ 同步成功并已推送到私有仓库。")
        else:
            print(f"[{timestamp}] ⚠️ 推送失败 (可能是网络或远端分支问题): {push_output}")
    else:
        print(f"[{timestamp}] ⚠️ 提交失败: {output}")

def main():
    print("===================================================")
    print("🛡️ DavidAgent 安全 Git 同步守护进程启动 🛡️")
    print(f"📂 监控目录: {PROJECT_ROOT}")
    print("⚠️  强制要求：请务必确认远程仓库设置为【私有仓库】！")
    print(f"⏳ 轮询间隔: {SYNC_INTERVAL} 秒")
    print("🔒 仅同步白名单后缀: .py, .json, .md, .txt, .csv, .html, .sh")
    print("===================================================\n")
    
    os.chdir(PROJECT_ROOT)
    
    success, output = run_cmd("git remote -v")
    if not success or not output.strip():
        print("❌ 致命错误：当前目录未配置 Git 远程仓库！请先执行 git remote add ...")
        return

    print("✅ 检测到远程仓库配置，进入静默监听模式...\n")

    while True:
        try:
            git_sync()
            time.sleep(SYNC_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛑 守护进程已手动停止。")
            break
        except Exception as e:
            print(f"❌ 发生异常: {e}")
            time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
