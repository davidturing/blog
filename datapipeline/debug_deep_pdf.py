import os
from pypdf import PdfReader

pdf_path = "知识库/books/华为数据之道.pdf"

try:
    reader = PdfReader(pdf_path)
    print(f"Number of pages: {len(reader.pages)}")
    
    if len(reader.pages) > 50:
        page = reader.pages[50]
        text_layout = page.extract_text(extraction_mode="layout")
        text_plain = page.extract_text(extraction_mode="plain")
        
        print(f"Page 50 (Layout) Length: {len(text_layout)}")
        print(f"Page 50 (Plain) Length: {len(text_plain)}")
        
        if text_layout:
             print(f"Preview (Layout): {text_layout[:200]}")
    else:
        print("PDF has fewer than 50 pages.")

except Exception as e:
    print(f"Error reading PDF: {e}")
