# PDF 图像提取工具 (PDF Image Extraction Tool)

本工具旨在自动化从 PDF 书籍中提取高质量的图片（如架构图、流程图），并将其链接到 Markdown 章节文件中。它利用 Google Gemini Flash 模型智能识别并裁剪图片。

## 工作原理

1. **扫描 Markdown**: 读取 `chapter-XX-detailed.md` 文件，查找类似于 `图 2-1` 的图片引用。
2. **定位 PDF 页面**: 询问 Gemini "哪一页包含了 '图 2-1'？"，在相关的 PDF 页面范围内进行搜索。
3. **提取与裁剪**: 
   - 将识别出的 PDF 页面渲染为高分辨率图像。
   - 询问 Gemini "找到 '图 2-1' 的边界框 (Bounding Box)"。
   - 使用 Pillow 库根据边界框裁剪图片。
4. **更新 Markdown**: 将裁剪后的图片保存到 `images/` 目录，并更新 Markdown 文件以显示该图片。

## 前置条件

- **Python 3**
- **依赖库**: `google-genai`, `pymupdf` (fitz), `Pillow`, `python-dotenv`
- **Gemini API Key**: 必须在 `.env` 文件中配置 `GEMINI_API_KEY`。
- **源 PDF**: 默认为 `/Users/david/david_project/知识库/books/华为数据之道.pdf`

## 使用方法

在项目根目录或 `datapipeline` 目录下运行脚本：

```bash
# 处理特定章节 (例如：第2章)
python datapipeline/extract_images_from_pdf.py --chapter 2

# 处理所有章节 (默认 2-10 章)
python datapipeline/extract_images_from_pdf.py

# 指定自定义路径
python datapipeline/extract_images_from_pdf.py --chapter 2 --pdf /path/to/book.pdf
```

## 目录结构

默认使用情况下的预期结构：
```
project/
├── .env                    # 包含 GEMINI_API_KEY
├── datapipeline/
│   └── extract_images_from_pdf.py
├── 智能体/数据治理/参考文档/数据之道/
│   ├── chapter-01-detailed.md
│   ├── chapter-02-detailed.md
│   └── images/             # 提取的图片将保存于此
```

## 算法优化说明

针对图片裁剪不完整（只截取到标题）的问题，我们优化了 AI 提示词 (Prompt)：
- **强调视觉内容**: 明确指示 AI 寻找“主要视觉内容”、“图表”、“架构图”，而不仅仅是文本标签。
- **相对位置提示**: 明确告知 AI，如果标题在下方，图表通常在上方；反之亦然。
- **完整性**: 要求包含所有的图例、标注和说明文字。
