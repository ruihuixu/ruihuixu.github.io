---
title: "第 1 章：RL 思想框架 —— 为什么监督学习不够？"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "thinking-framework"
tags:
  - "RL"
  - "MDP"
  - "Policy Gradient"
categories:
  - "RL Tutorial"
description: "核心论点：监督学习的 loss 是代理指标，RL 直接优化真实目标。"
chapter: 1
difficulty: "入门"
section: "基础框架"
---

# 第 1 章：RL 思想框架 —— 为什么监督学习不够？

> **核心论点**：监督学习的 loss 是代理指标，RL 直接优化真实目标。
> **本章目标**：建立 RL 的思考框架，理解 MDP、Bellman 方程、Policy 三个核心概念。
> **代码**：Tabular Q-learning on GridWorld（~50行 numpy）。
> **前置**：概率论基础、Python/numpy。

## 全系列导航

本教程共 6 章，按两条线组织，覆盖 50+ 篇 2025-2026 年前沿论文：

```
Actor-Critic 线 (CartPole)           偏好对齐 + 推荐线 (GPT-2)
  ch01: RL 思想框架 [本章]
    |
  ch02: REINFORCE -> PPO
    |
  ch03: RLOO -> GRPO -> DAPO -----> ch05: 生成式推荐 RL
                                     ch06: 工业推荐 RL
                               /
  ch04: DPO -> KTO -> ORPO ----/
```

- **面试向**：每章末尾有追问清单，一阶基础 -> 三阶深度
- **代码向**：所有算法提供完整实现，可静态验证
- **前沿向**：融入 DeepSeek R1、OpenAI beneficial-trait RL、Anthropic MSM、Kuaishou OneReason 等

> **核心论点**：监督学习的 loss 是代理指标，RL 直接优化真实目标。
> **本章目标**：建立 RL 的思考框架，理解 MDP、Bellman 方程、Policy 三个核心概念。
> **代码**：Tabular Q-learning on GridWorld（~50行 numpy）。
> **前置**：概率论基础、Python/numpy。

## 1.1 监督学习的代理困境

监督学习（SL）解决的是**模式识别**问题：给定输入 $x$ 和标签 $y$，学习映射 $f: x \to y$。

但在序贯决策场景——推荐系统、LLM 对话、游戏、自动驾驶——SL 面临三个根本性问题：

### 问题 1：反馈是延迟的

- SL：每个样本有即时标签（这张图是猫 / 不是猫）
- RL：一个决策的后果可能 10 步之后才显现。你推荐了一个商品，用户可能三天后才购买

### 问题 2：标签不是正确答案

- SL 假设 `y` 是正确的目标输出
- RL 中不存在“正确动作”——一个推荐列表可能有 100 种合理选择，但它们的长期效果不同

### 问题 3：数据分布取决于策略

- SL：训练数据和测试数据都是 i.i.d.
- RL：你在时间 $t$ 推荐了什么，决定了用户在时间 $t+1$ 看到什么——数据分布和你的策略耦合

NeurIPS 2025 的一项研究揭示了 RCSL（Return-Conditioned Supervised Learning）的"拼接缺口"：
SL 方法在离线数据上学到的策略，无法泛化到训练分布以外的轨迹——因为 SL 学的是相关性，而非因果。

**本质差异**：SL 优化的是"在给定数据上做得像数据一样"，RL 优化的是"在真实环境中拿到高回报"。

## 1.2 MDP：描述序贯决策的语言

马尔可夫决策过程（Markov Decision Process, MDP）是 RL 的数学语言。它用五元组 $(\mathcal{S}, \mathcal{A}, P, R, \gamma)$ 描述一切序贯决策：

| 元素 | 含义 | 例子（推荐系统） |
|------|------|------------------|
| $\mathcal{S}$ | 状态空间 | 用户的兴趣向量 + 最近 50 次行为 |
| $\mathcal{A}$ | 动作空间 | 所有可选商品的集合 |
| $P(s'|s,a)$ | 状态转移概率 | 用户看到推荐后的行为分布 |
| $R(s,a)$ | 即时奖励 | 用户是否点击/购买 |
| $\gamma \in [0,1)$ | 折扣因子 | 今天的点击 vs 三天后的购买，哪个重要？ |

### 马尔可夫性

核心假设：**未来只取决于现在，不取决于过去**。

$$P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ...) = P(s_{t+1} | s_t, a_t)$$

这显然是理想化的——用户的兴趣显然依赖整个历史。但实际中，我们用 state 的设计来"堆"尽量多信息进 $s_t$，使马尔可夫性近似成立。

### 策略

策略 $\pi$ 是从状态到动作的映射：$\pi: \mathcal{S} \to \mathcal{A}$（确定性）或 $\pi(a|s) = P(a|s)$（随机性）。

RL 的核心问题：**找到最优策略 $\pi^*$，使累计折扣回报最大**。

$$\pi^* = \arg\max_\pi \mathbb{E}_\pi\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t)\right]$$

