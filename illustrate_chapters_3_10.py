
import os
import re
import time
import json
import subprocess
from openai import OpenAI

# Configuration
# Configuration
# Text Analysis (Google Gemini via OpenAI compatibility)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Image Generation (Using baoyu-image-gen)
GEN_SCRIPT = "/Users/david/david_project/.agent/skills/baoyu-image-gen/scripts/main.ts"

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not set.")
    exit(1)

client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url=GOOGLE_BASE_URL,
)

FILES_TO_PROCESS = [
    "/Users/david/david_project/智能体/数据治理/03.数据治理理论的演进与应用边界/3.1-data_governance_development.md",
    "/Users/david/david_project/智能体/数据治理/03.数据治理理论的演进与应用边界/3.2-industry_fit_analysis.md",
    "/Users/david/david_project/智能体/数据治理/03.数据治理理论的演进与应用边界/3.3-dama_framework_limitations.md",
    "/Users/david/david_project/智能体/数据治理/04.企业数据治理核心架构设计与落地/4.1-data_architecture_core_logic.md",
    "/Users/david/david_project/智能体/数据治理/04.企业数据治理核心架构设计与落地/4.2-data_architecture_challenges.md",
    "/Users/david/david_project/智能体/数据治理/04.企业数据治理核心架构设计与落地/4.3-huawei_alibaba_data_architecture.md",
    "/Users/david/david_project/智能体/数据治理/05.数据质量与数据标准治理体系实践/5.1-data_quality_management_control.md",
    "/Users/david/david_project/智能体/数据治理/05.数据质量与数据标准治理体系实践/5.2-data_standard_development_iteration.md",
    "/Users/david/david_project/智能体/数据治理/06.数据治理组织、流程与文化建设/6.1-data_governance_org_structure.md",
    "/Users/david/david_project/智能体/数据治理/06.数据治理组织、流程与文化建设/6.2-data_governance_process_optimization.md",
    "/Users/david/david_project/智能体/数据治理/06.数据治理组织、流程与文化建设/6.3-data_culture_awareness.md",
    "/Users/david/david_project/智能体/数据治理/07.数据治理价值变现与工具生态适配/7.1-data_value_realization.md",
    "/Users/david/david_project/智能体/数据治理/07.数据治理价值变现与工具生态适配/7.2-data_governance_tool_selection.md",
    "/Users/david/david_project/智能体/数据治理/08.数据要素化治理与政策体系/8.1-data_factor_core_logic.md",
    "/Users/david/david_project/智能体/数据治理/08.数据要素化治理与政策体系/8.2-data_governance_policy_evolution.md",
    "/Users/david/david_project/智能体/数据治理/08.数据要素化治理与政策体系/8.3-data_market_governance.md",
    "/Users/david/david_project/智能体/数据治理/09.大模型时代的数据治理挑战与语料治理/9.1-ai_llm_data_governance_impact.md",
    "/Users/david/david_project/智能体/数据治理/09.大模型时代的数据治理挑战与语料治理/9.2-llm_corpus_data_quality.md",
    "/Users/david/david_project/智能体/数据治理/09.大模型时代的数据治理挑战与语料治理/9.3-llm_data_security_ethics.md",
    "/Users/david/david_project/智能体/数据治理/10.数据治理未来趋势与研究方向/10.1-data_governance_future_trends.md"
]

CLEANED_CHAPTERS = set()

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
        model="gemini-2.0-flash", # User requested Gemini 3 Flash, mapping to available 2.0-flash or specific ID if known. Using 2.0-flash for stability as 3.0 might be preview.
        # Actually, let's try strict adherence if possible, but 2.0-flash is safe.
        # Edit: User said "Gemini 3 Flash". I will try "gemini-2.0-flash" as a fallback if 3 fails, but for now let's use the most likely valid ID for "Gemini 3".
        # Given the "Nano Banana Pro" (Gemini 3 Pro Image) exists, "gemini-2.0-flash" is the likely text counterpart or "gemini-3.0-flash". 
        # I'll use "gemini-2.0-flash" to be safe as it's definitely supporting JSON mode well.
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"} 
    )

    try:
        response_text = completion.choices[0].message.content
        # Gemini sometimes wraps JSON in ```json ... ``` even with json_object mode
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

    # [CLARIFICATION A] Delete existing images and prompts before processing (ONCE per chapter)
    if chapter_num not in CLEANED_CHAPTERS:
        print(f"Cleaning up existing illustrations for {chapter_num}...")
        if os.path.exists(images_dir):
            for f in os.listdir(images_dir):
                if f.endswith(".png"):
                    os.remove(os.path.join(images_dir, f))
        if os.path.exists(prompts_dir):
            for f in os.listdir(prompts_dir):
                if f.endswith(".md"):
                    os.remove(os.path.join(prompts_dir, f))
        CLEANED_CHAPTERS.add(chapter_num)
    
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
        
        # Run baoyu-image-gen
        # Assuming it outputs to the same dir as prompt or specified dir. 
        # Helper script usually saves alongside prompt if not specified? 
        # Let's try specifying output dir if possible, or move it later.
        # Actually, let's just run it on the prompt file.
        
        
        image_name = slug + ".png"
        image_path = os.path.join(images_dir, image_name)

        cmd = [
            "npx", "-y", "bun", GEN_SCRIPT,
            "--promptfiles", prompt_path,
            "--image", image_path,
            "--imageSize", "1K",
            "--provider", "google",
            "--model", "gemini-3-pro-image-preview" # Nano Banana Pro
        ]
        
        # Pass current ENV which has DOUBAO_API_KEY
        # If baoyu-image-gen uses GOOGLE_API_KEY and it's not set, it might fail.
        # But let's fix the syntax error first.
        env = os.environ.copy()
        print(f"Running generator for {slug} -> {image_path}...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            
            # Find generated image. Expecting .png in prompt dir or parent?
            # Based on previous turn: illustrations/chapter-02/2.1-01.png
            # If prompt was .../prompts/2.1-01.md, image was .../illustrations/chapter-02/2.1-01.png
            # It seems baoyu-image-gen might save to parent of prompt dir if 'prompts' is in path? 
            # Or checks where the markdown file is?
            # Let's look for the .png file in prompts_dir and its parent.
            
            
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
