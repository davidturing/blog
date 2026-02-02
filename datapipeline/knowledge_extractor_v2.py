import os
import time
import re
import tempfile
import shutil
from pathlib import Path
from google import genai
from google.genai import types

# Fix typo from my plan above
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path("/Users/david/david_project/.env"))

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

def get_chapters_from_toc(toc_path):
    with open(toc_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Looking for lines like "# 1. xxx" or "# 10. xxx"
    chapters = re.findall(r'^# (\d+\..*)$', content, re.MULTILINE)
    return chapters

def extract_detailed_chapter(chapter_name, cache_name, output_path, spec_content):
    print(f"Extracting detailed content for: {chapter_name}")
    
    prompt = f"""
    你是一位专业的数据架构师和知识管理专家。请基于缓存的PDF书籍《华为数据之道》，针对“{chapter_name}”进行**详尽且深入**的知识抽取。
    
    **文档规范要求**：
    你必须严格遵守以下文档规范进行输出：
    {spec_content}
    
    **内容抽取要求**：
    1. 覆盖该章节的所有子小节。
    2. 提取所有的核心概念、定义、方法论模型。
    3. 详细描述在该章节中提到的华为最佳实践。
    4. 如果有架构图或流程描述，请用文字详尽复现。
    5. 确保内容足够详细（目的是构建底层知识库，不要过于精简）。
    6. 确保关键术语在每节首次出现时**加粗**。
    7. 所有的提示、注意、警告内容必须使用 _斜体_。
    8. 嵌套列表必须使用 **4个空格** 的缩进。
    """

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            cached_content=cache_name,
            temperature=0.1,
            max_output_tokens=8192,
        )
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Finished: {output_path}")

def main():
    PDF_FILE = "/Users/david/david_project/知识库/books/华为数据之道.pdf"
    TOC_FILE = "/Users/david/david_project/智能体/数据治理/参考文档/数据之道/华为数据治理.md"
    OUTPUT_DIR = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道/")
    SPEC_FILE = "/Users/david/david_project/智能体/spec/doc-spec.md"
    
    if not os.path.exists(PDF_FILE):
        print("PDF not found")
        return
    
    # 1. Get Chapters
    chapters = get_chapters_from_toc(TOC_FILE)
    print(f"Found {len(chapters)} chapters for extraction.")

    # 2. Read Spec
    with open(SPEC_FILE, "r", encoding="utf-8") as f:
        spec_content = f.read()

    # 3. Upload File and Create Cache
    # Workaround for Unicode path
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / "source_book.pdf"
        shutil.copy(PDF_FILE, tmp_path)
        file_upload = client.files.upload(file=str(tmp_path))
        print(f"Uploaded file for caching: {file_upload.uri}")

        # Wait for file
        while file_upload.state == "PROCESSING":
            time.sleep(5)
            file_upload = client.files.get(name=file_upload.name)
        
        # Create Cache
        print("Creating Context Cache (valid for 1 hour)...")
        # Ensure we use a model that definitely supports caching
        cache_model = 'gemini-2.5-pro'
        cache = client.caches.create(
            model=cache_model,
            config=types.CreateCachedContentConfig(
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_uri(file_uri=file_upload.uri, mime_type="application/pdf")
                        ],
                        role="user"
                    )
                ],
                ttl="3600s",
                display_name="huawei_data_way_cache"
            )
        )
        print(f"Cache created: {cache.name}")

        # 4. Extract each chapter
        for i, chapter in enumerate(chapters, 1):
            filename = f"chapter-{i:02d}-detailed.md"
            output_path = OUTPUT_DIR / filename
            try:
                extract_detailed_chapter(chapter, cache.name, output_path, spec_content)
                # Rate limit safety for the free Tier / Pay-as-you-go
                time.sleep(5)
            except Exception as e:
                print(f"Error extracting {chapter}: {e}")
        
        # Cleanup cache is automatic by TTL, but let's be responsible
        # client.caches.delete(name=cache.name)

if __name__ == "__main__":
    main()
