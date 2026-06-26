---
title: "第 2 章：Policy Gradient → PPO"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "policy-gradient-ppo"
tags:
  - "RL"
  - "PPO"
  - "GAE"
  - "Actor-Critic"
categories:
  - "RL Tutorial"
description: "驱动问题：Q-learning 在连续/大动作空间中失效——推荐系统选 10 个商品有 种组合，LLM 选下一个 token 有 50000 种选择。Policy Gradient 直接优化策略参数，绕过价值函数的 。"
chapter: 2
difficulty: "核心"
section: "Actor-Critic 线"
---

# 第 2 章：Policy Gradient → PPO

> **驱动问题**：Q-learning 在连续/大动作空间中失效——推荐系统选 10 个商品有 $C_N^{10}$ 种组合，LLM 选下一个 token 有 50000 种选择。Policy Gradient 直接优化策略参数，绕过价值函数的 $\arg\max$。
> **本章目标**：完整理解 REINFORCE → Actor-Critic → GAE → PPO 的推导链。
> **代码**：完整 PPO on CartPole（~200行，对标 CleanRL 风格）。
> **前置**：ch01（MDP、策略、价值函数）。

### Policy Gradient Theorem（核心推导）

**Step 1: 目标函数的梯度**

$$\nabla_\theta J(\theta) = \nabla_\theta \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)] = \nabla_\theta \int P(\tau;\theta) R(\tau) d\tau$$

$$= \int \nabla_\theta P(\tau;\theta) \cdot R(\tau) d\tau$$

**Step 2: log-derivative trick**（关键技巧）

$$\nabla_\theta P(\tau;\theta) = P(\tau;\theta) \cdot \nabla_\theta \log P(\tau;\theta)$$

代入得：$\nabla_\theta J = \int P(\tau;\theta) \cdot \nabla_\theta \log P(\tau;\theta) \cdot R(\tau) d\tau = \mathbb{E}_{\tau}[\nabla_\theta \log P(\tau;\theta) \cdot R(\tau)]$

**Step 3: 展开轨迹概率**

$$P(\tau;\theta) = P(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t|s_t) P(s_{t+1}|s_t,a_t)$$

取 log：$\log P(\tau;\theta) = \log P(s_0) + \sum_t \log \pi_\theta(a_t|s_t) + \sum_t \log P(s_{t+1}|s_t,a_t)$

求梯度（环境动态 $P(s_{t+1}|s_t,a_t)$ 不依赖 $\theta$，梯度为 0）：

$$\nabla_\theta \log P(\tau;\theta) = \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t|s_t)$$

**Step 4: 用 $G_t$ 替代 $R(\tau)$**（因果性）

