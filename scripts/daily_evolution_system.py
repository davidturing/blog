#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 每日进化检视与自动发布系统主控脚本
整合所有组件，确保规则严格执行
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path("/Users/zhaoqinhuang/david_project")
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

def run_model_scheduler_monitor():
    """运行模型调度监控"""
    print("🔄 运行模型调度监控...")
    result = subprocess.run([
        "python3", str(SCRIPTS_DIR / "model_scheduler_monitor.py")
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 模型调度监控执行成功")
        return True
    else:
        print(f"❌ 模型调度监控执行失败: {result.stderr}")
        return False

def create_daily_release_template(date_str=None):
    """创建当日 release 模板（如果不存在）"""
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    release_file = PROJECT_ROOT / "release" / f"release-{date_str}.md"
    
    if not release_file.exists():
        template_content = f"""# DavidAgent 进化日志｜{date_str}｜架构自动演进

## 版本信息
- **版本号**: V{date_str.replace('-', '')}.1
- **日期**: {date_str}
- **执行环境**: Mac mini M4 (本地)

## 架构改进内容

### [待填写改进内容]

## 执行状态
- ⏳ 等待架构改进记录

## 下一步计划
- [待填写下一步计划]
"""
        with open(release_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"✅ 创建了当日 release 模板: {release_file}")
    else:
        print(f"📄 当日 release 文件已存在: {release_file}")

def run_auto_publish_if_ready(date_str=None):
    """如果 release 文件已完成，自动发布"""
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    release_file = PROJECT_ROOT / "release" / f"release-{date_str}.md"
    
    if not release_file.exists():
        print(f"⚠️  {date_str} 的 release 文件不存在，跳过发布")
        return False
    
    # 检查是否已完成（包含实际内容，不只是模板）
    with open(release_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "[待填写改进内容]" in content:
        print(f"⚠️  {date_str} 的 release 文件尚未完成，跳过发布")
        return False
    
    # 检查是否已经发布过
    publish_log = PROJECT_ROOT / "logs" / f"publish_{date_str}.log"
    if publish_log.exists():
        print(f"✅ {date_str} 的 release 文件已经发布过，跳过重复发布")
        return True
    
    print(f"🚀 准备发布 {date_str} 的进化日志...")
    
    # 这里应该调用实际的发布脚本
    # 由于 WordPress 凭据和 GitHub 配置需要额外设置
    # 目前先记录发布日志
    
    with open(publish_log, 'w') as f:
        f.write(f"Published on {datetime.datetime.now().isoformat()}\n")
    
    print(f"✅ 模拟发布完成，日志记录: {publish_log}")
    return True

def main():
    """主函数"""
    print("=== DavidAgent 每日进化检视与自动发布系统 ===")
    
    # 获取日期参数
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 1. 运行模型调度监控（确保规则严格执行）
    if not run_model_scheduler_monitor():
        print("❌ 模型调度监控失败，系统无法继续")
        sys.exit(1)
    
    # 2. 创建当日 release 模板
    create_daily_release_template(date_str)
    
    # 3. 尝试自动发布（如果已完成）
    run_auto_publish_if_ready(date_str)
    
    print("=== 系统检查完成 ===")

if __name__ == "__main__":
    main()