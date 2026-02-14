
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
    "/Users/david/david_project/智能体/数据治理/02.数据治理核心知识领域详解/2.1-data_architecture_management.md",
    "/Users/david/david_project/智能体/数据治理/02.数据治理核心知识领域详解/2.2-data_quality_management.md",
    "/Users/david/david_project/智能体/数据治理/02.数据治理核心知识领域详解/2.3-data_security_compliance.md",
    "/Users/david/david_project/智能体/数据治理/02.数据治理核心知识领域详解/2.4-other_key_knowledge.md"
]

def expand_content(file_path):
    print(f"Processing {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

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
        
        # Simple check to ensure we got markdown back
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
    for file_path in FILES_TO_EXPAND:
        expand_content(file_path)
        # Sleep to be nice to API limits if any, though enterprise endpoint usually high
        time.sleep(5) 
