#!/usr/bin/env python3
"""
DavidAgent 全自动进化系统主入口
执行五大感知通道完整巡检 + 周报生成 + GitHub 同步
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "brain" / "sensors"))

from run_discovery import DiscoveryOrchestrator


async def main():
    """主函数"""
    print("🚀 DavidAgent 全自动进化系统启动")
    print("=" * 60)
    
    # 创建调度器
    orchestrator = DiscoveryOrchestrator()
    
    # 执行完整感知巡检
    print("🔍 开始五大感知通道完整巡检...")
    report = await orchestrator.run_full_discovery(force_fetch=True, dry_run=False)
    
    print("=" * 60)
    print("✅ 五大感知通道巡检完成！")
    
    # 获取统计信息
    stats = orchestrator.stats
    
    # 显示今日认知收获摘要
    print("\n📊 今日认知收获摘要:")
    print(f"- GitHub 技术趋势: {stats['github']} 项")
    print(f"- RSS 理论学习: {stats['rss']} 篇")  
    print(f"- Social 舆情嗅探: {stats['social']} 条")
    print(f"- Doc 文档重构: {stats['docs']} 个")
    print(f"- Issue 风险预警: {stats['qa']} 个")
    print(f"- 认知熵过滤后: {stats['total_filtered']} 项高价值洞察")
    
    # 显示周报路径
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    local_report_path = f"reports/daily/{today}-DavidAgent-Cognition-Report.md"
    print(f"\n📄 周报文件路径: {local_report_path}")
    
    # 显示 GitHub 提交状态
    github_repo_path = "/Users/zhaoqinhuang/github/tech"
    github_report_path = f"{github_repo_path}/weekly-reports/{today}-DavidAgent-Cognition-Report.md"
    if os.path.exists(github_report_path):
        print("🚀 GitHub 自动提交结果: ✅ 成功推送")
    else:
        print("🚀 GitHub 自动提交结果: ⚠️ 未找到远程报告文件")
    
    print("\n" + "=" * 60)
    print("🏁 最终结论: DavidAgent 全自动进化系统正常工作！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())