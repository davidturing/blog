import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.memory.blackboard import get_blackboard

async def trigger_mock():
    print("🚀 开始通过神经黑板 (Blackboard) 触发模拟任务...")
    blackboard = get_blackboard()
    
    # 模拟两篇高质量文章
    mock_articles = [
        {
            "id": "mock_real_1",
            "text": "大语言模型（LLM）的幻觉问题（Hallucinations）是限制其在极度严谨领域（如法律、医疗）应用的核心痛点。在我们的双脑架构中，Left Brain 通过 Pydantic 定义严格的 Entity 和 Triple 数据结构，并强制模型在 Temperature=0.0 的设定下输出 JSON。这有效迫使模型在执行信息抽取（ETL）时，仅依赖上下文中存在的事实，而不会发散伪造。提取出的核心节点（Nodes）和边（Edges）随后会构成 PageIndex 图谱，作为系统认知的中流砥柱。"
        },
        {
            "id": "mock_real_2",
            "text": "对于复杂多智能体系统（Multi-Agent System），各个智能体之间的状态同步是一个巨大挑战。DavidAgent 摒弃了传统的 RPC 直接调用，转而采用『黑板模式』（Blackboard Architecture）。当感知器（Perceptor）抓取到新数据后，只会更新黑板上的 `raw_source` 键。随后，黑板的事件总线会自动唤醒订阅了该键的左脑分析器（LeftBrainAnalyzer），实现真正的物理和逻辑解耦。这种设计灵感完全来源于人类神经系统的信息传递机制。"
        }
    ]
    
    for article in mock_articles:
        # 真正触发生效的机制：通过 blackboard 的 update 方法发布事件
        print(f"📡 正在将模拟信号推入黑板: {article['id']}")
        blackboard.update('topic_id', "x_" + article['id'], 'MOCK_SPIDER')
        blackboard.update('raw_source', article['text'], 'MOCK_SPIDER')
        blackboard.update('workflow_status', 'START', 'SYSTEM')
        
        # 给 ag_worker 一些时间去处理第一条，再发第二条
        print(f"⏳ 等待 15 秒以便后台左脑进行 ETL 提取...")
        await asyncio.sleep(15)

    print("🎉 模拟信号已全部通过黑板抛出！")

if __name__ == "__main__":
    asyncio.run(trigger_mock())
