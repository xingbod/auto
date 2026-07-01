"""
step1_bandit.py
===============
Step 1: 多臂老虎机 (Multi-Armed Bandit)

核心问题: 在 N 个未知收益分布的"手臂"中,如何用最少的总遗憾
          找出收益最高的那一个?

四种策略对比 (3 个随机种子平均):
  1. random        -- 纯随机 (baseline)
  2. eps-greedy    -- 固定 ε 探索 (ε=0.1)
  3. ucb1          -- Upper Confidence Bound 1
  4. eps-decay     -- ε 随步数指数衰减 (0.5 -> 0.01)

跑完画图: outputs/bandit.png
"""
from __future__ import annotations

import os

import numpy as np

from utils import set_seed


# =============================================================================
# 老虎机环境
# =============================================================================
class BanditEnv:
    """K 臂伯努利老虎机(连续收益版本,用高斯采样)。"""

    def __init__(self, k: int = 5, seed: int = 0):
        rng = np.random.default_rng(seed)
        # 真实臂均值,范围 [-1, 1] 之间
        self.means = rng.uniform(-1.0, 1.0, size=k)
        self.k = k

    def pull(self, action: int, rng: np.random.Generator) -> float:
        """拉 action 号臂,返回一个 reward(均值+0.5*noise)。"""
        return float(self.means[action] + 0.5 * rng.standard_normal())


# =============================================================================
# 四种策略
# =============================================================================
def run_random(env: BanditEnv, steps: int, rng: np.random.Generator):
    rewards = np.zeros(steps)
    for t in range(steps):
        a = rng.integers(0, env.k)
        rewards[t] = env.pull(a, rng)
    return rewards


def run_eps_greedy(env: BanditEnv, steps: int, rng: np.random.Generator, eps: float = 0.1):
    Q = np.zeros(env.k)  # 估值
    N = np.zeros(env.k, dtype=int)  # 计数
    rewards = np.zeros(steps)
    for t in range(steps):
        if rng.random() < eps:
            a = rng.integers(0, env.k)
        else:
            a = int(np.argmax(Q))
        r = env.pull(a, rng)
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]  # 增量均值
        rewards[t] = r
    return rewards


def run_ucb1(env: BanditEnv, steps: int, rng: np.random.Generator, c: float = 2.0):
    Q = np.zeros(env.k)
    N = np.zeros(env.k, dtype=int)
    rewards = np.zeros(steps)
    for t in range(steps):
        # 未被选过的臂先选
        untried = np.where(N == 0)[0]
        if len(untried) > 0:
            a = int(untried[0])
        else:
            bonus = c * np.sqrt(np.log(t + 1) / N)
            a = int(np.argmax(Q + bonus))
        r = env.pull(a, rng)
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]
        rewards[t] = r
    return rewards


def run_eps_decay(env: BanditEnv, steps: int, rng: np.random.Generator,
                  eps_start: float = 0.5, eps_end: float = 0.01, decay: float = 200.0):
    Q = np.zeros(env.k)
    N = np.zeros(env.k, dtype=int)
    rewards = np.zeros(steps)
    for t in range(steps):
        eps = max(eps_end, eps_start * np.exp(-t / decay))
        if rng.random() < eps:
            a = rng.integers(0, env.k)
        else:
            a = int(np.argmax(Q))
        r = env.pull(a, rng)
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]
        rewards[t] = r
    return rewards


# =============================================================================
# 主程序
# =============================================================================
def main(steps: int = 1000, n_seeds: int = 5, save_path: str = "outputs/bandit.png") -> None:
    import matplotlib.pyplot as plt

    set_seed(0)

    strategies = {
        "random (baseline)":     ("random",     {}),
        "eps-greedy (eps=0.1)":   ("eps_greedy", {"eps": 0.1}),
        "UCB1 (c=2.0)":           ("ucb1",       {"c": 2.0}),
        "eps-decay (0.5->0.01)":  ("eps_decay",  {"eps_start": 0.5, "eps_end": 0.01, "decay": 200.0}),
    }
    runners = {
        "random":    run_random,
        "eps_greedy": run_eps_greedy,
        "ucb1":      run_ucb1,
        "eps_decay": run_eps_decay,
    }

    # 累加器
    all_rewards = {name: np.zeros((n_seeds, steps)) for name in strategies}
    optimal_arm_rewards = {name: np.zeros((n_seeds, steps)) for name in strategies}
    best_arm = 0
    best_mean = -np.inf

    for s in range(n_seeds):
        env = BanditEnv(k=5, seed=s)
        # 每个 seed 重新生成的最优臂
        if env.means.max() > best_mean:
            best_mean = float(env.means.max())
            best_arm = int(np.argmax(env.means))
        opt = env.means[best_arm]  # 近似最优回报(忽略噪声)

        for name, (fn_name, kwargs) in strategies.items():
            runner = runners[fn_name]
            rng = np.random.default_rng(1000 + s)
            r = runner(env, steps, rng, **kwargs)
            all_rewards[name][s] = r
            optimal_arm_rewards[name][s] = np.where(r >= opt - 0.5, 1.0, 0.0)
        print(f"  seed {s+1}/{n_seeds} done. best arm = {best_arm} (mean={best_mean:+.2f})")

    # 画图
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左:平均 reward (含噪声,每步瞬时)
    for name in strategies:
        mean = all_rewards[name].mean(axis=0)
        std = all_rewards[name].std(axis=0) / np.sqrt(n_seeds)
        x = np.arange(steps)
        axes[0].plot(x, mean, label=name, linewidth=2.0)
        axes[0].fill_between(x, mean - std, mean + std, alpha=0.15)
    axes[0].axhline(best_mean, color="green", linestyle="--", alpha=0.5,
                    label=f"optimal arm mean = {best_mean:+.2f}")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Average Reward (with noise)")
    axes[0].set_title("Bandit: Per-step Reward")
    axes[0].legend(loc="lower right")
    axes[0].grid(alpha=0.3)

    # 右:累积 reward (sum up)
    for name in strategies:
        cum = all_rewards[name].mean(axis=0).cumsum()
        axes[1].plot(cum, label=name, linewidth=2.0)
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Cumulative Reward")
    axes[1].set_title("Bandit: Cumulative Reward (higher is better)")
    axes[1].legend(loc="lower right")
    axes[1].grid(alpha=0.3)

    fig.suptitle("Multi-Armed Bandit: Exploration Strategies (5 seeds avg)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=120)
    print(f"\n[saved] {save_path}")

    # 控制台总结
    print("\n=== Final cumulative reward (mean over 5 seeds) ===")
    for name in strategies:
        cum_final = all_rewards[name].mean(axis=0).cumsum()[-1]
        print(f"  {name:<32s} {cum_final:+.1f}")


if __name__ == "__main__":
    main()
