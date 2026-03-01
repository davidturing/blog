import json
from datetime import datetime
import os

class SkillRL:
    def __init__(self, skill_file=None):
        if skill_file is None:
            # 使用项目根目录下的技能文件
            self.skill_file = "/Users/zhaoqinhuang/david_project/david_agent_skills.json"
        else:
            self.skill_file = skill_file
            
        self.skills = {}  # key: 意图/问题关键词, value: 技能内容
        self.query_count = {}  # 统计问题频率
        self._load()

    def _load(self):
        try:
            with open(self.skill_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.skills = data.get("skills", {})
                self.query_count = data.get("query_count", {})
        except:
            self._save()

    def _save(self):
        # 确保目录存在
        os.makedirs(os.path.dirname(self.skill_file), exist_ok=True)
        with open(self.skill_file, "w", encoding="utf-8") as f:
            json.dump({
                "skills": self.skills,
                "query_count": self.query_count
            }, f, indent=2, ensure_ascii=False)

    # 记录用户问题，统计频率
    def log_query(self, query):
        key = self._make_key(query)
        self.query_count[key] = self.query_count.get(key, 0) + 1
        self._save()

    # 简单关键词归一化
    def _make_key(self, query):
        return query.strip().lower()[:20]

    # 达到阈值就提炼成技能
    def try_learn_skill(self, query, answer, threshold=3):
        key = self._make_key(query)
        if self.query_count.get(key, 0) >= threshold and key not in self.skills:
            self.skills[key] = {
                "answer": answer,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "from": "skill_rl"
            }
            self._save()
            return True
        return False

    # 优先匹配技能（本能反应）
    def invoke_skill(self, query):
        key = self._make_key(query)
        if key in self.skills:
            return {
                "hit": True,
                "skill_key": key,
                "answer": self.skills[key]["answer"]
            }
        return {"hit": False}

    # 从 ReasoningBank 学习防坑技能（高级能力）
    def learn_from_reasoning_bank(self, reasoning_bank):
        for fail_item in reasoning_bank.rules.get("failure", []):
            task = fail_item["task"]
            fix = fail_item["fix"]
            key = self._make_key(task)
            if key not in self.skills:
                self.skills[key] = {
                    "answer": f"⚠️ 避坑技能：{fix}",
                    "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "from": "reasoning_bank"
                }
        self._save()