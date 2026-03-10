import numpy as np
from datetime import datetime
from collections import deque

# ==============================
# Mem-α 智能记忆核心
# 三级记忆 + 强化学习式自动筛选 + 时间遗忘
# ==============================
class MemoryAlpha:
    def __init__(self, 
                 sensory_size=20,    # 感知缓存
                 working_size=100,   # 工作记忆
                 forget_rate=0.01):  # 遗忘系数
        # 三级记忆
        self.sensory = deque(maxlen=sensory_size)    # 最短期
        self.working = []                            # 活跃记忆
        self.long_term_db = None                     # LanceDB 外部接入

        self.forget_rate = forget_rate
        self.working_size = working_size

    # 绑定 LanceDB 长期记忆
    def set_long_term(self, lancedb_table):
        self.long_term_db = lancedb_table

    # 加入新记忆
    def add(self, content, importance=0.5, timestamp=None):
        ts = timestamp or int(datetime.now().timestamp())
        memory = {
            "content": content,
            "importance": np.clip(importance, 0, 1),
            "timestamp": ts,
            "retrieve_count": 0,
            "last_access": ts
        }
        self.sensory.append(memory)
        self._evolve()

    # 记忆进化：感知 → 工作 → 长期（自动筛选）
    def _evolve(self):
        # 从感知缓存晋升到工作记忆
        while len(self.sensory) > 0 and len(self.working) < self.working_size:
            mem = self.sensory.popleft()
            self.working.append(mem)

        # 工作记忆按价值排序
        self.working.sort(key=lambda x: -self._score(x))

        # 自动遗忘低分记忆
        self.working = [m for m in self.working if self._score(m) > 0.2]

    # 记忆评分 = 重要性 + 访问频率 + 时间衰减
    def _score(self, mem):
        now = int(datetime.now().timestamp())
        days = (now - mem["timestamp"]) / 86400
        time_decay = np.exp(-self.forget_rate * days)
        freq_bonus = np.log1p(mem["retrieve_count"])
        return mem["importance"] * time_decay + freq_bonus

    # 检索：自动更新访问计数
    def retrieve(self, query_embedding=None, top_k=5):
        scored = []
        for mem in self.working:
            score = self._score(mem)
            scored.append((mem, score))

        # 按记忆价值倒排
        scored.sort(key=lambda x: -x[1])
        retrieved = [m for m, s in scored[:top_k]]

        # 更新访问
        for mem in retrieved:
            mem["retrieve_count"] += 1
            mem["last_access"] = int(datetime.now().timestamp())

        return retrieved

    # 把高价值记忆写入 LanceDB 长期存储
    def persist_to_long_term(self, threshold=0.7):
        if self.long_term_db is None:
            return
        to_save = [m for m in self.working if self._score(m) >= threshold]
        if to_save:
            # 实际使用时替换为真实向量
            data = [{
                "question": m["content"].get("q", ""),
                "answer": m["content"].get("a", ""),
                "vector": np.random.rand(1536).tolist(),
                "solved": 1,
                "timestamp": m["timestamp"],
                "has_code": 1 if "```" in str(m["content"]) else 0
            } for m in to_save]
            self.long_term_db.add(data)
        return len(to_save)

# ==============================
# 调用示例
# ==============================
if __name__ == "__main__":
    mem = MemoryAlpha()
    mem.add({"q": "LanceDB 7层检索", "a": "向量+关键词+去重..."}, importance=0.9)
    mem.add({"q": "SkillRL 技能提炼", "a": "高频问题变成本能"}, importance=0.85)

    result = mem.retrieve(top_k=2)
    print("Mem-α 工作记忆（最有价值前2条）：")
    for item in result:
        print(item["content"])