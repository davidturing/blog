from brain.left_brain.left_brain import LeftBrainGemini
from brain.utils.api_resilience import with_resilience

class LeftBrainAnalyzer:
    """
    左脑分析器 - 逻辑提取器、事实核查员
    驱动模型：Gemini 3.1 Pro 
    """
    def __init__(self, blackboard=None):
        self.blackboard = blackboard
        self.brain = LeftBrainGemini()
        
        # 挂载黑板监听器
        if self.blackboard:
            # 监听原始数据接入
            self.blackboard.subscribe('state_changed:raw_source', self.extract_information)
            # 监听审核草稿
            self.blackboard.subscribe('state_changed:draft_content', self.fact_check)
            
    @with_resilience(max_retries=3, base_delay=2)
    async def extract_information(self, raw_data, old_value=None):
        """信息解构：深度阅读并提取核心观点"""
        if not raw_data:
            return
            
        print(f"🧠 [左脑-Gemini] 收到原始数据，开始提取核心观点...")
        
        # 提取 topic_id 作为 source_id，如果没有则使用默认值
        source_id = "Auto_Extracted_Topic"
        if self.blackboard and self.blackboard.state.get('topic_id'):
            source_id = str(self.blackboard.state.get('topic_id'))
            
        try:
            # 调用新版 LeftBrainGemini
            graph_data = await self.brain.extract_knowledge(raw_data, source_id)
            
            if self.blackboard:
                # 追踪：记录提取结果摘要
                summary = graph_data.get('summary', '')[:200] if isinstance(graph_data, dict) else ''
                entity_count = len(graph_data.get('entities', [])) if isinstance(graph_data, dict) else 0
                self.blackboard.append_trace('LEFT_BRAIN_EXTRACT', f'知识图谱提取完成: {entity_count} 个实体', {
                    'source_id': source_id,
                    'raw_source_preview': str(raw_data)[:200],
                    'graph_summary': summary,
                    'entity_count': entity_count
                })
                # 成功后更新黑板的 extracted_graph
                self.blackboard.update('extracted_graph', graph_data, 'GEMINI_LEFT')
                
            return graph_data
        except Exception as e:
            print(f"❌ [左脑-Gemini] 提取信息异常: {e}")
            if self.blackboard:
                self.blackboard.update('workflow_status', 'ERROR', 'SYSTEM')
            raise e
            
    @with_resilience(max_retries=3, base_delay=2)
    async def build_knowledge_graph(self, extracted_data):
        """兼容旧版接口，图谱挖掘"""
        # 新版 LeftBrainGemini 已在 extract_knowledge 中直接实现了落盘，此处为了兼容直接返回
        return None
        
    @with_resilience(max_retries=3, base_delay=2)
    async def fact_check(self, draft_content, old_value=None):
        """逻辑审查：进行事实准确性的交叉验证"""
        if not draft_content:
            return
            
        if not self.blackboard:
            return 
            
        status = await self.blackboard.read('workflow_status')
        # 用户要求: 当工作流处于 REVIEWING 状态时才处理
        if status != 'REVIEWING':
            return
            
        graph_data = await self.blackboard.read('extracted_graph')
        if not graph_data:
             # 如果没有基准事实，直接通过
             self.blackboard.update('workflow_status', 'READY_TO_PUBLISH', 'GEMINI_LEFT')
             return
             
        try:
            result = await self.brain.review_draft(draft_content, graph_data)
            
            if result.get('passed', False):
                self.blackboard.update('review_feedback', "OK", 'GEMINI_LEFT')
                self.blackboard.append_trace('FACT_CHECK', '事实核查通过，准备发布')
                # 如果通过，状态变更为 READY_TO_PUBLISH
                self.blackboard.update('workflow_status', 'READY_TO_PUBLISH', 'SYSTEM')
            else:
                feedback = result.get('feedback', '未知错误')
                hallucinations = result.get('hallucinations', [])
                error_msg = f"核查不通过: {feedback} (包含幻觉: {hallucinations})"
                self.blackboard.append_trace('FACT_CHECK', f'事实核查未通过: {feedback}', {
                    'hallucinations': hallucinations
                })
                self.blackboard.update('review_feedback', error_msg, 'GEMINI_LEFT')
                # 如果不通过，状态回退为 DRAFTING
                self.blackboard.update('workflow_status', 'DRAFTING', 'SYSTEM')
                
            return result
        except Exception as e:
            print(f"❌ [左脑-Gemini] 事实核查出现错误: {e}")
            self.blackboard.update('workflow_status', 'ERROR', 'SYSTEM')
            raise e