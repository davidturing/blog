import json
import os
from datetime import datetime
from pathlib import Path

class ReasoningBank:
    def __init__(self, path=None):
        if path is None:
            # 使用项目根目录下的 reasoning_bank.json
            project_root = Path(__file__).parent.parent.parent.parent
            self.path = project_root / "reasoning_bank.json"
        else:
            self.path = Path(path)
        
        self.rules = {
            "success": [],    # 成功策略
            "failure": []     # 失败教训 / 防坑规则
        }
        self._load()

    def _load(self):
        try:
            if self.path.exists():
                with open(self.path, "r", encoding="utf-8") as f:
                    self.rules = json.load(f)
            else:
                self._save()
        except Exception as e:
            print(f"⚠️ ReasoningBank 加载失败: {e}")
            self._save()

    def _save(self):
        try:
            # 确保目录存在
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.rules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ ReasoningBank 保存失败: {e}")

    def add_success(self, task, method, effect=""):
        """添加成功策略"""
        item = {
            "task": task,
            "method": method,
            "effect": effect,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.rules["success"].append(item)
        self._save()
        return "✅ 已学习成功经验"

    def add_failure(self, task, error, fix=""):
        """添加失败教训"""
        item = {
            "task": task,
            "error": error,
            "fix": fix,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.rules["failure"].append(item)
        self._save()
        return "⚠️ 已记录失败教训"

    def match(self, task, top_n=3):
        """匹配相关策略和教训"""
        matched = []
        
        # 先匹配失败教训（优先级更高）
        for item in self.rules["failure"]:
            if self._task_matches(task, item["task"]):
                matched.append(("failure", item))
        
        # 再匹配成功策略
        for item in self.rules["success"]:
            if self._task_matches(task, item["task"]):
                matched.append(("success", item))
        
        return matched[:top_n]

    def _task_matches(self, query_task, stored_task):
        """判断任务是否匹配"""
        query_words = set(query_task.lower().split())
        stored_words = set(stored_task.lower().split())
        # 如果有共同的关键词就认为匹配
        return len(query_words & stored_words) > 0

    def judge_and_learn(self, task, result, detail=""):
        """自动判断并学习"""
        success_indicators = ["success", "ok", "done", "完成", "成功", "completed", "published"]
        failure_indicators = ["failed", "error", "timeout", "失败", "错误", "超时", "exception"]
        
        result_lower = str(result).lower()
        
        if any(indicator in result_lower for indicator in success_indicators):
            return self.add_success(task, method=detail)
        elif any(indicator in result_lower for indicator in failure_indicators):
            return self.add_failure(task, error=result, fix=detail)
        else:
            # 默认当作失败处理，更安全
            return self.add_failure(task, error=result, fix=detail)

# 全局实例
_REASONING_BANK_INSTANCE = None

def get_reasoning_bank():
    """获取全局 ReasoningBank 实例"""
    global _REASONING_BANK_INSTANCE
    if _REASONING_BANK_INSTANCE is None:
        _REASONING_BANK_INSTANCE = ReasoningBank()
    return _REASONING_BANK_INSTANCE