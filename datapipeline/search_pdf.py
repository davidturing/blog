import fitz

pdf_path = "/Users/david/david_project/知识库/books/华为数据之道.pdf"
doc = fitz.open(pdf_path)

target = "图 1-3"
found = False

for i in range(len(doc)):
    page = doc.load_page(i)
    text = page.get_text()
    if target in text:
        print(f"Found '{target}' on page index {i} (PDF page {i+1})")
        found = True
        # Don't break, find all occurrences to pick the right one (first is usually the diagram caption or reference)

if not found:
    print(f"'{target}' not found in PDF")
doc.close()
