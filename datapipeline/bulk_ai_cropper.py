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
HIGH_RES_DIR = Path("/Users/david/david_project/datapipeline/high_res")
TOC_OFFSETS = {
    1: 2, 2: 18, 3: 35, 4: 74, 5: 98, 6: 142, 7: 202, 8: 228, 9: 258, 10: 282
}
PDF_OFFSET = 21  # PDF Index = Printed Page + 21

load_dotenv(Path("/Users/david/david_project/.env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_pdf_page_index(chapter_num):
    return TOC_OFFSETS.get(chapter_num, 0) + PDF_OFFSET

def extract_high_res_page(page_idx):
    output_path = HIGH_RES_DIR / f"page_{page_idx + 1:03}.png"
    if output_path.exists():
        return output_path
    
    HIGH_RES_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    page = doc.load_page(page_idx)
    zoom = 4
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pix.save(output_path)
    doc.close()
    return output_path

def find_figure_on_pages(figure_name, start_idx, end_idx):
    """Ask Gemini which page in the range contains the figure."""
    doc = fitz.open(PDF_PATH)
    # We'll check 5 pages at a time to be efficient
    for i in range(start_idx, end_idx + 1, 5):
        current_batch = []
        batch_indices = []
        for j in range(i, min(i + 5, end_idx + 1)):
            page = doc.load_page(j)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) # low res for detection
            img_path = Path(f"/tmp/check_page_{j}.png")
            pix.save(img_path)
            current_batch.append(img_path)
            batch_indices.append(j)
        
        prompt = f"Which of these pages contains the diagram labeled '{figure_name}'? Return ONLY the page number (1, 2, 3, 4, or 5 corresponding to the order of images) or 'None'."
        
        contents = [types.Part.from_bytes(data=p.read_bytes(), mime_type="image/png") for p in current_batch]
        contents.append(types.Part.from_text(text=prompt))
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents
        )
        
        res_text = response.text.strip()
        if res_text.isdigit():
            idx = int(res_text) - 1
            if 0 <= idx < len(batch_indices):
                doc.close()
                return batch_indices[idx]
                
    doc.close()
    return None

def detect_and_crop(image_path, figure_name, output_path):
    print(f"Detecting boundary for {figure_name} on {image_path}...")
    with open(image_path, 'rb') as f:
        image_data = f.read()

    prompt = f"""
    Find the bounding box of the entire figure labeled '{figure_name}'. 
    The bounding box must include:
    1. The visual diagram/graphic itself.
    2. All associated labels, text boxes, and legends.
    3. The figure caption text (e.g., '{figure_name} xxx').
    
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
        print(f"Failed to detect boundary for {figure_name}: {response.text}")
        return False

    ymin, xmin, ymax, xmax = map(int, match.groups())
    
    img = Image.open(image_path)
    w, h = img.size
    left = xmin * w / 1000
    top = ymin * h / 1000
    right = xmax * w / 1000
    bottom = ymax * h / 1000
    
    margin = 35
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(w, right + margin)
    bottom = min(h, bottom + margin)

    img.crop((left, top, right, bottom)).save(output_path)
    print(f"Saved cropped {figure_name} to {output_path}")
    return True

def process_chapters():
    for ch in range(2, 11):
        filename = f"chapter-{ch:02}-detailed.md"
        md_path = BASE_DIR / filename
        if not md_path.exists(): continue
        
        print(f"Processing {filename}...")
        content = md_path.read_text()
        figures = sorted(list(set(re.findall(r'图\s*' + str(ch) + r'-\d+', content))))
        
        if not figures: continue
        
        start_idx = get_pdf_page_index(ch)
        next_ch_idx = get_pdf_page_index(ch + 1) if ch < 10 else 321
        end_idx = min(start_idx + 40, next_ch_idx + 5) # reasonable buffer
        
        for fig in figures:
            fig_clean = fig.replace(" ", "")
            output_img = IMAGES_DIR / f"{fig_clean}.png"
            
            if output_img.exists():
                print(f"Skipping {fig}, already exists.")
                # Ensure it's linked
                if f"![{fig}](images/{fig_clean}.png)" not in content:
                    content = content.replace(fig, f"![{fig}](images/{fig_clean}.png)")
                continue

            page_idx = find_figure_on_pages(fig, start_idx, end_idx)
            if page_idx is not None:
                high_res_page = extract_high_res_page(page_idx)
                if detect_and_crop(high_res_page, fig, output_img):
                    content = content.replace(fig, f"![{fig}](images/{fig_clean}.png)")
        
        md_path.write_text(content)

if __name__ == "__main__":
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    process_chapters()
