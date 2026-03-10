"""
双脑Agent封装
"""

import asyncio
import json
from typing import Dict, Any, Optional
from pydantic import ValidationError
from api_config import API_SEMAPHORE, MAX_RETRIES, BASE_DELAY, MAX_DELAY
from quant_models import StrategyRule, BacktestResult, FactCheckResult
from hippocampus_manager import HippocampusManager
from reasoning_bank_manager import ReasoningBankManager

class LeftBrainAgent:
    """左脑Agent (Gemini) - 负责分析-解构"""
    
    def __init__(self, blackboard, hippocampus_manager: HippocampusManager, reasoning_bank_manager: ReasoningBankManager):
        self.blackboard = blackboard
        self.hippocampus_manager = hippocampus_manager
        self.reasoning_bank_manager = reasoning_bank_manager
    
    async def generate_strategy(self, task_description: str) -> StrategyRule:
        """生成量化策略规则"""
        # 从海马体读取量化基础知识
        quant_knowledge = self.hippocampus_manager.read_logical_memory()
        
        # 模拟Gemini生成策略（实际应用中会调用API）
        # 这里使用硬编码的双均线策略作为示例
        strategy_rule = StrategyRule(
            strategy_name="DualMovingAverage",
            fast_window=10,
            slow_window=30,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
            description="双均线策略：快线上穿慢线买入，快线下穿慢线卖出"
        )
        
        # 将策略规则写入黑板
        self.blackboard.set_data("strategy_rule", strategy_rule.dict())
        self.blackboard.set_state(BlackboardState.STRATEGY_EXTRACTED)
        
        # 将策略规则写入海马体情景记忆
        self.hippocampus_manager.write_episodic_memory(
            task_name="DualMovingAverage",
            strategy=strategy_rule.dict()
        )
        
        return strategy_rule
    
    async def fact_check(self, backtest_result: BacktestResult) -> FactCheckResult:
        """红蓝对抗校验"""
        # 从黑板获取原始策略
        original_strategy = self.blackboard.get_data("strategy_rule")
        
        # 模拟校验逻辑（实际应用中会详细比对）
        is_consistent = True
        inconsistencies = []
        
        # 简单校验：检查回测结果中的策略名称是否匹配
        if backtest_result.strategy_name != original_strategy["strategy_name"]:
            is_consistent = False
            inconsistencies.append("策略名称不匹配")
        
        # 创建校验结果
        check_id = f"check_{int(asyncio.get_event_loop().time())}"
        fact_check_result = FactCheckResult(
            check_id=check_id,
            strategy_name=original_strategy["strategy_name"],
            is_consistent=is_consistent,
            inconsistencies=inconsistencies
        )
        
        # 保存校验日志到ReasoningBank
        self.reasoning_bank_manager.save_verify_log(
            verify_id=check_id,
            verify_info={
                "check_id": check_id,
                "strategy_name": original_strategy["strategy_name"],
                "is_consistent": is_consistent,
                "inconsistencies": inconsistencies,
                "timestamp": str(fact_check_result.timestamp)
            }
        )
        
        return fact_check_result

