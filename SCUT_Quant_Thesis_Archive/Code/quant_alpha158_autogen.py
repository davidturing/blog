#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华南理工大学课题：LLM+因果推断因子挖掘
AutoGen 仿生双脑架构主入口
数据源：Baostock（彻底移除Qlib依赖）
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

# 导入自定义模块
from blackboard import Blackboard
from autogen_agents import create_autogen_system
from data_loader_baostock import load_baostock_data

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('autogen_quant.log'),
            logging.StreamHandler()
        ]
    )

def main():
    parser = argparse.ArgumentParser(description='AutoGen 仿生双脑量化因子挖掘')
    parser.add_argument('--autogen', action='store_true', help='启用AutoGen模式')
    parser.add_argument('--dml', action='store_true', help='启用DML因果推断引擎模式')
    parser.add_argument('--data-path', default='~/.qlib/qlib_data/cn_data', 
                       help='数据路径')
    
    args = parser.parse_args()
    
    if args.dml:
        print("-> 触发 DML 双重机器学习因果引擎...")
        import dml_pipeline
        dml_pipeline.run_dml_pipeline()
        return

    if not args.autogen:
        print("请使用 --autogen 或 --dml 参数")
        return
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 初始化黑板
        blackboard = Blackboard()
        
        # 加载Baostock数据
        logger.info("开始加载Baostock数据...")
        data = load_baostock_data()
        blackboard.update_state('DATA_LOAD', {'factor_data': data})
        logger.info("数据加载完成")
        
        # 创建并启动AutoGen系统
        logger.info("启动AutoGen仿生双脑系统...")
        autogen_system = create_autogen_system(blackboard)
        autogen_system.start()
        
    except Exception as e:
        logger.error(f"主程序执行错误: {e}")
        # 错误处理和重试机制
        handle_error_and_retry(e, blackboard)

def handle_error_and_retry(error, blackboard):
    """错误处理和自动重试机制"""
    import traceback
    error_msg = str(error)
    traceback.print_exc()
    
    # 记录错误到黑板
    blackboard.log_error(error_msg)
    
    # 回滚到上一状态
    previous_state = blackboard.get_previous_state()
    if previous_state:
        blackboard.rollback_to_state(previous_state)
    
    # 触发Gemini审查
    from autogen_agents import trigger_gemini_review
    trigger_gemini_review(error_msg, blackboard)

if __name__ == "__main__":
    main()