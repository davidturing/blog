
import json
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path("/Users/david/david_project/知识库/microblock/extracted_knowledge.json")
OUTPUT_MD = Path("/Users/david/david_project/知识库/microblock/Microblock知识分类.md")

def main():
    if not INPUT_FILE.exists():
        print("Input file not found.")
        return
        
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Consolidate Knowledge
    entities_by_type = defaultdict(dict)
    relations = []
    summaries = []
    
    for article in data:
        # Collect summaries
        if "summary" in article:
            summaries.append(f"- **{article.get('source_title')}**: {article['summary']}")
            
        # Collect entities
        for ent in article.get("entities", []):
            e_name = ent.get("name")
            e_type = ent.get("type", "UNKNOWN").upper()
            if e_name and e_name not in entities_by_type[e_type]:
                entities_by_type[e_type][e_name] = ent.get("description", "")
                
        # Collect relations
        for rel in article.get("relations", []):
            relations.append(rel)

    # Generate Markdown
    md = []
    md.append("# MicroBlocks 知识库 (Knowledge Base)\n")
    md.append("> 本文档基于自动化知识抽取构建，包含核心概念、实体分类及关系网络。\n")
    
    # 1. Ontology / Taxonomy
    md.append("## 1. 知识本体 (Ontology)\n")
    md.append("MicroBlocks 生态系统的顶层知识分类体系：\n")
    md.append("- **HARDWARE (硬件)**: 支持的主板、传感器、扩展板。")
    md.append("- **SOFTWARE (软件)**: 编程环境功能、库、扩展。")
    md.append("- **EVENT (活动)**: 相关的教育活动、会议。")
    md.append("- **ORGANIZATION (组织)**: 客观存在的基金会、公司、学校。")
    md.append("- **PERSON (人物)**: 核心开发者、主要贡献者。")
    md.append("- **CONCEPT (概念)**: 相关的计算机科学与教育概念。\n")
    
    # 2. Entity Detail
    md.append("## 2. 核心实体 (Key Entities)\n")
    
    # Sort types for consistency
    for e_type in sorted(entities_by_type.keys()):
        md.append(f"### {e_type}\n")
        # Sort entities by name
        sorted_entities = sorted(entities_by_type[e_type].items())
        for name, desc in sorted_entities:
            md.append(f"- **{name}**: {desc}")
        md.append("")
        
    # 3. Relations
    md.append("## 3. 关系图谱 (Relation Graph)\n")
    md.append("| 主体 (Source) | 关系 (Relation) | 客体 (Target) | 备注 (Context) |")
    md.append("| --- | --- | --- | --- |")
    for rel in relations:
        src = rel.get('source', '')
        r_type = rel.get('relation', '')
        tgt = rel.get('target', '')
        desc = rel.get('description', '')
        md.append(f"| {src} | {r_type} | {tgt} | {desc} |")
        
    md.append("\n## 4. 来源摘要 (Source Summaries)\n")
    for s in summaries:
        md.append(s)
        
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
        
    print(f"Generated Knowledge Base at {OUTPUT_MD}")

if __name__ == "__main__":
    main()
