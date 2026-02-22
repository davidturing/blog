#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Sensor Skill - 使用示例
"""

import asyncio
import os
from github_spider import GithubSpider

async def main():
    """主函数示例"""
    
    # 初始化GitHub感知器（自动从环境变量读取GITHUB_TOKEN）
    spider = GithubSpider()
    
    print("🚀 GitHub感知器技能演示")
    print("=" * 50)
    
    # 示例1: 获取每日技术趋势
    print("\n1. 获取今日Top 3技术趋势...")
    try:
        trending_repos = await spider.fetch_daily_trending(limit=3, hours=24, language="python")
        for i, repo in enumerate(trending_repos, 1):
            print(f"\n【趋势项目 #{i}】")
            print(f"   仓库: {repo['author']}/{repo['source_id'].replace('repo_', '')}")
            print(f"   URL: {repo['original_url']}")
            print(f"   时间: {repo['timestamp']}")
            # 只显示core_text的前200个字符
            preview = repo['core_text'][:200] + "..." if len(repo['core_text']) > 200 else repo['core_text']
            print(f"   预览: {preview}")
    except Exception as e:
        print(f"   ❌ 获取趋势失败: {e}")
    
    # 示例2: 监控特定用户的动态
    print("\n2. 监控行业大佬动态 (示例: torvalds)...")
    try:
        events = await spider.fetch_user_events("torvalds", limit=2)
        if events:
            print(f"   ✅ 获取到{len(events)}条动态")
            for event in events[:1]:  # 只显示第一条
                print(f"   类型: {event.get('type', 'N/A')}")
                print(f"   时间: {event.get('created_at', 'N/A')}")
                if 'repo' in event:
                    print(f"   仓库: {event['repo']['name']}")
        else:
            print("   ℹ️  暂无公开动态")
    except Exception as e:
        print(f"   ❌ 获取用户动态失败: {e}")
    
    print("\n" + "=" * 50)
    print("✅ GitHub感知器技能演示完成！")

if __name__ == "__main__":
    # 设置环境变量示例（实际使用时应通过.env文件或系统环境变量设置）
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  警告: 未设置GITHUB_TOKEN，API调用将受限")
        print("   请设置环境变量: export GITHUB_TOKEN=your_github_token")
    
    asyncio.run(main())