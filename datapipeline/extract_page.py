import fitz
import os

pdf_path = "/Users/david/david_project/知识库/books/华为数据之道.pdf"
output_path = "/Users/david/david_project/datapipeline/high_res/page_28.png"

doc = fitz.open(pdf_path)
# Let's try index 28 (PDF page 29)
page_num = 28
page = doc.load_page(page_num)

zoom = 4
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
pix.save(output_path)
print(f"Saved high-res page {page_num + 1} to {output_path}")
doc.close()
