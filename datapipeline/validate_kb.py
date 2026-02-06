
import os
from pathlib import Path

ROOT_DIR = Path("/Users/david/david_project/智能体/数据治理")

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def validate():
    print("Starting Validation...")
    errors = []
    
    # Check max depth and filenames
    # Structure:
    # Level 0: Root
    # Level 1: Chapters (e.g. 01.xxx)
    # Level 2: Files (.md) or images/
    # Level 3: Files inside images/ (allowed)
    # 
    # Spec says: "最大层级限制：知识库章节结构最多支持 3 层"
    # "仅第 1 层章节必须创建独立目录"
    # "严禁创建第 2 层或第 3 层子目录" (implies business content subdirs)
    
    for root, dirs, files in os.walk(ROOT_DIR):
        rel_path = Path(root).relative_to(ROOT_DIR)
        parts = rel_path.parts
        depth = len(parts)
        
        # Check depth
        # Depth 0: Root (ok)
        # Depth 1: 01.xxx (ok)
        # Depth 2: images (ok)
        # Depth >= 2 and NOT images -> Violation if it's a directory?
        # Actually os.walk walks INTO directories.
        # So 'root' is the directory being inspected.
        
        if depth >= 2:
            # Level 2 directories are only allowed if they are 'images' or 'resources'
            # or if they are inside '参考文档' (References might have structure? Spec didn't explicitly exempt ref docs but we flattened them too)
            # Let's be strict based on the flattening we just did.
            
            parent_dir_name = parts[-1]
            if parent_dir_name not in ['images', 'resources', '.DS_Store']:
                # But wait, if we are AT depth 2, it means we are INSIDE a Level 1 dir.
                # If 'root' is `.../01.xxx/subdir`, depth is 2.
                # If subdir is 'images', it's allowed.
                # If subdir is 'nested_chapter', it's NOT allowed.
                if parent_dir_name not in ['images', 'resources']:
                     errors.append(f"Directory Violation: Found nested directory '{rel_path}' (Depth {depth})")

        # Check filenames in this directory
        for file in files:
            if file == '.DS_Store': continue
            
            file_path = Path(root) / file
            
            # Check ASCII
            if file.endswith('.md'):
                # index.md is allowed
                if file.lower() == 'index.md':
                    continue
                if file.lower() == 'readme.md':
                    continue
                    
                if not is_ascii(file):
                    errors.append(f"Filename Violation: Non-ASCII filename '{file}' in '{rel_path}'")

    if errors:
        print(f"FAILED: Found {len(errors)} violations:")
        for e in errors:
            print(f"  - {e}")
        exit(1)
    else:
        print("SUCCESS: All checks passed.")
        print("- No deep directories found.")
        print("- All markdown filenames are ASCII/English.")

if __name__ == "__main__":
    validate()
