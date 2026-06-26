---
title: "第 6 章：工业推荐 RL"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "industrial-recsys-rl"
tags:
  - "RL"
  - "推荐系统"
  - "工业实践"
  - "ByteDance"
categories:
  - "RL Tutorial"
description: "驱动问题：ch05 讲了生成式推荐的 RL 理论方案——但真正在 10 亿用户系统中部署 RL 是什么样子的？"
chapter: 6
difficulty: "进阶"
section: "推荐交汇"
---

# 第 6 章：工业推荐 RL

> **驱动问题**：ch05 讲了生成式推荐的 RL 理论方案——但真正在 10 亿用户系统中部署 RL 是什么样子的？
> **本章目标**：理解工业推荐 RL 的三大挑战（E&E / Offline-Online Gap / Slate RL）和实战方案。
> **代码**：电商推荐模拟器 + PPO vs 贪心对比。
> **前置**：ch05（生成式推荐 MDP）、ch02（PPO）。

## 6.1 推荐 RL 的特殊挑战

和游戏 RL / LLM RL 的根本区别：

| 维度 | 游戏 RL | LLM RL | 推荐 RL |
|------|--------|--------|--------|
| 在线代价 | 低（重开一局）| 中（推理 cost）| **极高**（影响用户体验）|
| State 空间 | 小（几百维）| 中（prompt 长度）| **大**（亿级用户×千万级物品）|
| Action 空间 | 小（几个按键）| 大（5 万词表）| **巨大**（千万到十亿物品）|
| Reward 延迟 | 短（秒级）| 短（推理结果立即评估）| **长**（曝光到转化可能几天）|
| Reward 噪声 | 低（明确的成功/失败）| 中（回答难以客观评分）| **极高**（用户行为极其随机）|
| 动作类型 | 单 action | 单 token | **Slate**（一次 K 个 item）|

### 四大挑战

1. **在线交互代价极高**：不能给用户看"探索性"的烂结果——用户流失的代价远大于一次实验的收益
2. **State/Action 空间巨大**：10 亿用户 × 1 亿物品 = $10^{17}$ 级别的 state-action 对（非 tabular 可解）
3. **Reward 稀疏、噪声大、延迟长**：点击率 1-10%，购买率 0.1-1%，大部分信号是噪声
4. **Slate 组合爆炸**：从 $M$ 个 item 选 $K$ 个有 $C_M^K$ 种组合——当 $M=10^7, K=10$ 时，天文数字

## 6.2 Exploration/Exploitation：推荐系统的主线矛盾

E&E 是推荐 RL 的核心矛盾，也是面试中必问的主题。

### 四种 E&E 策略

#### 1. $\varepsilon$-Greedy（最简单但最低效）

以 $\varepsilon$ 概率随机推荐，$1-\varepsilon$ 概率推荐最优。

- **优势**：实现简单，一个超参
- **劣势**：探索完全随机——可能探索明显很差的 item，浪费探索预算

#### 2. UCB（Upper Confidence Bound）

$$a_t = \arg\max_a \left[\hat{r}_a + c \cdot \sqrt{\frac{\log t}{n_a}}\right]$$

- $\hat{r}_a$：item $a$ 的预估 reward
- $n_a$：item $a$ 被选中的次数
- **直觉**：如果某个 item 被选得少，它的置信区间宽——UCB 会"给个机会"
- **劣势**：需要维护每个 item 的 $n_a$ 统计量——在 1 亿 item 级别成本高

#### 3. Thompson Sampling（贝叶斯视角）

维护每个 item 的 reward 后验分布 $P(r_a | \text{history})$，每次从后验采样 $\tilde{r}_a$，选最大的。

- **优势**：在理论上是最优的 E&E 策略（在 bandit setting 中 minimize regret）
- **劣势**：需要 maintain 后验——在推荐 RL（非 bandit）中，后验的计算复杂

