import docx

# 读取Target文档
doc = docx.Document('/Users/zhaoqinhuang/.openclaw/media/inbound/Target零售巨头数据泄露事件案例深度分析---4e1203af-573d-4e78-8821-06538b0beafc.docx')

# 提取所有文本
full_text = []
for paragraph in doc.paragraphs:
    if paragraph.text.strip():
        full_text.append(paragraph.text)

print('\n'.join(full_text))