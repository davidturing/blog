
import json
import shutil
import os
from pathlib import Path

MAPPING_FILE = Path("/Users/david/david_project/rename_mapping.json")

def main():
    print("Starting refactoring...")
    
    if not MAPPING_FILE.exists():
        print(f"Error: {MAPPING_FILE} not found.")
        return

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
        
    for old_path_str, new_path_str in mapping.items():
        old_path = Path(old_path_str)
        new_path = Path(new_path_str)
        
        if not old_path.exists():
            print(f"Skipping (not found): {old_path}")
            continue
            
        # Ensure destination directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing: {old_path.name} -> {new_path.name}")
        
        try:
            # Move/Rename
            shutil.move(old_path, new_path)
            print("  Success")
        except Exception as e:
            print(f"  Error: {e}")
            
    # Cleanup empty directories
    # We walk bottom-up to delete nested empty dirs
    print("\nCleaning up empty directories...")
    root_dir = Path("/Users/david/david_project/智能体/数据治理")
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                # Check if empty (ignoring .DS_Store)
                has_files = any(f for f in os.listdir(dir_path) if f != '.DS_Store')
                if not has_files:
                    print(f"Removing empty dir: {dir_path}")
                    shutil.rmtree(dir_path) # rmtree to force delete .DS_Store
            except Exception as e:
                print(f"Error checking/removing {dir_path}: {e}")

if __name__ == "__main__":
    main()
