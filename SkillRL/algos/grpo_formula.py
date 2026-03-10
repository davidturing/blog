"""
GRPO (Generalized Reward Proximal Optimization) 算法核心公式
用于量化策略的递归技能增强
"""

import numpy as np
import torch
from typing import Dict, List, Tuple

def compute_advantages(
    rewards: np.ndarray, 
    values: np.ndarray, 
    gamma: float = 0.99, 
    lam: float = 0.95
) -> np.ndarray:
    """
    计算广义优势估计 (GAE)
    
    Args:
        rewards: 奖励序列
        values: 价值函数估计
        gamma: 折扣因子
        lam: GAE参数
        
    Returns:
        advantages: 优势估计
    """
    # 计算TD误差
    deltas = rewards[:-1] + gamma * values[1:] - values[:-1]
    
    # 计算GAE
    advantages = np.zeros_like(deltas)
    gae = 0
    for t in reversed(range(len(deltas))):
        gae = deltas[t] + gamma * lam * gae
        advantages[t] = gae
        
    return advantages

def grpo_loss(
    old_log_probs: torch.Tensor,
    new_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    epsilon: float = 0.2,
    beta: float = 0.01
) -> torch.Tensor:
    """
    GRPO损失函数
    
    Args:
        old_log_probs: 旧策略的对数概率
        new_log_probs: 新策略的对数概率
        advantages: 优势估计
        epsilon: PPO裁剪参数
        beta: 熵正则化系数
        
    Returns:
        loss: GRPO损失
    """
    # 计算概率比
    ratio = torch.exp(new_log_probs - old_log_probs)
    
    # PPO裁剪目标
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - epsilon, 1 + epsilon) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()
    
    # 熵正则化
    entropy = -torch.sum(torch.exp(new_log_probs) * new_log_probs)
    
    # 总损失
    loss = policy_loss - beta * entropy
    
    return loss