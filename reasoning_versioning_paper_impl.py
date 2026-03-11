"""
Reasoning Bank & Versioning Bank (Paper-Level Implementation)
对齐 arXiv:2602.08234 核心设定：
1. Reasoning Bank: 基于真实向量存储的失败经验池，用于生成修正梯度(Correction Prompts)与计算价值惩罚。
2. Versioning Bank: 追踪 SkillNode 的演化历史 (v1->v2)，基于 Q-value 和 Success Rate 实现技能的优胜劣汰与回滚。
"""

import os
import json
import torch
import numpy as np
from datetime import datetime
from core_embedding import get_embedding

# ==========================================
# 1. Versioning Bank (技能版本管理)
# ==========================================
class SkillVersionNode:
    def __init__(self, skill_id: str, version: int, code_payload: str, q_value: float = 0.0):
        self.skill_id = skill_id
        self.version = version
        self.code_payload = code_payload
        self.q_value = q_value
        self.success_count = 0
        self.fail_count = 0
        self.created_at = datetime.now().isoformat()

    def update_metrics(self, reward: float):
        # 贝尔曼价值更新 (指数平滑)
        self.q_value = 0.9 * self.q_value + 0.1 * reward
        if reward > 0:
            self.success_count += 1
        else:
            self.fail_count += 1

    def to_dict(self):
        return {
            "version": self.version,
            "code": self.code_payload,
            "q_value": self.q_value,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "created_at": self.created_at
        }

class VersioningBank:
    def __init__(self, storage_path="SkillRL/versioning_bank.json"):
        self.storage_path = storage_path
        self.registry = {}  # skill_id -> list of SkillVersionNode
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self._load()

    def commit_version(self, skill_id: str, code_payload: str, q_value: float = 0.0) -> int:
        """提交一个技能的新版本"""
        if skill_id not in self.registry:
            self.registry[skill_id] = []
        
        new_version = len(self.registry[skill_id]) + 1
        node = SkillVersionNode(skill_id, new_version, code_payload, q_value)
        self.registry[skill_id].append(node)
        self._save()
        return new_version

    def record_feedback(self, skill_id: str, version: int, reward: float):
        """记录真实 RL 反馈，更新对应版本的 Q-value"""
        if skill_id in self.registry and 0 < version <= len(self.registry[skill_id]):
            self.registry[skill_id][version - 1].update_metrics(reward)
            self._save()

    def get_best_version(self, skill_id: str) -> SkillVersionNode:
        """根据 Q-value 提取最优版本，实现自我进化淘汰"""
        if skill_id not in self.registry or not self.registry[skill_id]:
            return None
        # 按照 q_value 降序排序
        sorted_versions = sorted(self.registry[skill_id], key=lambda x: x.q_value, reverse=True)
        return sorted_versions[0]

    def _save(self):
        data = {k: [v.to_dict() for v in versions] for k, versions in self.registry.items()}
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self):
        if not os.path.exists(self.storage_path): return
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for skill_id, versions_data in data.items():
                self.registry[skill_id] = []
                for v_data in versions_data:
                    node = SkillVersionNode(skill_id, v_data["version"], v_data["code"], v_data["q_value"])
                    node.success_count = v_data.get("success_count", 0)
                    node.fail_count = v_data.get("fail_count", 0)
                    node.created_at = v_data.get("created_at", "")
                    self.registry[skill_id].append(node)
        except Exception:
            pass

# ==========================================
# 2. Reasoning Bank (推理避坑库)
# ==========================================
class ReasoningBank:
    def __init__(self, lancedb_table=None):
        # 如果挂载了LanceDB，可以用于更大规模持久化；这里用内存 list 模拟高维空间池
        self.failures_pool = [] 
        self.lancedb_table = lancedb_table
        
    def record_failure(self, task_desc: str, failed_code: str, error_trace: str, root_cause_insight: str):
        """
        基于真实轨迹记录失败原因。
        task_desc: 当前 MDP 的 State
        failed_code: 执行的 Action
        error_trace: 惩罚信号
        root_cause_insight: 提炼的逻辑修正 (Effect correction)
        """
        task_emb = get_embedding(task_desc)
        error_emb = get_embedding(error_trace)
        
        record = {
            "task_desc": task_desc,
            "task_emb": task_emb,
            "failed_code": failed_code,
            "error_trace": error_trace,
            "error_emb": error_emb,
            "insight": root_cause_insight,
            "timestamp": datetime.now().isoformat()
        }
        self.failures_pool.append(record)
        print(f"🧠 [ReasoningBank] 记录深度失败轨迹，已映射至 384 维语义空间。")

    def retrieve_correction(self, current_task: str, top_k=1) -> list:
        """基于真实连续语义空间检索最近似的失败教训，用于指导策略网络避坑"""
        if not self.failures_pool:
            return []
            
        q_emb = get_embedding(current_task)
        scored = []
        for record in self.failures_pool:
            t_emb = record["task_emb"]
            # Cosine similarity
            sim = np.dot(q_emb, t_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(t_emb) + 1e-9)
            scored.append((record, sim))
            
        scored.sort(key=lambda x: -x[1])
        
        # 只返回相似度超过阈值的真理
        results = [rec for rec, sim in scored[:top_k] if sim > 0.4]
        return results

