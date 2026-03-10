import json
import time
from datetime import datetime

class ReasoningBank:
    def __init__(self, path="reasoning_bank.json"):
        self.path = path
        self.rules = {
            "success": [],    # 成功策略
            "failure": []     # 失败教训 / 防坑规则
        }
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
        except:
            self._save()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)

    def add_success(self, task, method, effect=""):
        item = {
            "task": task,
            "method": method,
            "effect": effect,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.rules["success"].append(item)
        self._save()

    def add_failure(self, task, error, fix=""):
        item = {
            "task": task,
            "error": error,
            "fix": fix,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.rules["failure"].append(item)
        self._save()

    def match(self, task, top_n=3):
        matched = []
        # 优先匹配失败教训（防坑）
        for item in self.rules["failure"]:
            if any(k in task for k in item["task"].split()):
                matched.append(("failure", item))
        # 然后匹配成功策略
        for item in self.rules["success"]:
            if any(k in task for k in item["task"].split()):
                matched.append(("success", item))
        return matched[:top_n]

    def judge_and_learn(self, task, result, detail=""):
        if result.lower() in ["success", "ok", "done", "完成", "成功"]:
            self.add_success(task, method=detail)
            return "✅ 已学习成功经验"
        else:
            self.add_failure(task, error=result, fix=detail)
            return "⚠️ 已记录失败教训"

# 调用示例
if __name__ == "__main__":
    rb = ReasoningBank()
    # 清空测试数据
    rb.rules = {"success": [], "failure": []}
    rb._save()
    
    rb.judge_and_learn("LanceDB检索报错", "失败", "检查表是否存在")
    rb.judge_and_learn("7层检索调用", "成功", "按顺序执行向量+BM25")
    
    print("匹配 '检索' 相关策略:")
    results = rb.match("检索")
    for typ, item in results:
        if typ == "failure":
            print(f"⚠️ 失败教训: {item['task']} -> {item['error']}")
            if item['fix']:
                print(f"   解决方案: {item['fix']}")
        else:
            print(f"✅ 成功策略: {item['task']} -> {item['method']}")
        print(f"   时间: {item['time']}\n")