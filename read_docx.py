import docx
import sys

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

if __name__ == "__main__":
    file_path = "/Users/zhaoqinhuang/.openclaw/media/inbound/Knight_Capital_僵尸代码_事故案例分析研究---51c468e9-4df3-4c77-b568-f876ac05f40e.docx"
    content = read_docx(file_path)
    print(content)