#### 4. Bootstrap-based Exploration（工程最友好）

训练多个模型（不同随机种子 or 不同数据子集），用模型之间的 disagreement 作为不确定性估计。

- **优势**：不需要修改训练流程，业界最常用的 exploration 方案
- **劣势**：需要训练和维护多个模型

## 6.3 Offline → Online Gap

### 问题：训练用离线数据，部署到在线——分布偏移

离线数据 $D_{\text{log}}$ 来自**上一版线上策略** $\pi_{\text{log}}$。
当新策略 $\pi_\theta$ 和 $\pi_{\text{log}}$ 差异大时，离线评估完全不靠谱。

### 解决方案

#### 1. Importance Sampling（IS）校正

$$\hat{J}(\pi_\theta) = \frac{1}{N} \sum_{i=1}^{N} \frac{\pi_\theta(a_i|s_i)}{\pi_{\text{log}}(a_i|s_i)} \cdot r_i$$

- **直觉**：如果新策略更倾向选动作 $a$，就给 $a$ 对应的 reward 更高权重
- **问题**：当 $\pi_\theta$ 和 $\pi_{\text{log}}$ 差异大时，重要性权重方差爆炸——少数样本的权重主导估计

#### 2. CQL（Conservative Q-Learning）

核心思想：对 OOD（Out-Of-Distribution）action 的 Q 值加惩罚：

$$L_{\text{CQL}} = \mathbb{E}_{s \sim D}\left[\log \sum_a \exp Q(s,a) - \mathbb{E}_{a \sim D}[Q(s,a)]\right]$$

- **直觉**：让模型对"没见过但可能很诱人的动作"保持悲观——只相信数据中见过的好结果
- **优势**：理论保证，在 offline RL benchmark 上效果好

#### 3. IQL（Implicit Q-Learning）

核心思想：不查询 OOD action——只更新 appeared action 的 Q 值：

$$L_{\text{IQL}} = \mathbb{E}_{(s,a,s') \sim D}[\ell_2^\tau(Q(s,a) - r - \gamma V(s'))]$$

- 使用 expectile regression（而非 MSE），避免对 OOD action 的乐观外推
- **优势**：比 CQL 更简单（不需要采样 OOD action），且不引入保守偏差

#### 4. 行业实践（最朴素但最有效）

> Offline 训练 → Online 小流量 A/B → 收集新数据 → 再 Offline 训练 → ...

每次 online 部署只比 offline 训练的 baseline 好一点点（1-2% 的 metric 提升），
然后迅速收集新的"on-policy"数据。这个循环做 10 轮，累计提升可能 20%+。

### 离线评估指标（Off-Policy Evaluation, OPE）

在没有在线实验的情况下，如何估计新策略的真实效果？

- **Direct Method (DM)**：用学到的 reward model 直接预测（方差低但偏差大）
- **Inverse Propensity Scoring (IPS)**：IS 校正（方差高但无偏）
- **Doubly Robust (DR)**：DM + IPS 结合——两个中只要一个对，估计就无偏

## 6.4 Slate RL：一次推荐多 item

### 问题

action 不是单个 item，而是 size-K 的 item 集合——action 空间是组合的。

$|\mathcal{A}| = C_M^K$，其中 $M$ 是 item 数量。当 $M=10^7, K=10$ 时，$|\mathcal{A}| > 10^{70}$。

### 三种解法

#### 解法 1：分解为单 item，逐位生成

这正是 ch05 生成式推荐的做法——把 slate 当作 token sequence 自回归生成。

**优势**：动作空间从 $C_M^K$ 降到 $M \times K$（每步从 M 个 item 中选 1 个，共 K 步）

**劣势**：前一步的选择影响后一步的最优解（自回归的"曝光偏差"问题）

#### 解法 2：Top-K 近似

用打分函数 $f(s, a)$ 给每个 item 打分，取 Top-K：

