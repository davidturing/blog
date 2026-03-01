#!/usr/bin/env python3
"""
DavidAgent 夜间反思机制 - 实现规则剪枝与合并
解决Prompt膨胀问题，保持系统长期高效运行
"""

import os
import sys
import sqlite3
import asyncio
from pathlib import Path
from typing import List, Tuple, Optional
from openai import AsyncOpenAI

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 避坑指南的持久化文件
GUIDELINES_FILE = project_root / "dynamic_guidelines.md"


class NightlyReflection:
    """夜间反思智能体 - DavidAgent的元认知中枢"""
    
    def __init__(self):
        self.db_path = project_root / "david_agent_memory.db"
        self.client = AsyncOpenAI(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
    async def extract_flawed_episodes(self) -> List[Tuple]:
        """
        提取过去24小时的"失败/被批评"记忆
        
        Returns:
            List[Tuple]: 失败任务记录列表
        """
        print("🔍 [午夜反思] 提取昨日犯错记录...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找被左脑打回过，或者人类打分有低于4分的任务
        cursor.execute('''
            SELECT task_id, review_feedback, logic_score, tone_score, format_score, human_comment 
            FROM trace_logs 
            WHERE (review_feedback != '' AND review_feedback IS NOT NULL)
               OR (logic_score < 4 OR tone_score < 4 OR format_score < 4)
               OR (human_comment != '' AND human_comment IS NOT NULL)
            ORDER BY timestamp DESC LIMIT 10
        ''')
        flawed_episodes = cursor.fetchall()
        conn.close()
        
        if not flawed_episodes:
            print("😴 [午夜反思] 昨天表现完美，没有需要反思的错误，继续睡觉。")
            return []
            
        print(f"📊 [午夜反思] 找到 {len(flawed_episodes)} 条需要反思的记录")
        return flawed_episodes
    
    def read_old_guidelines(self) -> str:
        """
        读取旧的避坑指南
        
        Returns:
            str: 旧指南内容，如果不存在则返回空字符串
        """
        if GUIDELINES_FILE.exists():
            with open(GUIDELINES_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def format_mistakes_context(self, flawed_episodes: List[Tuple]) -> str:
        """
        整理错误日志供大模型分析
        
        Args:
            flawed_episodes: 失败任务记录列表
            
        Returns:
            str: 格式化的错误上下文
        """
        mistakes_context = "【昨日犯错记录】\n"
        for ep in flawed_episodes:
            mistakes_context += f"- 任务ID {ep[0]}:\n"
            if ep[1]: 
                mistakes_context += f"  * 左脑拦截意见: {ep[1]}\n"
            if ep[5]: 
                mistakes_context += f"  * 人类长官批评: {ep[5]} (逻辑:{ep[2]}, 网感:{ep[3]}, 排版:{ep[4]})\n"
        return mistakes_context
    
    async def generate_consolidated_guidelines(self, old_guidelines: str, mistakes_context: str) -> str:
        """
        召唤反思智能体生成压缩后的精简规则
        
        Args:
            old_guidelines: 旧的避坑指南
            mistakes_context: 错误上下文
            
        Returns:
            str: 新的精简避坑指南
        """
        print("🧠 [午夜反思] 召唤元认知中枢进行规则压缩...")
        
        system_prompt = """
你是 DavidAgent 的元认知中枢。你的任务是进行"规则压缩与合并"。

你将收到两份输入：
1. 【旧的避坑指南】：系统过去积累的经验。
2. 【昨日犯错记录】：昨天被拦截或被人类长官批评的具体原因。

工作流程：
1. 根因分析：深刻理解昨日犯错的本质原因。
2. 吸收旧规则：审视旧指南，剔除过时的、重复的规则。
3. 生成新法则：将昨日的教训提炼成新的规则，与旧规则完美融合。

🚨【绝对约束】：
- 规则总数绝对不能超过 10 条！
- 语言必须极其精炼，高度概括。如果规则过多，请强制将同类规则合并。
- 输出必须是纯 Markdown 格式，不要多余的寒暄。
- 总字数必须控制在 1000 字以内。
- 每条规则必须以 "-" 开头，简洁明了。
"""

        user_prompt = f"【旧的避坑指南】:\n{old_guidelines}\n\n{mistakes_context}\n\n请输出合并压缩后的全新避坑指南："

        try:
            response = await self.client.chat.completions.create(
                model="qwen-coder-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # 总结规则需要理性和克制
                max_tokens=1000
            )
            
            new_guidelines = response.choices[0].message.content
            return new_guidelines
            
        except Exception as e:
            print(f"❌ [午夜反思] 反思过程失败: {e}")
            raise e
    
    async def save_new_guidelines(self, new_guidelines: str):
        """
        落盘新规则，覆盖旧规则（避免Prompt膨胀）
        
        Args:
            new_guidelines: 新的避坑指南
        """
        with open(GUIDELINES_FILE, "w", encoding="utf-8") as f:
            f.write(new_guidelines)
        print("💾 [午夜反思] 新规则已保存！")
    
    async def run_reflection(self):
        """执行完整的夜间反思流程"""
        print("🌙 [午夜反思] DavidAgent 开始进入梦境，进行自我批判与规则合并...")
        
        try:
            # 1. 提取失败记录
            flawed_episodes = await self.extract_flawed_episodes()
            if not flawed_episodes:
                return
                
            # 2. 读取旧指南
            old_guidelines = self.read_old_guidelines()
            
            # 3. 格式化错误上下文
            mistakes_context = self.format_mistakes_context(flawed_episodes)
            
            # 4. 生成新指南
            new_guidelines = await self.generate_consolidated_guidelines(old_guidelines, mistakes_context)
            
            # 5. 保存新指南
            await self.save_new_guidelines(new_guidelines)
            
            print("💡 [午夜反思] 反思完毕！新规则已生成并覆盖。Prompt 膨胀危机已解除。")
            print("====== 新版核心指南预览 ======")
            print(new_guidelines[:500] + "..." if len(new_guidelines) > 500 else new_guidelines)
            
        except Exception as e:
            print(f"❌ [午夜反思] 整体反思过程失败: {e}")
            # 即使反思失败，也要确保系统能继续运行
            # 可以选择保留旧指南或创建一个默认指南
            if not GUIDELINES_FILE.exists():
                default_guidelines = "- 保持客观、专业即可。\n- 避免过度口语化表达。\n- 确保技术描述准确无误。"
                with open(GUIDELINES_FILE, "w", encoding="utf-8") as f:
                    f.write(default_guidelines)
                print("✅ [午夜反思] 创建默认指南以确保系统正常运行。")


async def main():
    """主函数"""
    reflection = NightlyReflection()
    await reflection.run_reflection()


if __name__ == "__main__":
    asyncio.run(main())