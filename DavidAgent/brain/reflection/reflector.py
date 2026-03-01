#!/usr/bin/env python3
"""
夜间反思器 - 系统的元认知中枢 (Nightly Reflector)
分析情景记忆，提取失败根因，生成动态避坑指南。
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from google.genai import GenerativeModel
import google.genai as genai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置环境
project_root = Path(__file__).parent.parent.parent
sys_path_inserted = False
if not sys_path_inserted:
    import sys
    sys.path.insert(0, str(project_root))
    sys_path_inserted = True

from brain.memory.episodic_memory import get_episodic_memory_db

class NightlyReflector:
    """元认知反射镜 - 负责系统的自我进化"""
    
    def __init__(self):
        self.db = get_episodic_memory_db()
        self.guidelines_file = project_root / "dynamic_guidelines.md"
        
        # 初始化用于总结的AI模型
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key, transport='rest')
            self.model = GenerativeModel("models/gemini-flash-latest")
        else:
            self.model = None
            print("⚠️ [Reflector] 缺少 GEMINI_API_KEY，反思功能将受限。")

    async def reflect_and_evolve(self):
        """执行全量反思流程"""
        print("🌙 [Reflector] 正在进入夜间反思模式，梳理往昔记忆...")
        
        # 1. 获取最近 24 小时内的所有缺陷/失败记忆
        flaws = self.db.get_flawed_episodes(hours=24, limit=10)
        
        if not flaws:
            print("✨ [Reflector] 今日无暇，系统表现完美，无需生成新规则。")
            return
            
        print(f"🧐 [Reflector] 发现 {len(flaws)} 条缺陷记忆，正在深度复盘...")
        
        # 2. 构建反思提示词
        reflection_prompt = self._build_reflection_prompt(flaws)
        
        try:
            # 3. 调用 AI 进行元认知分析 (REST + to_thread)
            def _sync_reflect():
                return self.model.generate_content(reflection_prompt)
                
            response = await asyncio.to_thread(_sync_reflect)
            new_rules = response.text.strip()
            
            # 4. 固化为动态指南
            self._save_guidelines(new_rules)
            print("🚀 [Reflector] 自我进化完成！新的避坑指南已同步至右脑。")
            
        except Exception as e:
            print(f"❌ [Reflector] 反思过程异常: {e}")

    def _build_reflection_prompt(self, flaws: List[Dict]) -> str:
        """构建反思 Prompt"""
        history_str = ""
        for i, f in enumerate(flaws):
            history_str += f"\n--- Case {i+1} ---\n"
            history_str += f"反馈意见: {f.get('review_feedback') or f.get('human_comment')}\n"
            history_str += f"评分 (逻辑/网感/排版): {f.get('logic_score')}/{f.get('tone_score')}/{f.get('format_score')}\n"
            
        prompt = f"""
        你现在是 DavidAgent 的元认知中枢（夜间反思器）。
        以下是系统在过去 24 小时内收到的【负面反馈】和【逻辑报错】：
        {history_str}
        
        请深刻反思这些错误，找出共性规律，并生成最多 8 条极其精简的“避坑指南”。
        这些指南将直接作为 System Prompt 注入右脑的后续创作中。
        
        要求：
        1. 针对性强：直接指出不要做什么，应该做什么。
        2. 语气威严：具有强制性约束力。
        3. 保持紧凑：删除废话，每条建议不超过 50 字。
        4. Markdown 格式：使用无序列表输出。
        """
        return prompt

    def _save_guidelines(self, content: str):
        """保存规则到文件"""
        header = "# 🚨 动态避坑指南 (Dynamic Guidelines)\n"
        header += f"> 更新于: {asyncio.get_event_loop().time()}\n\n"
        with open(self.guidelines_file, "w", encoding="utf-8") as f:
            f.write(header + content)

if __name__ == "__main__":
    reflector = NightlyReflector()
    asyncio.run(reflector.reflect_and_evolve())
