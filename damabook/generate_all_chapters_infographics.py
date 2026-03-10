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

def create_chapter_11_infographic():
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
    draw.text((width//2 - 200, 100), "元数据管理", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Metadata Types
    draw.rectangle([200, 350, 1100, 750], outline='blue', width=3)
    draw.text((300, 400), "元数据类型", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• 业务元数据\n• 技术元数据\n• 操作元数据\n• 管理元数据", fill='black', font=body_font)
    
    # Management Framework
    draw.rectangle([1360, 350, 2260, 750], outline='green', width=3)
    draw.text((1460, 400), "管理框架", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 管理策略\n• 核心流程\n• 技术架构", fill='black', font=body_font)
    
    # Best Practices
    draw.rectangle([200, 850, 1100, 1250], outline='purple', width=3)
    draw.text((300, 900), "最佳实践", fill='purple', font=subtitle_font)
    draw.text((300, 980), "• 渐进式实施\n• 自动化与人工结合\n• 用户参与\n• 与治理集成", fill='black', font=body_font)
    
    # Future Trends
    draw.rectangle([1360, 850, 2260, 1250], outline='orange', width=3)
    draw.text((1460, 900), "未来趋势", fill='orange', font=subtitle_font)
    draw.text((1460, 980), "• 智能元数据管理\n• 主动元数据管理\n• 元数据即服务", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_11_infographic.png')
    print("Chapter 11 infographic created successfully!")

def create_chapter_12_infographic():
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
    draw.text((width//2 - 200, 100), "数据质量", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Quality Dimensions
    draw.rectangle([200, 350, 1100, 750], outline='blue', width=3)
    draw.text((300, 400), "质量维度", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• 准确性\n• 完整性\n• 一致性\n• 及时性\n• 唯一性\n• 有效性", fill='black', font=body_font)
    
    # Assessment Methods
    draw.rectangle([1360, 350, 2260, 750], outline='green', width=3)
    draw.text((1460, 400), "评估方法", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 数据剖析\n• 质量规则定义\n• 指标监控\n• 根本原因分析", fill='black', font=body_font)
    
    # Improvement Strategies
    draw.rectangle([200, 850, 1100, 1250], outline='purple', width=3)
    draw.text((300, 900), "改进策略", fill='purple', font=subtitle_font)
    draw.text((300, 980), "• 预防性措施\n• 纠正性措施\n• 持续改进", fill='black', font=body_font)
    
    # Business Value
    draw.rectangle([1360, 850, 2260, 1250], outline='orange', width=3)
    draw.text((1460, 900), "业务价值", fill='orange', font=subtitle_font)
    draw.text((1460, 980), "• 提升决策质量\n• 增强客户体验\n• 降低合规风险\n• 提高运营效率", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_12_infographic.png')
    print("Chapter 12 infographic created successfully!")

def create_chapter_13_infographic():
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
    draw.text((width//2 - 300, 100), "数据管理成熟度评估", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Maturity Models
    draw.rectangle([200, 350, 1100, 700], outline='blue', width=3)
    draw.text((300, 400), "成熟度模型", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• CMMI扩展\n• DCAM模型\n• DAMA-DMBOK框架", fill='black', font=body_font)
    
    # Assessment Dimensions
    draw.rectangle([1360, 350, 2260, 700], outline='green', width=3)
    draw.text((1460, 400), "评估维度", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 战略与治理\n• 流程与方法\n• 技术与架构\n• 人员与技能\n• 文化与意识", fill='black', font=body_font)
    
    # Maturity Levels
    draw.rectangle([200, 800, 1100, 1150], outline='purple', width=3)
    draw.text((300, 850), "成熟度等级", fill='purple', font=subtitle_font)
    draw.text((300, 930), "• Level 0-1: 不存在/初始\n• Level 2-3: 已管理/已定义\n• Level 4-5: 量化管理/优化", fill='black', font=body_font)
    
    # Implementation Roadmap
    draw.rectangle([1360, 800, 2260, 1150], outline='orange', width=3)
    draw.text((1460, 850), "实施路线图", fill='orange', font=subtitle_font)
    draw.text((1460, 930), "• 短期行动(0-6月)\n• 中期行动(6-18月)\n• 长期行动(18-36月)", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_13_infographic.png')
    print("Chapter 13 infographic created successfully!")

def create_chapter_14_infographic():
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
    draw.text((width//2 - 300, 100), "组织与变革管理", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Organizational Models
    draw.rectangle([200, 350, 1100, 700], outline='blue', width=3)
    draw.text((300, 400), "组织模型", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• 集中式模型\n• 分散式模型\n• 联邦式模型(推荐)", fill='black', font=body_font)
    
    # Key Roles
    draw.rectangle([1360, 350, 2260, 700], outline='green', width=3)
    draw.text((1460, 400), "关键角色", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 首席数据官(CDO)\n• 数据治理委员会\n• 数据架构师\n• 数据管家\n• 数据工程师", fill='black', font=body_font)
    
    # Change Management
    draw.rectangle([200, 800, 1100, 1150], outline='purple', width=3)
    draw.text((300, 850), "变革管理", fill='purple', font=subtitle_font)
    draw.text((300, 930), "• ADKAR模型应用\n• 变革准备度评估\n• 沟通策略", fill='black', font=body_font)
    
    # Culture Building
    draw.rectangle([1360, 800, 2260, 1150], outline='orange', width=3)
    draw.text((1460, 850), "文化建设", fill='orange', font=subtitle_font)
    draw.text((1460, 930), "• 数据驱动文化特征\n• 文化建设策略\n• 能力建设", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_14_infographic.png')
    print("Chapter 14 infographic created successfully!")

def create_chapter_15_infographic():
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
    draw.text((width//2 - 200, 100), "CDMP认证指南", fill='black', font=title_font)
    draw.text((width//2 - 400, 200), "DAMA数据管理知识体系", fill='gray', font=subtitle_font)
    
    # Draw main content areas
    # Certification Overview
    draw.rectangle([200, 350, 1100, 700], outline='blue', width=3)
    draw.text((300, 400), "认证概述", fill='blue', font=subtitle_font)
    draw.text((300, 480), "• 认证价值\n• 四个级别\n• 全球认可", fill='black', font=body_font)
    
    # Exam Structure
    draw.rectangle([1360, 350, 2260, 700], outline='green', width=3)
    draw.text((1460, 400), "考试结构", fill='green', font=subtitle_font)
    draw.text((1460, 480), "• 11个知识领域\n• 权重分布\n• 题型难度", fill='black', font=body_font)
    
    # Preparation Strategy
    draw.rectangle([200, 800, 1100, 1150], outline='purple', width=3)
    draw.text((300, 850), "准备策略", fill='purple', font=subtitle_font)
    draw.text((300, 930), "• 学习资源\n• 3-6个月计划\n• 经验要求", fill='black', font=body_font)
    
    # Career Development
    draw.rectangle([1360, 800, 2260, 1150], outline='orange', width=3)
    draw.text((1460, 850), "职业发展", fill='orange', font=subtitle_font)
    draw.text((1460, 930), "• 典型职业角色\n• 薪酬影响\n• 发展建议", fill='black', font=body_font)
    
    # Save the image
    img.save('/Users/zhaoqinhuang/david_project/damabook/chapter_15_infographic.png')
    print("Chapter 15 infographic created successfully!")

if __name__ == "__main__":
    create_chapter_09_infographic()
    create_chapter_10_infographic()
    create_chapter_11_infographic()
    create_chapter_12_infographic()
    create_chapter_13_infographic()
    create_chapter_14_infographic()
    create_chapter_15_infographic()
    print("All 7 chapter infographics generated successfully!")