class RightBrainAgent:
    """右脑Agent (Qwen) - 负责语境-建构"""
    
    def __init__(self, blackboard, hippocampus_manager: HippocampusManager, skillrl_manager, reasoning_bank_manager: ReasoningBankManager):
        self.blackboard = blackboard
        self.hippocampus_manager = hippocampus_manager
        self.skillrl_manager = skillrl_manager
        self.reasoning_bank_manager = reasoning_bank_manager
    
    async def run_backtest(self) -> BacktestResult:
        """执行回测"""
        # 从黑板获取策略规则
        strategy_rule = self.blackboard.get_data("strategy_rule")
        
        # 从海马体读取情景记忆（如果有）
        episodic_memory = self.hippocampus_manager.read_episodic_memory(strategy_rule["strategy_name"])
        
        # 模拟回测执行（实际应用中会使用polars+duckdb）
        # 这里使用硬编码的回测结果作为示例
        backtest_result = BacktestResult(
            strategy_name=strategy_rule["strategy_name"],
            total_return=0.15,
            max_drawdown=0.08,
            annual_sharpe=1.2,
            trade_count=24,
            win_rate=0.65,
            profit_factor=1.8,
            signals=[]  # 实际应用中会有具体的交易信号
        )
        
        # 将回测草稿结果写入黑板
        self.blackboard.set_data("backtest_result", backtest_result.dict())
        self.blackboard.set_state(BlackboardState.BACKTEST_DRAFT)
        
        # 将回测结果写入海马体情景记忆
        self.hippocampus_manager.write_episodic_memory(
            task_name=strategy_rule["strategy_name"],
            strategy=strategy_rule,
            backtest_result=backtest_result.dict()
        )
        
        return backtest_result
    
    async def finalize_strategy(self, backtest_result: BacktestResult, is_valid: bool):
        """最终化策略"""
        if is_valid:
            # 保存成功策略到SkillRL
            self.skillrl_manager.save_successful_strategy(
                strategy_name=backtest_result.strategy_name,
                strategy_info=backtest_result.dict()
            )
            
            # 更新黑板状态
            self.blackboard.set_state(BlackboardState.BACKTEST_COMPLETED)
        else:
            # 保存失败案例到ReasoningBank
            failure_id = f"failure_{int(asyncio.get_event_loop().time())}"
            self.reasoning_bank_manager.save_failure_case(
                case_id=failure_id,
                failure_info={
                    "case_id": failure_id,
                    "strategy_name": backtest_result.strategy_name,
                    "failure_type": "validation_failed",
                    "market_conditions": "simulated",
                    "root_cause": "Strategy validation failed during fact-checking",
                    "lessons_learned": "Need to improve strategy generation logic",
                    "timestamp": str(datetime.now())
                }
            )
            
            # 保存失败案例到SkillRL经验库
            self.skillrl_manager.save_failure_case(
                strategy_name=backtest_result.strategy_name,
                failure_info={
                    "strategy_name": backtest_result.strategy_name,
                    "failure_reason": "Validation failed",
                    "improvement_suggestions": "Review strategy generation logic"
                }
            )
from datetime import datetime
from blackboard import BlackboardState

class AutoGenSystem:
    def __init__(self, blackboard, left_brain, right_brain):
        self.blackboard = blackboard
        self.left_brain = left_brain
        self.right_brain = right_brain
        
    def start(self):
        print("AutoGen System Started (Mock Sync Wrapper)")
        import asyncio
        asyncio.run(self._async_start())
        
    async def _async_start(self):
        print("Left Brain: Generating strategy...")
        strategy = await self.left_brain.generate_strategy("挖掘量化因子")
        
        print("Right Brain: Running backtest...")
        backtest_result = await self.right_brain.run_backtest()
        
        print("Left Brain: Fact checking...")
        fact_check = await self.left_brain.fact_check(backtest_result)
        
        print("Right Brain: Finalizing...")
        await self.right_brain.finalize_strategy(backtest_result, fact_check.is_consistent)
        print("Workflow completed.")

def create_autogen_system(blackboard):
    from hippocampus_manager import HippocampusManager
    from reasoning_bank_manager import ReasoningBankManager
    try:
        from skillrl_manager import SkillRLManager
        skillrl_mgr = SkillRLManager()
    except ImportError:
        class MockSkillRLManager:
            def save_successful_strategy(self, *args, **kwargs): pass
            def save_failure_case(self, *args, **kwargs): pass
        skillrl_mgr = MockSkillRLManager()
        
    hippo_mgr = HippocampusManager()
    reason_mgr = ReasoningBankManager()
    
    left_brain = LeftBrainAgent(blackboard, hippo_mgr, reason_mgr)
    right_brain = RightBrainAgent(blackboard, hippo_mgr, skillrl_mgr, reason_mgr)
    
    return AutoGenSystem(blackboard, left_brain, right_brain)

def trigger_gemini_review(error_msg, blackboard):
    print(f"Triggering Gemini Review for error: {error_msg}")
    blackboard.update_state('ERROR_REVIEW', {'latest_error': error_msg})
