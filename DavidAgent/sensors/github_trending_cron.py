#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending 定时任务脚本
用于定期采集最新的AI技术趋势并更新知识图谱
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from DavidAgent.sensors.github_trending_worker import GitHubTrendingWorker

async def main():
    """主函数：运行GitHub趋势感知器"""
    print("⏰ GitHub Trending 定时任务开始执行...")
    
    # 初始化GitHub趋势感知器
    worker = GitHubTrendingWorker()
    
    try:
        # 采集最新的AI资讯（过去24小时）
        await worker.collect_ai_trends(hours=24, limit=10)
        
        # 采集最新的Python项目（过去24小时）
        await worker.collect_python_trends(hours=24, limit=5)
        
        print("✅ GitHub Trending 定时任务执行完成！")
        
    except Exception as e:
        print(f"❌ GitHub Trending 定时任务执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查GITHUB_TOKEN环境变量
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️ 警告: 未设置GITHUB_TOKEN环境变量，API调用将受限")
        print("   请设置: export GITHUB_TOKEN=your_github_token")
    
    asyncio.run(main())