import os
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path("/Users/david/david_project/.env"))

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

def detect_and_crop(image_path, target_path, figure_name):
    print(f"Detecting boundary for {figure_name} on {image_path}...")
    
    with open(image_path, 'rb') as f:
        image_data = f.read()

    prompt = f"""
    Find the bounding box of the entire figure labeled '{figure_name}'. 
    The bounding box must include:
    1. The visual diagram/graphic itself.
    2. All associated labels, text boxes, and legends belonging to this figure.
    3. The figure caption text (e.g., '{figure_name} xxx').
    
    Ensure the box is wide and tall enough to encompass every element without clipping.
    Return ONLY the coordinates as [ymin, xmin, ymax, xmax] in 0-1000 scale.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[
            types.Content(
                parts=[
                    types.Part.from_bytes(data=image_data, mime_type="image/png"),
                    types.Part.from_text(text=prompt)
                ]
            )
        ]
    )

    text = response.text.strip()
    print(f"AI Output: {text}")
    
    # Extract coordinates [ymin, xmin, ymax, xmax]
    import re
    match = re.search(r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]', text)
    if not match:
        print(f"Failed to parse coordinates for {figure_name}")
        return

    ymin, xmin, ymax, xmax = map(int, match.groups())
    
    # Process image
    img = Image.open(image_path)
    w, h = img.size
    
    # Convert normalized to pixel coordinates
    left = xmin * w / 1000
    top = ymin * h / 1000
    right = xmax * w / 1000
    bottom = ymax * h / 1000
    
    # Add a generous margin
    margin = 30
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(w, right + margin)
    bottom = min(h, bottom + margin)

    img.crop((left, top, right, bottom)).save(target_path)
    print(f"Saved cropped {figure_name} to {target_path}")

def main():
    images_dir = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道/images")
    high_res_dir = Path("/Users/david/david_project/datapipeline/high_res")
    
    tasks = [
        (high_res_dir / "page_28.png", images_dir / "图1-3.png", "图 1-3"),
        (high_res_dir / "page_34.png", images_dir / "图1-6.png", "图 1-6"),
        (high_res_dir / "page_35.png", images_dir / "图1-7.png", "图 1-7"),
    ]
    
    for src, dst, name in tasks:
        detect_and_crop(src, dst, name)

if __name__ == "__main__":
    main()