$\pi(s) = \arg\text{TopK}_a f(s, a)$

**优势**：实现极其简单，工业界的默认做法

**劣势**：item 之间独立评分，不考虑 slate 内部的多样性或互补性

#### 解法 3：Slate-Q

把整个 slate 映射到一个低维 embedding（例如用 Transformer 编码一组 item），
然后学习 $Q(s, \text{slate})$ 的估计。

**优势**：理论上最完备——可以学习 slate 内部的任何交互

**劣势**：训练成本极高，且 slate action 空间仍然很大多，exploration 困难

### 选择指南

- **快速上线** → Top-K 近似
- **需要 slate 内多样性** → 逐位生成（引入 diversity constraint 在 reward 中）
- **学术界 / 极致优化** → Slate-Q（但工业界很少直接使用）

## 6.5 工业案例一览（2026-06 更新）

> 以下数据基于 2024-2026 年各公司公开技术博客和论文。

| 公司 | RL 方法 | 场景 | 关键创新 | 指标 |
|------|--------|------|---------|------|
| **字节跳动** | GRPO(推荐) / VAPO(推理) | 抖音短视频/音乐 | 明确分工：GRPO 做推荐（value-free 更稳定），VAPO 做推理 | 音乐 App +46.49% 活跃天数 |
| **快手** | Taiji POPO / OneReason(RFT+MOPD) | 短视频/广告 | OneReason 首个 CoT 推荐模型(8B)超非思考模式；Fast-Slow 架构 | 400M+ 用户, +10.33% 曝光, ROI>5 |
| **美团** | GRPO + MTGenRec | 外卖/多业务 | 6 篇 ACL 2026；物流 RL 用混合 RL+超启发式 | +3.98% CTCVR, 物流成本 -12% |
| **Meta** | GEARS(agentic ranking) + Memento | Facebook/Instagram | LLM Agent 自主优化排序策略；365 天超长记忆 RAG | 86% Top-1, +1% CTR, 10% Reels 时长 |
| **Google (YouTube)** | Self-Evolving LLM Agents | YouTube | LLM 作为 ML Engineer 自主设计 reward/架构/A/B | 已部署 YouTube |
| **Amazon** | HarmoRec / UGR(KDD 2026) | 电商 | Offline RL + 长尾 fairness + 用户行为模拟(Shop-R1) | +8-10% 整体, +17-20% 长尾 |
| **阿里巴巴** | 6 种 GRPO 变体 | 淘宝/天猫/国际 | GRC/EG-GRPO/TaoSR-AGRL/AIGQ/QueryAgent-R1 | >50% 曝光, >72% 购买, +4.9% GMV |
| **JD** | GenRec GRPO-SR | 电商 | Page-wise 生成 + NLL 正则化防止不稳定 | +9.5% 点击, +8.7% 交易 |

### 2026 年六大趋势

1. **GRPO 是推荐 RL 的默认选择**：字节/快手/美团/阿里/JD 全部使用 GRPO 或变体——value-free 在 scale 上更稳定
2. **Agentic / Self-Evolving 系统**：Meta GEARS 和 Google 的 LLM-as-ML-Engineer 让 AI 自主优化推荐系统
3. **CoT 推荐**：Kuaishou OneReason 证明"思维链"能稳定提升推荐质量——这是推荐范式的新方向
4. **Pareto 最优多目标**：快手 POPO 和阿里 EG-GRPO 在多个冲突目标间做 Pareto 优化
5. **Offline RL 工业落地**：Washington Post CQL+OPE paywall (+6% 订阅)、DRPO 硬过滤理论保证、京东 GRPO-SR NLL 正则化——离线 RL 从论文走向生产
1. 记忆**：Meta Memento 365 天 + 快手/Taiji 的用户长期兴趣建模


## 6.6 代码：推荐环境 + PPO vs 贪心

模拟电商推荐：user 浏览 → 推荐 → 点击/不点击 → 推荐下一轮。

