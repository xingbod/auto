# 强化学习互动教程 · RL from Scratch

从零起步,通过 **6 节互动教程** + **5 个可运行 Python 脚本**,把强化学习的核心算法 (Bandit / Q-Learning / DQN / REINFORCE / PPO) 走一遍,最终在 **CartPole-v1** 上完整跑通。

> 入口: 打开 `tutorial.html` (推荐用 Chrome / Safari) 开始互动学习,
>       然后用本 README 跑 Python 代码生成训练曲线。

## 文件结构

```
rl-tutorial/
├── tutorial.html            # 6 步互动教程 (纯 HTML, 无外部依赖, 离线可开)
├── utils.py                 # 共享:QNetwork / PolicyNetwork / ActorCritic / evaluate / plot
├── step1_bandit.py          # 多臂老虎机, 4 策略对比
├── step2_q_learning.py      # FrozenLake 4x4 + 表格 Q-Learning
├── step3_dqn.py             # CartPole-v1 + DQN (含 ReplayBuffer + Target Net)
├── step4_reinforce.py       # CartPole-v1 + REINFORCE (策略梯度)
├── step5_ppo.py             # CartPole-v1 + PPO (GAE + Clip)
├── outputs/                 # 训练曲线 / 热图 / 网格图
│   ├── bandit.png
│   ├── qlearning.png
│   ├── dqn.png
│   ├── reinforce.png
│   ├── ppo.png
│   └── compare.png
├── requirements.txt
└── README.md                # ← 你正在读
```

## 快速开始

```bash
# 1) 装依赖
pip install -r requirements.txt

# 2) 跑 5 个 step (按顺序)
python3 step1_bandit.py        # ~10s
python3 step2_q_learning.py    # ~30s
python3 step3_dqn.py           # ~3-5 min (CartPole 训练 500 ep)
python3 step4_reinforce.py     # ~3-5 min
python3 step5_ppo.py           # ~2-4 min

# 3) 看 outputs/ 里的训练曲线
open outputs/compare.png       # (Mac) 三算法对比
```

## 5 个算法对比

| 算法 | 类型 | CartPole 解决 ep | 训练稳定性 | 关键创新 |
|------|------|----------------|-----------|---------|
| Bandit (ε-decay) | 无状态 | — | — | 探索/利用 |
| Q-Learning | Value, tabular | (FrozenLake 60-80%) | 中 | Bellman + TD |
| DQN | Value, function approx | 100-300 | 中 | Replay Buffer + Target Net |
| REINFORCE | Policy gradient | 1000+ | 高方差 (抖) | 直接优化策略 |
| PPO | Actor-Critic | 200-500 | 低方差 (稳) | Clip 限制步长 |

## 推荐学习顺序

1. **打开 `tutorial.html`** 跟着 6 步互动走, 每步都有可视化 demo 可以点
2. 看完某步后, 跳到对应 `stepN_*.py` 读代码, 关键算法都对应 demo 里的概念
3. 自己跑一遍 `python3 stepN_*.py` 看真实训练曲线
4. 改超参 (在每个文件顶部的 `TrainConfig` 里), 观察训练曲线变化

## 关键概念对照

| tutorial.html 概念 | 对应 Python 文件 | 关键函数 / 类 |
|--------------------|------------------|---------------|
| RL 闭环 | (全 5 个 step) | `env.step()`, `agent.act()` |
| Q 值更新 (Bandit) | `step1_bandit.py` | `run_eps_greedy`, `run_ucb1` |
| Bellman / TD | `step2_q_learning.py` | `q_learning()` 内层循环 |
| 神经网络 + 经验回放 | `step3_dqn.py` | `DQNAgent`, `ReplayBuffer` |
| 策略梯度 | `step4_reinforce.py` | `compute_returns()` + `loss = -logπ·G` |
| GAE + Clip | `step5_ppo.py` | `compute_gae()`, `ppo_update()` |

## 常见问题

**Q: 训练很慢怎么办?**
A: CartPole 训练 500 ep 在 M1 Mac 上约 2-3 分钟, CPU 即可。GPU 不需要。

**Q: `import gymnasium` 报错?**
A: 本项目用新版 Gymnasium (`gymnasium` 不是 `gym`)。`pip install gymnasium` 即可。

**Q: 中文方块字?**
A: matplotlib 默认字体不含中文, 项目的图都是英文标签 (避免这个问题)。

**Q: 怎么把训练好的 agent 加载回来玩?**
A: 每个 step 的 net 对象在训练后存在局部变量, 可加一行 `torch.save(net.state_dict(), "model.pt")` 保存。

## 依赖

- Python ≥ 3.9
- PyTorch ≥ 2.0 (CPU 即可)
- Gymnasium ≥ 0.29
- NumPy, Matplotlib
- (可选) `pyglet<2` 如果用 `render_mode="human"` 弹窗

详见 `requirements.txt`。

---

由 DONG XINGBO 创建整理 · 非授权禁止转载 · © 2026 DONG XINGBO
