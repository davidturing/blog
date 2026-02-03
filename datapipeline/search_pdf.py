import fitz
import json

pdf_path = "/Users/david/david_project/知识库/books/华为数据之道.pdf"
doc = fitz.open(pdf_path)

# Context strings from the markdown files
search_terms = {
    "图 2-1": "建立企业级数据综合治理体系",
    "图 2-3": "流程图解析",
    "图 2-4": "华为数据治理决策体系",
    "图 2-5": "华为数据管理组织",
    "图 2-6": "华为数据全生命周期治理规范与方案",
    "图 3-1": "华为数据分类管理框架",
    "图 8-1": "该框架（图 8-1）由三个核心部分构成"
}

results = {}

for i in range(len(doc)):
    page = doc.load_page(i)
    text = page.get_text()
    for fig, term in search_terms.items():
        if term in text:
            if fig not in results:
                results[fig] = []
            results[fig].append(i)

print(json.dumps(results, indent=2, ensure_ascii=False))
doc.close()
