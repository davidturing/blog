#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GitHub趋势感知器
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensors.github_trending_sensor import GitHubTrendingSensor

async def main():
    """测试函数"""
    print("🚀 测试GitHub趋势感知器...")
    sensor = GitHubTrendingSensor()
    await sensor.ingest_to_blackboard(limit=3, hours=48)

if __name__ == "__main__":
    asyncio.run(main())