因为 $t$ 时刻的决策只影响 $t$ 之后的奖励：$\mathbb{E}[\nabla_\theta \log \pi_\theta(a_t|s_t) \cdot r_{t'}] = 0$ for $t' < t$

所以 $R(\tau) = \sum_{t'=0}^{T-1} r_{t'}$ 中，只有 $t' \ge t$ 的项对 $\nabla_\theta \log \pi_\theta(a_t|s_t)$ 有非零期望。因此每项的权重是 $G_t = \sum_{k=t}^{T-1} \gamma^{k-t} r_k$。

**最终：Policy Gradient Theorem**

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$

**直觉**：如果 $G_t$ 高就增大该动作的概率，$G_t$ 低就减小。$\nabla_\theta \log \pi_\theta$ 告诉你如何调参数。

## 2.2 REINFORCE：最朴素的策略梯度

### 算法

对于一个 episode 的每个时间步 $(s_t, a_t, r_t)$，用 Monte Carlo 回报 $G_t$ 作为权重更新策略：

$$\theta \leftarrow \theta + \alpha \cdot G_t \cdot \nabla_\theta \log \pi_\theta(a_t|s_t)$$

### 问题：高方差

不同 episode 的 $G_t$ 可能差异巨大（有时运气好 100 分，有时运气差 -50 分），
导致梯度估计方差极高，训练不稳定。

### 问题 2：credit assignment 粗糙

一个 episode 中，第 1 步的好动作和第 10 步的坏动作都被同一个 $G_t$ 加权——
无法区分哪一步真正贡献了回报。

> **为什么 unbiased 还不够？** REINFORCE 的梯度估计是无偏的（$\mathbb{E}[\hat{g}] = \nabla J$），
> 但方差太大。RL 中 bias-variance tradeoff 贯穿始终——下一节用 Critic 引入 bias 换方差。

## 2.3 Actor-Critic：用 Critic 降方差

### 核心思想

用 $G_t - V(s_t)$ 替代 $G_t$ 作为更新权重。$V(s_t)$ 是 baseline——它在期望意义下不改变梯度方向，但大幅降低方差：

$$\nabla_\theta J = \mathbb{E}[\nabla_\theta \log \pi_\theta(a|s) \cdot (G_t - V(s_t))]$$

定义 **优势函数（Advantage）**：$A(s,a) = Q(s,a) - V(s) \approx G_t - V(s)$

### 为什么 baseline 不改变期望？

$\mathbb{E}[\nabla_\theta \log \pi \cdot b(s)] = \int \pi \cdot \nabla_\theta \log \pi \cdot b(s) = b(s) \cdot \nabla_\theta \int \pi = b(s) \cdot \nabla_\theta 1 = 0$

(关键：$\nabla_\theta \int \pi(a|s) da = \nabla_\theta 1 = 0$，因为概率分布积分恒为 1)

### 为什么降低方差？

$G_t$ 包含的不仅是当前动作的影响，还包含状态本身的"运气"（好状态即使躺平也能拿高分）。
$V(s)$ 捕捉了状态的固有价值，$A(s,a)$ 才是动作的"净贡献"。

### 架构

- **Actor（策略网络）**：$\pi_\theta(a|s)$——决定做什么
- **Critic（价值网络）**：$V_\phi(s)$——评估当前位置的好坏
- Critic 的训练目标：$\min_\phi \mathbb{E}[(V_\phi(s_t) - G_t)^2]$（回归到真实回报）

## 2.4 GAE：Bias-Variance 的优雅权衡

### 问题：$G_t$ 用什么估计？

- **Monte Carlo**（$G_t = r_t + \gamma r_{t+1} + ...$）：无偏，方差高
- **TD(0)**（$G_t \approx r_t + \gamma V(s_{t+1})$）：方差低，有偏（$V$ 不完美）

GAE（Generalized Advantage Estimation）在这两者之间插值：

$$\hat{A}_t^{\text{GAE}(\lambda)} = \sum_{l=0}^{\infty} (\gamma\lambda)^l \delta_{t+l}$$

其中 $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ 是 TD error。

### $\lambda$ 的含义

| $\lambda$ | 退化 | Bias | Variance |
|----------|------|------|----------|
| 0 | TD(0) | 高偏 | 低方差 |
| 1 | Monte Carlo | 无偏 | 高方差 |
| 0.95 | 实践中常用 | 中 | 中 |

### GAE 的直觉

$\lambda$ 控制的是"向后看多远"。$\lambda=0.95$ 意味着你信任 Critic 的估计，
但当证据足够强时（多步 reward 持续偏离预期），你也愿意修正。

## 2.5 PPO：信任区域的实际实现

### 动机

REINFORCE + Actor-Critic 仍不稳定。问题在于：**策略更新步长太大时，新策略和旧策略差异过大，导致采样数据失效。**

TRPO 用 KL 散度约束解决此问题，但实现复杂（共轭梯度 + 线搜索）。
**PPO 用一个巧妙的 clip 操作取代了 KL 约束**，实现极其简单，效果几乎一样好。

### PPO-Clip 目标函数

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta) \hat{A}_t,\; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t\right)\right]$$

其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ 是新旧策略的概率比。

### Clip 机制详解

分两种情况：

| $\hat{A}_t$ | 希望的更新方向 | Clip 防止什么？ |
|------------|-------------|--------------|
| > 0（好动作）| 增大 $\pi(a_t|s_t)$ | $r_t$ 不能超过 $1+\epsilon$——防止"过于自信" |
| < 0（坏动作）| 减小 $\pi(a_t|s_t)$ | $r_t$ 不能低于 $1-\epsilon$——防止"过于悔改" |

### 为什么对称 clip？

直觉：无论好坏，都不允许一次更新改变策略超过 $\epsilon$。非对称 clip（如只 clip 正方向）
会导致策略在"好动作"方向上的更新量远大于"坏动作"方向，长期来看策略逐渐漂移。

### PPO 完整训练循环

1. 用 $\pi_{\theta_{old}}$ 收集一批轨迹
2. 计算 GAE 优势 $\hat{A}_t$
3. 多 epoch 用 clip 目标更新 $\theta$（不重复采样！）
4. 更新 $\theta_{old} \leftarrow \theta$，回到步骤 1

## 2.6 代码：完整 PPO on CartPole

