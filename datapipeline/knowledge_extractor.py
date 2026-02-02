import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv(Path("/Users/david/david_project/.env"))

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

def extract_knowledge(pdf_path, output_path, spec_path):
    print(f"Uploading file: {pdf_path}")
    
    import tempfile
    import shutil
    
    # Create a temporary ASCII filename to avoid Unicode issues in headers
    file_upload = None
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / "source_book.pdf"
        shutil.copy(pdf_path, tmp_path)
        
        # Upload the PDF using the ASCII temporary path
        file_upload = client.files.upload(file=str(tmp_path))
        print(f"Uploaded file as: {file_upload.uri}")

    # Wait for processing
    print("Waiting for file processing...")
    file_upload = client.files.get(name=file_upload.name)
    while file_upload.state == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(5)
        file_upload = client.files.get(name=file_upload.name)
    
    if file_upload.state != "ACTIVE":
        raise Exception(f"File {file_upload.name} failed to process with state: {file_upload.state}")
    print("...file active")

    # Read the specification
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_content = f.read()

    print("Sending request to Gemini for knowledge extraction...")
    
    prompt = f"""
    你是一位专业的数据架构师和知识管理专家。请基于上传的PDF书籍《华为数据之道》，构建一份详尽的知识文档。
    
    **文档规范要求**：
    你必须严格遵守以下文档规范进行输出：
    {spec_content}
    
    **内容要求**：
    1. 包含完整的目录结构（章节标题）。
    2. 对每个章节进行内容总结，提取核心知识点、方法论、架构图描述以及华为在数据治理方面的最佳实践。
    3. 结构要清晰，各级标题使用合理。
    4. 尽量保留书中的专业术语。
    5. 语言为中文。
    6. 确保关键术语在每节首次出现时**加粗**。
    7. 所有的提示、注意、警告内容必须使用 _斜体_。
    8. 嵌套列表必须使用 **4个空格** 的缩进。
    
    输出路径将是：{output_path.name}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=file_upload.uri,
                        mime_type="application/pdf"
                    ),
                    types.Part.from_text(text=prompt)
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=8192,
        )
    )
    
    # Save the output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Knowledge extraction complete! Saved to {output_path}")

if __name__ == "__main__":
    PDF_FILE = "/Users/david/david_project/知识库/books/华为数据之道.pdf"
    OUTPUT_FILE = Path("/Users/david/david_project/智能体/数据治理/参考文档/huawei-data-way.md")
    SPEC_FILE = "/Users/david/david_project/智能体/spec/doc-spec.md"
    
    if not os.path.exists(PDF_FILE):
        print(f"Error: PDF file not found at {PDF_FILE}")
    elif not os.path.exists(SPEC_FILE):
        print(f"Error: Specification file not found at {SPEC_FILE}")
    else:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        extract_knowledge(PDF_FILE, OUTPUT_FILE, SPEC_FILE)
