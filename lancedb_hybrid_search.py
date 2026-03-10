import lancedb
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import pyarrow as pa

# ==============================
# 1. 初始化 LanceDB 连接
# ==============================
db = lancedb.connect("./lancedb_memory")

# 定义表结构
schema = pa.schema([
    pa.field("vector", pa.list_(pa.float32(), list_size=1536)),
    pa.field("question", pa.string()),
    pa.field("answer", pa.string()),
    pa.field("solved", pa.int32()),
    pa.field("timestamp", pa.int64()),
    pa.field("has_code", pa.int32()),
])

if "resolved_questions" not in db.table_names():
    db.create_table("resolved_questions", schema=schema, mode="overwrite")
table = db.open_table("resolved_questions")

# ==============================
# 2. 7层混合检索核心实现
# ==============================
def hybrid_search_7layer(query_embedding, query_text, top_k=3):
    now_ts = int(datetime.now().timestamp())

    # ---------- 第1层：向量检索 ----------
    candidates = table.search(query_embedding).limit(20).to_list()
    if not candidates:
        return {"status": "no_memory", "message": "【无相关历史记忆】"}

    # ---------- 第2层：BM25 关键词打分（简化版） ----------
    def bm25_score(text, query):
        tokens = query.lower().split()
        return sum(1 for t in tokens if t in text.lower())
    for c in candidates:
        c["bm25"] = bm25_score(c["question"], query_text)

    # ---------- 第3层：MMR 去重 ----------
    def mmr_deduplicate(items, lambda_mult=0.5):
        selected = []
        while len(selected) < 10 and items:
            scores = [
                lambda_mult * i["bm25"]
                - (1 - lambda_mult) * max(
                    cosine_similarity([i["vector"]], [s["vector"]])[0][0]
                    for s in selected
                )
                if selected else i["bm25"]
                for i in items
            ]
            best_idx = np.argmax(scores)
            best = items[best_idx]
            selected.append(best)
            items.pop(best_idx)
        return selected
    candidates = mmr_deduplicate(candidates.copy())

    # ---------- 第4层：元数据过滤 ----------
    candidates = [c for c in candidates if c.get("solved", 0) == 1]

    # ---------- 第5层：时间衰减 ----------
    def time_score(ts):
        days = (now_ts - ts) / (3600 * 24)
        return np.exp(-0.01 * days)
    for c in candidates:
        c["time_score"] = time_score(c["timestamp"])

    # ---------- 第6层：用户偏好加权（代码/步骤优先） ----------
    for c in candidates:
        c["final_score"] = (
            0.4 * c["bm25"]
            + 0.3 * c["time_score"]
            + 0.3 * c.get("has_code", 0)
        )

    # ---------- 第7层：重排序输出 top3 ----------
    candidates = sorted(candidates, key=lambda x: -x["final_score"])[:top_k]

    if not candidates:
        return {"status": "no_memory", "message": "【无相关历史记忆】"}

    return {
        "status": "found",
        "message": f"【记忆召回·已解决】\n{candidates[0]['answer']}",
        "results": candidates[:3]
    }

# ==============================
# 3. 添加测试数据的函数
# ==============================
def add_test_data():
    """添加一些测试数据到数据库"""
    test_data = [
        {
            "vector": np.random.rand(1536).tolist(),
            "question": "怎么安装LanceDB插件",
            "answer": "使用 pip install lancedb 命令安装 LanceDB 插件，确保在虚拟环境中运行。",
            "solved": 1,
            "timestamp": int(datetime.now().timestamp()) - 86400,  # 1天前
            "has_code": 1,
        },
        {
            "vector": np.random.rand(1536).tolist(),
            "question": "WordPress 发布博客的方法",
            "answer": "使用 WordPress XML-RPC API 或 REST API 发布博客，需要应用密码和正确的端点配置。",
            "solved": 1,
            "timestamp": int(datetime.now().timestamp()) - 172800,  # 2天前
            "has_code": 1,
        },
        {
            "vector": np.random.rand(1536).tolist(),
            "question": "DAMA-DMBOK2 教程内容",
            "answer": "DAMA-DMBOK2 是数据管理知识体系指南，包含11个知识领域和DAMA三步法（Plan-Develop-Control-Operate）。",
            "solved": 1,
            "timestamp": int(datetime.now().timestamp()) - 259200,  # 3天前
            "has_code": 0,
        }
    ]
    
    # 添加到表中
    table.add(test_data)
    print(f"✅ 已添加 {len(test_data)} 条测试数据到数据库")

# ==============================
# 4. 调用示例
# ==============================
if __name__ == "__main__":
    # 先添加测试数据
    add_test_data()
    
    # 测试查询
    query = "怎么安装LanceDB插件"
    query_embedding = np.random.rand(1536).tolist()  # 使用随机 embedding 作为示例
    result = hybrid_search_7layer(query_embedding, query)
    print(result["message"])