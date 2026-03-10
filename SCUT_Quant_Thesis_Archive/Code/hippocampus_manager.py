"""
海马体管理器
"""

import sqlite3
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class HippocampusManager:
    """海马体管理器，负责三层记忆体系的读写"""
    
    def __init__(self, base_path: str = "/Users/zhaoqinhuang/david_project/hippocampus"):
        self.base_path = base_path
        self.episodic_db = os.path.join(base_path, "episodic", "quant_task.db")
        self.semantic_path = os.path.join(base_path, "semantic", "quant_chroma")
        self.logical_path = os.path.join(base_path, "logical", "quant_knowledge.md")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.episodic_db), exist_ok=True)
        os.makedirs(self.semantic_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.logical_path), exist_ok=True)
        
        # 初始化SQLite数据库
        self._init_episodic_db()
    
    def _init_episodic_db(self):
        """初始化情景记忆数据库"""
        conn = sqlite3.connect(self.episodic_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_name TEXT,
                strategy TEXT,
                backtest_result TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def read_logical_memory(self) -> str:
        """读取语义记忆（量化基础知识）"""
        if os.path.exists(self.logical_path):
            with open(self.logical_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def write_episodic_memory(self, task_name: str, strategy: Dict[str, Any], backtest_result: Optional[Dict[str, Any]] = None):
        """写入情景记忆"""
        conn = sqlite3.connect(self.episodic_db)
        cursor = conn.cursor()
        
        strategy_str = json.dumps(strategy, ensure_ascii=False)
        result_str = json.dumps(backtest_result, ensure_ascii=False) if backtest_result else None
        
        cursor.execute(
            "INSERT INTO tasks (task_name, strategy, backtest_result) VALUES (?, ?, ?)",
            (task_name, strategy_str, result_str)
        )
        conn.commit()
        conn.close()
    
    def read_episodic_memory(self, task_name: str) -> Optional[Dict[str, Any]]:
        """读取情景记忆"""
        conn = sqlite3.connect(self.episodic_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT strategy, backtest_result FROM tasks WHERE task_name = ? ORDER BY created_at DESC LIMIT 1",
            (task_name,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            strategy = json.loads(row[0]) if row[0] else None
            backtest_result = json.loads(row[1]) if row[1] else None
            return {"strategy": strategy, "backtest_result": backtest_result}
        return None