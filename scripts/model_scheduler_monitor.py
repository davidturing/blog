#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 模型调度监控脚本
确保模型使用规则严格执行
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/zhaoqinhuang/david_project/logs/model_scheduler.log'),
        logging.StreamHandler()
    ]
)

# 项目配置
PROJECT_ROOT = Path("/Users/zhaoqinhuang/david_project")
MODELS_CONFIG_FILE = PROJECT_ROOT / "config" / "models.json"
LOG_DIR = PROJECT_ROOT / "logs"

# 强制主力模型配置
REQUIRED_DEFAULT_MODEL = "qwenprovider/qwen3-max-2026-01-23"

class ModelSchedulerMonitor:
    def __init__(self):
        self.ensure_directories()
        self.load_models_config()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        LOG_DIR.mkdir(exist_ok=True)
        (PROJECT_ROOT / "config").mkdir(exist_ok=True)
    
    def load_models_config(self):
        """加载模型配置文件"""
        if MODELS_CONFIG_FILE.exists():
            with open(MODELS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.models_config = json.load(f)
        else:
            # 创建默认配置
            self.models_config = {
                "default": REQUIRED_DEFAULT_MODEL,
                "allowed_models": [
                    "qwenprovider/qwen3-max-2026-01-23",
                    "googleprovider/models/gemini-3.1-pro-preview"
                ],
                "temporary_switches": []
            }
            self.save_models_config()
    
    def save_models_config(self):
        """保存模型配置文件"""
        with open(MODELS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.models_config, f, indent=2, ensure_ascii=False)
    
    def enforce_default_model(self):
        """强制执行默认模型规则"""
        current_default = self.models_config.get("default", "")
        
        if current_default != REQUIRED_DEFAULT_MODEL:
            logging.warning(f"检测到默认模型被修改: {current_default} -> {REQUIRED_DEFAULT_MODEL}")
            self.models_config["default"] = REQUIRED_DEFAULT_MODEL
            self.save_models_config()
            logging.info("✅ 默认模型已强制恢复为千问主力模型")
            return True
        
        return False
    
    def check_gemini_errors(self, error_message):
        """检查是否为 Gemini API 错误，需要自动恢复"""
        gemini_error_indicators = [
            "429", "rate limit", "quota exceeded", 
            "connection error", "timeout", "permission denied",
            "API quota", "exceeded quota"
        ]
        
        error_lower = error_message.lower()
        for indicator in gemini_error_indicators:
            if indicator in error_lower:
                logging.warning(f"检测到 Gemini API 错误: {error_message}")
                self.enforce_default_model()
                return True
        
        return False
    
    def log_model_switch(self, from_model, to_model, reason=""):
        """记录模型切换日志"""
        switch_record = {
            "timestamp": datetime.now().isoformat(),
            "from": from_model,
            "to": to_model,
            "reason": reason
        }
        
        # 添加到临时切换记录
        if "temporary_switches" not in self.models_config:
            self.models_config["temporary_switches"] = []
        
        self.models_config["temporary_switches"].append(switch_record)
        
        # 只保留最近100条记录
        if len(self.models_config["temporary_switches"]) > 100:
            self.models_config["temporary_switches"] = self.models_config["temporary_switches"][-100:]
        
        self.save_models_config()
        logging.info(f"模型切换记录: {from_model} -> {to_model} ({reason})")
    
    def auto_recover_to_default(self):
        """自动恢复到默认模型（用于临时切换后的恢复）"""
        current_default = self.models_config.get("default", "")
        if current_default != REQUIRED_DEFAULT_MODEL:
            self.enforce_default_model()
            self.log_model_switch(current_default, REQUIRED_DEFAULT_MODEL, "auto-recovery")
            return True
        return False
    
    def validate_models_config(self):
        """验证模型配置的完整性"""
        required_keys = ["default", "allowed_models"]
        for key in required_keys:
            if key not in self.models_config:
                logging.error(f"模型配置缺少必要字段: {key}")
                return False
        
        # 确保主力模型在允许列表中
        if REQUIRED_DEFAULT_MODEL not in self.models_config["allowed_models"]:
            self.models_config["allowed_models"].append(REQUIRED_DEFAULT_MODEL)
            self.save_models_config()
            logging.info("✅ 主力模型已添加到允许列表")
        
        return True
    
    def run_health_check(self):
        """运行健康检查"""
        logging.info("=== 模型调度健康检查开始 ===")
        
        # 验证配置
        if not self.validate_models_config():
            logging.error("❌ 模型配置验证失败")
            return False
        
        # 强制执行默认模型
        if self.enforce_default_model():
            logging.info("✅ 默认模型强制执行完成")
        else:
            logging.info("✅ 默认模型配置正确")
        
        # 清理过期的临时切换记录（超过24小时）
        self.cleanup_old_switches()
        
        logging.info("=== 模型调度健康检查完成 ===")
        return True
    
    def cleanup_old_switches(self):
        """清理超过24小时的临时切换记录"""
        if "temporary_switches" not in self.models_config:
            return
        
        current_time = datetime.now()
        valid_switches = []
        
        for switch in self.models_config["temporary_switches"]:
            try:
                switch_time = datetime.fromisoformat(switch["timestamp"])
                if (current_time - switch_time).total_seconds() < 86400:  # 24小时
                    valid_switches.append(switch)
            except (ValueError, KeyError):
                continue
        
        if len(valid_switches) != len(self.models_config["temporary_switches"]):
            self.models_config["temporary_switches"] = valid_switches
            self.save_models_config()
            logging.info(f"清理了 {len(self.models_config['temporary_switches']) - len(valid_switches)} 条过期切换记录")

def main():
    """主函数"""
    monitor = ModelSchedulerMonitor()
    
    # 运行健康检查
    if monitor.run_health_check():
        print("✅ 模型调度监控系统运行正常")
    else:
        print("❌ 模型调度监控系统发现问题")
        exit(1)

if __name__ == "__main__":
    main()