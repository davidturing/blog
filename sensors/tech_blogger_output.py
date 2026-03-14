"""
科技达人专属输出模块 - 世界感知自主演进日志生成器

负责将世界感知结果格式化为科技达人风格的演进日志，
并输出到指定的 GitHub 仓库路径。
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import logging


class TechBloggerOutput:
    """科技达人演进日志输出器"""
    
    def __init__(self):
        self.logger = logging.getLogger("TechBloggerOutput")
        self.output_dir = "/Users/zhaoqinhuang/github/tech/davidagent_evolution"
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info(f"确保输出目录存在: {self.output_dir}")
        
    def generate_evolution_filename(self, timestamp: datetime) -> str:
        """生成符合要求的文件名
        
        Args:
            timestamp: 演进时间戳
            
        Returns:
            格式化的文件名
        """
        # 格式: DavidAgent自主演进YYYYMMDD_HHMM.md
        date_str = timestamp.strftime("%Y%m%d_%H%M")
        filename = f"DavidAgent自主演进{date_str}.md"
        return filename
        
    def format_evolution_content(self, evolution_data: Dict[str, Any]) -> str:
        """格式化演进日志内容
        
        Args:
            evolution_data: 演进数据字典
            
        Returns:
            格式化的Markdown内容
        """
        content = []
        
        # 标题
        start_time = evolution_data.get("start_time", "未知时间")
        content.append(f"# DavidAgent 自主演进报告")
        content.append(f"**演进开始时间**: {start_time}")
        content.append("")
        
        # 数据源与总量
        sources = evolution_data.get("sources", {})
        total_items = sum(sources.values()) if isinstance(sources, dict) else 0
        content.append(f"## 📊 抓取数据源与总量")
        content.append(f"**总抓取量**: {total_items} 项")
        if isinstance(sources, dict):
            for source, count in sources.items():
                content.append(f"- **{source}**: {count} 项")
        content.append("")
        
        # 认知熵识别的新技术/热点
        new_tech = evolution_data.get("new_technologies", [])
        content.append(f"## 🔍 认知熵识别到的新技术/热点")
        if new_tech:
            for tech in new_tech[:10]:  # 限制显示前10个
                title = tech.get("title", "未知技术")
                source = tech.get("source", "未知来源")
                similarity = tech.get("similarity_score", 0)
                content.append(f"- **{title}** ({source}) - 相似度: {similarity:.3f}")
        else:
            content.append("未发现显著新认知缺口")
        content.append("")
        
        # 蒸馏后的核心知识
        distilled_knowledge = evolution_data.get("distilled_knowledge", [])
        content.append(f"## 💡 蒸馏后的核心知识")
        if distilled_knowledge:
            for knowledge in distilled_knowledge[:5]:  # 限制显示前5个
                title = knowledge.get("title", "未知知识")
                insights = knowledge.get("key_insights", [])
                content.append(f"### {title}")
                if insights:
                    for insight in insights[:3]:  # 每个知识限制3个洞察
                        content.append(f"- {insight}")
                content.append("")
        else:
            content.append("未成功蒸馏有效知识")
        content.append("")
        
        # 验证结果
        validation_results = evolution_data.get("validation_results", {})
        content.append(f"## ✅ 验证结果")
        validated_skills = validation_results.get("validated_skills", 0)
        failed_validations = validation_results.get("failed_validations", 0)
        content.append(f"- **成功验证**: {validated_skills} 项")
        content.append(f"- **验证失败**: {failed_validations} 项")
        content.append("")
        
        # 存储统计
        storage_stats = evolution_data.get("storage_stats", {})
        skillbank_entries = storage_stats.get("skillbank_entries", 0)
        reasoning_entries = storage_stats.get("reasoning_entries", 0)
        content.append(f"## 📦 存入 SkillBank / ReasoningBank 数量")
        content.append(f"- **SkillBank 条目**: {skillbank_entries} 条")
        content.append(f"- **ReasoningBank 避坑规则**: {reasoning_entries} 条")
        content.append("")
        
        # 资源使用
        resource_usage = evolution_data.get("resource_usage", {})
        bandwidth_used = resource_usage.get("bandwidth_mb", 0)
        entropy_reduction = resource_usage.get("entropy_reduction", 0)
        memory_usage = resource_usage.get("memory_mb", 0)
        content.append(f"## 📈 流量使用、认知熵变化")
        content.append(f"- **流量使用**: {bandwidth_used:.2f} MB")
        content.append(f"- **认知熵降低**: {entropy_reduction:.2f}%")
        content.append(f"- **内存占用**: {memory_usage:.2f} MB")
        content.append("")
        
        # 今日演进总结
        summary = evolution_data.get("summary", "今日演进完成")
        content.append(f"## 🎯 今日演进总结")
        content.append(summary)
        content.append("")
        
        # 元数据
        content.append(f"---")
        content.append(f"*本报告由「科技达人」数字分身自动生成*")
        content.append(f"*执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(content)
        
    def save_evolution_report(self, evolution_data: Dict[str, Any]) -> str:
        """保存演进报告到指定位置
        
        Args:
            evolution_data: 演进数据
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.fromisoformat(evolution_data["start_time"]) if "start_time" in evolution_data else datetime.now()
        filename = self.generate_evolution_filename(timestamp)
        filepath = os.path.join(self.output_dir, filename)
        
        content = self.format_evolution_content(evolution_data)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        self.logger.info(f"演进报告已保存: {filepath}")
        return filepath
        
    def git_commit_and_push(self, filepath: str, evolution_data: Dict[str, Any]):
        """自动提交到 GitHub 仓库
        
        Args:
            filepath: 演进报告文件路径
            evolution_data: 演进数据用于提交信息
        """
        try:
            timestamp = datetime.fromisoformat(evolution_data["start_time"]) if "start_time" in evolution_data else datetime.now()
            commit_message = f"🤖 DavidAgent 自主演进 {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            # 切换到 tech 仓库目录
            tech_repo_path = "/Users/zhaoqinhuang/github/tech"
            if not os.path.exists(tech_repo_path):
                self.logger.error(f"GitHub 仓库路径不存在: {tech_repo_path}")
                return
                
            # 执行 git 操作
            import subprocess
            subprocess.run(["git", "add", filepath], cwd=tech_repo_path, check=True)
            subprocess.run(["git", "commit", "-m", commit_message], cwd=tech_repo_path, check=True)
            subprocess.run(["git", "push"], cwd=tech_repo_path, check=True)
            
            self.logger.info(f"演进报告已推送到 GitHub: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Git 提交失败: {e}")