以下代码对标 CleanRL 风格：结构清晰、可独立运行、每个函数功能单一。

```python
import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import numpy as np
import matplotlib.pyplot as plt

# ---- 1. 网络定义：共享 backbone 的 Actor-Critic ----
class ActorCritic(nn.Module):
    """一个网络输出 policy logits (Actor) 和 state value (Critic)"""
    def __init__(self, obs_dim, n_actions, hidden=64):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(obs_dim, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh()
        )
        self.actor = nn.Linear(hidden, n_actions)   # policy logits
        self.critic = nn.Linear(hidden, 1)           # V(s)

    def get_value(self, x):
        return self.critic(self.shared(x))

    def get_action_and_value(self, x, action=None):
        hidden = self.shared(x)
        logits = self.actor(hidden)
        probs = Categorical(logits=logits)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action), probs.entropy(), self.critic(hidden)
```

```python
# ---- 2. GAE 计算 ----
def compute_gae(rewards, values, dones, gamma=0.99, gae_lambda=0.95):
    """计算 Generalized Advantage Estimation。

    Args:
        rewards: [T] 每步即时奖励
        values:  [T+1] 每步的 V(s)，最后一个是 V(s_T) 或 0
        dones:   [T]  是否到达终止状态
        gamma:  折扣因子
        gae_lambda: GAE λ，0→TD(0)，1→MC
    Returns:
        advantages: [T] GAE 优势估计
        returns:    [T] 用于 Critic 训练的目标值
    """
    T = len(rewards)
    advantages = torch.zeros(T)
    gae = 0.0
    for t in reversed(range(T)):
        # δ_t = r_t + γ*V(s_{t+1})*(1-done) - V(s_t)
        delta = rewards[t] + gamma * values[t+1] * (1 - dones[t]) - values[t]
        gae = delta + gamma * gae_lambda * (1 - dones[t]) * gae
        advantages[t] = gae
    returns = advantages + values[:-1]  # R_t = A_t + V(s_t)
    return advantages, returns
```

```python
# ---- 3. PPO 训练 ----
def train_ppo(env_id="CartPole-v1", total_steps=50000, lr=2.5e-4, gamma=0.99,
              gae_lambda=0.95, clip_eps=0.2, update_epochs=4, batch_size=8):
    env = gym.make(env_id)
    obs_dim = env.observation_space.shape[0]
    n_actions = env.action_space.n

    agent = ActorCritic(obs_dim, n_actions)
    optimizer = optim.Adam(agent.parameters(), lr=lr, eps=1e-5)

    obs, _ = env.reset()
    ep_returns = []
    ep_return = 0

    obs_buffer, act_buffer, rew_buffer, val_buffer, done_buffer = [], [], [], [], []

    for step in range(1, total_steps + 1):
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
        with torch.no_grad():
            action, log_prob, _, value = agent.get_action_and_value(obs_tensor)

        next_obs, reward, terminated, truncated, _ = env.step(action.item())
        done = terminated or truncated
        ep_return += reward

        obs_buffer.append(obs)
        act_buffer.append(action)
        rew_buffer.append(reward)
        val_buffer.append(value)
        done_buffer.append(done)

        obs = next_obs

        if done:
            ep_returns.append(ep_return)
            ep_return = 0
            obs, _ = env.reset()

        # 收集完一个 mini-batch 更新一次
        if len(obs_buffer) >= batch_size:
            # 准备数据
            with torch.no_grad():
                next_val = agent.get_value(torch.FloatTensor(obs).unsqueeze(0))

            obs_t = torch.FloatTensor(np.array(obs_buffer))
            act_t = torch.LongTensor(np.array(act_buffer))
            rew_t = torch.FloatTensor(np.array(rew_buffer))
            val_t = torch.cat(val_buffer).squeeze()
            val_next = torch.cat([val_t[1:], next_val.squeeze()])
            don_t = torch.FloatTensor(np.array(done_buffer, dtype=np.float32))

            advantages, returns = compute_gae(rew_t, torch.cat([val_t, next_val]), don_t, gamma, gae_lambda)
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            # PPO 更新（多 epoch）
            _, old_log_prob, _, _ = agent.get_action_and_value(obs_t, act_t)
            old_log_prob = old_log_prob.detach()

            for _ in range(update_epochs):
                _, new_log_prob, entropy, new_value = agent.get_action_and_value(obs_t, act_t)
                ratio = torch.exp(new_log_prob - old_log_prob)

                # PPO clip loss
                surr1 = ratio * advantages
                surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages
                actor_loss = -torch.min(surr1, surr2).mean()

                # Critic loss
                critic_loss = 0.5 * (returns - new_value.squeeze()).pow(2).mean()

                # Entropy bonus (鼓励探索)
                entropy_bonus = 0.01 * entropy.mean()

                loss = actor_loss + critic_loss - entropy_bonus
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            obs_buffer, act_buffer, rew_buffer, val_buffer, done_buffer = [], [], [], [], []

    env.close()
    return ep_returns
```

