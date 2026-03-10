#!/usr/bin/env python3
"""
DavidAgent 每日专业洞察自动化Pipeline - 修复版本
专注于AI/技术领域的Twitter内容，严格过滤非相关主题
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/zhaoqinhuang/david_project/DavidAgent/pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_daily_insight_pipeline():
    """运行每日专业洞察pipeline - 严格限定AI/技术领域"""
    logger.info("=" * 60)
    logger.info("🚀 启动 DavidAgent 每日专业洞察自动化Pipeline (科技达人版)...")
    logger.info("🎯 专注领域: AI, Vibe Coding, AI Agent, Agentic AI, Modern Software Development")
    logger.info("=" * 60)
    
    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # 使用subprocess调用修复后的搜索pipeline
        import subprocess
        
        # 构建命令 - 使用修复后的搜索脚本
        cmd = [
            "/Users/zhaoqinhuang/david_project/DavidAgent/venv/bin/python3",
            "/Users/zhaoqinhuang/david_project/skills/twitter-insight-task/fixed_search_pipeline.py"
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            cwd="/Users/zhaoqinhuang/david_project",
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            logger.info("✅ Pipeline执行成功！")
            logger.info(f"输出:\n{result.stdout}")
        else:
            logger.error(f"❌ Pipeline执行失败，返回码: {result.returncode}")
            logger.error(f"错误输出:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Pipeline执行超时（超过5分钟）")
        return False
    except Exception as e:
        logger.error(f"❌ Pipeline执行过程中发生异常: {e}")
        logger.exception("详细错误信息:")
        return False
        
    logger.info("=" * 60)
    logger.info("🎉 DavidAgent 每日专业洞察Pipeline执行完成！")
    logger.info("✅ 严格遵循科技达人数字分身定位")
    logger.info("=" * 60)
    return True

if __name__ == "__main__":
    success = run_daily_insight_pipeline()
    sys.exit(0 if success else 1)