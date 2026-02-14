import os
import re
import time
import json
import subprocess
from openai import OpenAI

# Configuration
# Text Analysis (Doubao)
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY")
DOUBAO_ENDPOINT_ID = os.environ.get("DOUBAO_ENDPOINT_ID")
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# Image Generation (Using baoyu-image-gen, assumes ENV is set for it, e.g. GOOGLE_API_KEY)
GEN_SCRIPT = "/Users/david/david_project/.agent/skills/baoyu-image-gen/scripts/main.ts"

if not DOUBAO_API_KEY or not DOUBAO_ENDPOINT_ID:
    print("Error: DOUBAO_API_KEY or DOUBAO_ENDPOINT_ID not set.")
    exit(1)

client = OpenAI(
    api_key=DOUBAO_API_KEY,
    base_url=DOUBAO_BASE_URL,
)

FILES_TO_PROCESS = [
    "/Users/david/david_project/智能体/数据治理/01.数据治理核心概念与理论框架/1.1-data_governance_definition.md",
    "/Users/david/david_project/智能体/数据治理/01.数据治理核心概念与理论框架/1.2-dama_dmbok2_framework.md",
    "/Users/david/david_project/智能体/数据治理/01.数据治理核心概念与理论框架/1.3-data_governance_principles_methodology.md"
]

def analyze_and_generate_prompts(file_path):
    print(f"Analyzing {file_path} for illustrations...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Prompt Doubao to identify illustration points
    system_prompt = "You are an expert article illustrator. Analyze the content and identify 1-2 key concepts that would benefit most from a visual illustration. For each concept, generate a prompt for an AI image generator."
    user_prompt = f"""
Analyze the following article content. Identify 1 to 2 positions where an illustration would significantly enhance understanding.

For each position, output a JSON object in a list:
[
  {{
    "position_pattern": "Unique text snippet from the article (approx 10-20 chars) to locate where to insert the image AFTER.",
    "filename_suffix": "short-kebab-case-name",
    "prompt": "Detailed image generation prompt. Style: 'Scientific / Textbook / Academic Illustration'. Visuals: 'Clean, high-contrast, diagrams, white background, precise labeling, academic aesthetic, similar to Nature/Science journal illustrations'. Text: 'Must include Chinese text: [Keywords related to concept]'. Resolution: 'Square 1:1'." 
  }},
  ...
]

Requirements:
1. **Style**: Strictly 'Scientific / Textbook / Academic Illustration'. Clean, white background.
2. **Text**: Images MUST contain relevant CHINESE text labels.
3. **Resolution**: 1K (Square).
4. **Quantity**: 1-2 images per file.

Content:
{content[:4000]}... (truncated)
"""

    completion = client.chat.completions.create(
        model=DOUBAO_ENDPOINT_ID,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"} # If supported, else parse text
    )

    try:
        response_text = completion.choices[0].message.content
        # Extract JSON if wrapped in markdown code blocks
        match = re.search(r"```json(.*?)```", response_text, re.DOTALL)
        if match:
            response_text = match.group(1)
        
        data = json.loads(response_text)
        items = data.get("illustrations", []) if "illustrations" in data else data
        if isinstance(items, dict): # Handle if root is dict but not "illustrations"
             # Try to find a list in the dict
             for k, v in items.items():
                 if isinstance(v, list):
                     items = v
                     break
        
        if not isinstance(items, list):
            print(f"Warning: Could not parse list from JSON for {file_path}")
            return []

        return items

    except Exception as e:
        print(f"Error parsing Doubao response for {file_path}: {e}")
        return []

def process_file(file_path):
    illustrations = analyze_and_generate_prompts(file_path)
    
    if not illustrations:
        print(f"No illustrations generated for {file_path}")
        return

    # Setup directories
    file_dir = os.path.dirname(file_path)
    # Extract chapter number from dir name (e.g. 03. -> chapter-03)
    chapter_dir_name = os.path.basename(file_dir)
    chapter_num = chapter_dir_name.split('.')[0]
    
    # Save prompts to illustrations/chapter-XX/prompts/
    prompts_dir = os.path.join(file_dir, "illustrations", f"chapter-{chapter_num}", "prompts")
    images_dir = os.path.join(file_dir, "illustrations", f"chapter-{chapter_num}")

    # [CLARIFICATION A] Delete existing images and prompts before processing
    print(f"Cleaning up existing illustrations for {chapter_num}...")
    if os.path.exists(images_dir):
        for f in os.listdir(images_dir):
            if f.endswith(".png"):
                os.remove(os.path.join(images_dir, f))
    if os.path.exists(prompts_dir):
        for f in os.listdir(prompts_dir):
            if f.endswith(".md"):
                os.remove(os.path.join(prompts_dir, f))
    
    os.makedirs(prompts_dir, exist_ok=True)
    
    generated_images = []

    for item in illustrations:
        slug = item.get("filename_suffix", "image")
        prompt_text = item.get("prompt", "")
        position_pattern = item.get("position_pattern", "")
        
        # Save prompt file
        prompt_filename = f"{slug}.md"
        prompt_path = os.path.join(prompts_dir, prompt_filename)
        
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
            
        print(f"Generated prompt: {prompt_path}")
        
        image_name = slug + ".png"
        image_path = os.path.join(images_dir, image_name)

        cmd = [
            "npx", "-y", "bun", GEN_SCRIPT,
            "--promptfiles", prompt_path,
            "--image", image_path,
            "--imageSize", "1K"
        ]
        
        env = os.environ.copy()
        print(f"Running generator for {slug} -> {image_path}...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            
            if os.path.exists(image_path):
                print(f"Image generated: {image_path}")
                generated_images.append({
                    "position_pattern": position_pattern,
                    "image_path": image_path,
                    "relative_path": os.path.relpath(image_path, file_dir)
                })
            else:
                print(f"Warning: Image not found at {image_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error generating image: {e.stderr}")

    # Insert into Markdown
    if generated_images:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # [CLARIFICATION A] Remove existing image links
        # Matches ![...](...iterations/chapter-XX/...)
        content = re.sub(r'\n\n!\[.*?\]\(.*?illustrations\/chapter-.*?\)\n\n', '', content)
        
        for img in generated_images:
            pattern = img["position_pattern"]
            rel_path = img["relative_path"]
            markdown_img = f"\n\n![{os.path.basename(rel_path)}]({rel_path})\n\n"
            
            # Find position
            idx = content.find(pattern)
            if idx != -1:
                # Insert after pattern + reasonable spacing
                insert_idx = idx + len(pattern)
                content = content[:insert_idx] + markdown_img + content[insert_idx:]
                print(f"Inserted image at pattern: '{pattern}'")
            else:
                print(f"Warning: Could not find pattern '{pattern}' in {file_path}. Appending to end.")
                content += markdown_img
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")

if __name__ == "__main__":
    for i, file_path in enumerate(FILES_TO_PROCESS):
        print(f"[{i+1}/{len(FILES_TO_PROCESS)}] Processing {file_path}...")
        process_file(file_path)
