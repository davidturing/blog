
import os
import re
import fitz
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Config
BASE_DIR = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道")
PDF_PATH = Path("/Users/david/david_project/知识库/books/华为数据之道.pdf")
IMAGES_DIR = BASE_DIR / "images"
FIGURE_NAME = "图 2-1"
OUTPUT_FILENAME = "图2-1.png"

# Load environment variables
load_dotenv(Path("/Users/david/david_project/.env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_page_image(page_idx, rotate=0):
    """Gets a high-res image of the page, optionally rotated."""
    doc = fitz.open(PDF_PATH)
    page = doc.load_page(page_idx)
    
    # Increase zoom for better quality
    zoom = 3 
    mat = fitz.Matrix(zoom, zoom)
    if rotate:
        # fitz rotation is in degrees clockwise
        page.set_rotation(rotate)
        
    pix = page.get_pixmap(matrix=mat)
    img_path = Path(f"/tmp/temp_page_{page_idx}_rot{rotate}.png")
    pix.save(img_path)
    doc.close()
    return img_path

def find_target_page_visual():
    """Finds the page containing Figure 2-1 using Gemini Vision."""
    start_page = 38
    end_page = 43
    print(f"Visually searching for {FIGURE_NAME} between pages {start_page} and {end_page}...")

    doc = fitz.open(PDF_PATH)
    
    # We'll batch all candidate pages
    current_batch = []
    batch_indices = []
    
    for j in range(start_page, end_page + 1):
        page = doc.load_page(j)
        # Use low res for detection
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) 
        img_path = Path(f"/tmp/check_page_{j}.png")
        pix.save(img_path)
        current_batch.append(img_path)
        batch_indices.append(j)
    
    doc.close()
    
    prompt = f"Which of these pages contains the diagram labeled '{FIGURE_NAME}' (or 'Figure 2-1' or just '2-1')? Return ONLY the index number (0 to {len(batch_indices)-1}) of the image in the provided list. If none, return 'None'."
    
    contents = [types.Part.from_bytes(data=p.read_bytes(), mime_type="image/png") for p in current_batch]
    contents.append(types.Part.from_text(text=prompt))
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents
    )
    
    res_text = response.text.strip()
    print(f"Gemini page search response: {res_text}")
    
    match = re.search(r'\d+', res_text)
    if match:
        idx = int(match.group())
        if 0 <= idx < len(batch_indices):
            found_page = batch_indices[idx]
            print(f"Found {FIGURE_NAME} on page {found_page}")
            return found_page
            
    print("Could not visually find figure. Defaulting to 40.")
    return 40

def detect_and_crop(image_path, output_path):
    print(f"Detecting boundary for {FIGURE_NAME} on {image_path}...")
    with open(image_path, 'rb') as f:
        image_data = f.read()

    prompt = f"""
    Look at the image. It contains a large diagram titled '{FIGURE_NAME}' (or similar).
    
    Task: Identify the bounding box of the ENTIRE diagram content area.
    Include:
    - The main graphical elements.
    - All surrounding text labels, legends, and keys.
    - The Figure Caption at the bottom ('图 2-1 ...').
    
    Do NOT crop it too tightly. I want the full figure. 
    If there are multiple parts, include ALL of them in one big box.
    Exclude only the empty page margins and page headers/footers.
    
    Return ONLY the coordinates as [ymin, xmin, ymax, xmax] in 0-1000 scale.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/png"),
            types.Part.from_text(text=prompt)
        ]
    )

    match = re.search(r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]', response.text)
    if not match:
        print(f"Failed to detect boundary: {response.text}")
        return False

    ymin, xmin, ymax, xmax = map(int, match.groups())
    
    print(f"Detected coordinates: {ymin, xmin, ymax, xmax}")

    img = Image.open(image_path)
    w, h = img.size
    left = xmin * w / 1000
    top = ymin * h / 1000
    right = xmax * w / 1000
    bottom = ymax * h / 1000
    
    # Add a small padding
    margin = 20
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(w, right + margin)
    bottom = min(h, bottom + margin)

    img.crop((left, top, right, bottom)).save(output_path)
    print(f"Saved cropped image to {output_path}")
    return True

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # User said current (+90 CW) needs -90 CCW to be normal.
    # So correct rotation from PDF is 0.
    page_idx = 39 
    
    print(f"Extracting page {page_idx} with 0 degree rotation...")
    doc = fitz.open(PDF_PATH)
    page = doc.load_page(page_idx)
    zoom = 3
    mat = fitz.Matrix(zoom, zoom)
    # 0 rotation
    pix = page.get_pixmap(matrix=mat)
    img_path = Path("/tmp/page_39_rot0.png")
    pix.save(img_path)
    doc.close()
    
    output_path = IMAGES_DIR / OUTPUT_FILENAME
    
    print(f"Detecting architecture diagram on {img_path}...")
    with open(img_path, 'rb') as f:
        image_data = f.read()

    # Precise prompt to remove irrelevant text
    prompt = """
    Identify the bounding box of the ARCHITECTURE DIAGRAM in this image.
    
    A "Architecture Diagram" here is the structured flow-chart/block-diagram part.
    Exclude:
    - Running text paragraphs above or below the diagram.
    - Page headers, footers, and page numbers.
    - Any textual content that is NOT part of the diagram box itself.
    
    Include:
    - The diagram graphics.
    - Labels INSIDE or immediately attached to the blocks.
    - The Figure Caption ('图 2-1 华为数据治理体系框架').
    
    Return ONLY the coordinates as [ymin, xmin, ymax, xmax] in 0-1000 scale.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/png"),
            types.Part.from_text(text=prompt)
        ]
    )

    # Improved parsing to handle JSON blocks or raw lists
    match = re.search(r'\[\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\]', response.text)
    if not match:
        # Try a more broad search for 4 numbers in brackets
        match = re.search(r'\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]', response.text, re.DOTALL)
        
    if not match:
        print(f"Failed to detect boundary: {response.text}")
        return

    ymin, xmin, ymax, xmax = map(int, match.groups())
    print(f"Detected coordinates: {ymin, xmin, ymax, xmax}")

    img = Image.open(img_path)
    w, h = img.size
    left = xmin * w / 1000
    top = ymin * h / 1000
    right = xmax * w / 1000
    bottom = ymax * h / 1000
    
    # Small margin
    pad = 20
    img.crop((max(0, left-pad), max(0, top-pad), min(w, right+pad), min(h, bottom+pad))).save(output_path)
    print(f"Saved refined image to {output_path}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
