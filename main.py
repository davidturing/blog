"""
量化交易全流程主函数
"""

import asyncio
import json
from blackboard import Blackboard, BlackboardState
from hippocampus_manager import HippocampusManager
from skillrl_manager import SkillRLManager
from reasoning_bank_manager import ReasoningBankManager
from autogen_agents import LeftBrainAgent, RightBrainAgent
from test_data import create_test_ohlc_data
from backtest_engine import calculate_indicators, generate_signals, calculate_performance
from quant_models import StrategyRule, BacktestResult

async def main():
    """主函数，执行完整的量化交易流程"""
    print("=== 量化金融老师 - 双脑多智能体量化交易系统 ===")
    
    # 初始化组件
    blackboard = Blackboard()
    hippocampus_manager = HippocampusManager()
    skillrl_manager = SkillRLManager()
    reasoning_bank_manager = ReasoningBankManager()
    
    # 创建测试数据
    print("1. 创建测试OHLC数据...")
    ohlc_data = create_test_ohlc_data()
    print(f"   已创建{len(ohlc_data)}个交易日的测试数据")
    
    # 初始化双脑Agent
    left_brain = LeftBrainAgent(blackboard, hippocampus_manager, reasoning_bank_manager)
    right_brain = RightBrainAgent(blackboard, hippocampus_manager, skillrl_manager, reasoning_bank_manager)
    
    # 订阅黑板状态变化
    async def on_strategy_extracted(blackboard):
        """当策略提取完成时的回调"""
        print("3. 左脑已完成策略生成，右脑开始回测...")
        await right_brain.run_backtest()
    
    async def on_backtest_draft(blackboard):
        """当回测草稿完成时的回调"""
        print("4. 右脑已完成回测，左脑开始校验...")
        backtest_result_dict = blackboard.get_data("backtest_result")
        backtest_result = BacktestResult(**backtest_result_dict)
        fact_check_result = await left_brain.fact_check(backtest_result)
        
        # 根据校验结果决定是否接受策略
        if fact_check_result.is_consistent:
            print("5. 校验通过，策略有效")
            await right_brain.finalize_strategy(backtest_result, True)
        else:
            print(f"5. 校验失败，发现不一致: {', '.join(fact_check_result.inconsistencies)}")
            await right_brain.finalize_strategy(backtest_result, False)
    
    blackboard.subscribe(BlackboardState.STRATEGY_EXTRACTED, on_strategy_extracted)
    blackboard.subscribe(BlackboardState.BACKTEST_DRAFT, on_backtest_draft)
    
    # 启动左脑生成策略
    print("2. 左脑开始生成量化策略...")
    task_description = "基于双均线的量化交易策略"
    await left_brain.generate_strategy(task_description)
    
    # 等待流程完成
    await blackboard.wait_for_state(BlackboardState.BACKTEST_COMPLETED)
    
    # 输出最终结果
    final_result = blackboard.get_data("backtest_result")
    if final_result:
        print("\n=== 量化回测结果 ===")
        print(f"策略名称: {final_result['strategy_name']}")
        print(f"累计收益: {final_result['total_return']:.2%}")
        print(f"最大回撤: {final_result['max_drawdown']:.2%}")
        print(f"年化夏普比率: {final_result['annual_sharpe']:.2f}")
        print(f"交易次数: {final_result['trade_count']}")
        print(f"胜率: {final_result['win_rate']:.2%}")
        print(f"盈亏比: {final_result['profit_factor']:.2f}")
    else:
        print("\n=== 策略未通过校验，无有效回测结果 ===")
    
    print("\n=== 组件数据归档情况 ===")
    print("- 海马体: 情景记忆已保存策略和回测结果")
    print("- SkillRL: 成功策略已保存到技能库")
    print("- ReasoningBank: 推理过程、校验日志和失败案例已归档")
    
    print("\n系统执行完成！")

if __name__ == "__main__":
    asyncio.run(main())