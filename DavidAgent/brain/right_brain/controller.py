"""
右脑中枢控制器 - 全局统筹者、创意总监、Persona合成器
驱动模型：qwen3-coder-plus (通义千问)
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .persona_synthesizer import RightBrainPersonaSynthesizer
from ..utils.api_resilience import with_resilience


class RightBrainController:
    def __init__(self, blackboard=None):
        self.model = "qwen3-coder-plus"
        self.persona = "科技达人"
        self.blackboard = blackboard
        self.synthesizer = RightBrainPersonaSynthesizer()
        
        if self.blackboard:
            self._setup_listeners()
        
    def _setup_listeners(self):
        """设置事件监听器"""
        # 监听左脑完成知识提取的事件
        self.blackboard.subscribe('state_changed:extracted_graph', self._on_extracted_graph)
        # 监听左脑审查反馈事件（用于重写）
        self.blackboard.subscribe('state_changed:review_feedback', self._on_review_feedback)
        
    async def _on_extracted_graph(self, graph_data, old_value):
        """处理知识图谱完成事件"""
        print("🎨 [事件] 左脑完成知识提取，唤醒右脑(Qwen)...")
        try:
            import json
            knowledge_markdown = json.dumps(graph_data, ensure_ascii=False, indent=2)
                
            generation_result = await self.create_content(knowledge_markdown)
            
            # 追踪：记录右脑创作结果
            draft_text = generation_result.get("draft", "")
            draft_title = draft_text.split('\n')[0][:100] if draft_text else '无标题'
            token_usage = generation_result.get("token_usage", {})
            self.blackboard.append_trace('RIGHT_BRAIN_DRAFT', f'草稿生成完毕: {draft_title}', {
                'draft_title': draft_title,
                'token_usage': token_usage,
                'draft_length': len(draft_text)
            })
            
            # 先变更状态灯为 REVIEWING，再抛出载荷，保证订阅者不会拦截
            self.blackboard.update('workflow_status', 'REVIEWING', 'SYSTEM')
            
            # 主草稿
            self.blackboard.update('draft_content', generation_result.get("draft", ""), 'QWEN_RIGHT')
            
            # 记录海马体记忆切片与溢出裁剪状态（Dashboard 面板 4.3 可视化所需）
            self.blackboard.update('right_brain_historical_context', generation_result.get("historical_context", ""), 'QWEN_RIGHT')
            self.blackboard.update('right_brain_is_pruned', generation_result.get("is_pruned", False), 'QWEN_RIGHT')
            self.blackboard.update('right_brain_ontological_associations', generation_result.get("ontological_associations", ""), 'QWEN_RIGHT')
            
            # API 通讯底层抓包 (供 Developer Trace 面板使用)
            self.blackboard.update('qwen_raw_system_prompt', generation_result.get("raw_system_prompt", ""), 'QWEN_RIGHT')
            self.blackboard.update('qwen_raw_user_prompt', generation_result.get("raw_user_prompt", ""), 'QWEN_RIGHT')
            self.blackboard.update('qwen_token_usage', generation_result.get("token_usage", {}), 'QWEN_RIGHT')
            
        except Exception as e:
            print(f"❌ 右脑创作失败: {e}")
            self.blackboard.update('workflow_status', 'ERROR', 'SYSTEM')
            
    async def _on_review_feedback(self, feedback, old_value):
        """处理审查反馈事件（重写逻辑）"""
        if not feedback:
            return
        print(f"⚠️ [右脑-Qwen] 收到左脑的修改意见: {feedback}，正在重写草稿...")
        # TODO: 实现重写逻辑
        pass
        
    @with_resilience(max_retries=3, base_delay=3)
    async def dispatch_intent(self, stimulus):
        """意图分发：决定何时将子任务委托给左脑"""
        pass
        
    @with_resilience(max_retries=3, base_delay=3)  
    async def create_content(self, context_data):
        """内容创作：生成富有网感的对外发布内容"""
        return await self.synthesizer.draft_blog_post("auto_topic", context_data)
        
    async def manage_tone(self, interaction_context):
        """情感与共情：处理交互中的基调把控"""
        pass