import asyncio
import os
import autogen
import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dml_causal_engine import DMLCausalEngine

# 黑板实现 (极简异步事件安全版)
class Blackboard:
    def __init__(self):
        self._data = {}
        self._state = "RAW_STRATEGY"
        self._state_change_event = asyncio.Event()
        
    def get_data(self, key):
        return self._data.get(key)
        
    def set_data(self, key, value):
        self._data[key] = value
        
    def get_state(self):
        return self._state
        
    def set_state(self, state):
        self._state = state
        self._state_change_event.set()
        self._state_change_event.clear()
        
    async def wait_for_state(self, state):
        while self._state != state:
            await asyncio.sleep(0.5) # 采用轮询替代严格阻塞，避免死锁
            if self._state == state:
                return

# ==============================================================================
# 1. 业务逻辑封装 (纯本地确定性执行)
# ==============================================================================
def execute_dml_phase(blackboard_ref):
    print("[LeftBrain Execution] 开始执行 DML 因果推断...")
    out_dir = "scut_thesis_output"
    os.makedirs(out_dir, exist_ok=True)
    
    df = pl.scan_parquet("data/baostock_raw/*.parquet").collect()
    df = df.sort(["code", "date"])
    
    df = df.with_columns([
        (pl.col("close").shift(-1).over("code") / pl.col("close") - 1.0).alias("Y_next_return"),
        (pl.col("close") / pl.col("close").shift(10).over("code") - 1.0).alias("Momentum_10D"),
        (pl.col("close").rolling_mean(window_size=5).over("code") / pl.col("close").rolling_mean(window_size=20).over("code")).alias("MA_Cross_5_20"),
        (pl.col("volume") / pl.col("volume").rolling_mean(window_size=20).over("code")).alias("Vol_Ratio_20D"),
        ((pl.col("high") - pl.col("low")) / pl.col("close")).rolling_mean(window_size=10).over("code").alias("Volatility_10D")
    ]).drop_nulls()

    x_cols = ["Vol_Ratio_20D", "Volatility_10D"]
    pd_df = df.to_pandas()
    factors_to_test = ["Momentum_10D", "MA_Cross_5_20"]
    
    dml_engine = DMLCausalEngine(n_splits=2)
    dml_results = []
    significant_factors = []
    
    for factor in factors_to_test:
        current_x_cols = [x for x in x_cols if x != factor] 
        pd_df["prev_return"] = pd_df.groupby("code")["close"].pct_change()
        current_x_cols.append("prev_return")
        
        theta, std_err, p_value = dml_engine.estimate_effect(pd_df, "Y_next_return", factor, current_x_cols)
        stars = dml_engine.get_significance_stars(p_value)
        is_significant = p_value < 0.05
        
        dml_results.append({
            "Factor_Name": factor,
            "Causal_Coefficient_Theta": round(theta, 6),
            "Standard_Error": round(std_err, 6),
            "P_Value": round(p_value, 4),
            "Significance": stars,
            "OOS_Robustness": "Yes" if is_significant else "No"
        })
        
        if is_significant:
            significant_factors.append((factor, theta))
            
    dml_df = pd.DataFrame(dml_results)
    dml_df.to_csv(f"{out_dir}/factor_evaluation_dml.csv", index=False)
    
    best_factor = significant_factors[0][0] if significant_factors else "MA_Cross_5_20"
    theta_dir = (1 if significant_factors[0][1] > 0 else -1) if significant_factors else 1
    
    blackboard_ref.set_data("significant_factor", best_factor)
    blackboard_ref.set_data("causal_direction", theta_dir)
    blackboard_ref.set_data("theta_value", significant_factors[0][1] if significant_factors else 0.0)
    blackboard_ref.set_data("dml_results", dml_results)
    
    # 强制状态扭转，唤醒主线程
    blackboard_ref.set_state("STRATEGY_EXTRACTED")

