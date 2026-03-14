"""
科技达人数字分身 - 世界感知自主演进主入口

专门负责「科技达人」分身的世界感知任务，
严格按照凌晨 01:00 执行，并输出到指定 GitHub 路径。
"""

import asyncio
import logging
from datetime import datetime, time
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensors.external_watcher import ExternalWatcher
from sensors.tech_blogger_output import TechBloggerOutput


class TechBloggerWatcher:
    """科技达人世界感知协调器"""
    
    def __init__(self):
        self.logger = logging.getLogger("TechBloggerWatcher")
        self.watcher = ExternalWatcher()
        self.output_handler = TechBloggerOutput()
        
    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """执行完整的演进周期"""
        start_time = datetime.now().isoformat()
        self.logger.info(f"🚀 科技达人世界感知演进开始: {start_time}")
        
        try:
            # 执行世界感知
            perception_result = await self.watcher.run_full_cycle()
            
            # 构建演进数据
            evolution_data = {
                "start_time": start_time,
                "sources": {
                    "github": 0,  # 这些会在实际实现中填充
                    "rss": 0,
                    "social": 0,
                    "docs": 0,
                    "qa": 0
                },
                "new_technologies": [],  # 认知熵识别的新技术
                "distilled_knowledge": [],  # 蒸馏后的核心知识
                "validation_results": {
                    "validated_skills": perception_result.get("validated_skills", 0),
                    "failed_validations": perception_result.get("reasoning_entries", 0)
                },
                "storage_stats": {
                    "skillbank_entries": perception_result.get("skillbank_entries", 0),
                    "reasoning_entries": perception_result.get("reasoning_entries", 0)
                },
                "resource_usage": {
                    "bandwidth_mb": perception_result.get("bandwidth_used", 0),
                    "entropy_reduction": perception_result.get("entropy_reduction", 0),
                    "memory_mb": 0  # 实际实现中会监控内存使用
                },
                "summary": self._generate_summary(perception_result)
            }
            
            # 保存演进报告
            report_path = self.output_handler.save_evolution_report(evolution_data)
            
            # 自动推送到 GitHub
            self.output_handler.git_commit_and_push(report_path, evolution_data)
            
            self.logger.info(f"✅ 科技达人世界感知演进完成: {report_path}")
            return evolution_data
            
        except Exception as e:
            self.logger.error(f"❌ 演进周期失败: {e}")
            # 即使失败也要生成错误报告
            error_data = {
                "start_time": start_time,
                "error": str(e),
                "summary": f"演进周期执行失败: {str(e)}"
            }
            report_path = self.output_handler.save_evolution_report(error_data)
            self.logger.info(f"⚠️ 错误报告已保存: {report_path}")
            raise
            
    def _generate_summary(self, perception_result: Dict[str, Any]) -> str:
        """生成演进总结"""
        new_tech_count = perception_result.get("new_tech_count", 0)
        validated_skills = perception_result.get("validated_skills", 0)
        bandwidth_used = perception_result.get("bandwidth_used", 0)
        entropy_reduction = perception_result.get("entropy_reduction", 0)
        
        if new_tech_count > 0:
            return f"今日成功发现 {new_tech_count} 项新技术，验证 {validated_skills} 个有效技能，认知熵降低 {entropy_reduction:.2f}%，流量使用 {bandwidth_used:.2f}MB。系统持续进化中！"
        else:
            return f"今日未发现显著新认知缺口，系统保持稳定。流量使用 {bandwidth_used:.2f}MB，认知熵维持在较低水平。"
            
    def should_run_now(self) -> bool:
        """检查是否应该现在运行（凌晨 01:00）"""
        now = datetime.now().time()
        target_time = time(1, 0)  # 凌晨 01:00
        
        # 允许一定的时间窗口（比如前后5分钟）
        time_window_minutes = 5
        window_start = time((target_time.hour - (time_window_minutes // 60)) % 24, 
                           max(0, target_time.minute - (time_window_minutes % 60)))
        window_end = time((target_time.hour + (time_window_minutes // 60)) % 24,
                         min(59, target_time.minute + (time_window_minutes % 60)))
        
        # 处理跨天的情况
        if window_start > window_end:
            return now >= window_start or now <= window_end
        else:
            return window_start <= now <= window_end


# 主执行函数
async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/tech_blogger_watcher.log'),
            logging.StreamHandler()
        ]
    )
    
    watcher = TechBloggerWatcher()
    
    # 检查是否在正确的时间运行
    if not watcher.should_run_now() and '--force' not in sys.argv:
        print("⏰ 当前不是凌晨 01:00，跳过执行。使用 --force 强制运行。")
        return
        
    try:
        await watcher.run_evolution_cycle()
        print("✅ 科技达人世界感知演进完成！")
    except Exception as e:
        print(f"❌ 演进失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())