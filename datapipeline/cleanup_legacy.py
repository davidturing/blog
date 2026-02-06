
import shutil
import os
from pathlib import Path

SOURCE_DIR = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道/images")
TARGET_DIR = Path("/Users/david/david_project/智能体/数据治理/参考文档/images")
DIR_TO_REMOVE = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道")

def cleanup():
    # 1. Move images
    if SOURCE_DIR.exists():
        if not TARGET_DIR.exists():
            TARGET_DIR.mkdir(parents=True)
            
        print(f"Moving images from {SOURCE_DIR} to {TARGET_DIR}...")
        for item in os.listdir(SOURCE_DIR):
            s = SOURCE_DIR / item
            d = TARGET_DIR / item
            if d.exists():
                print(f"Warning: {item} already exists in target. Overwriting.")
            shutil.move(str(s), str(d))
        
        # Remove empty source images dir
        try:
            SOURCE_DIR.rmdir()
            print("Removed source images dir.")
        except Exception as e:
            print(f"Could not remove source images dir: {e}")

    # 2. Remove the parent directory if empty
    try:
        # Check if empty (ignoring .DS_Store)
        if hasattr(os, 'listdir'): # Safety check
             remaining = [f for f in os.listdir(DIR_TO_REMOVE) if f != '.DS_Store']
             if not remaining:
                 shutil.rmtree(DIR_TO_REMOVE)
                 print(f"Removed directory: {DIR_TO_REMOVE}")
             else:
                 print(f"Directory not empty, could not remove: {remaining}")
    except Exception as e:
        print(f"Error removing directory: {e}")

if __name__ == "__main__":
    cleanup()
