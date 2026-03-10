#!/usr/bin/env python3
"""
Generate infographics for DAMA handbook chapters 9-15
This script creates simple but informative infographics using PIL
"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_infographic(chapter_num, title, subtitle, content_points):
    """Create a simple infographic for a chapter"""
    
    # Create a new image with white background (2K resolution: 2048x1152)
    width, height = 2048, 1152
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default if not available
    try:
        # Try to find a Chinese font
        font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 64)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        font_content = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    except:
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 64)
            font_subtitle = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            font_content = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_content = ImageFont.load_default()
    
    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 100), title, fill='black', font=font_title)
    
    # Draw subtitle
    if subtitle:
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        draw.text((subtitle_x, 200), subtitle, fill='darkgray', font=font_subtitle)
    
    # Draw content points
    y_position = 300
    for point in content_points[:10]:  # Limit to 10 points to avoid overflow
        # Wrap text to fit within the image
        wrapped_text = textwrap.fill(point, width=60)
        draw.text((100, y_position), wrapped_text, fill='black', font=font_content)
        # Calculate height of wrapped text
        lines = wrapped_text.count('\n') + 1
        y_position += lines * 35 + 20
    
    # Add a simple decorative element
    draw.line([(50, height - 100), (width - 50, height - 100)], fill='lightgray', width=2)
    draw.text((width//2 - 100, height - 80), f"Chapter {chapter_num:02d} - DAMA Handbook", 
              fill='darkgray', font=font_content)
    
    return img

def main():
    # Chapter data
    chapters = {
        9: {
            "title": "参考数据与主数据",
            "subtitle": "DAMA数据管理知识体系",
            "content": [
                "参考数据：用于分类或分组其他数据的数据",
                "主数据：关于业务实体的核心数据",
                "参考数据特征：稳定性、共享性、标准化、有限值域",
                "主数据域：客户、产品、供应商、员工、位置",
                "MDM架构：数据整合、匹配合并、黄金记录、分发服务",
                "MDM方法：注册表式、集中式、混合式、事务式",
                "治理角色：数据所有者、数据管家、参考数据管理员",
                "合规要求：GDPR、SOX、行业法规、数据主权",
                "关键指标：完整性、准确性、一致性、处理效率",
                "持续改进：评估→识别差距→制定计划→实施→监控→调整"
            ]
        },
        10: {
            "title": "数据仓库与商务智能",
            "subtitle": "DAMA数据管理知识体系",
            "content": [
                "数据仓库特征：面向主题、集成性、非易失性、时变性",
                "DW架构：数据源→ETL→存储层→访问层",
                "BI组件：可视化、报表、OLAP、数据挖掘、预测分析",
                "实施方法：自上而下(Inmon) vs 自下而上(Kimball)",
                "现代架构：数据湖、云数据仓库、实时处理、数据网格",
                "治理要素：元数据管理、数据质量、性能、安全、变更",
                "成功因素：明确需求、高质量数据、用户参与、渐进实施",
                "实践建议：从小处着手、关注质量、建立字典、培训用户",
                "技术演进：从传统DW到现代化数据平台",
                "价值实现：支持数据驱动决策的核心基础设施"
            ]
        },
        11: {
            "title": "元数据管理",
            "subtitle": "关于数据的数据",
            "content": [
                "元数据类型：业务、技术、操作、管理元数据",
                "业务元数据：定义、规则、所有者、分类、术语",
                "技术元数据：表结构、格式、ETL规则、接口规范",
                "管理框架：创建→存储→维护→分发→使用",
                "技术栈：存储库、提取工具、目录、血缘分析、质量工具",
                "实施策略：渐进式、自动化+人工、用户参与、治理集成",
                "常见挑战：分散、质量差、缺乏参与、技术复杂、ROI难量化",
                "解决方案：中央存储库、质量管控、价值认知、合适工具",
                "未来趋势：智能元数据、主动管理、元数据即服务",
                "核心价值：数据发现、理解、治理、集成、血缘追踪"
            ]
        },
        12: {
            "title": "数据质量",
            "subtitle": "数据管理的核心要素",
            "content": [
                "质量维度：准确性、完整性、一致性、及时性、唯一性、有效性",
                "评估方法：数据剖析、质量规则、指标监控、根本原因分析",
                "改进策略：预防性措施、纠正性措施、持续改进",
                "管理框架：组织结构、流程方法、技术架构",
                "业务价值：提升决策、增强体验、降低风险、提高效率、支持创新",
                "实施路线：启动→规划→执行→监控优化",
                "最佳实践：从业务价值出发、端到端视角、协作文化",
                "预防措施：输入验证、标准化、培训意识",
                "纠正措施：数据清洗、整合、自动化修复",
                "持续改进：反馈循环、质量文化、技术投资"
            ]
        },
        13: {
            "title": "数据管理成熟度评估",
            "subtitle": "从混乱到优化的演进路径",
            "content": [
                "成熟度模型：CMMI、DCAM、DAMA-DMBOK框架",
                "评估维度：战略治理、流程方法、技术架构、人员技能、文化意识",
                "成熟度等级：不存在→初始→已管理→已定义→量化管理→优化",
                "评估方法：准备→数据收集→分析评分→报告建议",
                "实施路线：短期(0-6月)→中期(6-18月)→长期(18-36月)",
                "常见挑战：缺乏支持、资源限制、组织阻力、技术复杂、度量困难",
                "应对策略：业务关联、渐进方法、变革管理、模块化、简单指标",
                "持续改进：定期评估、监控、敏捷调整、知识共享",
                "成功要素：高层支持、业务驱动、跨职能协作、持续沟通",
                "价值实现：系统性提升数据管理能力，实现数据驱动转型"
            ]
        },
        14: {
            "title": "组织与变革管理",
            "subtitle": "数据管理的人与组织维度",
            "content": [
                "组织模型：集中式、分散式、联邦式(推荐)",
                "关键角色：CDO、治理委员会、架构师、数据管家、工程师",
                "变革框架：ADKAR模型(认知→意愿→知识→能力→强化)",
                "文化建设：数据驱动决策、共享精神、质量意识、学习导向",
                "能力建设：技能矩阵、培训路径、人才招聘保留",
                "项目管理：敏捷方法、风险管理、成功度量",
                "常见障碍：部门孤岛、责任不清、技能缺口、优先级冲突",
                "成功要素：高层支持、业务驱动、渐进方法、跨职能协作",
                "沟通策略：多渠道、分层信息、双向对话、持续更新、故事化",
                "持续改进：定期评估、最佳实践分享、外部对标、组织学习"
            ]
        },
        15: {
            "title": "CDMP认证指南",
            "subtitle": "认证数据管理专业人士",
            "content": [
                "认证级别：基础级、专家级、大师级、研究员级",
                "考试结构：11个知识领域，数据治理(20%)、架构(15%)等",
                "准备策略：3-6个月计划，全面学习→深入学习→强化训练",
                "考试技巧：时间管理、答题策略、多选题处理",
                "申请流程：资格审查→报名→缴费→预约→准备",
                "认证维持：3年有效期，120 CEU学分，职业道德",
                "职业发展：多种角色适用，10-25%薪酬提升",
                "学习资源：官方教材、在线课程、实践指南、模拟考试",
                "经验要求：基础级无要求，专家级2年，大师级10年",
                "全球认可：跨国企业、咨询公司的重要专业标志"
            ]
        }
    }
    
    # Generate infographics for all chapters
    for chapter_num, data in chapters.items():
        print(f"Generating infographic for Chapter {chapter_num:02d}...")
        img = create_infographic(
            chapter_num, 
            data["title"], 
            data["subtitle"], 
            data["content"]
        )
        
        # Save the image
        filename = f"/Users/zhaoqinhuang/david_project/damabook/chapter_{chapter_num:02d}_infographic.png"
        img.save(filename, "PNG", quality=95)
        print(f"Chapter {chapter_num:02d} infographic saved to {filename}")
    
    print("All infographics generated successfully!")

if __name__ == "__main__":
    main()