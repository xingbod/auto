"""
step5_ppo.py
============
Step 5: PPO (Proximal Policy Optimization, Schulman 2017)

环境: CartPole-v1
算法: PPO-Clip + GAE 优势估计

核心思想:
  REINFORCE 太抖 (一次坏 episode 可能让策略崩), PPO 限制每次更新"步长",
  用 clip 截断概率比 r(θ) = π_new/π_old, 让其偏离 1±ε 之内。

Loss:
  L_clip(θ) = E_t [ min( r_t(θ) · Â_t,  clip(r_t(θ), 1-ε, 1+ε) · Â_t ) ]
  其中 Â_t = GAE advantage = Σ (γλ)^l · δ_{t+l},  δ_t = r_t + γV(s_{t+1}) - V(s_t)
  L_total = L_clip + c1 * L_value - c2 * H(π)   (policy + value + entropy)

实现要点:
  - 收集 rollouts: 每轮用当前策略采 N 步, 然后更新 K 个 epoch
  - GAE 优势: 用 minibatch 跑 K 次梯度
  - 重要性采样: r(θ) = exp(log π_new - log π_old) 因为旧策略在 buffer 里只存了 log_prob
"""
from __future__ import annotations

import os
import pickle
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import torch
import torch.optim as optim

from utils import (
    ActorCritic,
    Timer,
    fmt_time,
    set_seed,
    evaluate_policy,
    ac_policy,
    plot_rewards,
)


# =============================================================================
# 1. GAE 优势估计
# =============================================================================
def compute_gae(
    rewards: np.ndarray,
    values: np.ndarray,
    dones: np.ndarray,
    next_value: float,
    gamma: float = 0.99,
    lam: float = 0.95,
) -> Tuple[np.ndarray, np.ndarray]:
    """广义优势估计 (Generalized Advantage Estimation)。
    returns: (advantages, returns) 两个 array
    """
    T = len(rewards)
    advantages = np.zeros(T, dtype=np.float32)
    gae = 0.0
    for t in reversed(range(T)):
        if t == T - 1:
            next_v = next_value
        else:
            next_v = values[t + 1]
        # 如果该步终止, 则 next_v 不参与 bootstrap
        nonterminal = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_v * nonterminal - values[t]
        gae = delta + gamma * lam * nonterminal * gae
        advantages[t] = gae
    returns = advantages + values
    return advantages, returns


# =============================================================================
# 2. PPO 更新
# =============================================================================
def ppo_update(
    net: ActorCritic,
    optimizer: optim.Optimizer,
    states: torch.Tensor,
    actions: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    returns: torch.Tensor,
    clip_eps: float = 0.2,
    c1: float = 0.5,
    c2: float = 0.01,
    epochs: int = 4,
    minibatch_size: int = 64,
) -> dict:
    """跑 K 个 epoch, 每个 epoch 把数据切成 minibatch 更新。"""
    n = states.shape[0]
    losses = {"policy": [], "value": [], "entropy": [], "total": []}

    for _ in range(epochs):
        idx = np.random.permutation(n)
        for start in range(0, n, minibatch_size):
            mb_idx = idx[start:start + minibatch_size]
            mb_s = states[mb_idx]
            mb_a = actions[mb_idx]
            mb_old_lp = old_log_probs[mb_idx]
            mb_adv = advantages[mb_idx]
            mb_ret = returns[mb_idx]

            logits, values = net(mb_s)
            dist = torch.distributions.Categorical(logits=logits)
            new_log_probs = dist.log_prob(mb_a)
            entropy = dist.entropy().mean()

            # 重要性采样比 r(θ) = exp(log π_new - log π_old)
            ratio = torch.exp(new_log_probs - mb_old_lp)

            # 标准化 advantage (per minibatch)
            mb_adv_norm = (mb_adv - mb_adv.mean()) / (mb_adv.std() + 1e-8)

            # PPO-Clip 目标
            surr1 = ratio * mb_adv_norm
            surr2 = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * mb_adv_norm
            policy_loss = -torch.min(surr1, surr2).mean()

            value_loss = ((values.squeeze(-1) - mb_ret) ** 2).mean()

            loss = policy_loss + c1 * value_loss - c2 * entropy

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), max_norm=0.5)
            optimizer.step()

            losses["policy"].append(policy_loss.item())
            losses["value"].append(value_loss.item())
            losses["entropy"].append(entropy.item())
            losses["total"].append(loss.item())

    return {k: float(np.mean(v)) for k, v in losses.items()}


