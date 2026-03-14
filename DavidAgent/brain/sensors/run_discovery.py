"""
DavidAgent 感知收割机总调度入口

统一协调五大感知通道，执行认知熵过滤，输出每日数字战利品报告。
"""

import asyncio
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from github_watcher import GitHubWatcher
from rss_gatherer import RSSGatherer
from social_sniffer import SocialSniffer
from doc_spider import DocSpider
from qa_miner import QAMiner
from cognitive_filter import CognitiveEntropyFilter


class DiscoveryOrchestrator:
    """感知收割机总调度器"""
    
    def __init__(self, config_path: str = "DavidAgent/brain/sensors/config.json"):
        """初始化总调度器
        
        Args:
            config_path: 配置文件路径
        """
        # 设置日志
        self._setup_logging()
        self.logger = logging.getLogger("DiscoveryOrchestrator")
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化各感知模块
        self.github_watcher = GitHubWatcher(self.config)
        self.rss_gatherer = RSSGatherer(self.config)
        self.social_sniffer = SocialSniffer(self.config)
        self.doc_spider = DocSpider(self.config)
        self.qa_miner = QAMiner(self.config)
        
        # 初始化认知熵过滤器
        self.cognitive_filter = CognitiveEntropyFilter(self.config)
        
        # 感知统计
        self.stats = {
            "github": 0,
            "rss": 0,
            "social": 0,
            "docs": 0,
            "qa": 0,
            "total_filtered": 0
        }
        
    def _setup_logging(self):
        """设置日志系统"""
        log_dir = Path("DavidAgent/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "discovery.log"),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"配置加载成功: {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            raise
            
    async def run_all_channels(self, force_fetch: bool = False) -> List[Dict[str, Any]]:
        """并发运行所有感知通道
        
        Args:
            force_fetch: 是否强制抓取（忽略缓存）
            
        Returns:
            所有感知结果列表
        """
        self.logger.info("🚀 启动五大感知通道...")
        
        tasks = [
            self._run_github_channel(),
            self._run_rss_channel(),
            self._run_social_channel(),
            self._run_docs_channel(),
            self._run_qa_channel()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并所有结果
        all_insights = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_insights.extend(result)
                # 更新统计
                channel_names = ["github", "rss", "social", "docs", "qa"]
                if i < len(channel_names):
                    self.stats[channel_names[i]] = len(result)
            elif isinstance(result, Exception):
                self.logger.error(f"感知通道异常: {result}")
                
        self.logger.info(f"📊 感知完成: GitHub {self.stats['github']} | RSS {self.stats['rss']} | Social {self.stats['social']} | Docs {self.stats['docs']} | QA {self.stats['qa']}")
        
        return all_insights
        
    async def _run_github_channel(self) -> List[Dict[str, Any]]:
        """运行 GitHub 通道"""
        try:
            return self.github_watcher.run_discovery()
        except Exception as e:
            self.logger.error(f"GitHub 通道失败: {e}")
            return []
            
    async def _run_rss_channel(self) -> List[Dict[str, Any]]:
        """运行 RSS 通道"""
        try:
            return await self.rss_gatherer.run_discovery()
        except Exception as e:
            self.logger.error(f"RSS 通道失败: {e}")
            return []
            
    async def _run_social_channel(self) -> List[Dict[str, Any]]:
        """运行社交通道"""
        try:
            return self.social_sniffer.run_discovery()
        except Exception as e:
            self.logger.error(f"Social 通道失败: {e}")
            return []
            
    async def _run_docs_channel(self) -> List[Dict[str, Any]]:
        """运行文档通道"""
        try:
            return await self.doc_spider.run_discovery()
        except Exception as e:
            self.logger.error(f"Docs 通道失败: {e}")
            return []
            
    async def _run_qa_channel(self) -> List[Dict[str, Any]]:
        """运行 QA 通道"""
        try:
            return self.qa_miner.run_discovery()
        except Exception as e:
            self.logger.error(f"QA 通道失败: {e}")
            return []
            
    def apply_cognitive_filter(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用认知熵过滤
        
        Args:
            insights: 所有洞察列表
            
        Returns:
            过滤后的高价值洞察列表
        """
        self.logger.info(f"🔍 开始认知熵过滤，共 {len(insights)} 项洞察...")
        
        filtered_insights = self.cognitive_filter.filter_content_batch(insights)
        self.stats["total_filtered"] = len(filtered_insights)
        
        self.logger.info(f"✅ 认知熵过滤完成，保留 {len(filtered_insights)} 项高价值洞察")
        return filtered_insights
        
    def save_to_memory(self, insights: List[Dict[str, Any]]):
        """保存洞察到记忆系统
        
        Args:
            insights: 洞察列表
        """
        if not insights:
            return
            
        # 保存到 episodic memory
        memory_dir = Path("DavidAgent/hippocampus/episodic")
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_file = memory_dir / f"discovery_{timestamp}.json"
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"💾 洞察已保存到记忆: {memory_file}")
        
    def save_to_reasoning_bank(self, insights: List[Dict[str, Any]]):
        """保存到 ReasoningBank
        
        Args:
            insights: 洞察列表
        """
        if not insights:
            return
            
        reasoning_bank_path = Path("DavidAgent/brain/reasoning_bank.jsonl")
        reasoning_bank_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(reasoning_bank_path, 'a', encoding='utf-8') as f:
            for insight in insights:
                f.write(json.dumps(insight, ensure_ascii=False) + '\n')
                
        self.logger.info(f"📚 已追加 {len(insights)} 条到 ReasoningBank")
        
    def generate_daily_report(self, insights: List[Dict[str, Any]]) -> str:
        """生成每日数字战利品报告
        
        Args:
            insights: 最终洞察列表
            
        Returns:
            报告文本
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# DavidAgent 每日数字战利品报告
**生成时间**: {timestamp}

## 📊 感知统计
- GitHub 仓库: {self.stats['github']} 项
- RSS 文章: {self.stats['rss']} 项
- 社交趋势: {self.stats['social']} 项
- 技术文档: {self.stats['docs']} 项
- QA 补丁: {self.stats['qa']} 项
- **总计**: {sum(self.stats.values()) - self.stats['total_filtered']} 项

## 🔍 认知熵过滤
- 过滤前: {sum(self.stats.values()) - self.stats['total_filtered']} 项
- 过滤后: {self.stats['total_filtered']} 项
- 信息增益阈值: {self.config.get('cognitive_threshold', 0.65)}

## 💎 高价值发现
"""
        
        # 添加前5个高价值洞察
        for i, insight in enumerate(insights[:5], 1):
            source = insight.get('source', 'unknown')
            title = insight.get('title', '无标题')
            info_gain = insight.get('information_gain', 0)
            
            report += f"\n### {i}. {title}\n"
            report += f"- 来源: {source}\n"
            report += f"- 信息增益: {info_gain:.3f}\n"
            
            content = insight.get('content', '')[:200]
            report += f"- 内容摘要: {content}...\n"
            
        report += f"""
## 📈 资源使用
- 内存限制: {self.config.get('memory_limit_mb', 2048)} MB
- 带宽限制: {self.config.get('bandwidth_limit_mb', 100)} MB
- 执行窗口: {self.config.get('execution_window', {}).get('start_hour', 1)}:00 - {self.config.get('execution_window', {}).get('end_hour', 6)}:00

---
*本报告由 DavidAgent 感知收割机自动生成*
"""
        
        return report
        
    async def run_full_discovery(self, force_fetch: bool = False, dry_run: bool = False) -> str:
        """运行完整的感知发现流程
        
        Args:
            force_fetch: 是否强制抓取
            dry_run: 是否仅模拟运行
            
        Returns:
            每日报告
        """
        start_time = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info("🚀 DavidAgent 感知收割机启动")
        self.logger.info("=" * 60)
        
        try:
            # 1. 运行所有感知通道
            all_insights = await self.run_all_channels(force_fetch)
            
            if not all_insights:
                self.logger.warning("未获取到任何感知内容")
                return "未获取到任何感知内容"
                
            # 2. 应用认知熵过滤
            filtered_insights = self.apply_cognitive_filter(all_insights)
            
            if dry_run:
                self.logger.info("🔍 [DRY-RUN] 模拟运行，不保存数据")
            else:
                # 3. 保存到记忆系统
                self.save_to_memory(filtered_insights)
                
                # 4. 保存到 ReasoningBank
                self.save_to_reasoning_bank(filtered_insights)
                
            # 5. 生成每日报告
            report = self.generate_daily_report(filtered_insights)
            
            # 保存报告
            report_dir = Path("DavidAgent/reports")
            report_dir.mkdir(parents=True, exist_ok=True)
            report_file = report_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                
            self.logger.info(f"📄 每日报告已生成: {report_file}")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.info("=" * 60)
            self.logger.info(f"✅ 感知收割完成，耗时 {elapsed:.2f} 秒")
            self.logger.info("=" * 60)
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ 感知收割失败: {e}", exc_info=True)
            raise


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DavidAgent 感知收割机")
    parser.add_argument("--force_fetch", action="store_true", help="强制抓取，忽略缓存")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不保存数据")
    
    args = parser.parse_args()
    
    # 创建总调度器
    orchestrator = DiscoveryOrchestrator()
    
    # 运行完整流程
    report = await orchestrator.run_full_discovery(
        force_fetch=args.force_fetch,
        dry_run=args.dry_run
    )
    
    # 输出报告
    print(report)


if __name__ == "__main__":
    asyncio.run(main())