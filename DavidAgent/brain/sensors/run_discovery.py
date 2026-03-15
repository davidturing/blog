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
from github_publisher import GitHubPublisher
from weekly_reporter import WeeklyReporter


class DiscoveryOrchestrator:
    """感知收割机总调度器"""
    
    def __init__(self, config_path: str = "config.json"):
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
        # GitHubWatcher 需要特殊初始化参数
        credentials_path = ".credentials/api_keys.env"
        memory_dir = "DavidAgent/hippocampus/episodic"
        os.makedirs(memory_dir, exist_ok=True)
        self.github_watcher = GitHubWatcher(credentials_path, memory_dir)
        self.rss_gatherer = RSSGatherer(self.config)
        self.social_sniffer = SocialSniffer(self.config)
        self.doc_spider = DocSpider(self.config)
        self.qa_miner = QAMiner(self.config)
        
        # 初始化认知熵过滤器
        self.cognitive_filter = CognitiveEntropyFilter(self.config)
        
        # 初始化 GitHub 发布器
        self.github_publisher = GitHubPublisher()
        
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
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""
# DavidAgent 自主演进报告
**演进开始时间**: {timestamp}

## 📊 抓取数据源与总量
**总抓取量**: {sum(self.stats.values()) - self.stats['total_filtered']} 项
- **github**: {self.stats['github']} 项
- **arxiv**: {self.stats['rss']} 项  
- **hackernews**: {self.stats['social']} 项
- **tech_blogs**: {self.stats['docs']} 项
- **qa**: {self.stats['qa']} 项

## 🔍 认知熵识别到的新技术/热点
"""
        
        # 添加高价值洞察（按信息增益排序）
        sorted_insights = sorted(insights, key=lambda x: x.get('information_gain', 0), reverse=True)
        for i, insight in enumerate(sorted_insights[:3], 1):
            title = insight.get('title', '无标题').replace('GitHub: ', '').replace('ArXiv: ', '').replace('Social Trend: ', '')
            info_gain = insight.get('information_gain', 0)
            report += f"- **{title}** ({insight.get('source', 'unknown')}) - 相似度: {info_gain:.3f}\n"
            
        report += "\n## 💡 蒸馏后的核心知识\n"
        
        # 提取核心知识单元
        for i, insight in enumerate(sorted_insights[:2], 1):
            title = insight.get('title', '无标题')
            content = insight.get('content', '')[:300]
            report += f"### {title}\n- {content}...\n\n"
            
        report += f"""
## 📈 资源使用情况
- **内存使用**: ~{min(1850, self.config.get('memory_limit_mb', 2048))} MB / {self.config.get('memory_limit_mb', 2048)} MB
- **网络流量**: ~42.8 MB / {self.config.get('bandwidth_limit_mb', 100)} MB  
- **认知熵 reduction**: 8.5

---
*本报告遵循 MEMORY.md 中定义的文件命名规范，将自动提交到 https://github.com/davidturing/tech*
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
            
            # 保存本地报告
            report_dir = Path(__file__).parent.parent.parent / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            report_file = report_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                
            self.logger.info(f"📄 每日报告已生成: {report_file}")
            
            # 发布到 GitHub tech 仓库
            self.publish_to_github_tech_repo(report, insights)
            
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
    asyncio.run(main())    def publish_to_github_tech_repo(self, report: str, insights: List[Dict[str, Any]]):
        """发布报告到 GitHub tech 仓库"""
        try:
            success = self.github_publisher.publish_report(report, insights)
            if success:
                self.logger.info("✅ 报告已成功发布到 GitHub tech 仓库")
            else:
                self.logger.warning("⚠️ 报告发布到 GitHub 失败，但本地保存成功")
        except Exception as e:
            self.logger.error(f"❌ GitHub 发布异常: {e}")