# =============================================================================
# 3. Rollout 收集
# =============================================================================
def collect_rollout(env, net: ActorCritic, n_steps: int) -> dict:
    """跑 n_steps 步, 收集 PPO 更新需要的全部数据。"""
    states, actions, rewards, dones, log_probs, values = [], [], [], [], [], []
    state, _ = env.reset()
    ep_rewards = []
    ep_reward = 0.0

    for _ in range(n_steps):
        s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits, v = net(s)
            dist = torch.distributions.Categorical(logits=logits)
            a = dist.sample()
            lp = dist.log_prob(a)

        a_int = int(a.item())
        s_next, r, term, trunc, _ = env.step(a_int)
        done = term or trunc

        states.append(state)
        actions.append(a_int)
        rewards.append(float(r))
        dones.append(float(done))
        log_probs.append(lp.item())
        values.append(v.item())

        state = s_next
        ep_reward += float(r)
        if done:
            ep_rewards.append(ep_reward)
            ep_reward = 0.0
            state, _ = env.reset()

    # 最后一步的 bootstrap value
    with torch.no_grad():
        s = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
        _, next_v = net(s)
        next_v = next_v.item()

    return {
        "states": np.array(states, dtype=np.float32),
        "actions": np.array(actions, dtype=np.int64),
        "rewards": np.array(rewards, dtype=np.float32),
        "dones": np.array(dones, dtype=np.float32),
        "log_probs": np.array(log_probs, dtype=np.float32),
        "values": np.array(values, dtype=np.float32),
        "next_value": next_v,
        "ep_rewards": ep_rewards,
    }


# =============================================================================
# 4. PPO 主训练
# =============================================================================
@dataclass
class TrainConfig:
    env_id: str = "CartPole-v1"
    n_episodes: int = 500
    rollout_steps: int = 256
    gamma: float = 0.99
    gae_lam: float = 0.95
    clip_eps: float = 0.2
    c1: float = 0.5     # value loss coefficient
    c2: float = 0.01    # entropy bonus coefficient
    lr: float = 3e-4
    hidden: int = 128
    ppo_epochs: int = 4
    minibatch_size: int = 64
    eval_every: int = 5   # 每 5 个 rollout 评估一次
    eval_episodes: int = 10
    save_path: str = "outputs/ppo.png"
    pkl_path: str = "outputs/ppo.pkl"


def train_ppo(cfg: TrainConfig, seed: int = 0):
    import gymnasium as gym

    set_seed(seed)
    env = gym.make(cfg.env_id)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    net = ActorCritic(state_dim, action_dim, hidden=cfg.hidden)
    optimizer = optim.Adam(net.parameters(), lr=cfg.lr)
    rewards_hist: List[float] = []  # 每个 episode 的 return

    with Timer() as t:
        rollout_count = 0
        while len(rewards_hist) < cfg.n_episodes:
            rollout = collect_rollout(env, net, cfg.rollout_steps)
            rewards_hist.extend(rollout["ep_rewards"])

            # GAE
            adv, ret = compute_gae(
                rollout["rewards"], rollout["values"], rollout["dones"],
                rollout["next_value"], cfg.gamma, cfg.gae_lam,
            )

            # 转 tensor
            states = torch.as_tensor(rollout["states"], dtype=torch.float32)
            actions = torch.as_tensor(rollout["actions"], dtype=torch.int64)
            old_lp = torch.as_tensor(rollout["log_probs"], dtype=torch.float32)
            adv_t = torch.as_tensor(adv, dtype=torch.float32)
            ret_t = torch.as_tensor(ret, dtype=torch.float32)

            # PPO 更新
            losses = ppo_update(
                net, optimizer, states, actions, old_lp, adv_t, ret_t,
                clip_eps=cfg.clip_eps, c1=cfg.c1, c2=cfg.c2,
                epochs=cfg.ppo_epochs, minibatch_size=cfg.minibatch_size,
            )

            rollout_count += 1
            if rollout_count % cfg.eval_every == 0:
                mean_train = np.mean(rewards_hist[-20:]) if rewards_hist else 0.0
                eval_mean, _ = evaluate_policy(cfg.env_id, ac_policy(net), n_episodes=cfg.eval_episodes, seed=30_000 + rollout_count)
                print(f"  rollout {rollout_count:3d} | eps {len(rewards_hist):4d} | "
                      f"train20={mean_train:6.1f} | eval={eval_mean:6.1f} | "
                      f"L_pi={losses['policy']:+.3f} L_v={losses['value']:+.3f} H={losses['entropy']:.3f}")

    env.close()
    print(f"\n[done] 训练 {len(rewards_hist)} ep 用时 {fmt_time(t.elapsed)}")

    final_mean, final_std = evaluate_policy(cfg.env_id, ac_policy(net), n_episodes=50, seed=77777)
    print(f"  最终评估 (50 ep): {final_mean:.1f} ± {final_std:.1f}")
    solved = "✓ SOLVED" if final_mean >= 475 else "✗ unsolved"
    print(f"  CartPole-v1 解决标准 = 475 → {solved}")

    plot_rewards(
        rewards_hist,
        title=f"PPO on {cfg.env_id}\nfinal eval: {final_mean:.0f} ± {final_std:.0f} ({solved})",
        target=475,
        save_path=cfg.save_path,
    )
    print(f"[saved] {cfg.save_path}")

    os.makedirs(os.path.dirname(cfg.pkl_path) or ".", exist_ok=True)
    with open(cfg.pkl_path, "wb") as f:
        pickle.dump(rewards_hist, f)

    return net, rewards_hist


# =============================================================================
# 5. 主程序
# =============================================================================
if __name__ == "__main__":
    cfg = TrainConfig()
    net, rewards = train_ppo(cfg)
