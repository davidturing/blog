"""
Memory Alpha (智能记忆层) 
重构版：移除假向量，与 LanceDB、RL 真正连通。
"""

import numpy as np
from datetime import datetime
from collections import deque
from core_embedding import get_embedding

class MemoryAlpha:
    def __init__(self, sensory_size=50, working_size=200, forget_rate=0.01):
        self.sensory = deque(maxlen=sensory_size)  # 最短期缓存 (MDP 轨迹收集站)
        self.working = []                          # 活跃工作记忆
        self.long_term_db = None                   # LanceDB table instance
        self.forget_rate = forget_rate
        self.working_size = working_size

    def set_long_term(self, lancedb_table):
        self.long_term_db = lancedb_table

    def add(self, content, importance=0.5):
        """添加新记忆"""
        ts = int(datetime.now().timestamp())
        # 计算真实向量 (State Embedding)
        vector = get_embedding(str(content))
        
        memory = {
            "content": content,
            "vector": vector,
            "importance": np.clip(importance, 0.0, 1.0),
            "timestamp": ts,
            "retrieve_count": 0,
            "last_access": ts
        }
        self.sensory.append(memory)
        self._evolve()

    def _evolve(self):
        """感知 -> 工作 -> 长期的进化机制"""
        while len(self.sensory) > 0 and len(self.working) < self.working_size:
            self.working.append(self.sensory.popleft())
        
        self.working.sort(key=lambda x: -self._score(x))
        # 保留前 N 个
        self.working = self.working[:self.working_size]

    def _score(self, mem):
        """Value function heuristics for memory retention"""
        now = int(datetime.now().timestamp())
        days = (now - mem["timestamp"]) / 86400
        time_decay = np.exp(-self.forget_rate * days)
        freq_bonus = np.log1p(mem["retrieve_count"])
        return mem["importance"] * time_decay + freq_bonus

    def retrieve(self, query: str, top_k=5):
        """从工作记忆中基于真实语义向量检索"""
        if not self.working:
            return []
            
        query_vector = get_embedding(query)
        scored = []
        for mem in self.working:
            # Cosine similarity
            vec = mem["vector"]
            sim = np.dot(query_vector, vec) / (np.linalg.norm(query_vector) * np.linalg.norm(vec) + 1e-9)
            
            # Combine semantic similarity with memory value score
            combined_score = 0.7 * sim + 0.3 * self._score(mem)
            scored.append((mem, combined_score))
            
        scored.sort(key=lambda x: -x[1])
        retrieved = [m for m, s in scored[:top_k]]
        
        for mem in retrieved:
            mem["retrieve_count"] += 1
            mem["last_access"] = int(datetime.now().timestamp())
            
        return retrieved

    def persist_to_long_term(self, threshold=0.7):
        """把高价值记忆写入 LanceDB 长期存储 (写入真实的 vector)"""
        if self.long_term_db is None:
            return 0
            
        to_save = [m for m in self.working if self._score(m) >= threshold]
        if not to_save:
            return 0
            
        data = [{
            "question": str(m["content"])[:200],  # Snapshot
            "answer": str(m["content"]),
            "vector": m["vector"].tolist(),       # REAL EMBEDDING
            "solved": 1,
            "timestamp": m["timestamp"],
            "has_code": 1 if "```" in str(m["content"]) else 0
        } for m in to_save]
        
        self.long_term_db.add(data)
        return len(to_save)
