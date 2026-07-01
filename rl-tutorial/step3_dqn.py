"""
step3_dqn.py
============
Step 3: DQN (Deep Q-Network, Mnih 2013/2015)

环境: CartPole-v1 (连续 4 维状态, 2 个离散动作, 满分 500)
算法: DQN (off-policy, value-based, function approximation)

三大件 (本 step 的核心):
  ① Replay Buffer: 存最近 N 条 (s, a, r, s', done), 训练时随机采样 batch
  ② Target Network: 慢速更新的 Q' 用于算 TD 目标, 每 C 步同步一次
  ③ ε-decay: 动作选择 ε-greedy, ε 从 1.0 指数衰减到 0.05

超参 (Sutton & Barto 经典配置):
  lr=1e-3, gamma=0.99, batch=64, buffer=10000, target_update=10
  eps: 1.0 → 0.05, decay_rate=200 (per-step)
  hidden=128, 2 层 MLP

跑完: outputs/dqn.png (训练曲线 + 评估曲线对比)
"""
from __future__ import annotations

import os
import random
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from utils import (
    QNetwork,
    Timer,
    fmt_time,
    set_seed,
    evaluate_policy,
    dqn_policy,
    plot_rewards,
)


# =============================================================================
# 1. Replay Buffer
# =============================================================================
class ReplayBuffer:
    """固定大小的循环队列, 存 (s, a, r, s', done) 五元组。"""

    def __init__(self, capacity: int):
        self.buf: deque = deque(maxlen=capacity)

    def push(self, s, a, r, s_next, done):
        self.buf.append((s, a, r, s_next, done))

    def sample(self, batch_size: int) -> Tuple:
        batch = random.sample(self.buf, batch_size)
        s, a, r, s_next, done = zip(*batch)
        return (
            torch.as_tensor(np.array(s), dtype=torch.float32),
            torch.as_tensor(a, dtype=torch.int64).unsqueeze(1),
            torch.as_tensor(r, dtype=torch.float32).unsqueeze(1),
            torch.as_tensor(np.array(s_next), dtype=torch.float32),
            torch.as_tensor(done, dtype=torch.float32).unsqueeze(1),
        )

    def __len__(self) -> int:
        return len(self.buf)


# =============================================================================
# 2. DQN Agent
# =============================================================================
class DQNAgent:
    """两个网络 (online + target), ε-greedy 选动作, MSE loss 训练。"""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden: int = 128,
        lr: float = 1e-3,
        gamma: float = 0.99,
        buffer_capacity: int = 10000,
        batch_size: int = 64,
        target_update: int = 10,
    ):
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update = target_update

        self.online = QNetwork(state_dim, action_dim, hidden)
        self.target = QNetwork(state_dim, action_dim, hidden)
        self.target.load_state_dict(self.online.state_dict())  # 初始同步
        self.target.eval()  # target 不参与训练

        self.optimizer = optim.Adam(self.online.parameters(), lr=lr)
        self.buffer = ReplayBuffer(buffer_capacity)

    def act(self, state: np.ndarray, eps: float) -> int:
        """ε-greedy: ε 概率随机, 否则 argmax Q。"""
        if random.random() < eps:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            q = self.online(s)
            return int(q.argmax(dim=1).item())

    def learn(self) -> float | None:
        """采样 batch 算 TD 误差, 反向传播更新 online 网络。"""
        if len(self.buffer) < self.batch_size:
            return None
        s, a, r, s_next, done = self.buffer.sample(self.batch_size)

        with torch.no_grad():
            # 用 target 网络算下一步的最大 Q 值
            q_next = self.target(s_next).max(dim=1, keepdim=True)[0]
            target = r + self.gamma * q_next * (1.0 - done)

        q_pred = self.online(s).gather(1, a)
        loss = nn.functional.mse_loss(q_pred, target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.item())

    def sync_target(self) -> None:
        """把 online 网络的权重复制到 target。"""
        self.target.load_state_dict(self.online.state_dict())


# =============================================================================
# 3. 训练主循环
# =============================================================================
@dataclass
class TrainConfig:
    env_id: str = "CartPole-v1"
    n_episodes: int = 500
    max_steps: int = 500
    eps_start: float = 1.0
    eps_end: float = 0.05
    eps_decay: float = 200.0  # 指数衰减常数 (越大衰减越慢)
    target_update: int = 10   # 每 C 个 episode 同步 target 网络
    eval_every: int = 20
    eval_episodes: int = 10
    save_path: str = "outputs/dqn.png"
    pkl_path: str = "outputs/dqn.pkl"  # 训练数据 pickle, 给 plot_comparison 用


def train_dqn(cfg: TrainConfig, seed: int = 0) -> Tuple[DQNAgent, List[float], List[float]]:
    import gymnasium as gym
    import pickle

    set_seed(seed)
    env = gym.make(cfg.env_id)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    agent = DQNAgent(state_dim, action_dim)
    rewards_hist: List[float] = []
    eval_hist: List[Tuple[int, float, float]] = []  # (ep, mean, std)

    with Timer() as t:
        for ep in range(cfg.n_episodes):
            # ε 指数衰减 (按 step 衰减更平滑, 但这里简化按 episode)
            eps = max(cfg.eps_end, cfg.eps_start * np.exp(-ep / cfg.eps_decay))
            state, _ = env.reset(seed=seed + ep)
            total = 0.0

            for step in range(cfg.max_steps):
                a = agent.act(state, eps)
                s_next, r, term, trunc, _ = env.step(a)
                done = term or trunc
                agent.buffer.push(state, a, r, s_next, float(done))
                agent.learn()

                state = s_next
                total += float(r)
                if done:
                    break

            rewards_hist.append(total)

            # 定期同步 target + 评估
            if (ep + 1) % cfg.target_update == 0:
                agent.sync_target()
            if (ep + 1) % cfg.eval_every == 0:
                mean, std = evaluate_policy(cfg.env_id, dqn_policy(agent.online), n_episodes=cfg.eval_episodes, seed=10_000 + ep)
                eval_hist.append((ep + 1, mean, std))
                print(f"  ep {ep+1:4d} | train={total:6.1f} | eval={mean:6.1f}±{std:5.1f} | eps={eps:.3f} | buf={len(agent.buffer)}")

    env.close()
    print(f"\n[done] 训练 {cfg.n_episodes} ep 用时 {fmt_time(t.elapsed)}")

    # 评估最终策略
    final_mean, final_std = evaluate_policy(cfg.env_id, dqn_policy(agent.online), n_episodes=50, seed=99999)
    print(f"  最终评估 (50 ep): {final_mean:.1f} ± {final_std:.1f}")
    solved = "✓ SOLVED" if final_mean >= 475 else "✗ unsolved"
    print(f"  CartPole-v1 解决标准 = 475 (满分 500) → {solved}")

    # 画图
    plot_rewards(
        rewards_hist,
        title=f"DQN on {cfg.env_id}\nfinal eval: {final_mean:.0f} ± {final_std:.0f} ({solved})",
        target=475,
        save_path=cfg.save_path,
    )
    print(f"[saved] {cfg.save_path}")

    # pickle 训练曲线
    os.makedirs(os.path.dirname(cfg.pkl_path) or ".", exist_ok=True)
    with open(cfg.pkl_path, "wb") as f:
        pickle.dump(rewards_hist, f)

    return agent, rewards_hist, eval_hist


# =============================================================================
# 4. 主程序
# =============================================================================
if __name__ == "__main__":
    cfg = TrainConfig()
    agent, rewards, evals = train_dqn(cfg)
