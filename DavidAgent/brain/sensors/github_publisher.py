"""
GitHub Tech 仓库发布器
将感知收割机报告发布到 davidturing/tech 仓库
"""

import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class GitHubPublisher:
    """GitHub Tech 仓库发布器"""
    
    def __init__(self, tech_repo_path: str = "/Users/zhaoqinhuang/github/tech"):
        """初始化发布器
        
        Args:
            tech_repo_path: tech 仓库本地路径
        """
        self.logger = logging.getLogger("GitHubPublisher")
        self.tech_repo_path = Path(tech_repo_path)
        self.evolution_dir = self.tech_repo_path / "davidagent_evolution"
        
        # 确保目录存在
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        
    def publish_report(self, report_content: str, insights: List[Dict[str, Any]]) -> bool:
        """发布报告到 GitHub tech 仓库
        
        Args:
            report_content: 报告内容
            insights: 洞察列表
            
        Returns:
            发布是否成功
        """
        try:
            # 生成文件名（遵循 MEMORY.md 规范）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"DavidAgent自主演进{timestamp}.md"
            filepath = self.evolution_dir / filename
            
            # 写入报告文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            self.logger.info(f"✅ 报告已保存到 tech 仓库: {filepath}")
            
            # 自动提交到 GitHub
            success = self._git_commit_and_push(filepath, timestamp)
            
            if success:
                self.logger.info("✅ 报告已成功推送到 GitHub")
                return True
            else:
                self.logger.error("❌ GitHub 推送失败")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 发布到 GitHub 失败: {e}")
            return False
            
    def _git_commit_and_push(self, filepath: Path, timestamp: str) -> bool:
        """执行 Git 提交和推送
        
        Args:
            filepath: 文件路径
            timestamp: 时间戳
            
        Returns:
            是否成功
        """
        try:
            # 切换到 tech 仓库目录
            original_cwd = os.getcwd()
            os.chdir(self.tech_repo_path)
            
            # Git 操作
            subprocess.run(["git", "add", str(filepath.relative_to(self.tech_repo_path))], 
                         check=True, capture_output=True)
            commit_msg = f"🤖 DavidAgent 自主演进 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(["git", "commit", "-m", commit_msg], 
                         check=True, capture_output=True)
            subprocess.run(["git", "push"], check=True, capture_output=True)
            
            os.chdir(original_cwd)
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git 操作失败: {e}")
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            return False
        except Exception as e:
            self.logger.error(f"Git 操作异常: {e}")
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            return False