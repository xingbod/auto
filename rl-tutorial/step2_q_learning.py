"""
step2_q_learning.py
===================
Step 2: 表格型 Q-learning

环境: FrozenLake-v1, is_slippery=True (4x4 网格,带随机滑)
  S 起点, G 终点(给 +1 reward), H 洞(0 reward 终止), F 普通格
  用 slippery 是因为它让随机走更容易意外触达 G,加速学习
  (真正 model-free 训练会同时学到对付滑动的稳健策略)

算法: Q-learning (off-policy, model-free)
  Q(s,a) <- Q(s,a) + α * [r + γ * max_a' Q(s', a') - Q(s,a)]

超参:
  α = 0.3    学习率
  γ = 0.99   折扣
  ε 1.0 -> 0.05 指数衰减 (decay=2000)
  10000 episodes

输出: outputs/qlearning.png
  - 左: episode reward 曲线 (100-ep 滑动平均)
  - 中: 最终 Q-table 16x4 热图
  - 右: 4x4 网格 + 最优策略箭头
"""
from __future__ import annotations

import os

import numpy as np

from utils import set_seed


# =============================================================================
# 4x4 网格布局
# =============================================================================
# FrozenLake 4x4 的格子布局 (从左上开始 0-15):
#
#  S F F F        S=start(0), F=frozen(非终止), H=hole(终止), G=goal(15)
#  F H F F
#  F F F H
#  H F F G
#
# 箭头可视化时把 state idx 映射到 (row, col)
def idx_to_rc(idx: int, n: int = 4):
    return idx // n, idx % n


def plot_arrow(arrow: str):
    return {"left": "←", "right": "→", "up": "↑", "down": "↓"}[arrow]


# FrozenLake 4x4 地图标记
FROZEN_LAKE_MAP = [
    "SFFF",
    "FHFH",
    "FFFH",
    "HFFG",
]


# =============================================================================
# Q-learning 主体
# =============================================================================
def q_learning(
    env,
    n_episodes: int = 2000,
    alpha: float = 0.1,
    gamma: float = 0.99,
    eps_start: float = 1.0,
    eps_end: float = 0.01,
    decay: float = 300.0,
    seed: int = 0,
) -> tuple[np.ndarray, list[float]]:
    n_states = env.observation_space.n
    n_actions = env.action_space.n
    Q = np.zeros((n_states, n_actions))

    rewards_history: list[float] = []
    rng = np.random.default_rng(seed)

    for ep in range(n_episodes):
        eps = max(eps_end, eps_start * np.exp(-ep / decay))
        state, _ = env.reset(seed=seed + ep)
        total = 0.0
        done = False
        steps = 0
        max_steps = 200  # 防止死循环

        while not done and steps < max_steps:
            # ε-greedy
            if rng.random() < eps:
                action = int(rng.integers(0, n_actions))
            else:
                action = int(np.argmax(Q[state]))
            next_state, reward, term, trunc, _ = env.step(action)
            done = term or trunc

            # Q-learning 更新
            target = reward + gamma * (0.0 if done else np.max(Q[next_state]))
            td_error = target - Q[state, action]
            Q[state, action] += alpha * td_error

            state = next_state
            total += reward
            steps += 1

        rewards_history.append(total)

    return Q, rewards_history


