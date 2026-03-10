"""
AutoGen黑板机制实现
"""

import asyncio
from typing import Any, Dict, Optional
from enum import Enum

class BlackboardState(Enum):
    """黑板状态枚举"""
    RAW_STRATEGY = "RAW_STRATEGY"
    DATA_LOAD = "DATA_LOAD"
    DML_RUNNING = "DML_RUNNING"
    STRATEGY_EXTRACTED = "STRATEGY_EXTRACTED"
    BACKTEST_DRAFT = "BACKTEST_DRAFT"
    BACKTEST_CHECKING = "BACKTEST_CHECKING"
    BACKTEST_COMPLETED = "BACKTEST_COMPLETED"

class Blackboard:
    """黑板类，用于智能体间通信和状态管理"""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._state: BlackboardState = BlackboardState.RAW_STRATEGY
        self._state_change_event = asyncio.Event()
        self._subscribers: Dict[BlackboardState, list] = {
            state: [] for state in BlackboardState
        }
    
    def get_data(self, key: str) -> Optional[Any]:
        """获取黑板数据"""
        return self._data.get(key)
    
    def set_data(self, key: str, value: Any) -> None:
        """设置黑板数据"""
        self._data[key] = value
    
    def get_state(self) -> BlackboardState:
        """获取当前状态"""
        return self._state
    
    def set_state(self, state: BlackboardState) -> None:
        """设置状态并触发事件"""
        self._state = state
        self._state_change_event.set()
        self._state_change_event.clear()
        
        # 通知订阅者
        for callback in self._subscribers[state]:
            asyncio.create_task(callback(self))
    
    async def wait_for_state(self, state: BlackboardState) -> None:
        """等待特定状态"""
        if self._state == state:
            return
        await self._state_change_event.wait()
    
    def subscribe(self, state: BlackboardState, callback) -> None:
        """订阅特定状态变化"""
        self._subscribers[state].append(callback)
        
    # Helpers added for AutoGen System compatibility
    def update_state(self, state_name, data_dict):
        for k, v in data_dict.items():
            self.set_data(k, v)
        # Attempt to map string state to enum if possible
        try:
            if hasattr(BlackboardState, state_name):
                enum_state = getattr(BlackboardState, state_name)
                self.set_state(enum_state)
        except Exception:
            pass

    def log_error(self, error_msg):
        self.set_data("latest_error", error_msg)
        
    def get_previous_state(self):
        # mock returning None
        return None
        
    def rollback_to_state(self, state):
        pass