### 压缩推导（4 步）

1. **定义 V(s)**：$V^\pi(s) = \mathbb{E}_\pi[G_t \mid s_t = s]$

   价值函数是给定当前状态 $s$ 下，$G_t$ 的条件期望。

2. **展开 $G_t$**：$G_t = r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \dots = r_t + \gamma G_{t+1}$

   将第一项奖励提出来，剩余部分就是下一时刻的折扣回报。

3. **代入 $V(s)$ 的定义**：

   $V^\pi(s) = \mathbb{E}_\pi[r_t + \gamma G_{t+1} \mid s_t = s]$

   $= \mathbb{E}_\pi[r_t \mid s_t = s] + \gamma \cdot \mathbb{E}_\pi[G_{t+1} \mid s_t = s]$

4. **第二项的递归**：$\mathbb{E}_\pi[G_{t+1} \mid s_t = s] = \sum_{s'} P(s'|s,a) \cdot V^\pi(s')$

   从 $s$ 出发，以概率 $P(s'|s,a)$ 转移到 $s'$，而 $s'$ 的价值就是 $V^\pi(s')$。

综合得到 **Bellman 期望方程**：$V^\pi(s) = \sum_a \pi(a|s)[R(s,a) + \gamma \sum_{s'} P(s'|s,a) V^\pi(s')]$

## 1.4 Policy：从价值到行为

有了价值函数，如何得到策略？有两种基本范式：

### Value-Based（价值驱动）

学习最优 $Q^*(s,a)$（注意：Q-learning 是 **off-policy**——它用 $\max_a Q(s',a)$ 选最优动作，但实际采样的动作可能来自不同策略），然后贪心选择：$\pi(s) = \arg\max_a Q^*(s,a)$。

代表：Q-learning、DQN。
局限：当动作空间巨大或连续时（推荐系统选 10 个商品、LLM 选下一个 token），$\arg\max$ 不可行。

### Policy-Based（策略驱动）

直接学习策略函数 $\pi_\theta(a|s)$，不经过价值函数。

代表：REINFORCE、PPO、GRPO。
优势：天然支持随机策略（对探索至关重要）、连续动作、大动作空间。

### 统一视角

两类方法的核心差异在于**如何表示"好决策"**：
- Value-Based："这个动作值多少钱？"——先评估，再选择
- Policy-Based："在这种情况下该怎么做？"——直接输出决策

后续章节将全部聚焦 **Policy-Based** 方法，因为推荐和 LLM 场景的动作空间使得 Value-Based 基本不可行。

> **注**：Actor-Critic 方法（ch02）是两者的结合——Policy 做决策（Actor），Value 做评价（Critic）。

## 1.5 代码：Tabular Q-learning on GridWorld

下面用约 50 行 numpy 实现 Q-learning on GridWorld，展示 RL 最纯粹的形式。

```python
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# ---- 1. 环境定义 ----
class GridWorld:
    """5x5 网格世��，agent 从 (0,0) 出发，目标是 (4,4)。
    动作：0=上, 1=右, 2=下, 3=左。碰到边界留在原地。
    """
    def __init__(self, size=5):
        self.size = size
        self.goal = (size-1, size-1)
        self.start = (0, 0)
        # 障碍物：不可通过的格子
        self.obstacles = [(1, 2), (2, 2), (3, 2)]
        self.state = self.start

    def reset(self):
        self.state = self.start
        return self._encode(self.state)

    def step(self, action):
        x, y = self.state
        if action == 0:   x = max(0, x-1)        # 上
        elif action == 1: y = min(self.size-1, y+1)  # 右
        elif action == 2: x = min(self.size-1, x+1)  # 下
        elif action == 3: y = max(0, y-1)        # 左

        # 检查障碍物
        if (x, y) in self.obstacles:
            x, y = self.state  # 碰到障碍物留在原地

        self.state = (x, y)
        done = (self.state == self.goal)
        reward = 10.0 if done else -0.1  # 到达目标得 10，每步小惩罚鼓励快速到达
        return self._encode(self.state), reward, done

    def _encode(self, pos):
        """状态编码：将 (x,y) 映射到离散索引"""
        return pos[0] * self.size + pos[1]

# ---- 2. Q-learning Agent ----
class QLearningAgent:
    def __init__(self, n_states, n_actions, lr=0.1, gamma=0.95, eps=1.0, eps_decay=0.995, eps_min=0.01):
        self.Q = np.zeros((n_states, n_actions))
        self.lr = lr
        self.gamma = gamma
        self.eps = eps
        self.eps_decay = eps_decay
        self.eps_min = eps_min

    def act(self, state):
        """ε-greedy 选动作"""
        if np.random.random() < self.eps:
            return np.random.randint(4)  # 探索
        return np.argmax(self.Q[state])   # 利用

    def learn(self, s, a, r, s_next, done):
        """Q-learning 更新：Q(s,a) ← Q(s,a) + α[r + γ*max_a' Q(s',a') - Q(s,a)]"""
        target = r if done else r + self.gamma * np.max(self.Q[s_next])
        self.Q[s, a] += self.lr * (target - self.Q[s, a])

    def decay_epsilon(self):
        self.eps = max(self.eps_min, self.eps * self.eps_decay)
```

```python
# ---- 3. 训练 ----
env = GridWorld(size=5)
agent = QLearningAgent(n_states=25, n_actions=4)

episode_rewards = []
n_episodes = 300

for ep in range(n_episodes):
    state = env.reset()
    total_reward = 0
    for step in range(100):  # 最大步数截断
        action = agent.act(state)
        next_state, reward, done = env.step(action)
        agent.learn(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward
        if done:
            break
    episode_rewards.append(total_reward)
    agent.decay_epsilon()
```

```python
# ---- 4. 可视化 ----
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# 4a. 训练曲线
axes[0].plot(episode_rewards, alpha=0.5, color='steelblue')
axes[0].plot(np.convolve(episode_rewards, np.ones(20)/20, mode='valid'), color='darkred', linewidth=2)
axes[0].set_xlabel('Episode'); axes[0].set_ylabel('Total Reward')
axes[0].set_title('Training Progress (smoothed in red)')
axes[0].grid(True, alpha=0.3)

# 4b. 最优策略（箭头展示）
action_arrows = {0: '↑', 1: '→', 2: '↓', 3: '←'}
ax = axes[1]
for i in range(5):
    for j in range(5):
        s = i * 5 + j
        best_a = np.argmax(agent.Q[s])
        ax.text(j, 4-i, action_arrows[best_a], ha='center', va='center', fontsize=14, fontweight='bold')
        if (i, j) == env.goal:
            ax.add_patch(plt.Rectangle((j-0.5, (4-i)-0.5), 1, 1, facecolor='lightgreen', alpha=0.5))
        if (i, j) in env.obstacles:
            ax.add_patch(plt.Rectangle((j-0.5, (4-i)-0.5), 1, 1, facecolor='gray', alpha=0.5))
ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 4.5)
ax.set_xticks(range(5)); ax.set_yticks(range(5))
ax.set_yticklabels(range(4, -1, -1)); ax.set_title('Learned Policy (arrows)')
ax.grid(True, alpha=0.3)

# 4c. Q 值热力图
V = np.max(agent.Q, axis=1).reshape(5, 5)
im = axes[2].imshow(V, cmap='YlOrRd', origin='lower')
axes[2].set_title('Max Q-value per State')
axes[2].set_xticks(range(5)); axes[2].set_yticks(range(5))
for i in range(5):
    for j in range(5):
        axes[2].text(j, i, f'{V[i,j]:.1f}', ha='center', va='center', fontsize=9)
plt.colorbar(im, ax=axes[2])
plt.tight_layout()
plt.show()
```

### 关键观察

1. **Q 表从零开始收敛**——agent 最初随机探索，$\varepsilon$ 逐渐衰减后转为利用学到的知识
2. **离目标越近的格子 Q 值越高**——Bellman 方程的递归传播：目标周围先学会，然后向外扩散
3. **障碍物周围的策略绕路**——agent 学会了避免无效动作

这就是 RL 最朴素的形式：**在试错中，将"即时奖励 + 未来预测"用一张表记住。**

## 1.6 面试追问清单

以下问题的答案应能在本章正文中找到。

**Q1**: 为什么推荐系统不能用点击率作为唯一优化信号？

<details><summary>答案要点</summary>

1. 点击率是即时信号，不代表长期用户满意度
2. 推荐是序贯决策，今天的推荐影响明天的兴趣
3. 幸存者偏差：只观察到被推荐 item 的点击
</details>

**Q2**: MDP 和 Bandit 的本质区别是什么？什么场景必须用 MDP？

**Q3**: Bellman 方程假设马尔可夫性——现实中不满足怎么办？实际工程中如何应对？

**Q4**: Q-learning 中 $\varepsilon$ 衰减太快或太慢分别会导致什么？

<details><summary>答案要点</summary>

- 衰减太快: agent 过早收敛到次优策略，Q 表某些状态从未被充分访问
- 衰减太慢: 大量步数浪费在随机探索上，reward 曲线上升缓慢
- 实践: 指数衰减 (如 eps*=0.995) + eps_min 下限 (如 0.01) 保证永远有一定探索
</details>

**Q5**: 如果 GridWorld 变成 100x100，Tabular Q-learning 还 work 吗？为什么？这引出了什么方向？

<details><summary>答案要点</summary>

- 不 work: 10000 状态需要每个都被充分访问才能学到准确 Q 值——访问 10000 个状态需要指数级增加的训练步数
- 引出 function approximation: 用神经网络(而非表格)表示 Q(s,a) 或 pi(a|s)，相近状态共享参数 → DQN、Policy Gradient (ch02)
</details>×100，Tabular Q-learning 还 work 吗？为什么？这引出了什么方向？

---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/ch01-thinking-framework.ipynb" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
