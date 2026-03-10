#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

def create_chapter_09_infographic():
    # Create a 2K image (2560x1440)
    width, height = 2560, 1440
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a Chinese font, fallback to default if not available
    try:
        # Try common Chinese fonts on macOS
        font_path = "/System/Library/Fonts/PingFang.ttc"
        title_font = ImageFont.truetype(font_path, 72)
        subtitle_font = ImageFont.truetype(font_path, 48)
        body_font = ImageFont.truetype(font_path, 36)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
    
    # Draw title
    draw.text((width//2 - 300, 100), "参考数据与主数据", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Reference Data Management section
    draw.rectangle([200, 350, 1100, 800], outline='blue', width=3)
    draw.text((300, 400), "参考数据管理", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• 定义与特征\n• 管理挑战\n• 最佳实践", fill='black', font=body_font)
    
    # Master Data Management section
    draw.rectangle([1360, 350, 2260, 800], outline='green', width=3)
    draw.text((1460, 400), "主数据管理", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 定义与范围\n• MDM架构\n• 实施方法", fill='black', font=body_font)
    
    # Integration section
    draw.rectangle([200, 900, 1100, 1300], outline='purple', width=3)
    draw.text((300, 950), "协同管理", fill='purple', font=subtitle_font)
    draw.text((300, 1030), "• 集成策略\n• 技术架构\n• 治理与合规", fill='black', font=body_font)
    
    # Success Metrics section
    draw.rectangle([1360, 900, 2260, 1300], outline='orange', width=3)
    draw.text((1460, 950), "成功度量", fill='orange', font=subtitle_font)
    draw.text((1460, 1030), "• 关键绩效指标\n• 持续改进循环", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_09_infographic.png')
    print("Chapter 09 infographic created successfully!")

def create_chapter_10_infographic():
    # Create a 2K image (2560x1440)
    width, height = 2560, 1440
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a Chinese font, fallback to default if not available
    try:
        font_path = "/System/Library/Fonts/PingFang.ttc"
        title_font = ImageFont.truetype(font_path, 72)
        subtitle_font = ImageFont.truetype(font_path, 48)
        body_font = ImageFont.truetype(font_path, 36)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
    
    # Draw title
    draw.text((width//2 - 300, 100), "数据仓库与商务智能", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Data Warehouse Architecture
    draw.rectangle([200, 350, 1100, 700], outline='blue', width=3)
    draw.text((300, 400), "数据仓库架构", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• 面向主题\n• 集成性\n• 非易失性\n• 时变性", fill='black', font=body_font)
    
    # BI Components
    draw.rectangle([1360, 350, 2260, 700], outline='green', width=3)
    draw.text((1460, 400), "商务智能组件", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 数据可视化\n• 报表系统\n• OLAP\n• 数据挖掘", fill='black', font=body_font)
    
    # Implementation Strategies
    draw.rectangle([200, 800, 1100, 1150], outline='purple', width=3)
    draw.text((300, 850), "实施策略", fill='purple', font=subtitle_font)
    draw.text((300, 930), "• 自上而下 vs 自下而上\n• 现代数据仓库架构", fill='black', font=body_font)
    
    # Governance & Best Practices
    draw.rectangle([1360, 800, 2260, 1150], outline='orange', width=3)
    draw.text((1460, 850), "治理与实践", fill='orange', font=subtitle_font)
    draw.text((1460, 930), "• 元数据管理\n• 数据质量监控\n• 安全管理\n• 变更管理", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_10_infographic.png')
    print("Chapter 10 infographic created successfully!")

# Add functions for other chapters similarly...

if __name__ == "__main__":
    create_chapter_09_infographic()
    create_chapter_10_infographic()
    print("Infographics generation completed!")