
import fitz
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path

PDF_PATH = Path("/Users/david/david_project/知识库/books/华为数据之道.pdf")
OUTPUT_PATH = Path("/Users/david/david_project/智能体/数据治理/参考文档/数据之道/images/图2-1.png")
PAGE_IDX = 39

def crop_content(page_idx):
    doc = fitz.open(PDF_PATH)
    page = doc.load_page(page_idx)
    
    # Render high res
    zoom = 3
    mat = fitz.Matrix(zoom, zoom)
    page.set_rotation(90) # Clockwise 90
    pix = page.get_pixmap(matrix=mat)
    
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Convert to grayscale
    gray = img.convert("L")
    
    # Threshold to binary (ink is black=0, paper is white=255)
    # Invert so ink is white for bbox
    inverted = ImageOps.invert(gray)
    
    # Get bounding box of all "ink"
    bbox = inverted.getbbox()
    
    if bbox:
        print(f"Original Content BBox: {bbox}")
        # bbox is (left, top, right, bottom)
        
        # We likely want to ignore page headers/footers.
        # Let's check aspect ratio or position.
        # If the bbox spans the whole height, it might include headers.
        # Let's try to remove top 5% and bottom 5% before finding bbox.
        
        w, h = img.size
        # Margin to exclude headers/footers
        margin_top = int(h * 0.08) 
        margin_bottom = int(h * 0.08)
        
        # Crop the inverted image to exclude headers
        roi = inverted.crop((0, margin_top, w, h - margin_bottom))
        
        # Find bbox in ROI
        roi_bbox = roi.getbbox()
        
        if roi_bbox:
            # Adjust bbox back to original coordinates
            # roi_bbox is relative to the crop
            final_left = roi_bbox[0]
            final_top = roi_bbox[1] + margin_top
            final_right = roi_bbox[2]
            final_bottom = roi_bbox[3] + margin_top
            
            # Add some padding
            pad = 20
            final_left = max(0, final_left - pad)
            final_top = max(0, final_top - pad)
            final_right = min(w, final_right + pad)
            final_bottom = min(h, final_bottom + pad)
            
            print(f"Final Crop Box: {final_left, final_top, final_right, final_bottom}")
            
            final_crop = img.crop((final_left, final_top, final_right, final_bottom))
            final_crop.save(OUTPUT_PATH)
            print(f"Saved to {OUTPUT_PATH}")
        else:
            print("No content found in ROI")
            # Fallback to original bbox
            img.crop(bbox).save(OUTPUT_PATH)
    else:
        print("Page seems empty?")
    
    doc.close()

if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    crop_content(PAGE_IDX)
