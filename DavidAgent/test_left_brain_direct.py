import asyncio
import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain.left_brain.left_brain import LeftBrainGemini
from brain.left_brain.schemas import GraphData

async def test_extraction():
    print("Testing LeftBrainGemini.extract_knowledge directly...")
    brain = LeftBrainGemini()
    
    test_text = "大语言模型（LLM）的幻觉问题（Hallucinations）是限制其在极度严谨领域（如法律、医疗）应用的核心痛点。在我们的双脑架构中，Left Brain 通过 Pydantic 定义严格的 Entity 和 Triple 数据结构，并强制模型在 Temperature=0.0 的设定下输出 JSON。这有效迫使模型在执行信息抽取（ETL）时，仅依赖上下文中存在的事实，而不会发散伪造。提取出的核心节点（Nodes）和边（Edges）随后会构成 PageIndex 图谱，作为系统认知的中流砥柱。"
    
    try:
        result = await brain.extract_knowledge(test_text, "test_source_1")
        print("Success! Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Extraction failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_extraction())
