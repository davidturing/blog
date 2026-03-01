import os
import glob
from pathlib import Path

def search_pageindex(keyword: str) -> str:
    """
    Search the local documentation and knowledge graph (PageIndex) for a specific keyword.
    Returns surrounding text snippets from markdown files where the keyword is found.
    Use this tool when you encounter unknown architectural concepts or entities.
    
    Args:
        keyword: The concept, entity, or term to search for (e.g. "海马体", "Perceptor", "GraphData").
    """
    project_root = Path(__file__).parent.parent.parent
    
    # 搜索范围：系统架构文档 + 左脑已提取的图谱沉淀
    search_dirs = [
        project_root / "docs",
        project_root / "skills" / "self-learning-agent" / "pageindex" / "knowledge"
    ]
    
    results = []
    snippet_length = 200 # 提取关键字前后200字的上下文
    
    print(f"🔍 [PageIndex Tool] 左脑触发翻查动作: 搜索关键字 '{keyword}'...")
    
    for directory in search_dirs:
        if not directory.exists():
            continue
            
        # 递归查找所有 markdown 文件
        for md_file in directory.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 简单的大小写不敏感搜索
                keyword_lower = keyword.lower()
                content_lower = content.lower()
                
                start_idx = 0
                snippet_count = 0
                
                while snippet_count < 3: # 每个文件最多取3个片段
                    found_idx = content_lower.find(keyword_lower, start_idx)
                    if found_idx == -1:
                        break
                        
                    # 计算截取范围
                    snippet_start = max(0, found_idx - snippet_length)
                    snippet_end = min(len(content), found_idx + len(keyword) + snippet_length)
                    
                    snippet = content[snippet_start:snippet_end].strip()
                    # 标记来源：提取文件中的 signal_id 便于复盘溯源
                    source_label = md_file.stem
                    result_entry = f"--- Source: {md_file.name} (signal: {source_label}) ---\n...{snippet}..."
                    results.append(result_entry)
                    
                    start_idx = found_idx + len(keyword)
                    snippet_count += 1
                    
            except Exception as e:
                # 忽略读取错误的特定文件
                continue
                
    if not results:
        print(f"⚠️ [PageIndex Tool] 未找到包含 '{keyword}' 的内容。")
        return f"No results found for '{keyword}' in local PageIndex and docs."
        
    print(f"✅ [PageIndex Tool] 搜索完毕，共在 {len(results)} 处找到 '{keyword}' 的定义或关联。")
    # 为了避免上下文溢出，限制总返回片段数为 5 个
    final_output = "\n\n".join(results[:5])
    return final_output
