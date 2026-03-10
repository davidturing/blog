import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import asyncio
import json
import sqlite3
import os
from typing import Dict, Any, Optional
from enum import Enum

# 1. Blackboard 黑板机制
class BlackboardState(Enum):
    RAW_STRATEGY = "RAW_STRATEGY"
    STRATEGY_EXTRACTED = "STRATEGY_EXTRACTED" 
    BACKTEST_DRAFT = "BACKTEST_DRAFT"
    BACKTEST_CHECKING = "BACKTEST_CHECKING"
    BACKTEST_COMPLETED = "BACKTEST_COMPLETED"

class Blackboard:
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._state: BlackboardState = BlackboardState.RAW_STRATEGY
        
    def set_data(self, key: str, value: Any):
        self._data[key] = value
        
    def get_data(self, key: str) -> Optional[Any]:
        return self._data.get(key)
        
    def set_state(self, state: BlackboardState):
        self._state = state
        
    def get_state(self) -> BlackboardState:
        return self._state

# 2. 海马体管理器
class HippocampusManager:
    def __init__(self):
        self.db_path = "hippocampus_episodic.db"
        os.makedirs("hippocampus", exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_name TEXT,
                strategy TEXT,
                backtest_result TEXT
            )
        """)
        conn.commit()
        conn.close()
        
    def save_task(self, task_name: str, strategy: Dict, result: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_name, strategy, backtest_result) VALUES (?, ?, ?)",
            (task_name, json.dumps(strategy), json.dumps(result))
        )
        conn.commit()
        conn.close()

# 3. 创建 AutoGen 智能体
# 从环境变量读取API密钥
import os
from dotenv import load_dotenv
load_dotenv()

config_list = [
    {
        "model": "glm-5",
        "api_key": os.getenv("GLM_API_KEY"),
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4/"
    },
    {
        "model": "gemini-3.1-pro-preview", 
        "api_key": os.getenv("GEMINI_API_KEY"), 
        "base_url": "https://generativelanguage.googleapis.com/v1beta/"
    },
    {
        "model": "qwen3-max-2026-01-23",
        "api_key": os.getenv("QWEN_API_KEY"),
        "base_url": "https://coding.dashscope.aliyuncs.com/v1"
    }
]

# CoderAgent - 负责生成量化交易代码
coder_agent = AssistantAgent(
    name="CoderAgent",
    llm_config={"config_list": [config_list[0]]},
    system_message="""你是一个量化交易系统开发专家。你的任务是：
    1. 实现完整的仿生双脑量化交易系统
    2. 包含左脑策略生成和右脑回测引擎
    3. 使用Polars+DuckDB进行高性能回测
    4. 实现参数级红蓝对抗校验
    5. 集成海马体持久化、SkillRL技能沉淀、ReasoningBank日志
    输出完整的Python代码，确保可直接运行。"""
)

# CodeReviewAgent - 负责代码初审
reviewer_agent = AssistantAgent(
    name="CodeReviewAgent", 
    llm_config={"config_list": [config_list[1]]},
    system_message="""你是一个严格的代码审查专家。审查标准：
    1. 必须使用原生autogen库创建真实智能体
    2. 必须实现GroupChat自动调度流程
    3. 左脑必须实现参数级红蓝对抗（均线周期、开平仓条件、止损止盈）
    4. 右脑必须使用Polars+DuckDB计算6项核心指标
    5. 必须集成海马体、SkillRL、ReasoningBank
    任何不符合要求的代码都必须打回重写。"""
)

# FinalJudgeAgent - 负责最终架构终审  
judge_agent = AssistantAgent(
    name="FinalJudgeAgent",
    llm_config={"config_list": [config_list[2]]},
    system_message="""你是最终架构终审官。只有当代码满足以下条件才通过：
    1. 架构完全符合仿生双脑设计
    2. 所有组件真实可运行，无伪实现
    3. AutoGen智能体间能真对话自动派任务
    4. 可本地直接执行，形成完整闭环
    发现任何问题都拒绝通过。"""
)

# UserProxy - 触发整个流程
user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False
)

# 4. 创建 GroupChat 和 Manager
groupchat = GroupChat(
    agents=[user_proxy, coder_agent, reviewer_agent, judge_agent],
    messages=[],
    max_round=15,
    speaker_selection_method="auto"
)

manager = GroupChatManager(
    groupchat=groupchat, 
    llm_config={"config_list": config_list}
)

# 5. 启动量化交易系统开发任务
if __name__ == "__main__":
    # 初始化黑板和海马体
    blackboard = Blackboard()
    hippocampus = HippocampusManager()
    
    # 触发AutoGen工作流
    user_proxy.initiate_chat(
        manager,
        message="""开发完整的量化交易仿生双脑系统：
        1. 使用原生autogen库创建真实智能体
        2. 实现GroupChat自动调度：Coder→Reviewer→Judge
        3. 集成Blackboard黑板状态机
        4. 左脑策略生成 + 参数级红蓝对抗校验
        5. 右脑Polars+DuckDB回测引擎（6项核心指标）
        6. 海马体持久化、SkillRL技能沉淀、ReasoningBank日志
        7. 输出可直接运行的.py文件，可本地执行。
        确保无伪实现、空函数、无效校验。"""
    )