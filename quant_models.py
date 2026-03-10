"""
量化交易Pydantic数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class StrategyRule(BaseModel):
    """策略规则模型"""
    strategy_name: str = Field(..., description="策略名称")
    fast_window: int = Field(..., description="快线窗口期")
    slow_window: int = Field(..., description="慢线窗口期")
    stop_loss_pct: float = Field(..., description="止损百分比")
    take_profit_pct: float = Field(..., description="止盈百分比")
    description: str = Field(..., description="策略描述")
    
class TradeSignal(BaseModel):
    """交易信号模型"""
    timestamp: datetime = Field(..., description="信号时间戳")
    symbol: str = Field(..., description="交易标的")
    signal_type: str = Field(..., description="信号类型 (BUY/SELL)")
    price: float = Field(..., description="信号价格")
    quantity: float = Field(..., description="交易数量")
    strategy_id: str = Field(..., description="策略ID")
    
class BacktestResult(BaseModel):
    """回测结果模型"""
    strategy_name: str = Field(..., description="策略名称")
    total_return: float = Field(..., description="累计收益")
    max_drawdown: float = Field(..., description="最大回撤率")
    annual_sharpe: float = Field(..., description="年化夏普比率")
    trade_count: int = Field(..., description="交易次数")
    win_rate: float = Field(..., description="胜率")
    profit_factor: float = Field(..., description="盈亏比")
    signals: List[TradeSignal] = Field(..., description="交易信号列表")
    
class FactCheckResult(BaseModel):
    """事实校验结果模型"""
    check_id: str = Field(..., description="校验ID")
    strategy_name: str = Field(..., description="策略名称")
    is_consistent: bool = Field(..., description="是否一致")
    inconsistencies: List[str] = Field(default_factory=list, description="不一致点列表")
    timestamp: datetime = Field(default_factory=datetime.now, description="校验时间戳")