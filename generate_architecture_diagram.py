#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 DavidAgent 四重增强架构图
使用 Google GenAI SDK 生成符合 DAMA-DMBOK2 教程图像标准的专业架构图
"""

import os
import json
from google import genai

def generate_architecture_diagram():
    """生成 DavidAgent 四重增强架构图"""
    print("🚀 开始生成 DavidAgent 四重增强架构图...")
    
    # 配置 API 密钥
    api_key = None
    if "GOOGLE_API_KEY" in os.environ:
        api_key = os.environ["GOOGLE_API_KEY"]
        print("Using GOOGLE_API_KEY.")
    elif "GEMINI_API_KEY" in os.environ:
        api_key = os.environ["GEMINI_API_KEY"]
        print("Using GEMINI_API_KEY.")
    else:
        print("❌ 错误: 未找到 GOOGLE_API_KEY 或 GEMINI_API_KEY 环境变量")
        return False
    
    if not api_key:
        print("❌ 错误: API 密钥为空")
        return False
    
    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)
        
        # 架构图描述
        architecture_description = """
        创建一个专业级的 DavidAgent 四重增强架构图，符合以下要求：
        
        **整体风格**: Professional blueprint aesthetic with technical precision
        **背景**: Dark blue gradient (#093572 to #103D78)
        **文字**: High contrast white/light blue text for readability
        **布局**: Clean, organized grid with clear hierarchy
        **分辨率**: 2K quality, 16:9 aspect ratio
        
        **架构层次**（从上到下）：
        
        1. **⚡ SkillRL（本能技能层）- 最高优先级**
           - 标题: "⚡ 本能技能层 (SkillRL)"
           - 描述: "高频问题即时响应，实现'本能反应'"
           - 特点: 直接秒回，跳过复杂处理
        
        2. **💡 ReasoningBank（推理避坑层）- 第二优先级**
           - 标题: "💡 推理避坑层 (ReasoningBank)"
           - 描述: "成功经验总结 + 失败教训记录"
           - 特点: 主动预警，避免重复踩坑
        
        3. **🧠 Memory Alpha（智能记忆层）- 第三优先级**
           - 标题: "🧠 智能记忆层 (Memory Alpha)"
           - 描述: "三级记忆架构：感知缓存 → 工作记忆 → 长期存储"
           - 特点: 智能筛选，自动遗忘
        
        4. **📊 LanceDB 7层混合检索（精确检索层）- 底层保障**
           - 标题: "📊 精确检索层 (LanceDB 7层)"
           - 描述: "7层 pipeline：向量→BM25→MMR→过滤→衰减→加权→重排序"
           - 特点: 精准历史记忆召回
        
        **数据流向**:
        - 查询流程: 用户输入 → 技能检查 → 推理检查 → 记忆检查 → 精确检索
        - 学习流程: 任务结果 → ReasoningBank学习 → SkillRL提炼 → Memory Alpha管理
        
        **视觉元素**:
        - 使用箭头表示数据流向
        - 每层用不同颜色的边框区分
        - 包含 DavidAgent Logo 和 "四重增强架构" 标题
        - 整体呈现为专业的技术架构图
        """
        
        # 生成内容 - 使用正确的模型名称
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=architecture_description,
            config={
                "response_mime_type": "text/plain",
                "temperature": 0.7,
                "max_output_tokens": 2048
            }
        )
        
        print("✅ 架构图生成成功！")
        print(f"响应类型: {type(response)}")
        print(f"响应属性: {dir(response)}")
        
        # 尝试获取文本内容
        text_content = None
        if hasattr(response, 'text'):
            text_content = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            text_content = response.candidates[0].content.parts[0].text
        
        if text_content:
            print(f"响应内容: {text_content[:200]}...")
            # 保存结果
            with open("david_agent_architecture_description.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
            return True
        else:
            print("❌ 响应中没有找到文本内容")
            return False
        
    except Exception as e:
        print(f"❌ 生成架构图时发生错误: {e}")
        return False

if __name__ == "__main__":
    success = generate_architecture_diagram()
    if success:
        print("✅ 架构图描述已保存到 david_agent_architecture_description.txt")
    else:
        print("❌ 架构图生成失败，请检查配置和网络连接。")