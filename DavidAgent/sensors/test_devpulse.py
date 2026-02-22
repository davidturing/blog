#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevPulse-Sensor 测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensors.devpulse_sensor import DevPulseSensor

async def main():
    """主测试函数"""
    print("🚀 测试DevPulse-Sensor (开发者脉搏感知器)...")
    print("=" * 60)
    
    # 初始化传感器
    sensor = DevPulseSensor()
    
    try:
        # 测试Hacker News智能嗅探
        print("\n1. 测试Hacker News智能嗅探...")
        hn_articles = await sensor.fetch_hacker_news_tech_posts(limit=2)
        if hn_articles:
            print(f"✅ 成功获取 {len(hn_articles)} 个HN技术帖子")
            for i, article in enumerate(hn_articles[:1], 1):
                print(f"   📰 标题: {article['core_text'][:100]}...")
                print(f"   🔗 URL: {article['original_url']}")
        else:
            print("   ℹ️  暂无符合条件的HN技术帖子")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    try:
        # 测试RSS订阅源
        print("\n2. 测试RSS订阅源...")
        rss_articles = await sensor.fetch_rss_tech_articles(limit_per_feed=1)
        if rss_articles:
            print(f"✅ 成功获取 {len(rss_articles)} 篇RSS技术文章")
            for i, article in enumerate(rss_articles[:1], 1):
                print(f"   📰 标题: {article['core_text'][:100]}...")
                print(f"   🔗 URL: {article['original_url']}")
        else:
            print("   ℹ️  暂无符合条件的RSS技术文章")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ DevPulse-Sensor 测试完成！")

if __name__ == "__main__":
    asyncio.run(main())