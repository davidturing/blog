#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 每日进化检视与自动发布系统主控脚本
"""

import os
import sys
import datetime
import subprocess
from pathlib import Path

# 项目配置
PROJECT_ROOT = Path("/Users/zhaoqinhuang/david_project")
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RELEASE_DIR = PROJECT_ROOT / "release"

def run_model_scheduler_monitor():
    """运行模型调度监控"""
    print("🔧 运行模型调度监控...")
    result = subprocess.run([
        "python3", str(SCRIPTS_DIR / "model_scheduler_monitor.py")
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 模型调度监控执行成功")
        return True
    else:
        print(f"❌ 模型调度监控执行失败: {result.stderr}")
        return False

def create_daily_release_file(date_str=None):
    """创建当日 release 文件（如果不存在）"""
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    release_file = RELEASE_DIR / f"release-{date_str}.md"
    
    if not release_file.exists():
        # 创建基础模板
        template_content = f"""# DavidAgent 进化日志｜{date_str}｜架构自动演进

## 版本信息
- **版本号**: V{date_str.replace('-', '')}.1
- **日期**: {date_str}
- **执行环境**: Mac mini M4 (本地)

## 架构改进内容

### 1. [待填写改进内容]

## 执行状态
- ⏳ 等待架构改进记录
- ⏳ WordPress 自动发布流程待执行
- ⏳ GitHub 同步待执行
"""
        with open(release_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ 创建了新的 release 文件: {release_file}")
        return True
    else:
        print(f"ℹ️  release 文件已存在: {release_file}")
        return True

def check_for_architecture_changes():
    """检查是否有架构改动需要记录"""
    # 这里可以集成 git diff 或其他变更检测机制
    # 目前先简单检查是否有新文件或修改
    print("🔍 检查架构改动...")
    
    # 检查 scripts 目录是否有新文件
    script_files = list(SCRIPTS_DIR.glob("*.py"))
    if script_files:
        print(f"发现 {len(script_files)} 个脚本文件")
    
    # 检查 config 目录
    config_files = list((PROJECT_ROOT / "config").glob("*"))
    if config_files:
        print(f"发现 {len(config_files)} 个配置文件")
    
    return True

def main():
    """主函数"""
    print("🚀 DavidAgent 每日进化检视与自动发布系统启动")
    print("=" * 60)
    
    # 获取日期参数
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 1. 运行模型调度监控
    if not run_model_scheduler_monitor():
        print("❌ 模型调度监控失败，终止执行")
        sys.exit(1)
    
    # 2. 创建当日 release 文件
    if not create_daily_release_file(date_str):
        print("❌ 创建 release 文件失败")
        sys.exit(1)
    
    # 3. 检查架构改动
    check_for_architecture_changes()
    
    # 4. 准备自动发布（实际发布由单独的定时任务触发）
    print("\n📋 系统状态:")
    print(f"   - Release 目录: {RELEASE_DIR}")
    print(f"   - 脚本目录: {SCRIPTS_DIR}")
    print(f"   - 配置文件: {PROJECT_ROOT / 'config' / 'models.json'}")
    
    print("\n✅ DavidAgent 每日进化系统初始化完成")
    print("💡 提示: 使用 auto_publish_evolution.py 脚本执行实际发布")

if __name__ == "__main__":
    main()