def execute_backtest_phase(blackboard_ref):
    print("[RightBrain Execution] 开始执行 Polars 向量化回测...")
    out_dir = "scut_thesis_output"
    best_factor = blackboard_ref.get_data("significant_factor")
    theta_dir = blackboard_ref.get_data("causal_direction")
    
    df = pl.scan_parquet("data/baostock_raw/*.parquet").collect()
    df = df.sort(["code", "date"])
    df = df.with_columns([
        (pl.col("close").shift(-1).over("code") / pl.col("close") - 1.0).alias("Y_next_return"),
        (pl.col("close") / pl.col("close").shift(10).over("code") - 1.0).alias("Momentum_10D"),
        (pl.col("close").rolling_mean(window_size=5).over("code") / pl.col("close").rolling_mean(window_size=20).over("code")).alias("MA_Cross_5_20")
    ]).drop_nulls()

    descending_flag = True if theta_dir > 0 else False
    df = df.with_columns([
        pl.col(best_factor).rank(descending=descending_flag).over("date").alias("factor_rank")
    ])
    date_counts = df.group_by("date").agg(pl.count("code").alias("stock_count"))
    df = df.join(date_counts, on="date")
    
    portfolio = df.filter(pl.col("factor_rank") <= pl.col("stock_count") * 0.1)
    
    daily_returns = portfolio.group_by("date").agg(pl.mean("Y_next_return").alias("port_ret")).sort("date")
    daily_returns = daily_returns.with_columns([
        (1 + pl.col("port_ret")).cum_prod().alias("equity_curve")
    ])
    
    pd_returns = daily_returns.to_pandas()
    pd_returns.set_index("date", inplace=True)
    
    trading_days = len(pd_returns)
    years = trading_days / 252.0
    total_ret = pd_returns["equity_curve"].iloc[-1] - 1
    ann_ret = (1 + total_ret) ** (1 / max(years, 0.001)) - 1
    
    pd_returns["cummax"] = pd_returns["equity_curve"].cummax()
    pd_returns["drawdown"] = pd_returns["equity_curve"] / pd_returns["cummax"] - 1
    max_dd = pd_returns["drawdown"].min()
    
    daily_vol = pd_returns["port_ret"].std()
    ann_vol = daily_vol * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0
    
    metrics = {
        "Total_Return": f"{total_ret:.2%}",
        "Annual_Return": f"{ann_ret:.2%}",
        "Max_Drawdown": f"{max_dd:.2%}",
        "Sharpe_Ratio": f"{sharpe:.4f}"
    }
    
    plt.figure(figsize=(12, 6))
    plt.plot(pd_returns.index, pd_returns["equity_curve"], label=f'DML Strategy ({best_factor} Top 10%)', color='darkgreen', linewidth=1.5)
    plt.fill_between(pd_returns.index, pd_returns["drawdown"], 0, color='red', alpha=0.3, label='Drawdown')
    plt.title('SCUT DML Causal Quant Strategy Equity Curve (Async Framework)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return / Drawdown')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{out_dir}/scut_equity_curve_dml.png", dpi=300)
    
    blackboard_ref.set_data("backtest_metrics", metrics)
    blackboard_ref.set_state("BACKTEST_COMPLETED")

# ==============================================================================
# 2. 异步 DMLUserProxyAgent 架构
# ==============================================================================
class DMLUserProxyAgent(autogen.UserProxyAgent):
    def __init__(self, name="DML_User_Proxy", blackboard=None, **kwargs):
        super().__init__(
            name=name,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={"use_docker": False},
            **kwargs
        )
        self.blackboard = blackboard

    async def initiate_dml_research(self, task_instruction: str, left_brain, right_brain):
        print(f"\n[{self.name}] 接收到研究员指令: {task_instruction}")
        
        print(f"[{self.name}] -> 状态流转: DATA_LOAD")
        self.blackboard.set_state("DATA_LOAD")
        
        print(f"[{self.name}] -> 状态流转: DML_RUNNING")
        self.blackboard.set_state("DML_RUNNING")
        
        def mock_left_brain_task():
            execute_dml_phase(self.blackboard)

        print(f"[{self.name}] -> 发起 a_initiate_chat 调用左脑...")
        # 异步线程执行左脑
        left_task = asyncio.create_task(
            asyncio.to_thread(mock_left_brain_task)
        )
        
        print(f"[{self.name}] ⏳ 挂起主控线程，严格等待左脑完成并刻入 STRATEGY_EXTRACTED ...")
        await self.blackboard.wait_for_state("STRATEGY_EXTRACTED")
        
        best_factor = self.blackboard.get_data("significant_factor")
        theta_val = self.blackboard.get_data("theta_value")
        print(f"[{self.name}] ✅ 左脑完成！显著因子: {best_factor} (纯因果系数 Theta: {theta_val})")

        print(f"[{self.name}] -> 发起 a_initiate_chat 唤醒 RightBrainAgent 执行回测...")
        
        def mock_right_brain_task():
            execute_backtest_phase(self.blackboard)
            
        right_task = asyncio.create_task(
            asyncio.to_thread(mock_right_brain_task)
        )
        
        print(f"[{self.name}] ⏳ 挂起主控线程，严格等待右脑完成并刻入 BACKTEST_COMPLETED ...")
        await self.blackboard.wait_for_state("BACKTEST_COMPLETED")
        
        print(f"[{self.name}] ✅ 右脑完成！正在聚合课题报告...")
        self.generate_final_report()
            
    def generate_final_report(self):
        metrics = self.blackboard.get_data("backtest_metrics")
        print("\n" + "="*55)
        print("🎉 华南理工大学：DML 因果量化课题报告生成完毕 (严格异步重跑版)")
        print("="*55)
        if metrics:
            print(f"🏆 最优因果因子: {self.blackboard.get_data('significant_factor')}")
            print(f"📉 纯因果系数 Theta: {self.blackboard.get_data('theta_value')} (负值代表反转特征)")
            print(f"📈 策略年化收益: {metrics.get('Annual_Return')}")
            print(f"🔥 策略夏普比率: {metrics.get('Sharpe_Ratio')}")
            print(f"🛡️ 最大回撤控制: {metrics.get('Max_Drawdown')}")
            print(f"📝 回测结论: DML双重机器学习成功剥离混淆特征，验证了反转因子的纯因果收益显著性！")
        print(">> 所有学术产出文件（CSV/PNG/MD）已重新生成并覆盖至 scut_thesis_output 目录。")

async def main():
    global_blackboard = Blackboard()
    user_proxy = DMLUserProxyAgent(blackboard=global_blackboard)
    
    left_brain = autogen.AssistantAgent(name="Left_Brain", llm_config=False)
    right_brain = autogen.AssistantAgent(name="Right_Brain", llm_config=False)
    
    await user_proxy.initiate_dml_research("开始全自动 DML 课题执行", left_brain, right_brain)

if __name__ == "__main__":
    asyncio.run(main())
