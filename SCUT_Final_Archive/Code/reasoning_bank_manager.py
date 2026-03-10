"""
ReasoningBank管理器
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

class ReasoningBankManager:
    """ReasoningBank管理器，负责推理与失败学习库相关操作"""
    
    def __init__(self, base_path: str = "/Users/zhaoqinhuang/david_project/ReasoningBank"):
        self.base_path = base_path
        self.strategy_reason_path = os.path.join(base_path, "strategy_reason")
        self.failure_case_path = os.path.join(base_path, "failure_case")
        self.verify_log_path = os.path.join(base_path, "verify_log")
        
        # 确保目录存在
        os.makedirs(self.strategy_reason_path, exist_ok=True)
        os.makedirs(self.failure_case_path, exist_ok=True)
        os.makedirs(self.verify_log_path, exist_ok=True)
    
    def save_strategy_reasoning(self, strategy_name: str, reasoning_info: Dict[str, Any]):
        """保存策略推理过程"""
        reason_file = os.path.join(self.strategy_reason_path, f"{strategy_name}_reasoning.json")
        with open(reason_file, 'w', encoding='utf-8') as f:
            json.dump(reasoning_info, f, ensure_ascii=False, indent=2)
    
    def save_failure_case(self, case_id: str, failure_info: Dict[str, Any]):
        """保存失败案例"""
        failure_file = os.path.join(self.failure_case_path, f"{case_id}.json")
        with open(failure_file, 'w', encoding='utf-8') as f:
            json.dump(failure_info, f, ensure_ascii=False, indent=2)
    
    def save_verify_log(self, verify_id: str, verify_info: Dict[str, Any]):
        """保存校验日志"""
        log_file = os.path.join(self.verify_log_path, f"{verify_id}.json")
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(verify_info, f, ensure_ascii=False, indent=2)