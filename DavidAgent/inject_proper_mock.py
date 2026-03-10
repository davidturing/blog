import asyncio
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import get_blackboard
from brain.memory.episodic_memory import get_episodic_memory_db

async def inject_proper_mock():
    print("🚀 开始全链路注入高质量模拟信号...")
    
    db = get_episodic_memory_db()
    blackboard = get_blackboard()
    
    # 模拟两篇高质量文章
    mock_articles = [
        {
            "handle": "arch_master",
            "author_name": "Arch Master 2026",
            "text": "大语言模型（LLM）的幻觉问题（Hallucinations）是限制其在极度严谨领域（如法律、医疗）应用的核心痛点。在我们的双脑架构中，Left Brain 通过 Pydantic 定义严格的 Entity 和 Triple 数据结构，并强制模型在 Temperature=0.0 的设定下输出 JSON。这有效迫使模型在执行信息抽取（ETL）时，仅依赖上下文中存在的事实，而不会发散伪造。提取出的核心节点（Nodes）和边（Edges）随后会构成 PageIndex 图谱，作为系统认知的中流砥柱。",
            "likes": 9800,
            "retweets": 3200
        },
        {
            "handle": "system_thinker",
            "author_name": "System Thinker",
            "text": "对于复杂多智能体系统（Multi-Agent System），各个智能体之间的状态同步是一个巨大挑战。DavidAgent 摒弃了传统的 RPC 直接调用，转而采用『黑板模式』（Blackboard Architecture）。当感知器（Perceptor）抓取到新数据后，只会更新黑板上的 `raw_source` 键。随后，黑板的事件总线会自动唤醒订阅了该键的左脑分析器（LeftBrainAnalyzer），实现真正的物理和逻辑解耦。这种设计灵感完全来源于人类神经系统的信息传递机制。",
            "likes": 4500,
            "retweets": 890
        }
    ]
    
    for i, article in enumerate(mock_articles):
        timestamp = datetime.now().isoformat()
        tweet_id = f"proper_mock_{int(datetime.now().timestamp())}_{i}"
        content_hash = hashlib.md5(article["text"].encode('utf-8')).hexdigest()
        
        signal_data = {
            'signal_id': "x_" + tweet_id,
            'content_hash': content_hash,
            'handle': article["handle"],
            'author_name': article["author_name"],
            'timestamp': timestamp,
            'likes': article["likes"],
            'retweets': article["retweets"],
            'raw_text': article["text"],
            'raw_json': json.dumps({"note_tweet": True, "text": article["text"]}, ensure_ascii=False),
            'signal_type': 'article'
        }
        
        # 1. 保存到原始信号库（为了让 Dashboard 的阶段一或感知中心能看到它）
        db.save_raw_signal(signal_data)
        print(f"✅ 已插入模拟信号至 raw_signals: {signal_data['signal_id']}")
        
        # 2. 从黑板触发（为了让正在运行的 ag_worker 真正去执行左脑的 ETL）
        print(f"📡 正在将模拟信号推入神经黑板激活左脑...")
        blackboard.update('topic_id', signal_data['signal_id'], 'MOCK_SPIDER')
        blackboard.update('raw_source', article['text'], 'MOCK_SPIDER')
        blackboard.update('workflow_status', 'START', 'SYSTEM')
        
        # 错峰触发
        await asyncio.sleep(15)
        
    print("🎉 完美注入！ag_worker 将在不久后生成 GraphData。")

if __name__ == "__main__":
    asyncio.run(inject_proper_mock())
