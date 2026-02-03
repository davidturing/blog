import os
import re
import fitz
import argparse
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Default Configuration
DEFAULT_BASE_DIR = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道")
DEFAULT_PDF_PATH = Path("/Users/david/david_project/知识库/books/华为数据之道.pdf")
DEFAULT_IMAGES_DIR_NAME = "images"
DEFAULT_HIGH_RES_DIR = Path("/Users/david/david_project/datapipeline/high_res")

# Table of Contents Offsets (Chapter Number -> PDF Page Index relative to start)
# Note: These might need adjustment if the PDF structure changes
TOC_OFFSETS = {
    1: 2, 2: 18, 3: 35, 4: 74, 5: 98, 6: 142, 7: 202, 8: 228, 9: 258, 10: 282
}
PDF_OFFSET = 21  # PDF Index = Printed Page + 21

def get_pdf_page_index(chapter_num):
    return TOC_OFFSETS.get(chapter_num, 0) + PDF_OFFSET

def extract_high_res_page(doc, page_idx, output_dir):
    output_path = output_dir / f"page_{page_idx + 1:03}.png"
    if output_path.exists():
        return output_path
    
    output_dir.mkdir(parents=True, exist_ok=True)
    page = doc.load_page(page_idx)
    zoom = 4
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pix.save(output_path)
    return output_path

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=4, max=60))
def find_figure_on_pages(client, doc, figure_name, start_idx, end_idx):
    """Ask Gemini which page in the range contains the figure."""
    # We'll check 5 pages at a time to be efficient
    for i in range(start_idx, end_idx + 1, 5):
        current_batch = []
        batch_indices = []
        for j in range(i, min(i + 5, end_idx + 1)):
            try:
                page = doc.load_page(j)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) # low res for detection
                # Use a temp directory or in-memory, but for simplicity saving to tmp
                img_path = Path(f"/tmp/check_page_{j}.png") 
                pix.save(img_path)
                current_batch.append(img_path)
                batch_indices.append(j)
            except Exception as e:
                print(f"Error loading page {j}: {e}")
                continue
        
        if not current_batch:
            continue

        prompt = f"Which of these pages contains the diagram labeled '{figure_name}'? Return ONLY the page number (1, 2, 3, 4, or 5 corresponding to the order of images) or 'None'."
        
        try:
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
                    return batch_indices[idx]
        except Exception as e:
            # Re-raise for tenacity to handle (unless it's a non-retriable error, but assuming all are for now)
            print(f"Error calling Gemini API checking pages {batch_indices}: {e}")
            raise e 
            
    return None

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=4, max=60))
def detect_and_crop(client, image_path, figure_name, output_path):
    print(f"Detecting boundary for {figure_name} on {image_path}...")
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        prompt = f"""
        Find the bounding box of the entire figure labeled '{figure_name}'. 
        
        CRITICAL SPATIAL REASONING:
        1. **LOCATE CAPTION**: First, find the text '{figure_name}' (e.g., "图 2-4 xxx"). This is the CAPTION.
        2. **LOOK UPWARDS**: The actual diagram/chart is the large visual element located **ABOVE** this caption.
           - The text is just the bottom anchor.
           - The bounding box must extend UPWARDS to include the entire graphical diagram.
        
        CRITICAL RULES:
        1. **INCLUDE EVERYTHING**: The box must include the Diagram + Legends + Axis Labels + The Caption itself.
        2. **HEIGHT CHECK**: The diagram is usually large. If your box height (ymax - ymin) is small (e.g., < 100), YOU ARE WRONG. You likely only selected the text.
           - You MUST select the large graphic above the text.
        3. **EXACT MATCH**: Ensure you are looking at the caption for '{figure_name}' and not a neighbor.
        
        Return ONLY the coordinates as [ymin, xmin, ymax, xmax] in 0-1000 scale.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_data, mime_type="image/png"),
                types.Part.from_text(text=prompt)
            ]
        )

        # Try to find the list pattern [y, x, y, x] anywhere in the text
        # Handles [1, 2, 3, 4] and ["1, 2, 3, 4"] and other variations
        match = re.search(r'\[\s*"?(\d+)"?,\s*"?(\d+)"?,\s*"?(\d+)"?,\s*"?(\d+)"?\s*\]', response.text)
        if not match:
            # Fallback for single string "y, x, y, x" inside brackets (quoted or not)
            # Matches ["1, 2, 3, 4"] or [1, 2, 3, 4] where the commas are inside the capture groups effectively
            # Actually simpler: just find 4 numbers in the text if strict patterns fail
            match = re.search(r'\[\s*"?(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)"?\s*\]', response.text)
            
        if not match:
            # Ultimate fallback: just find the first 4 integers in the response that look like coordinates
            # This is risky but better than failing if the format is slightly off
            numbers = re.findall(r'\d+', response.text)
            if len(numbers) >= 4:
                # Take first 4
                match = re.match(r'()', '') # dummy match to set groups
                # We can't easily fake a match object with groups, so we'll handle manual assignment
                ymin, xmin, ymax, xmax = map(int, numbers[:4])
                # Skip the match.groups() call below
            else:
                print(f"Failed to detect boundary for {figure_name}: {response.text}")
                return False
        else:
            ymin, xmin, ymax, xmax = map(int, match.groups())
            
        print(f"DEBUG: Raw Coords for {figure_name}: [{ymin}, {xmin}, {ymax}, {xmax}]")
        
        # VALIDATION: Reject garbage (e.g., [2, 6, 2, 4])
        # If the box is tiny in BOTH dimensions, it's just noise.
        if (xmax - xmin) < 20 or (ymax - ymin) < 20:
             raise ValueError(f"Detected coordinates are garbage/too small: [{ymin}, {xmin}, {ymax}, {xmax}]")

        # HEURISTIC: Check for "Caption Only" detection
        # If height is small (e.g. < 150), assume model found only the caption and force-expand UPWARDS.
        box_height = ymax - ymin
        if box_height < 150: # Increased threshold to 15%
            print(f"WARNING: Box height {box_height} is too small. Assuming caption-only detection. Expanding UPWARDS and HORIZONTALLY (FULL WIDTH).")
            # Move top up by 250 units (Reduced from 350 to reduce whitespace)
            ymin = max(0, ymin - 250)
            # FORCE FULL WIDTH to avoid any horizontal truncation
            xmin = 0
            xmax = 1000
            
        print(f"DEBUG: Adjusted Coords for {figure_name}: [{ymin}, {xmin}, {ymax}, {xmax}]")
        
        img = Image.open(image_path)
        w, h = img.size
        # Convert 1000-scale to pixels
        left = xmin * w / 1000
        top = ymin * h / 1000
        right = xmax * w / 1000
        bottom = ymax * h / 1000
        
        # AGGRESSIVE MARGIN
        margin = 50 # Reduced from 100 since we are expanding logic elsewhere
        left = max(0, left - margin)
        top = max(0, top - margin)
        right = min(w, right + margin)
        bottom = min(h, bottom + margin)

        img.crop((left, top, right, bottom)).save(output_path)
        print(f"Saved cropped {figure_name} to {output_path}")
        return True
    except Exception as e:
        # Re-raise for tenacity
        print(f"Error in detect_and_crop: {e}")
        raise e

def cleanup_markdown_links(content):
    """
    Fixes nested/duplicate markdown image links.
    """
    # 1. Remove lines that are purely `![`
    content = re.sub(r'^\s*!\[\s*$', '', content, flags=re.MULTILINE)
    
    # 2. Remove lines that look like `](images/...)`
    content = re.sub(r'^\s*\]\(images/.*?\)\s*$', '', content, flags=re.MULTILINE)
    
    # 3. Fix nested links: ![Desc](images/![Desc](Path).png) -> ![Desc](Path)
    # This happens when the script replaces the text inside the link path
    # Regex: !\[(.*?)\]\(images/!\[.*?\]\((.*?)\)\.png\)
    # We capture the description (group 1) and the real path (group 2)
    # Note: escaping [ and (
    pattern = r'!\[(.*?)\]\(images/!\[.*?\]\((.*?)\)\.png\)'
    content = re.sub(pattern, r'![\1](\2)', content)

    # 4. Remove recursive brackets from previous failures like `](images/![...](...).png)`
    # Sometimes it leaves trailing `)` or `.png)`
    
    return content

def process_chapter(chapter_num, base_dir, pdf_path, high_res_dir, client, target_figure=None):
    filename = f"chapter-{chapter_num:02}-detailed.md"
    md_path = base_dir / filename
    if not md_path.exists():
        print(f"Markdown file not found: {md_path}")
        return

    # MANUAL OVERRIDES
    MANUAL_OVERRIDES = {
        "图 2-6": {"page": 54, "action": "full_page_rotate_cw"},
        "图2-6": {"page": 54, "action": "full_page_rotate_cw"},
        "图 2-1": {"page": 40, "action": "manual_crop", "box": [100, 0, 950, 1000]},
        "图2-1": {"page": 40, "action": "manual_crop", "box": [100, 0, 950, 1000]},
        
        # Chapter 5
        "图 5-1": {"page": 121, "action": "full_page_rotate_cw"},
        "图5-1": {"page": 121, "action": "full_page_rotate_cw"},

        # Chapter 7
        "图 7-2": {"page": 228, "action": "full_page_rotate_cw"},
        "图7-2": {"page": 228, "action": "full_page_rotate_cw"},
        "图 7-6": {"page": 233, "action": "full_page_rotate_cw"},
        "图7-6": {"page": 233, "action": "full_page_rotate_cw"},
        "图 7-10": {"page": 242, "action": "manual_crop", "box": [100, 0, 900, 1000]}, # Keep as crop/heuristic if needed, but wasn't requested for rotation. Wait, 7-10 was just regenerated successfully. User didn't ask to rotate 7-10.
        
        # Chapter 9
        "图 9-6": {"page": 292, "action": "full_page_rotate_cw"},
        "图9-6": {"page": 292, "action": "full_page_rotate_cw"},
        
        # Chapter 10
        "图 10-1": {"page": 310, "action": "full_page_rotate_cw"},
        "图10-1": {"page": 310, "action": "full_page_rotate_cw"},
    }
    
    print(f"Processing {filename}...")
    content = md_path.read_text()
    
    # CLEANUP FIRST
    content = cleanup_markdown_links(content)
    
    figures = sorted(list(set(re.findall(r'图\s*' + str(chapter_num) + r'-\d+', content))))
    
    if target_figure:
        # Filter figures if target specified
        # Normalize spaces for comparison
        target_clean = target_figure.replace(" ", "")
        figures = [f for f in figures if f.replace(" ", "") == target_clean]
        if not figures:
             print(f"Target figure '{target_figure}' not found in {filename}")
             return

    if not figures:
        print(f"No figures found in {filename}")
        return
    
    images_dir = base_dir / DEFAULT_IMAGES_DIR_NAME
    images_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)

    start_idx = get_pdf_page_index(chapter_num)
    # Estimate end index for search range
    next_ch_idx = get_pdf_page_index(chapter_num + 1) if chapter_num < 10 else 321
    end_idx = min(start_idx + 40, next_ch_idx + 5) # reasonable buffer
    
    for fig in figures:
        fig_clean = fig.replace(" ", "")
        output_img = images_dir / f"{fig_clean}.png"
        
        # Check if image already exists
        if output_img.exists():
            print(f"Skipping {fig}, already exists.")
            # Ensure it's correctly linked in MD
            link_str = f"![{fig}](images/{fig_clean}.png)"
            if link_str not in content:
                 # Replace the text "图 X-Y" with the image markdown
                 # CAUTIOUS REPLACE: Only replace if not already part of an image tag?
                 # ideally we want to replace the standalone text or a placeholder.
                 # The regex was simple, so we just replace the first occurrence or all.
                 # Let's replace only if it looks like a caption not already inside []()
                 if f"![{fig}]" not in content:
                    content = content.replace(fig, link_str)
            continue

        print(f"Searching for {fig} in PDF...")
        
        # CHECK OVERRIDES FIRST
        if fig in MANUAL_OVERRIDES:
            override = MANUAL_OVERRIDES[fig]
            page_num = override['page']
            action = override['action']
            print(f"Applying MANUAL OVERRIDE for {fig}: Page {page_num}, Action {action}")
            
            image_path = high_res_dir / f"page_{page_num:03d}.png"
            if not image_path.exists():
                print(f"Error: Override page image not found: {image_path}")
                continue
                
            if action == 'full_page_rotate_cw':
                try:
                    img = Image.open(image_path)
                    # Rotate 90 degrees Clockwise (which is 270 degrees CCW)
                    cropped_img = img.transpose(Image.ROTATE_270)
                    
                    safe_name = fig.replace(" ", "")
                    save_path = images_dir / f"{safe_name}.png"
                    cropped_img.save(save_path)
                    print(f"Saved OVERRIDE {fig} to {save_path}")
                    # Update md
                    link_str = f"\n![{fig}](images/{safe_name}.png)\n"
                    content = content.replace(fig, link_str)
                except Exception as e:
                    print(f"Failed to apply override for {fig}: {e}")
            
            elif action == 'manual_crop':
                try:
                    img = Image.open(image_path)
                    box = override['box'] # [ymin, xmin, ymax, xmax] 0-1000
                    ymin, xmin, ymax, xmax = box
                    w, h = img.size
                    left = xmin * w / 1000
                    top = ymin * h / 1000
                    right = xmax * w / 1000
                    bottom = ymax * h / 1000
                    
                    cropped_img = img.crop((left, top, right, bottom))
                    
                    safe_name = fig.replace(" ", "")
                    save_path = images_dir / f"{safe_name}.png"
                    cropped_img.save(save_path)
                    print(f"Saved OVERRIDE {fig} to {save_path}")
                    # Update md
                    link_str = f"\n![{fig}](images/{safe_name}.png)\n"
                    content = content.replace(fig, link_str)
                except Exception as e:
                    print(f"Failed to apply override for {fig}: {e}")
                    # The original code had `results[fig] = save_path` here.
                    # Assuming `results` is meant to be a dictionary to store paths.
                    # If `results` is not defined elsewhere, it should be initialized.
                    # For now, I'll assume it's a local variable that should be defined.
                    # However, the provided snippet has `results = {}[fig] = save_path` which is a syntax error.
                    # I will define `results` as an empty dict at the start of the function if it's meant to collect all results.
                    # But given the context, it seems `results` was intended to be a local variable for this specific override block.
                    # Since the user's instruction is only to define MANUAL_OVERRIDES, and the provided snippet has a syntax error
                    # with `results = {}[fig] = save_path`, I will omit that line and assume `results` is handled elsewhere or not needed here.
                    # If `results` is indeed needed, the user should provide a correct definition.
                    # For now, I'll just ensure the MANUAL_OVERRIDES definition is correct and placed appropriately.
                except Exception as e:
                    print(f"Failed to apply override for {fig}: {e}")
            continue

        # Standard AI Search Logic
        page_idx = find_figure_on_pages(client, doc, figure_name=fig, start_idx=start_idx, end_idx=end_idx)
        
        if page_idx is not None:
            print(f"Found {fig} on page {page_idx + 1}")
            high_res_page = extract_high_res_page(doc, page_idx, high_res_dir)
            if detect_and_crop(client, high_res_page, fig, output_img):
                # Update markdown
                link_str = f"\n![{fig}](images/{fig_clean}.png)\n"
                # We replace the text occurrence. 
                # Note: This simple replacement might be aggressive if the text appears multiple times.
                # Assuming the "图 X-Y" text appears as a caption below/above where the image should be.
                content = content.replace(fig, link_str)
        else:
            print(f"Could not find {fig} in PDF range {start_idx}-{end_idx}")

    doc.close()
    md_path.write_text(content)
    print(f"Finished processing {filename}")

def main():
    parser = argparse.ArgumentParser(description="Extract figures from PDF based on markdown references.")
    parser.add_argument("--chapter", type=int, help="Chapter number to process (e.g., 2)")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF_PATH, help="Path to source PDF")
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR, help="Base directory containing markdown chapters")
    parser.add_argument("--high-res-dir", type=Path, default=DEFAULT_HIGH_RES_DIR, help="Directory to store temporary high-res PDF page images")
    parser.add_argument("--figure", type=str, help="Specific figure to process (e.g., '图 2-4')")
    
    args = parser.parse_args()
    
    # Load Environment
    load_dotenv(Path("/Users/david/david_project/.env"))
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    
    if args.chapter:
        process_chapter(args.chapter, args.base_dir, args.pdf, args.high_res_dir, client, target_figure=args.figure)
    else:
        # Process all chapters 2-10 if not specified (or whatever default range)
        for ch in range(2, 11):
             process_chapter(ch, args.base_dir, args.pdf, args.high_res_dir, client, target_figure=args.figure)

if __name__ == "__main__":
    main()
