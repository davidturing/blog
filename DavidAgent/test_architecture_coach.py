#!/usr/bin/env python3
"""
测试架构教练分身
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "brain" / "sensors"))
sys.path.insert(0, str(Path(__file__).parent / "brain" / "coach"))

from architecture_coach import ArchitectureCoach


async def test_architecture_coach():
    """测试架构教练"""
    print("🧪 测试架构教练分身...")
    
    # 创建模拟的通道实例
    class MockGitHubWatcher:
        def search_new_tech(self, topics, days_back):
            return []
            
    class MockRSSGatherer:
        def fetch_new_articles(self, max_per_feed):
            return []
            
    class MockSocialSniffer:
        def sniff_reddit(self, subreddits, limit):
            return []
            
    class MockDocSpider:
        def crawl(self, start_url, max_depth):
            return []
            
    class MockIssueExplorer:
        def explore_issues(self, repo_names, label_filter):
            return []
    
    # 创建通道字典
    channels = {
        "GitHubWatcher": MockGitHubWatcher(),
        "RSSGatherer": MockRSSGatherer(), 
        "SocialSniffer": MockSocialSniffer(),
        "DocSpider": MockDocSpider(),
        "IssueExplorer": MockIssueExplorer()
    }
    
    # 创建架构教练
    coach = ArchitectureCoach()
    
    # 运行完整校验周期
    results = await coach.run_full_validation_cycle(channels)
    
    print("\n✅ 架构教练测试完成！")
    print(f"教练状态: {results['coach_status']}")
    print(f"分析通道数: {results['channels_analyzed']}")
    print(f"GitHub验证: {'✅ 成功' if results['github_verification']['upload_successful'] else '❌ 失败'}")
    
    # 显示校验规则示例
    print("\n📋 5大通道校验规则示例:")
    validation_lib = coach.validation_lib
    for channel_name, rules in list(validation_lib.items())[:2]:  # 显示前2个作为示例
        print(f"\n{channel_name}:")
        print(f"  校验函数: {', '.join(rules['validation_functions'][:2])}")
        print(f"  错误处理: {list(rules['error_handling'].keys())[0] if rules['error_handling'] else '无'}")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_architecture_coach())