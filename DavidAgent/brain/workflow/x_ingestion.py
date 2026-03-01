"""
X网站知识吸收工作流
完整的流转过程：感知 → 左脑解析 → 右脑创作 → 左右脑互搏审查 → 运动神经输出
"""
from ..memory.blackboard import BrainBlackboard
from ..left_brain.analyzer import LeftBrainAnalyzer  
from ..right_brain.controller import RightBrainController
from ..sensors.x_spider import XSpider
from ..config import BrainConfig

class XIngestionWorkflow:
    def __init__(self):
        self.config = BrainConfig()
        self.blackboard = BrainBlackboard()
        self.left_brain = LeftBrainAnalyzer(self.blackboard)
        self.right_brain = RightBrainController(self.blackboard)
        self.x_spider = XSpider(self.blackboard)
        
        # 设置观察者模式
        self._setup_observers()
        
    def _setup_observers(self):
        """设置左右脑对黑板变化的监听"""
        self.blackboard.subscribe('state_changed:raw_source', self.left_brain.extract_information)
        self.blackboard.subscribe('state_changed:extracted_graph', self.right_brain.create_content)
        self.blackboard.subscribe('state_changed:draft_content', self.left_brain.fact_check)
        self.blackboard.subscribe('state_changed:workflow_status', self._handle_status_change)
        
    async def run_automated_ingestion(self):
        """启动自动化批量感知任务"""
        print("💡 [工作流] 启动 X 自动化批量感知任务...")
        await self.x_spider.batch_ingest(self.config.x_target_accounts)

    def process_x_thread(self, x_thread_data: dict):
        """处理模拟或传入的 X 数据"""
        self.blackboard.update('raw_source', x_thread_data.get('full_text', ''), 'MANUAL_INGEST')
        
    async def _handle_status_change(self, new_status, old_status):
        """处理状态变更事件"""
        if new_status == 'READY_TO_PUBLISH':
            await self._publish_content()

    async def _publish_content(self):
        """运动神经输出 - 发布逻辑"""
        print("🚀 [工作流] 任务已准备就绪，正在触发发布流程...")
        # 此处可对接 WordPress 或 X 发布
        self.blackboard.update('workflow_status', 'DONE', 'SYSTEM')