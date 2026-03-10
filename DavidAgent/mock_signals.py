import sqlite3
import json
import hashlib
from datetime import datetime

# 连接数据库
db_path = "david_agent_memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

mock_articles = [
    {
        "handle": "tech_visionary",
        "author_name": "Tech Visionary 2026",
        "raw_text": "在过去的十年里，人工智能的架构发生了翻天覆地的变化。从早期的单体大模型，到现在我们所推崇的『仿生多智能体架构』，系统变得越来越像真实的生物大脑。以最新的 DavidAgent 系统为例，它将职责严格分离：左脑负责极度理性的数据提取、实体识别以及事实回溯（类似于人类免疫系统对虚假记忆的排斥）；而右脑则专注于情感表达和创意生成。这种基于『黑板模式』（Blackboard Pattern）进行异步通讯的解耦设计，不仅保证了逻辑的严丝合缝，更使得创造力能够在受控的边界内自由飞翔。",
        "likes": 4200,
        "retweets": 850
    },
    {
        "handle": "ai_researcher",
        "author_name": "Dr. AI Researcher",
        "raw_text": "今天我们来深入探讨一下如何构建一个可信的知识图谱 (Knowledge Graph)。在非结构化文本处理中，最大的难点在于消除歧义和提取精确的实体关系 (Triples)。我们发现，如果在 Prompt 层面对大语言模型（如 Gemini 3.1 Pro）施加强制性的 Pydantic Schema 校验，并将其 Temperature 设置为 0.0，能够极大地遏制幻觉 (Hallucination) 的产生。这种做法实际上是在执行一种称为『ETL 数据清洗』的机制。提取出的结构化数据最终被持久化为 Markdown 格式的 PageIndex，这不仅利于机器索引，也方便人类专家进行二次审查。",
        "likes": 5600,
        "retweets": 1200
    }
]

for i, article in enumerate(mock_articles):
    # 生成唯一 ID 和 Hash
    timestamp = datetime.now().isoformat()
    tweet_id = f"mock_article_{int(datetime.now().timestamp())}_{i}"
    content_hash = hashlib.md5(article["raw_text"].encode('utf-8')).hexdigest()
    
    # 模拟原始 JSON
    raw_json_dict = {
        "id": tweet_id,
        "text": article["raw_text"],
        "createdAt": timestamp,
        "author": {"name": article["author_name"], "handle": article["handle"]},
        "note_tweet": {"is_mock": True} # 标记为长文
    }
    raw_json_str = json.dumps(raw_json_dict, ensure_ascii=False)
    
    # 1. 插入 raw_signals
    cursor.execute('''
        INSERT OR IGNORE INTO raw_signals 
        (signal_id, content_hash, handle, author_name, timestamp, likes, retweets, raw_text, raw_json, signal_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "x_" + tweet_id, content_hash, article["handle"], article["author_name"],
        timestamp, article["likes"], article["retweets"], article["raw_text"],
        raw_json_str, "article"
    ))
    
    print(f"✅ 已插入模拟信号: x_{tweet_id}")
    
    # 2. 触发黑板状态记录 (存入 trace_logs 供 ag_worker 处理)
    # 这将激活系统的 Left Brain 提取逻辑
    full_snapshot = {
        "topic_id": "x_" + tweet_id,
        "raw_source": article["raw_text"],
        "workflow_status": "START",
        "simulation": True
    }
    cursor.execute('''
        INSERT OR REPLACE INTO trace_logs 
        (task_id, timestamp, workflow_status, raw_source, left_brain_graph, full_snapshot)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        "x_" + tweet_id, timestamp, "START", article["raw_text"], "{}", json.dumps(full_snapshot, ensure_ascii=False)
    ))
    
    print(f"🔄 已创建对应的任务流水线 (trace_logs) 准备交由左脑处理...")

conn.commit()
conn.close()
print("🎉 模拟数据注入完成！")