# =============================================================================
# 主程序
# =============================================================================
def main(save_path: str = "outputs/qlearning.png") -> None:
    import gymnasium as gym
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrow

    set_seed(0)
    env = gym.make("FrozenLake-v1", is_slippery=True, map_name="4x4")

    print("Training Q-learning on FrozenLake-v1 (4x4, slippery)...")
    Q, rewards = q_learning(env, n_episodes=10000, alpha=0.3, gamma=0.99,
                            eps_start=1.0, eps_end=0.05, decay=2000.0, seed=0)

    # ===== 评估最终策略 =====
    n_eval = 100
    successes = 0
    for i in range(n_eval):
        s, _ = env.reset(seed=10_000 + i)
        done = False
        steps = 0
        while not done and steps < 200:
            a = int(np.argmax(Q[s]))
            s, r, term, trunc, _ = env.step(a)
            done = term or trunc
            steps += 1
        if r > 0:
            successes += 1
    success_rate = successes / n_eval
    print(f"  Final success rate: {success_rate * 100:.1f}% over {n_eval} eval episodes")
    print(f"  Last 100 ep mean reward: {np.mean(rewards[-100:]):.3f}")

    # ===== 画图 =====
    fig = plt.figure(figsize=(15, 5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.4, 1.0, 1.2])

    # 1) 训练曲线
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(rewards, alpha=0.3, color="C0", label="raw")
    win = 50
    if len(rewards) >= win:
        ma = np.convolve(rewards, np.ones(win) / win, mode="valid")
        ax1.plot(range(win - 1, len(rewards)), ma, color="C0", linewidth=2, label=f"moving avg ({win})")
    ax1.set_xlabel("Episode")
    ax1.set_ylabel("Reward (1 = reach goal)")
    ax1.set_title(f"Q-learning Training\n(success rate: {success_rate*100:.0f}%)")
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(alpha=0.3)
    ax1.legend(loc="upper left")

    # 2) Q-table 热图 (4x16)
    ax2 = fig.add_subplot(gs[1])
    im = ax2.imshow(Q.T, cmap="viridis", aspect="auto")
    ax2.set_xticks(range(16))
    ax2.set_yticks(range(4))
    ax2.set_yticklabels(["←", "↓", "→", "↑"])
    ax2.set_xlabel("State")
    ax2.set_title("Q-table (16 states × 4 actions)")
    for i in range(16):
        for j in range(4):
            ax2.text(i, j, f"{Q[i, j]:.2f}", ha="center", va="center",
                     color="white" if Q[i, j] < Q.max() * 0.6 else "black", fontsize=7)
    fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

    # 3) 4x4 网格 + 最优策略箭头
    ax3 = fig.add_subplot(gs[2])
    ax3.set_xlim(0, 4)
    ax3.set_ylim(0, 4)
    ax3.invert_yaxis()
    ax3.set_aspect("equal")
    ax3.set_xticks(range(5))
    ax3.set_yticks(range(5))
    ax3.grid(True, alpha=0.3)
    ax3.set_title("Optimal Policy (arrows)")

    action_to_delta = {0: (0, 0), 1: (0.0, 1.0), 2: (0.0, -1.0), 3: (-1.0, 0.0)}
    cell_labels = {
        0: "S", 1: "", 2: "", 3: "",
        4: "", 5: "H", 6: "", 7: "H",
        8: "", 9: "", 10: "", 11: "H",
        12: "H", 13: "", 14: "", 15: "G",
    }

    for idx in range(16):
        r, c = idx_to_rc(idx)
        cell = cell_labels[idx]
        if cell == "H":
            color = "lightcoral"
        elif cell == "G":
            color = "lightgreen"
        elif cell == "S":
            color = "lightskyblue"
        else:
            color = "white"
        ax3.add_patch(plt.Rectangle((c, r), 1, 1, facecolor=color, edgecolor="black", lw=1))
        ax3.text(c + 0.5, r + 0.3, cell, ha="center", va="center", fontsize=14, fontweight="bold")

        if cell in ("H", "G"):
            continue
        # 画最优动作箭头
        best_a = int(np.argmax(Q[idx]))
        dr, dc = action_to_delta[best_a]
        if dr == 0 and dc == 0:
            continue
        ax3.annotate(
            "",
            xy=(c + 0.5 + dc * 0.3, r + 0.5 + dr * 0.3),
            xytext=(c + 0.5, r + 0.5),
            arrowprops=dict(arrowstyle="->", color="navy", lw=2.0),
        )

    fig.suptitle("Q-learning on FrozenLake-v1 (deterministic)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    fig.savefig(save_path, dpi=120)
    print(f"[saved] {save_path}")
    env.close()


if __name__ == "__main__":
    main()
