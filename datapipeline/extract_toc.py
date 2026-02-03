import fitz
import os

pdf_path = "/Users/david/david_project/知识库/books/华为数据之道.pdf"
output_dir = "/Users/david/david_project/datapipeline/toc_images"
os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)
for i in range(min(20, len(doc))):
    page = doc.load_page(i)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    pix.save(os.path.join(output_dir, f"page_{i+1:03}.png"))
doc.close()
print(f"Extracted first 20 pages to {output_dir}")
