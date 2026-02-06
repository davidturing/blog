
import json
import re
import os
from pathlib import Path
from urllib.parse import unquote

MAPPING_FILE = Path("/Users/david/david_project/rename_mapping.json")
ROOT_DIR = Path("/Users/david/david_project/智能体/数据治理")

def update_link(match, file_dir, mapping):
    """
    Callback for regex replacement.
    match.group(1) = Link Text
    match.group(2) = Link URL
    """
    text = match.group(1)
    url = match.group(2)
    
    # Skip external links or anchors
    if url.startswith("http") or url.startswith("#") or url.startswith("mailto:"):
        return match.group(0)
    
    # Decode percent-encoded URL (e.g. %E6%95%B0 -> 数)
    # The filenames on disk / in mapping are utf-8 string, but markdown links might be encoded.
    decoded_url = unquote(url)
    
    # Try to resolve absolute path of the target
    try:
        # Resolve relative path using the DECODED url
        target_abs_path = (file_dir / decoded_url).resolve()
        
        target_abs_str = str(target_abs_path)
        
        # Check against mapping
        if target_abs_str in mapping:
            new_abs_path_str = mapping[target_abs_str]
            new_abs_path = Path(new_abs_path_str)
            
            # Compute new relative path
            new_rel_path = os.path.relpath(new_abs_path, file_dir)
            
            # Keep the format [text](new_url)
            print(f"  Fixed link: {url} -> {new_rel_path}")
            return f"[{text}]({new_rel_path})"
            
    except Exception as e:
        print(f"Error processing link {url}: {e}")
        return match.group(0)

    return match.group(0)

def main():
    print("Updating index.md links...")
    
    if not MAPPING_FILE.exists():
        print(f"Error: {MAPPING_FILE} not found.")
        return

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    # Walk through all directories to find .md files (source files that might contain links)
    # Actually, we should update ALL markdown files, not just index.md, just in case.
    # But the task specifically said "regenerate all index.md". 
    # Let's target all .md files to be safe, as cross-references might exist.
    
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue
                
            file_path = Path(root) / file
            
            # Read content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
            
            # Function to apply to each match
            # Regex for markdown links: [text](url)
            # Use non-greedy match for content
            new_content = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\)', 
                lambda m: update_link(m, file_path.parent, mapping), 
                content
            )
            
            if new_content != content:
                print(f"Updating links in: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

if __name__ == "__main__":
    main()
