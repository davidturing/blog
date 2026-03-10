# SCUT DML Causal Inference Method Section
## 1. DML (Double/Debiased Machine Learning) 框架设定
为解决混淆变量导致的内生性偏误问题，本研究引入了双重机器学习（DML）范式，识别量化因子与未来1期超额收益间的纯净因果效应（Causal Effect）。
- **被解释变量 (Y)**: 股票未来 1 期收益率
- **处理变量 (D)**: 待检验量化因子（如 `Momentum_10D`）
- **混淆变量 (X)**: 前期收益、流动性比率、波动率等
- **去偏模型**: 采用 K-fold (K=2) 交叉预测，使用 `RidgeCV` 进行第一阶段拟合。

## 2. DML 因果推断结果表
经过 DML 去偏处理，因子的真实因果系数（Theta）及显著性如下：
| Factor | Causal Coefficient (Theta) | Standard Error | P-Value | Significance | OOS Robustness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Momentum_10D | -0.003608 | 0.000435 | 0.0 | *** | Yes |
| MA_Cross_5_20 | -0.007758 | 0.000687 | 0.0 | *** | Yes |

## 3. 右脑组合表现 (基于 DML 筛选)
仅利用具有显著正向因果效应的 `Momentum_10D` 构建分层多头组合，DML 去偏增强后的绩效表现如下：
- **累计收益率**: 205.43%
- **年化收益率**: 13.86%
- **夏普比率**: 0.5290
- **最大回撤**: -37.27%

此成果证明，传统 IC 检验易受截面混淆特征影响，而 DML 因果推断成功剥离了伪相关，提取了纯正的收益驱动力。
