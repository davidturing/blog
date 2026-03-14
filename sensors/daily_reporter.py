"""
每日学习报告生成器。

在每天 08:00 自动生成学习汇报并写入 daily notes。
"""

import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path


class DailyReporter:
    """每日报告生成器。"""

    def __init__(self, config: Dict[str, Any]):
        """初始化每日报告生成器。
        
        Args:
            config: 配置字典。
        """
        self.logger = logging.getLogger("DailyReporter")
        self.config = config
        self.report_template = config.get("reporting", {}).get("report_template", "")
        self.daily_notes_path = Path(config.get("storage", {}).get("daily_notes_path", "./memory"))

    def generate_report(self, report_data: Dict[str, Any]) -> str:
        """生成每日报告。
        
        Args:
            report_data: 报告数据字典，包含 new_tech_count, validated_skills 等字段。
            
        Returns:
            格式化的报告字符串。
        """
        if not self.report_template:
            # Fallback template
            template = """
David，我已完成昨晚的世界探索：
发现新技术：{new_tech_count} | 验证技能：{validated_skills} | 存入 SkillBank：{skillbank_entries} 条 | 存入 ReasoningBank：{reasoning_entries} 条避坑规则 | 已同步所有分身 | 流量使用：{bandwidth_used}MB | 认知熵降低：{entropy_reduction}%
"""
        else:
            template = self.report_template
            
        try:
            report = template.format(**report_data)
            return report.strip()
        except KeyError as e:
            self.logger.error(f"Missing key in report data: {e}")
            # Create a basic report with available data
            basic_report = f"David，世界探索报告 - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            for key, value in report_data.items():
                basic_report += f"{key}: {value}\n"
            return basic_report

    def save_report(self, report: str) -> bool:
        """保存报告到 daily notes 目录。
        
        Args:
            report: 报告字符串。
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create daily notes directory if it doesn't exist
            self.daily_notes_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with today's date
            today = datetime.now().strftime("%Y-%m-%d")
            report_file = self.daily_notes_path / f"world_grounding_report_{today}.md"
            
            # Write report to file
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# World Grounding Daily Report\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(report)
                f.write("\n")
                
            self.logger.info(f"Daily report saved to {report_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save daily report: {e}")
            return False

    def run_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """运行每日报告生成和保存。
        
        Args:
            report_data: 报告数据字典。
            
        Returns:
            True if successful, False otherwise.
        """
        self.logger.info("Generating daily report...")
        report = self.generate_report(report_data)
        success = self.save_report(report)
        
        if success:
            self.logger.info("Daily report completed successfully")
        else:
            self.logger.error("Failed to complete daily report")
            
        return success