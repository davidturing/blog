#!/usr/bin/env python3
"""
Generate cover image for 2026 Python Data Analyst tech stack article
using Google Gemini (banana) model via nano-banana-pro CLI
"""

import subprocess
import json
import os

# Read the cover image prompt
with open('image_prompts.md', 'r') as f:
    content = f.read()
    # Extract cover prompt (first section)
    cover_prompt = """Professional blueprint aesthetic with technical precision, dark blue gradient background (#093572 to #103D78), high contrast white/light blue text, clean organized grid layout showing modern Python data stack: Polars + DuckDB + Streamlit + Plotly. 2K quality, 16:9 aspect ratio, shallow depth of field, cinematic lighting."""

# Generate cover image using nano-banana-pro
try:
    result = subprocess.run([
        'nano-banana-pro',
        '--prompt', cover_prompt,
        '--output', 'Cover_Image.png',
        '--size', '1920x1080',
        '--format', 'png'
    ], capture_output=True, text=True, cwd=os.path.expanduser('~/david_project/skills/wordpress-tech-publisher'))
    
    if result.returncode == 0:
        print("✅ Cover image generated successfully: Cover_Image.png")
    else:
        print(f"❌ Error generating cover image: {result.stderr}")
        
except FileNotFoundError:
    print("⚠️ nano-banana-pro CLI not found. Please install it first.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")