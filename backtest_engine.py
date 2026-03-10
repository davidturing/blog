"""
回测引擎实现
"""

import polars as pl
import duckdb
from typing import Dict, Any, List
from quant_models import StrategyRule, TradeSignal, BacktestResult

def calculate_indicators(df: pl.DataFrame, strategy_rule: StrategyRule) -> pl.DataFrame:
    """计算技术指标"""
    # 使用DuckDB计算移动平均线
    con = duckdb.connect()
    
    # 注册DataFrame
    con.register('price_data', df)
    
    # 计算快线和慢线
    query = f"""
    SELECT 
        *,
        AVG(close) OVER (ORDER BY date ROWS BETWEEN {strategy_rule.fast_window-1} PRECEDING AND CURRENT ROW) AS fast_ma,
        AVG(close) OVER (ORDER BY date ROWS BETWEEN {strategy_rule.slow_window-1} PRECEDING AND CURRENT ROW) AS slow_ma
    FROM price_data
    ORDER BY date
    """
    
    result_df = con.execute(query).fetchdf()
    con.close()
    
    # 转换为Polars DataFrame
    return pl.from_pandas(result_df)

def generate_signals(df: pl.DataFrame, strategy_rule: StrategyRule) -> List[TradeSignal]:
    """生成交易信号"""
    signals = []
    
    # 找到快线上穿慢线和下穿慢线的位置
    for i in range(1, len(df)):
        prev_fast_ma = df[i-1]["fast_ma"]
        prev_slow_ma = df[i-1]["slow_ma"]
        curr_fast_ma = df[i]["fast_ma"]
        curr_slow_ma = df[i]["slow_ma"]
        curr_date = df[i]["date"]
        curr_close = df[i]["close"]
        
        # 金叉（买入信号）
        if prev_fast_ma <= prev_slow_ma and curr_fast_ma > curr_slow_ma:
            signals.append(TradeSignal(
                timestamp=curr_date,
                symbol="TEST",
                signal_type="BUY",
                price=curr_close,
                quantity=100,  # 固定交易数量
                strategy_id=strategy_rule.strategy_name
            ))
        
        # 死叉（卖出信号）
        elif prev_fast_ma >= prev_slow_ma and curr_fast_ma < curr_slow_ma:
            signals.append(TradeSignal(
                timestamp=curr_date,
                symbol="TEST",
                signal_type="SELL",
                price=curr_close,
                quantity=100,
                strategy_id=strategy_rule.strategy_name
            ))
    
    return signals

def calculate_performance(signals: List[TradeSignal], df: pl.DataFrame) -> BacktestResult:
    """计算绩效指标"""
    if len(signals) == 0:
        return BacktestResult(
            strategy_name="DualMovingAverage",
            total_return=0.0,
            max_drawdown=0.0,
            annual_sharpe=0.0,
            trade_count=0,
            win_rate=0.0,
            profit_factor=0.0,
            signals=[]
        )
    
    # 模拟交易执行
    positions = []
    current_position = None
    
    for signal in signals:
        if signal.signal_type == "BUY" and current_position is None:
            current_position = {
                "entry_price": signal.price,
                "entry_date": signal.timestamp,
                "quantity": signal.quantity
            }
        elif signal.signal_type == "SELL" and current_position is not None:
            # 计算盈亏
            pnl = (signal.price - current_position["entry_price"]) * current_position["quantity"]
            positions.append({
                "entry_price": current_position["entry_price"],
                "exit_price": signal.price,
                "pnl": pnl,
                "entry_date": current_position["entry_date"],
                "exit_date": signal.timestamp,
                "win": pnl > 0
            })
            current_position = None
    
    # 计算绩效指标
    if len(positions) == 0:
        return BacktestResult(
            strategy_name="DualMovingAverage",
            total_return=0.0,
            max_drawdown=0.0,
            annual_sharpe=0.0,
            trade_count=0,
            win_rate=0.0,
            profit_factor=0.0,
            signals=signals
        )
    
    total_pnl = sum(pos["pnl"] for pos in positions)
    initial_capital = 100000  # 假设初始资金10万
    total_return = total_pnl / initial_capital
    
    # 计算最大回撤
    cumulative_pnl = [0]
    running_pnl = 0
    for pos in positions:
        running_pnl += pos["pnl"]
        cumulative_pnl.append(running_pnl)
    
    max_drawdown = 0
    peak = 0
    for pnl in cumulative_pnl:
        if pnl > peak:
            peak = pnl
        drawdown = (peak - pnl) / initial_capital
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # 计算胜率
    wins = sum(1 for pos in positions if pos["win"])
    win_rate = wins / len(positions)
    
    # 计算盈亏比
    avg_win = sum(pos["pnl"] for pos in positions if pos["win"]) / max(wins, 1)
    losses = len(positions) - wins
    avg_loss = abs(sum(pos["pnl"] for pos in positions if not pos["win"]) / max(losses, 1)) if losses > 0 else 1
    profit_factor = avg_win / avg_loss if avg_loss > 0 else float('inf')
    
    # 简化的年化夏普比率（假设无风险利率为0）
    returns = [pos["pnl"] / initial_capital for pos in positions]
    if len(returns) > 1:
        avg_return = sum(returns) / len(returns)
        std_return = (sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)) ** 0.5
        annual_sharpe = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
    else:
        annual_sharpe = 0
    
    return BacktestResult(
        strategy_name="DualMovingAverage",
        total_return=total_return,
        max_drawdown=max_drawdown,
        annual_sharpe=annual_sharpe,
        trade_count=len(positions),
        win_rate=win_rate,
        profit_factor=profit_factor,
        signals=signals
    )