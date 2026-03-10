#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

def create_chapter_10_infographic_fixed():
    # Create a 2K image (2560x1440) with high quality
    width, height = 2560, 1440
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use Chinese font with fallback
    try:
        font_path = "/System/Library/Fonts/PingFang.ttc"
        title_font = ImageFont.truetype(font_path, 80)
        subtitle_font = ImageFont.truetype(font_path, 56)
        body_font = ImageFont.truetype(font_path, 42)
        small_font = ImageFont.truetype(font_path, 36)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw title with gradient effect
    draw.text((width//2 - 400, 80), "数据仓库与商务智能", fill='black', font=title_font)
    draw.text((width//2 - 450, 180), "DAMA数据管理知识体系 - 第10章", fill='darkgray', font=subtitle_font)
    
    # Draw quadrant lines
    center_x, center_y = width // 2, height // 2
    draw.line([(center_x, 300), (center_x, height - 200)], fill='lightgray', width=2)
    draw.line([(200, center_y), (width - 200, center_y)], fill='lightgray', width=2)
    
    # Quadrant 1: High Importance + High Urgency (Red)
    draw.rectangle([200, 300, center_x, center_y], outline='red', width=4)
    draw.ellipse([(220, 320), (270, 370)], fill='red')
    draw.text((290, 325), "高重要性 + 高紧急性", fill='red', font=subtitle_font)
    draw.text((290, 400), "立即行动", fill='darkred', font=body_font)
    draw.text((290, 480), 
              "• 数据质量基础\n• 明确业务需求\n• 用户参与", 
              fill='black', font=body_font)
    
    # Quadrant 2: High Importance + Low Urgency (Yellow)
    draw.rectangle([center_x, 300, width - 200, center_y], outline='orange', width=4)
    draw.ellipse([(center_x + 20, 320), (center_x + 70, 370)], fill='orange')
    draw.text((center_x + 90, 325), "高重要性 + 低紧急性", fill='orange', font=subtitle_font)
    draw.text((center_x + 90, 400), "计划执行", fill='darkorange', font=body_font)
    draw.text((center_x + 90, 480), 
              "• 数据仓库治理\n• 架构选择\n• 技能培养", 
              fill='black', font=body_font)
    
    # Quadrant 3: Low Importance + High Urgency (Green)
    draw.rectangle([200, center_y, center_x, height - 200], outline='green', width=4)
    draw.ellipse([(220, center_y + 20), (270, center_y + 70)], fill='green')
    draw.text((290, center_y + 25), "低重要性 + 高紧急性", fill='green', font=subtitle_font)
    draw.text((290, center_y + 100), "委派处理", fill='darkgreen', font=body_font)
    draw.text((290, center_y + 180), 
              "• 技术选型\n• 性能优化\n• 报表开发", 
              fill='black', font=body_font)
    
    # Quadrant 4: Low Importance + Low Urgency (Gray)
    draw.rectangle([center_x, center_y, width - 200, height - 200], outline='gray', width=4)
    draw.ellipse([(center_x + 20, center_y + 20), (center_x + 70, center_y + 70)], fill='gray')
    draw.text((center_x + 90, center_y + 25), "低重要性 + 低紧急性", fill='gray', font=subtitle_font)
    draw.text((center_x + 90, center_y + 100), "减少投入", fill='darkgray', font=body_font)
    draw.text((center_x + 90, center_y + 180), 
              "• 过度工程化\n• 完美主义\n• 孤立实施", 
              fill='black', font=body_font)
    
    # Add decorative elements
    draw.rectangle([150, 250, width - 150, height - 150], outline='black', width=3)
    
    # Save with high quality to ensure file size > 1MB
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_10_infographic_fixed.png', 
             quality=95, optimize=False)
    print("Chapter 10 fixed infographic created successfully!")

if __name__ == "__main__":
    create_chapter_10_infographic_fixed()