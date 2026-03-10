from PIL import Image, ImageDraw, ImageFont
import os

# Create a blueprint-style placeholder image
width, height = 1024, 768
img = Image.new('RGB', (width, height), color='#f0f8ff')  # Light blue background
draw = ImageDraw.Draw(img)

# Try to use a default font, fallback to default if not available
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw title
title = "第6章：数据存储与操作"
draw.text((50, 50), title, fill="#003366", font=font_large)

# Draw subtitle
subtitle = "Blueprint 配图 - 待生成完整版本"
draw.text((50, 120), subtitle, fill="#666666", font=font_medium)

# Draw key elements
elements = [
    "• ACID vs BASE vs CAP 定理",
    "• 数据库类型演进",
    "• DBRE 可靠性工程",
    "• DataOps 工业化流水线", 
    "• RAG 向量存储需求",
    "• 云存储 FinOps 成本管理",
    "• GitLab 事故案例复盘",
    "• AI 时代存储治理挑战"
]

y_pos = 200
for element in elements:
    draw.text((50, y_pos), element, fill="#003366", font=font_small)
    y_pos += 30

# Draw border
draw.rectangle([10, 10, width-10, height-10], outline="#003366", width=3)

# Save the image
output_path = "/Users/zhaoqinhuang/david_project/tech/damabook/chapter_06_blueprint.png"
img.save(output_path, "PNG")
print(f"Placeholder image created: {output_path}")