
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
            
def analyze_page_content(image_path):
    print(f"Analyzing content of {image_path}...")
    with open(image_path, 'rb') as f:
        image_data = f.read()

    prompt = """
    Describe this image in detail. 
    1. Is there a large diagram or chart? Describe it.
    2. Is there text "Figure 2-1" or "图 2-1"? Where is it?
    3. What is the orientation of the text? Is it upright, or rotated?
    4. What are the approximate coordinates (0-1000 scale) of the MAIN DIAGRAM excluding the caption?
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/png"),
            types.Part.from_text(text=prompt)
        ]
    )
    print("--- Analysis ---")
    print(response.text)
    print("----------------")
    Path("debug_analysis.txt").write_text(response.text)
    return response.text

def detect_and_crop(image_path, output_path):
    print(f"Detecting boundary for {FIGURE_NAME} on {image_path}...")
    with open(image_path, 'rb') as f:
        image_data = f.read()

    prompt = f"""
    Find the bounding box of the architecture diagram labeled '{FIGURE_NAME}'. 
    The bounding box must include:
    1. The main architectural diagram.
    2. All labels, legends, and text boxes belonging to the diagram.
    3. The figure caption '图 2-1 华为数据治理体系框架'.
    
    Ensure the box is wide and tall enough to encompass every element without clipping.
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
    
    # Hardcode page 39
    page_idx = 39
    img_rot90 = get_page_image(page_idx, rotate=90)
    
    print("Analyzing Rotated 90 image:")
    analyze_page_content(img_rot90)

if __name__ == "__main__":
    main()
