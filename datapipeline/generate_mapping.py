
import os
import json
import re
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Config
ROOT_DIR = Path("/Users/david/david_project/智能体/数据治理")
MAPPING_FILE = Path("rename_mapping.json")

load_dotenv("/Users/david/david_project/.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_english_name(chinese_name, context_content=""):
    """
    Uses Gemini to translate/transliterate Chinese filename to English snake_case.
    """
    prompt = f"""
    You are a technical file naming expert.
    Task: Convert the given Chinese filename into a clean, concise English filename (snake_case).
    
    Rules:
    1. Use English technical terms where possible (e.g. "数据治理" -> "data_governance").
    2. Use snake_case (lowercase, underscores).
    3. Keep it concise (max 3-5 words).
    4. Return ONLY the filename string, no extension, no markdown.
    5. If the name starts with numbers like '1.1-', PRESERVE the numbers and the hyphen at the start.
       Example: '1.1-数据治理定义' -> '1.1-data_governance_definition'
    
    Input Filename: {chinese_name}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip().replace('`', '').replace(' ', '_').lower()
    except Exception as e:
        print(f"Error translating {chinese_name}: {e}")
        return chinese_name # Fallback

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def scan_and_map():
    mapping = {}
    
    # Get all Level 1 directories (e.g. 01.xxx, 02.xxx)
    # We assume ROOT contents are the Level 1 dirs + index.md
    
    level1_items = sorted(list(ROOT_DIR.iterdir()))
    
    for item in level1_items:
        if not item.is_dir():
            # Skip root files like index.md for flattening (they stay in root)
            continue
            
        if item.name.startswith('.'):
            continue

        print(f"Scanning Level 1 Directory: {item.name}")
        
        # Walk recursively inside this Level 1 directory
        for root, dirs, files in os.walk(item):
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                # We skip index.md files for renaming/moving IF they are the main Level 1 index
                # But if they are nested deep index.md, we might want to handle them?
                # Spec says: "每个一级目录下必须包含一个 index.md". 
                # So item/index.md should stay as item/index.md.
                
                file_path = Path(root) / file
                relative_path_from_l1 = file_path.relative_to(item)
                
                is_level1_index = (file == 'index.md' and len(relative_path_from_l1.parts) == 1)
                
                if is_level1_index:
                    print(f"  Skipping L1 Index: {file_path}")
                    continue
                
                # Determine new filename
                original_name = file_path.stem # name without suffix
                original_suffix = file_path.suffix
                
                # If needs rename (has non-ascii or we just want to standardize)
                if not is_ascii(original_name):
                    print(f"  Translating: {file}")
                    new_stem = get_english_name(original_name)
                    new_filename = f"{new_stem}{original_suffix}"
                    print(f"    -> {new_filename}")
                else:
                    new_filename = file

                # Determine new parent (Flattened to Level 1)
                new_parent = item 
                
                new_full_path = new_parent / new_filename
                
                # Check for collision
                if str(new_full_path) in mapping.values():
                    print(f"  Collision detected for {new_filename}! Appending variant.")
                    new_filename = f"{new_full_path.stem}_v2{new_full_path.suffix}"
                    new_full_path = new_parent / new_filename
                
                # Add to mapping only if path changes
                if file_path != new_full_path:
                    mapping[str(file_path)] = str(new_full_path)
                    print(f"  Mapped: {file_path.name} -> {new_filename}")

    return mapping

def main():
    print("Generating Mapping...")
    mapping = scan_and_map()
    
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved mapping with {len(mapping)} entries to {MAPPING_FILE}")

if __name__ == "__main__":
    main()