```python
# ---- 5. 简化 PPO 训练循环（概念演示） ----import torch.nn as nnimport torch.optim as optimclass RecPolicy(nn.Module):    """推荐策略网络：state -> item scores"""    def __init__(self, state_dim=8, n_items=200, hidden=64):        super().__init__()        self.net = nn.Sequential(            nn.Linear(state_dim, hidden), nn.ReLU(),            nn.Linear(hidden, hidden), nn.ReLU(),            nn.Linear(hidden, n_items)        )    def forward(self, state):        return self.net(state)  # [B, n_items]# ---- PPO 训练的一个简化 step ----def ppo_update_step(policy, optimizer, states, actions, rewards, old_log_probs, clip_eps=0.2):    """单步 PPO 更新（简化版，仅演示核心逻辑）。"""    logits = policy(states)  # [B, n_items]    log_probs = F.log_softmax(logits, dim=-1)    new_log_probs = log_probs.gather(1, actions.unsqueeze(1)).squeeze()  # [B]    ratio = torch.exp(new_log_probs - old_log_probs)  # π_new / π_old    advantages = (rewards - rewards.mean()) / (rewards.std() + 1e-8)    surr1 = ratio * advantages    surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages    loss = -torch.min(surr1, surr2).mean()    optimizer.zero_grad()    loss.backward()    optimizer.step()    return loss.item()# 演示：随机模拟一批数据做一个 PPO 更新policy = RecPolicy()optimizer = optim.Adam(policy.parameters(), lr=1e-3)# 模拟：batch=16, 每个 state 选 1 个 itemdummy_states = torch.randn(16, 8)dummy_actions = torch.randint(0, 200, (16,))dummy_rewards = torch.rand(16)  # simulated click reward (0 or 1)dummy_old_log_probs = torch.randn(16)  # from previous policyloss = ppo_update_step(policy, optimizer, dummy_states, dummy_actions, dummy_rewards, dummy_old_log_probs)print(f"PPO update step complete, loss = {loss:.4f}")print("(完整训练循环见 ch02 CartPole 示例 -- 这里只演示推荐场景的 PPO 接口)")
```

```python
import torch.nn as nnimport torch.optim as optimclass RecPolicy(nn.Module):    def __init__(self, s_dim=8, n_items=200, h=64):        super().__init__()        self.net = nn.Sequential(nn.Linear(s_dim,h), nn.ReLU(), nn.Linear(h,h), nn.ReLU(), nn.Linear(h,n_items))    def forward(self, s): return self.net(s)# Single PPO update step demopolicy = RecPolicy()opt = optim.Adam(policy.parameters(), lr=1e-3)states = torch.randn(16, 8)actions = torch.randint(0, 200, (16,))rewards = torch.rand(16)old_lp = torch.randn(16)logits = policy(states)new_lp = F.log_softmax(logits, dim=-1).gather(1, actions.unsqueeze(1)).squeeze()ratio = torch.exp(new_lp - old_lp)adv = (rewards - rewards.mean()) / (rewards.std() + 1e-8)  # simplified: GRPO-style; full PPO uses GAE (see ch02)loss = -torch.min(ratio*adv, torch.clamp(ratio, 0.8, 1.2)*adv).mean()opt.zero_grad(); loss.backward(); opt.step()print(f"PPO step: loss={loss:.4f}")
```

