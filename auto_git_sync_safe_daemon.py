#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 安全 Git 自动同步守护进程
【完全依照规则实现后台、白名单、黑名单拦截与自动同步】
"""

import os
import time
import subprocess
import fnmatch
from datetime import datetime

PROJECT_ROOT = "/Users/zhaoqinhuang/david_project"
SYNC_INTERVAL = 60

# ================================
# 4. 白名单扩展名和文件名
# ================================
WHITELIST_EXTS = {
    ".py", ".js", ".ts", ".html", ".css", ".scss", ".json", ".yml", ".yaml",
    ".toml", ".ini", ".sh", ".bash", ".bat", ".cmd", ".go", ".java", ".kt",
    ".rb", ".php", ".cpp", ".c", ".h", ".swift", ".vue", ".rs", ".lua",
    ".md", ".txt", ".csv",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp"
}

WHITELIST_FILES = {
    ".gitignore", "license", "readme", "dockerfile", "makefile"
}

# ================================
# 5. 黑名单扩展名、前缀/后缀、文件夹
# ================================
BLACKLIST_PATTERNS = [
    ".env", "*.key", "*key*.json", "credentials*", ".secrets",
    "*.db", "*.sqlite", "*.lancedb", "*.chroma", "*.wal", "*.shm",
    "__pycache__/*", ".cache/*", "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dylib", "*.exe",
    "*.log", "*.zip", "*.tar.gz", "*.rar", "*.7z",
    "temp/*", "*.tmp", "*.bak"
]

def run_cmd(cmd):
    """执行 Shell 命令，返回是否成功与输出"""
    try:
        res = subprocess.run(
            cmd, cwd=PROJECT_ROOT, shell=True, 
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return True, res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def get_modified_files():
    """检测本地改动，不论 tracked 还是 untracked (忽略 .gitignore 剔除的)"""
    success, out = run_cmd("git status --porcelain")
    if success and out:
        return True
    return False

def is_file_safe(filepath):
    """
    Python 级别双重保险判断：
    1. 必须不在黑名单
    2. 必须在白名单扩展名或白名单文件名内
    """
    basename = os.path.basename(filepath)
    ext = os.path.splitext(basename)[1].lower()
    
    # --- 1. 黑名单拦截 (绝对不上传) ---
    for pattern in BLACKLIST_PATTERNS:
        if fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(basename, pattern):
            return False

    # --- 2. 白名单放行 (允许上传) ---
    if ext in WHITELIST_EXTS:
        return True
        
    base_lower = basename.lower()
    for wf in WHITELIST_FILES:
        if wf in base_lower:
            return True
            
    return False

def check_and_filter_safety():
    """
    双重保险：虽然用户要求执行 git add .，
    但为防止 .gitignore 配置失误或漏加，
    在 commit 前再次扫描暂存区，如果发现非白名单或黑名单文件，直接从暂存区剔除。
    """
    success, out = run_cmd("git diff --cached --name-only")
    if not success or not out:
        return False
        
    staged_files = out.split('\n')
    has_unsafe = False
    
    for f in staged_files:
        if not f: continue
        if not is_file_safe(f):
            print(f"[拦截] 发现黑名单或非白名单文件，已自动从暂存区剔除: {f}")
            run_cmd(f'git reset HEAD "{f}"')
            has_unsafe = True
            
    return has_unsafe

def git_sync():
    """每分钟扫描文件变化并执行安全的同步流"""
    
    # 3. 同步策略: 有新增/修改/删除 → 立即自动提交
    if not get_modified_files():
        return # 无变化则静默等待
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 步骤1: 依照指令执行 git add .
    run_cmd("git add .")
    
    # 步骤1.5: [独家安全加固] 确保暂存区没有违规文件
    check_and_filter_safety()
    
    # 二次确认，剔除后如果暂存区空了，就跳过 commit
    success, cached_out = run_cmd("git diff --cached --name-only")
    if not success or not cached_out.strip():
        # print(f"[{timestamp}] 变动文件全部被安全拦截，无合法文件需要提交。")
        return
        
    print(f"\n[{timestamp}] 检测到合法文件变化，开始同步流程...")
    
    # 步骤2: git commit
    commit_msg = f"Auto-sync DavidAgent {timestamp}"
    success, commit_out = run_cmd(f'git commit -m "{commit_msg}"')
    
    if success:
        # 步骤3: git push
        push_success, push_out = run_cmd("git push work main")
        if push_success:
            print(f"[{timestamp}] ✅ 同步成功：已安全推送到 work main。")
        else:
            print(f"[{timestamp}] ⚠️ 推送失败 (网络或权限异常): {push_out}")
    else:
        print(f"[{timestamp}] ⚠️ 提交异常: {commit_out}")

def main():
    print("=========================================================")
    print("🛡️ DavidAgent 终极安全 Git 同步守护进程启动 🛡️")
    print(f"📂 监控目录: {PROJECT_ROOT}")
    print(f"⏳ 轮询间隔: {SYNC_INTERVAL} 秒")
    print("⚠️  已载入双重安全过滤：全白名单制 + 黑名单拦截，万无一失。")
    print("=========================================================\n")
    
    os.chdir(PROJECT_ROOT)
    
    while True:
        try:
            git_sync()
            time.sleep(SYNC_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛑 进程已停止。")
            break
        except Exception as e:
            print(f"❌ 运行异常: {e}")
            time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
