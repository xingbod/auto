"""
utils.py
========
RL tutorial 共享工具:网络结构、环境封装、评估、绘图。

涵盖 step3 (DQN) ~ step5 (PPO) 共用的基础组件。
step1 (Bandit) 和 step2 (Q-learning) 用纯 NumPy,不依赖 torch。
"""
from __future__ import annotations

import os
import random
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, List, Tuple

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn


# =============================================================================
# 1. 通用工具
# =============================================================================
def set_seed(seed: int = 0) -> None:
    """固定所有随机源,保证可复现。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_env(env_id: str, seed: int = 0, **kwargs) -> gym.Env:
    """工厂函数:统一处理 env 包装、随机种子。"""
    env = gym.make(env_id, **kwargs)
    env.reset(seed=seed)
    env.action_space.seed(seed)
    return env


# =============================================================================
# 2. 网络结构
# =============================================================================
class QNetwork(nn.Module):
    """DQN 用的 Q(s,a) 网络。输入 state,输出每个 action 的 Q 值。
    对 CartPole(4 维输入,2 个动作)够用。"""

    def __init__(self, state_dim: int, action_dim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class PolicyNetwork(nn.Module):
    """REINFORCE 用的策略网络。对离散动作输出 logits (softmax 在 loss 内部处理)。"""

    def __init__(self, state_dim: int, action_dim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def act(self, state: np.ndarray) -> Tuple[int, torch.Tensor]:
        """采样一个动作,返回 (action, log_prob)。"""
        s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
        logits = self.forward(s)
        dist = torch.distributions.Categorical(logits=logits)
        action = dist.sample()
        return int(action.item()), dist.log_prob(action)


class ActorCritic(nn.Module):
    """PPO 用的 Actor-Critic。共享 backbone,分两个头。"""

    def __init__(self, state_dim: int, action_dim: int, hidden: int = 128):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(state_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
        )
        self.actor = nn.Linear(hidden, action_dim)
        self.critic = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        return self.actor(h), self.critic(h)

    def act(self, state: np.ndarray) -> Tuple[int, torch.Tensor, torch.Tensor]:
        """采样动作,返回 (action, log_prob, value)。"""
        s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
        logits, value = self.forward(s)
        dist = torch.distributions.Categorical(logits=logits)
        action = dist.sample()
        return int(action.item()), dist.log_prob(action), value.squeeze(0)


# =============================================================================
# 3. 评估
# =============================================================================
def evaluate_policy(
    env_id: str,
    policy_fn: Callable[[np.ndarray], int],
    n_episodes: int = 20,
    seed: int = 1000,
) -> Tuple[float, float]:
    """运行 n_episodes 评估策略,返回 (mean_return, std)。"""
    env = make_env(env_id, seed=seed)
    returns: List[float] = []
    for ep in range(n_episodes):
        obs, _ = env.reset(seed=seed + ep)
        total = 0.0
        done = False
        while not done:
            action = policy_fn(obs)
            obs, reward, term, trunc, _ = env.step(action)
            total += float(reward)
            done = term or trunc
        returns.append(total)
    env.close()
    return float(np.mean(returns)), float(np.std(returns))


def dqn_policy(net: QNetwork, env_id: str = "CartPole-v1") -> Callable:
    """给 DQN 网络包装一个可调用的策略函数。"""
    net.eval()

    def fn(state: np.ndarray) -> int:
        with torch.no_grad():
            s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            q = net(s)
            return int(q.argmax(dim=1).item())

    return fn


def pg_policy(net, env_id: str = "CartPole-v1") -> Callable:
    """给策略网络包装一个 deterministic 策略:argmax over logits。"""

    def fn(state: np.ndarray) -> int:
        with torch.no_grad():
            s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            logits = net(s)
            return int(logits.argmax(dim=1).item())

    return fn


def ac_policy(net, env_id: str = "CartPole-v1") -> Callable:
    """给 ActorCritic 网络包装一个 deterministic 策略:argmax over actor logits。
    ActorCritic.forward 返回 (logits, value), 所以这里只取 logits。"""

    def fn(state: np.ndarray) -> int:
        with torch.no_grad():
            s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            out = net(s)
            logits = out[0] if isinstance(out, tuple) else out
            return int(logits.argmax(dim=1).item())

    return fn


# =============================================================================
# 4. 训练曲线绘制
# =============================================================================
def plot_rewards(
    rewards: List[float],
    window: int = 50,
    title: str = "Training Curve",
    save_path: str | None = None,
    ylabel: str = "Episode Return",
    target: float | None = None,
    ax=None,
) -> None:
    """绘制训练曲线 + 滑动平均 + 目标线。
    如果传 ax,画在现有 figure 上(用于子图对齐对比)。否则新建。
    """
    import matplotlib.pyplot as plt

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        created_fig = True

    ax.plot(rewards, alpha=0.3, color="C0", label="raw return")
    if len(rewards) >= window:
        moving = np.convolve(rewards, np.ones(window) / window, mode="valid")
        ax.plot(
            range(window - 1, len(rewards)),
            moving,
            color="C0",
            linewidth=2.0,
            label=f"moving avg (w={window})",
        )
    if target is not None:
        ax.axhline(target, color="green", linestyle="--", alpha=0.6, label=f"target = {target}")
    ax.set_xlabel("Episode")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")

    if created_fig and save_path is not None:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.tight_layout()
        fig.savefig(save_path, dpi=120)
        plt.close(fig)


def plot_comparison(
    curves: dict,
    title: str = "Algorithm Comparison on CartPole-v1",
    save_path: str = "outputs/compare.png",
    window: int = 20,
) -> None:
    """多算法对比:每条曲线一张子图 + 一张大对比图。"""
    import matplotlib.pyplot as plt

    n = len(curves)
    fig, axes = plt.subplots(1, n + 1, figsize=(5 * (n + 1), 4.5))

    # 每条曲线单独
    for ax, (name, rewards) in zip(axes[:n], curves.items()):
        plot_rewards(rewards, window=window, title=name, ax=ax, target=475)

    # 总对比(只画滑动平均)
    for i, (name, rewards) in enumerate(curves.items()):
        if len(rewards) >= window:
            moving = np.convolve(rewards, np.ones(window) / window, mode="valid")
            axes[-1].plot(
                range(window - 1, len(rewards)),
                moving,
                linewidth=2.0,
                label=name,
            )
        else:
            axes[-1].plot(rewards, linewidth=1.5, label=name, alpha=0.6)
    axes[-1].axhline(475, color="green", linestyle="--", alpha=0.6, label="solved=475")
    axes[-1].set_title("All algorithms (moving avg)")
    axes[-1].set_xlabel("Episode")
    axes[-1].set_ylabel("Return")
    axes[-1].grid(alpha=0.3)
    axes[-1].legend()

    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=120)
    plt.close(fig)
    print(f"[saved] {save_path}")


# =============================================================================
# 5. 训练统计辅助
# =============================================================================
@dataclass
class Timer:
    start: float = 0.0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = time.time() - self.start


def fmt_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(seconds, 60)
    return f"{int(m)}m{s:.0f}s"


class RunningMean:
    """维护最近 N 个 episode 的均值,用于打印日志。"""

    def __init__(self, n: int = 20):
        self.n = n
        self.buf: deque = deque(maxlen=n)

    def push(self, x: float) -> float:
        self.buf.append(x)
        return float(np.mean(self.buf))

    def __len__(self) -> int:
        return len(self.buf)


if __name__ == "__main__":
    # 烟测
    set_seed(0)
    env = make_env("CartPole-v1", seed=0)
    obs, _ = env.reset()
    print(f"CartPole reset obs: {obs.shape}, dtype: {obs.dtype}")
    net = QNetwork(4, 2)
    q = net(torch.zeros(1, 4))
    print(f"QNetwork output shape: {q.shape}")
    env.close()
    print("utils.py smoke test OK")