```python
import numpy as np

# ---- 1. 电商推荐环境 ----
class ECommerceRecEnv:
    """简化版电商推荐：user 兴趣向量 + item 特征 → 点击概率。

    每轮推荐 1 个 item（为简化，非 slate）。
    用户状态随点击行为漂移（兴趣变化）。
    """
    def __init__(self, n_items=200, n_user_types=10, state_dim=8):
        self.n_items = n_items
        self.state_dim = state_dim
        np.random.seed(42)
        # 生成 item embeddings
        self.item_embeds = np.random.randn(n_items, state_dim) * 0.5
        # 每类用户的初始兴趣向量
        self.user_interests = np.random.randn(n_user_types, state_dim)
        self.reset()

    def reset(self, user_type=None):
        self.user_type = user_type if user_type is not None else np.random.randint(10)
        self.user_state = self.user_interests[self.user_type].copy()
        self.history = []
        return self.user_state.copy()

    def step(self, action):
        """action: item index"""
        # 点击概率 = sigmoid(user_state · item_embed)
        score = np.dot(self.user_state, self.item_embeds[action])
        click_prob = 1 / (1 + np.exp(-score))
        clicked = np.random.random() < click_prob

        reward = 1.0 if clicked else 0.0
        self.history.append((action, clicked))

        # 用户状态漂移（兴趣变化）
        if clicked:
            self.user_state += 0.1 * self.item_embeds[action]  # 喜欢 → 兴趣偏向这个 item
        self.user_state += 0.01 * np.random.randn(self.state_dim)  # 兴趣自然演化
        self.user_state = self.user_state / (np.linalg.norm(self.user_state) + 1e-8)

        done = len(self.history) >= 20  # 每轮 session 推荐 20 次
        return self.user_state.copy(), reward, done

# ---- 2. 贪心策略 Baseline ----
class GreedyPolicy:
    """每次都推荐预估 CTR 最高的 item"""
    def __init__(self, env):
        self.item_embeds = env.item_embeds

    def act(self, state):
        scores = state @ self.item_embeds.T  # [n_items]
        return np.argmax(scores)

# ---- 3. Epsilon-Greedy Policy ----
class EpsilonGreedyPolicy:
    def __init__(self, env, epsilon=0.1):
        self.item_embeds = env.item_embeds
        self.epsilon = epsilon

    def act(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(len(self.item_embeds))
        scores = state @ self.item_embeds.T
        return np.argmax(scores)

# ---- 4. 对比 ----
env = ECommerceRecEnv()
greedy = GreedyPolicy(env)
eps_greedy = EpsilonGreedyPolicy(env, epsilon=0.15)

def evaluate(policy, env, n_sessions=100):
    """评估策略的平均 session reward"""
    total = 0
    for _ in range(n_sessions):
        state = env.reset()
        for _ in range(20):
            action = policy.act(state)
            state, reward, done = env.step(action)
            total += reward
            if done: break
    return total / n_sessions

greedy_avg = evaluate(greedy, env)
eps_avg = evaluate(eps_greedy, env)
print(f"Greedy average reward: {greedy_avg:.2f}")
print(f"Epsilon-Greedy (ε=0.15) average reward: {eps_avg:.2f}")
print(f"\n分析：ε-greedy 短期可能略低于贪心（因为 15% 的时间在随机探索），")
print(f"但长期来看探索到的新兴趣区域会提升总体奖励——这就是 E&E 的本质 trade-off。")
```

## 6.7 面试追问清单

**Q1**: 推荐 RL 和游戏 RL 的核心区别是什么？为什么推荐 RL 更难？

**Q2**: Offline RL 训练完直接上线有什么风险？怎么缓解？

**Q3**: Exploration 在推荐中怎么设计才安全？（提示：考虑"安全探索"的概念）

**Q4**: Slate 动作空间组合爆炸，工业界常用的三种解法及其 trade-off？

**Q5**: CQL 和 IQL 的核心差异是什么？为什么 CQL 是"悲观"的，IQL 是"不乐观"的？

**Q6**: Doubly Robust 估计为什么比单独的 DM 或 IPS 好？"只要两个中一个正确"是怎么做到的？

**Q7**: 你在论文中读到的推荐 RL 方法，在实际 10 亿用户系统中能直接用吗？瓶颈在哪？

---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/ch06-industrial-recsys-rl.ipynb" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
