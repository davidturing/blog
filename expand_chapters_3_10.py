
import os
import time
from openai import OpenAI

# Configuration
API_KEY = os.environ.get("DOUBAO_API_KEY")
ENDPOINT_ID = os.environ.get("DOUBAO_ENDPOINT_ID")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

if not API_KEY or not ENDPOINT_ID:
    print("Error: DOUBAO_API_KEY or DOUBAO_ENDPOINT_ID not set.")
    exit(1)

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

FILES_TO_EXPAND = [
    "/Users/david/david_project/智能体/数据治理/03.数据治理理论的演进与应用边界/3.1-data_governance_development.md",
    "/Users/david/david_project/智能体/数据治理/03.数据治理理论的演进与应用边界/3.2-industry_fit_analysis.md",
    "/Users/david/david_project/智能体/数据治理/03.数据治理理论的演进与应用边界/3.3-dama_framework_limitations.md",
    "/Users/david/david_project/智能体/数据治理/04.企业数据治理核心架构设计与落地/4.1-data_architecture_core_logic.md",
    "/Users/david/david_project/智能体/数据治理/04.企业数据治理核心架构设计与落地/4.2-data_architecture_challenges.md",
    "/Users/david/david_project/智能体/数据治理/04.企业数据治理核心架构设计与落地/4.3-huawei_alibaba_data_architecture.md",
    "/Users/david/david_project/智能体/数据治理/05.数据质量与数据标准治理体系实践/5.1-data_quality_management_control.md",
    "/Users/david/david_project/智能体/数据治理/05.数据质量与数据标准治理体系实践/5.2-data_standard_development_iteration.md",
    "/Users/david/david_project/智能体/数据治理/06.数据治理组织、流程与文化建设/6.1-data_governance_org_structure.md",
    "/Users/david/david_project/智能体/数据治理/06.数据治理组织、流程与文化建设/6.2-data_governance_process_optimization.md",
    "/Users/david/david_project/智能体/数据治理/06.数据治理组织、流程与文化建设/6.3-data_culture_awareness.md",
    "/Users/david/david_project/智能体/数据治理/07.数据治理价值变现与工具生态适配/7.1-data_value_realization.md",
    "/Users/david/david_project/智能体/数据治理/07.数据治理价值变现与工具生态适配/7.2-data_governance_tool_selection.md",
    "/Users/david/david_project/智能体/数据治理/08.数据要素化治理与政策体系/8.1-data_factor_core_logic.md",
    "/Users/david/david_project/智能体/数据治理/08.数据要素化治理与政策体系/8.2-data_governance_policy_evolution.md",
    "/Users/david/david_project/智能体/数据治理/08.数据要素化治理与政策体系/8.3-data_market_governance.md",
    "/Users/david/david_project/智能体/数据治理/09.大模型时代的数据治理挑战与语料治理/9.1-ai_llm_data_governance_impact.md",
    "/Users/david/david_project/智能体/数据治理/09.大模型时代的数据治理挑战与语料治理/9.2-llm_corpus_data_quality.md",
    "/Users/david/david_project/智能体/数据治理/09.大模型时代的数据治理挑战与语料治理/9.3-llm_data_security_ethics.md",
    "/Users/david/david_project/智能体/数据治理/10.数据治理未来趋势与研究方向/10.1-data_governance_future_trends.md"
]

def expand_content(file_path):
    print(f"Processing {file_path}...")
    try:
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (File not found)")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip if content is already long enough (simple check, maybe > 4000 chars ~ 2000 chinese words?)
        # User asked to expand TO 1000-2000 words. 
        # But let's just always expand to be safe/thorough as requested.

        prompt = f"""
你是一名资深的数据治理专家。请对以下 Markdown 章节内容进行扩写，使其更加详实、深入，字数在 1000-2000 字左右。

要求：
1. **保持原有结构**：不要改变原有的一级、二级、三级标题结构。
2. **增加深度**：对每个概念进行深度剖析，增加背景、原理、实施细节。
3. **增加案例**：在合适的段落增加实际的企业案例或行业最佳实践。
4. **增加图表描述**：如果适合，可以增加对图表的文字描述（Mermaid 代码除外，保留原有 Mermaid）。
5. **专业性**：使用专业术语，逻辑严密，语言流畅。
6. **保留引用**：保留原有的引用块（> 摘要）。
7. **完整性**：输出完整的内容，不要截断。

原始内容：
{content}
"""

        print("Sending request to Doubao...")
        completion = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in Data Governance."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )

        expanded_content = completion.choices[0].message.content
        
        if not expanded_content.strip():
            print(f"Error: Empty response for {file_path}")
            return

        # Backup original
        backup_path = file_path + ".bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Backed up to {backup_path}")

        # Write expanded content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(expanded_content)
        print(f"Successfully expanded {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    for i, file_path in enumerate(FILES_TO_EXPAND):
        print(f"[{i+1}/{len(FILES_TO_EXPAND)}] Starting expansion...")
        expand_content(file_path)
        time.sleep(2) 
