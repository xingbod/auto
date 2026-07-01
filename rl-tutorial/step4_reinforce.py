"""
step4_reinforce.py
==================
Step 4: REINFORCE (Williams 1992, Policy Gradient)

环境: CartPole-v1
算法: 蒙特卡洛策略梯度 (回合制, on-policy)

核心公式 (Policy Gradient Theorem):
  ∇θ J(θ) = E_τ [ Σ_t ∇θ log π(a_t | s_t; θ) · G_t ]
  loss = - Σ_t log π(a_t | s_t; θ) · G_t   (取负号, 用梯度下降优化)

要点:
  - 回合制更新: 必须等一个完整 episode 结束才能算 G_t
  - G_t 从后往前算: G_t = r_t + γ * G_{t+1},  终止时 G_T = 0
  - 标准化 G_t (减去均值除以标准差) 可以显著降低方差 (baseline trick)

超参:
  lr=1e-3, gamma=0.99, hidden=128
  无 replay buffer, 每个 episode 一次性更新
"""
from __future__ import annotations

import os
import pickle
from dataclasses import dataclass
from typing import List

import numpy as np
import torch
import torch.optim as optim

from utils import (
    PolicyNetwork,
    Timer,
    fmt_time,
    set_seed,
    evaluate_policy,
    pg_policy,
    plot_rewards,
)


# =============================================================================
# 1. 单 episode 数据收集
# =============================================================================
def collect_trajectory(env, net: PolicyNetwork, max_steps: int) -> tuple:
    """跑一个 episode, 返回 (states, actions, rewards, log_probs, total_reward)。"""
    states, actions, rewards, log_probs = [], [], [], []
    state, _ = env.reset()
    total = 0.0
    for _ in range(max_steps):
        a, lp = net.act(state)
        s_next, r, term, trunc, _ = env.step(a)
        states.append(state)
        actions.append(a)
        rewards.append(float(r))
        log_probs.append(lp)
        state = s_next
        total += float(r)
        if term or trunc:
            break
    return states, actions, rewards, log_probs, total


# =============================================================================
# 2. 折扣回报 + baseline 标准化
# =============================================================================
def compute_returns(rewards: List[float], gamma: float = 0.99) -> np.ndarray:
    """从后往前算 G_t = r_t + γ * G_{t+1}。"""
    G = np.zeros(len(rewards), dtype=np.float32)
    running = 0.0
    for t in reversed(range(len(rewards))):
        running = rewards[t] + gamma * running
        G[t] = running
    return G


# =============================================================================
# 3. REINFORCE 训练
# =============================================================================
@dataclass
class TrainConfig:
    env_id: str = "CartPole-v1"
    n_episodes: int = 1500
    max_steps: int = 500
    gamma: float = 0.99
    lr: float = 1e-3
    hidden: int = 128
    use_baseline: bool = True
    eval_every: int = 50
    eval_episodes: int = 10
    save_path: str = "outputs/reinforce.png"
    pkl_path: str = "outputs/reinforce.pkl"


def train_reinforce(cfg: TrainConfig, seed: int = 0):
    import gymnasium as gym

    set_seed(seed)
    env = gym.make(cfg.env_id)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    net = PolicyNetwork(state_dim, action_dim, hidden=cfg.hidden)
    optimizer = optim.Adam(net.parameters(), lr=cfg.lr)
    rewards_hist: List[float] = []

    with Timer() as t:
        for ep in range(cfg.n_episodes):
            states, actions, rewards, log_probs, total = collect_trajectory(env, net, cfg.max_steps)
            rewards_hist.append(total)

            returns = compute_returns(rewards, cfg.gamma)
            if cfg.use_baseline:
                # 减均值除标准差, 大幅降方差 (类似加 V(s) baseline)
                returns = (returns - returns.mean()) / (returns.std() + 1e-8)

            # 构造 loss: -Σ log π(a|s) * G_t
            log_probs_tensor = torch.stack(log_probs)
            loss = -(log_probs_tensor * torch.as_tensor(returns, dtype=torch.float32)).sum()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (ep + 1) % cfg.eval_every == 0:
                eval_mean, _ = evaluate_policy(cfg.env_id, pg_policy(net), n_episodes=cfg.eval_episodes, seed=20_000 + ep)
                window = rewards_hist[-50:] if len(rewards_hist) >= 50 else rewards_hist
                print(f"  ep {ep+1:4d} | train={total:6.1f} | train_avg50={np.mean(window):6.1f} | eval={eval_mean:6.1f} | loss={loss.item():+.2f}")

    env.close()
    print(f"\n[done] 训练 {cfg.n_episodes} ep 用时 {fmt_time(t.elapsed)}")

    # 最终评估
    final_mean, final_std = evaluate_policy(cfg.env_id, pg_policy(net), n_episodes=50, seed=88888)
    print(f"  最终评估 (50 ep): {final_mean:.1f} ± {final_std:.1f}")
    solved = "✓ SOLVED" if final_mean >= 475 else "✗ unsolved"
    print(f"  CartPole-v1 解决标准 = 475 → {solved}")

    plot_rewards(
        rewards_hist,
        title=f"REINFORCE on {cfg.env_id}\nfinal eval: {final_mean:.0f} ± {final_std:.0f} ({solved})",
        target=475,
        save_path=cfg.save_path,
    )
    print(f"[saved] {cfg.save_path}")

    os.makedirs(os.path.dirname(cfg.pkl_path) or ".", exist_ok=True)
    with open(cfg.pkl_path, "wb") as f:
        pickle.dump(rewards_hist, f)

    return net, rewards_hist


# =============================================================================
# 4. 主程序
# =============================================================================
if __name__ == "__main__":
    cfg = TrainConfig()
    net, rewards = train_reinforce(cfg)