```python
# ---- 4. 运行训练并可视化 ----
# 注意：以下为示例代码结构。实际运行建议减小 total_steps 到 10000 以快速验证。
returns = train_ppo(total_steps=50000)

fig, ax = plt.subplots(figsize=(10, 4))
window = 50
smoothed = np.convolve(returns, np.ones(window)/window, mode='valid')
ax.plot(returns, alpha=0.3, color='steelblue', label='Episode Return')
ax.plot(range(window-1, len(returns)), smoothed, color='darkred', linewidth=2, label=f'{window}-episode MA')
ax.axhline(y=500, color='green', linestyle='--', label='CartPole max (500)')
ax.set_xlabel('Episode'); ax.set_ylabel('Return')
ax.set_title('PPO on CartPole-v1')
ax.legend(); ax.grid(True, alpha=0.3); plt.show()
```

## 2.7 PPO 的 On-Policy 困境

### 问题

PPO 是 **近似 on-policy** 算法：每次采集数据时使用当前策略 $\pi_\theta$（on-policy 采集），但通过 importance sampling ratio $r_t = \pi_\theta / \pi_{\theta_{old}}$ 和 clip 机制，允许在旧数据上做多次（通常 4-10 epoch）更新后才重新采集。严格来说是 on-policy 采集 + 小范围 off-policy 更新。 $\pi_\theta$ 采样的数据更新。
一旦更新了 $\theta$，旧数据就"过期"了——因为旧数据来自 $\pi_{\theta_{old}}$，
importance sampling ratio $r_t$ 需要旧策略的概率，但可以用 importance sampling 校正（$\rho$ 比例）。

实际上 PPO 通过多个 epoch 重复使用同一批数据（$\theta_{old}$ 固定），
但只在 $r_t$ 偏离 1 不太远时有效（这就是 clip 的作用）。

### 为什么在 LLM 训练中是瓶颈？

在大模型中，每次 forward pass 都极其昂贵。PPO 需要 4 个模型：
- Actor $\pi_\theta$（当前策略）
- Actor $\pi_{\theta_{old}}$（旧策略，用于算 ratio）
- Critic $V_\phi$
- Reward Model $r_\psi$

四个模型同时在 GPU 上，以 7B 模型为例：Actor(fp32) ~28GB + Critic ~28GB + Old Actor ~28GB + RM ~28GB ≈ 112GB —— 需要 3 张 A100。这就是为什么 ch03 要讲 GRPO 和 RLOO——
它们通过去掉 Critic 来降低显存和复杂度。

## 2.8 面试追问清单

**Q1**: PPO clip 为什么是对称的？如果只 clip 正优势会怎样？

**Q2**: GAE $\lambda=0$ 退化为什么？$\lambda=1$ 呢？实际 $\lambda$ 选多少？

**Q3**: Actor-Critic 中 Critic 越准越好吗？

<details><summary>答案要点</summary>

- Critic 越准 → advantage 越精确 → 梯度方差越低 ✅
- 但 Critic 过于精确时：V(s) 完美拟合 G_t → advantage→0 → 梯度消失
- 更实际的问题: Critic 过拟合到训练分布，在新状态上估计偏差大 → Actor 被误导
</details>Critic 太准有什么问题？

**Q4**: PPO 和 TRPO 的核心差异？TRPO 被 PPO 取代的根本原因？

**Q5**: 为什么 PPO 在大模型 RLHF 中被 GRPO 取代？（预告 ch03）

**Q6**: 代码中 advantages 标准化这行是干什么的？去掉会怎样？

<details><summary>答案要点</summary>

- 作用: 将 advantage 标准化为均值 0、方差 1，确保每批数据梯度尺度一致
- 去掉后: 不同 batch advantage 幅度差异大 → 梯度不稳定，需频繁调学习率
- RL 常见技巧，类似 BatchNorm 但只做一次全局标准化
</details>

---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/ch02-policy-gradient-ppo.ipynb" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
