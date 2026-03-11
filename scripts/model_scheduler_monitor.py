#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DavidAgent 模型调度监控脚本
确保模型调度规则严格执行
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path("/Users/zhaoqinhuang/david_project")
CREDENTIALS_DIR = PROJECT_ROOT / ".credentials"

# 主力模型配置
PRIMARY_MODEL = "qwenprovider/qwen3-max-2026-01-23"
DEFAULT_MODEL_CONFIG = {
    "default": PRIMARY_MODEL,
    "models": {
        "qwen": PRIMARY_MODEL,
        "gemini": "googleprovider/models/gemini-3.1-pro-preview"
    }
}

class ModelSchedulerMonitor:
    def __init__(self):
        self.config_file = PROJECT_ROOT / "models.json"
        self.log_file = PROJECT_ROOT / "model_scheduler.log"
        self.ensure_config_exists()
    
    def ensure_config_exists(self):
        """确保模型配置文件存在且正确"""
        if not self.config_file.exists():
            # 创建默认配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_MODEL_CONFIG, f, indent=2, ensure_ascii=False)
            self.log("创建默认模型配置文件")
        else:
            # 验证并修复配置
            self.validate_and_fix_config()
    
    def validate_and_fix_config(self):
        """验证并修复模型配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 确保 default 始终为主力千问模型
            if config.get("default") != PRIMARY_MODEL:
                config["default"] = PRIMARY_MODEL
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.log(f"强制修复 default 模型为 {PRIMARY_MODEL}")
            
            # 确保 qwen 模型配置正确
            if config.get("models", {}).get("qwen") != PRIMARY_MODEL:
                if "models" not in config:
                    config["models"] = {}
                config["models"]["qwen"] = PRIMARY_MODEL
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.log(f"强制修复 qwen 模型为 {PRIMARY_MODEL}")
                
        except Exception as e:
            self.log(f"配置验证失败: {e}")
            # 强制重置为默认配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_MODEL_CONFIG, f, indent=2, ensure_ascii=False)
            self.log("强制重置模型配置文件")
    
    def check_gemini_errors(self, error_message):
        """检查是否为 Gemini 相关错误"""
        gemini_error_keywords = [
            "429", "rate limit", "quota exceeded", "API quota",
            "connection error", "timeout", "permission denied",
            "authentication failed", "invalid api key"
        ]
        
        error_lower = error_message.lower()
        for keyword in gemini_error_keywords:
            if keyword in error_lower:
                return True
        return False
    
    def handle_gemini_error(self, error_message):
        """处理 Gemini 错误，自动切回主力模型"""
        if self.check_gemini_errors(error_message):
            self.log(f"检测到 Gemini 错误: {error_message}")
            self.switch_to_primary_model()
            return True
        return False
    
    def switch_to_primary_model(self):
        """切换回主力千问模型"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if config.get("default") != PRIMARY_MODEL:
            config["default"] = PRIMARY_MODEL
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log(f"自动切换回主力模型: {PRIMARY_MODEL}")
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(log_entry.strip())
    
    def monitor_loop(self):
        """监控循环"""
        self.log("启动模型调度监控")
        while True:
            try:
                self.validate_and_fix_config()
                time.sleep(60)  # 每分钟检查一次
            except KeyboardInterrupt:
                self.log("监控停止")
                break
            except Exception as e:
                self.log(f"监控异常: {e}")
                time.sleep(10)

def main():
    """主函数"""
    monitor = ModelSchedulerMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            # 启动持续监控
            monitor.monitor_loop()
        elif sys.argv[1] == "handle-error" and len(sys.argv) > 2:
            # 处理特定错误
            error_msg = " ".join(sys.argv[2:])
            if monitor.handle_gemini_error(error_msg):
                print("已自动切换回主力模型")
            else:
                print("非 Gemini 错误，无需处理")
        elif sys.argv[1] == "switch-primary":
            # 手动切换回主力模型
            monitor.switch_to_primary_model()
            print("已切换回主力模型")
    else:
        # 默认：验证配置
        monitor.validate_and_fix_config()
        print("模型配置验证完成")

if __name__ == "__main__":
    import sys
    main()