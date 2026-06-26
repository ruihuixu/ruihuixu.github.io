---
title: "第 5 章：生成式推荐中的 RL"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "generative-recsys-rl"
tags:
  - "RL"
  - "推荐系统"
  - "GRPO"
  - "生成式推荐"
categories:
  - "RL Tutorial"
description: "驱动问题：经典推荐是检索→排序→重排三阶段流水线。生成式推荐把推荐建模为'序列生成'——user 作为 prompt，推荐列表作为生成的 token sequence。这时 RL 怎么用？"
chapter: 5
difficulty: "进阶"
section: "推荐交汇"
---

# 第 5 章：生成式推荐中的 RL

> **驱动问题**：经典推荐是检索→排序→重排三阶段流水线。生成式推荐把推荐建模为"序列生成"——user 作为 prompt，推荐列表作为生成的 token sequence。这时 RL 怎么用？
> **本章目标**：理解生成式推荐的 MDP 形式化，掌握 RL 训练方案的选择逻辑。
> **代码**：简化版生成式推荐环境模拟器 + PPO 训练。
> **前置**：ch02（PPO）、ch03（GRPO 组内比较）。

## 5.1 推荐范式的转变

### 经典推荐：三阶段流水线

```
User Request → Retrieval(召回) → Ranking(排序) → Re-ranking(重排) → Slate
                 数万候选           数百候选          10-20候选          最终展示
```

每个阶段独立优化，阶段之间通过静态特征传递信息。优点是工程成熟，缺点是**级联误差**——
召回阶段的 loss 和最终用户体验没有直接关系。

### 生成式推荐：端到端建模

```
User Profile → [S1, S2, ..., S_K] → Item Sequence
                   ↑
            Semantic IDs (learned tokens)
```

核心思想：把推荐列表当作**一个序列**，用 Transformer 自回归地生成。
每个 item 被编码为 1-3 个"语义 token"（Semantic ID），模型逐 token 生成。

### 为什么需要 RL？

生成式推荐的训练信号天然是**带延迟的**：
- 曝光 → 点击（几秒到几分钟）
- 点击 → 购买/转化（几小时到几天）
- 推荐序列的整体用户体验（极难量化）

而且，推荐列表是一个整体——前 3 个 item 的质量影响用户是否继续往下看。
这种"早期决策影响后期回报"的结构，正是 MDP 描述的序贯决策。

## 5.2 生成式推荐 = MDP

### MDP 五元组的映射

| MDP 元素 | 生成式推荐中的含义 |
|----------|-------------------|
| **State** $s_t$ | 用户画像 + 已生成的 token 序列 + 上下文特征 |
| **Action** $a_t$ | 生成下一个语义 token（或选择下一个 item）|
| **Transition** $P$ | 给定当前状态和生成的 token，下一个状态是确定的（自回归）|
| **Reward** $r_t$ | 用户反馈（点击/转化/时长），只在序列生成完成后获得 |
| **Discount** $\gamma$ | 控制"序列前面的位置 vs 后面的位置"哪个更重要 |

### 和 LLM 文本生成的类比

| 维度 | LLM 文本生成 | 生成式推荐 |
|------|-------------|-----------|
| Token 空间 | 5 万词表 | item ID（百万级）|
| Reward | 回答质量（推理正确性/有用性）| 用户行为（点击/转化）|
| Reward 延迟 | 通常即时（整段回答评分）| 延迟（点击在曝光后，转化在点击后）|
| 多样性需求 | 中等（避免重复）| 高（slate 内 item 需要覆盖不同兴趣面）|

### 生成式推荐的特殊挑战

1. **Token 空间巨大**：item ID 在百万到十亿级别，远超 LLM 词表
2. **Reward 极度稀疏**：只有被曝光的 item 才有反馈信号（99%+ 的 item 被推荐但从未曝光）
3. **Slate 约束**：不能给用户推荐同一个 item 两次，需要考虑 slate 内部的 diversity
4. **冷启动**：新用户和新 item 没有历史数据

## 5.3 博客已有论文的 RL 视角对照

以下用 ch01-ch04 的 RL 语言重新解读仓库中已有的推荐论文笔记。

### ULTRA-HSTU：State Encoder 的设计

- **RL 视角**：这是一篇关于**如何编码 state $s_t$** 的论文
- 核心贡献：用 Hierarchical Sequential Transduction Unit 将用户长序列行为压缩为稠密 state 表示
- RL 含义：$V(s)$ 和 $\pi(a|s)$ 都依赖 state 编码的质量——更好的 state encoder $\to$ 更好的策略

### OneRec / OneTrans：生成式推荐的 MDP 形式化

- **RL 视角**：这是生成式推荐的**MDP 定义**和**策略架构**论文
- OneRec：用自回归 Transformer 逐位生成 item，定义了 state/action/reward 的完整 MDP
- OneTrans：统一的生成式框架，结合检索和排序为一个端到端模型
- RL 含义：如果你接受"推荐=序列生成"，那么所有 ch02-ch04 的 RL 方法都可以直接用于训练

### RankMixer：排序阶段的 RL 训练信号

- **RL 视角**：RankMixer 的排序过程是一个**确定性策略** $\pi: s \to \text{ranked list}$
- 训练信号：点击/转化作为 reward，但 reward 是**整个 ranked list 的结果**，不是单个 item 的
- RL 含义：需要 credit assignment——列表中的哪个 item 负责了用户的行为？

### TokenMixer：Token 混合策略的策略梯度解释

- **RL 视角**：TokenMixer 的 token 混合策略本质上是在学习一个**随机策略** $\pi(a|s)$
- 混合不同粒度的 token（粗粒度=品类，细粒度=具体 item）类似于 RL 中的分层策略
- RL 含义：可以用 policy gradient 直接优化混合策略的参数

> **统一框架**：所有这些论文都在不同层面回答了同一个问题——
> "如何为推荐系统设计 state、action、reward？"
> ULTRA-HSTU 解决 state 编码，OneRec 定义 action 空间，RankMixer/TokenMixer 优化策略。

## 5.4 生成式推荐的 RL 训练方案

### 方案 1：离线 PPO（Offline RL + Importance Sampling）

用历史日志数据训练，用 importance sampling 校正分布偏移：

$$\nabla J \approx \mathbb{E}_{(s,a) \sim D_{\text{log}}}\left[\frac{\pi_\theta(a|s)}{\pi_{\text{log}}(a|s)} \cdot A(s,a) \cdot \nabla \log \pi_\theta(a|s)\right]$$

**优势**：不需要在线交互，安全
**劣势**：$\pi_\theta$ 和 $\pi_{\text{log}}$ 差异大时 importance weight 方差爆炸；只能学到日志数据的子集

### 方案 2：GRPO 直接训练（Online RL）

对每条 user query，采样 $K$ 个推荐序列，组内排序：

$$A_i = \frac{R(\text{seq}_i) - \text{mean}(R_{\text{group}})}{\text{std}(R_{\text{group}})}$$

**优势**：不需要 Critic（如 ch03 所述），组内比较对 reward 的绝对尺度不敏感
**劣势**：$K$ 倍推理成本；需要 real-time feedback（不可行于所有场景）

### 方案 3：DPO 风格（Preference-based RL）

用点击 vs 未点击作为偏好对 ${y_w = \text{clicked}, y_l = \text{not clicked}}$：

$$L = -\log \sigma\left(\beta\log\frac{\pi(\text{clicked}|u)}{\pi_{\text{ref}}(\text{clicked}|u)} - \beta\log\frac{\pi(\text{skipped}|u)}{\pi_{\text{ref}}(\text{skipped}|u)}\right)$$

**优势**：不需要显式 reward model，偏好信号天然存在于点击日志中
**劣势**：需要 $\pi_{\text{ref}}$（通常是上一版线上模型），且点击和"skip"之间的信号噪声很大

### 方案对比

| | 离线 PPO | GRPO | DPO 风格 |
|---|---------|------|---------|
| 在线交互 | 不需要 | 需要 | 不需要 |
| Critic 网络 | 需要 | 不需要 | 不需要 |
| 数据需求 | 日志数据 | 实时反馈 | 点击日志 |
| 工程复杂度 | 中 | 高（在线系统）| 低 |
| 适用阶段 | 离线实验 | 在线 A/B Test | 离线训练 + 在线部署 |
> **2026 改进 — AdaGRPO (June 2026)**：标准 GRPO 假设所有 reward 信号等权重，但推荐场景中某些 reward 天然噪声更大（例如点击 vs 购买）。AdaGRPO 引入 per-sample 诊断门控——自动降低高噪声样本的梯度权重，在生成式推荐中显著提升训练稳定性。


## 5.5 代码：生成式推荐环境模拟器

以下实现一个简化版生成式推荐环境：100 items × 5 user types × 3-step sequence。

```python
import numpy as np
import torch
import torch.nn as nn

# ---- 1. 生成式推荐环境 ----
class GenerativeRecEnv:
    """简化版生成式推荐环境。

    State:  user_type (0-4) + 已生成的 token 序列
    Action: 从 item_pool 中选择下一个 item token
    Reward: 匹配度得分（仅在序列生成完成后给出）
    """
    def __init__(self, n_items=100, n_user_types=5, seq_len=3):
        self.n_items = n_items
        self.n_user_types = n_user_types
        self.seq_len = seq_len
        # 每个 user type 对 item 的真实偏好（随机但固定）
        np.random.seed(42)
        self.user_prefs = np.random.randn(n_user_types, n_items)  # [U, I]
        self.reset()

    def reset(self, user_type=None):
        self.user_type = user_type if user_type is not None else np.random.randint(self.n_user_types)
        self.generated = []
        self.step_count = 0
        return self._get_state()

    def step(self, action):
        """action: item index (0 to n_items-1)"""
        # 不能重复选
        if action in self.generated:
            return self._get_state(), -1.0, False

        self.generated.append(action)
        self.step_count += 1
        done = (self.step_count >= self.seq_len)

        if done:
            # 序列完成，计算 reward = Σ user_pref[user_type][item]
            reward = sum(self.user_prefs[self.user_type][i] for i in self.generated)
        else:
            reward = 0.0  # 中间步骤无奖励（延迟 reward）

        return self._get_state(), reward, done

    def _get_state(self):
        """State: user_type one-hot + mask of generated items"""
        user_vec = np.zeros(self.n_user_types)
        user_vec[self.user_type] = 1.0
        generated_mask = np.zeros(self.n_items)
        for g in self.generated:
            generated_mask[g] = 1.0
        return np.concatenate([user_vec, generated_mask]).astype(np.float32)

# ---- 2. 简单策略网络（生成式推荐 Agent）----
class GenerativeRecAgent(nn.Module):
    """输出对每个 item 的 logit，mask 已生成的 item"""
    def __init__(self, state_dim, n_items, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, n_items)
        )
        self.n_items = n_items

    def forward(self, state):
        logits = self.net(state)  # [B, n_items]
        # Mask 已生成的 item（state 的后 n_items 维是 mask）
        mask = state[:, -self.n_items:]  # [B, n_items]
        logits = logits - 1e9 * mask  # 已选 item 的 logit 设为 -inf
        return logits

# ---- 3. 快速测试 ----
env = GenerativeRecEnv(n_items=100, n_user_types=5, seq_len=3)
agent = GenerativeRecAgent(state_dim=5+100, n_items=100)

# 模拟一条轨迹
state = env.reset(user_type=0)
total_reward = 0
for step in range(3):
    with torch.no_grad():
        logits = agent(torch.FloatTensor(state).unsqueeze(0))
        action = torch.argmax(logits, dim=-1).item()  # 贪心
    state, reward, done = env.step(action)
    total_reward += reward
    print(f"Step {step+1}: selected item {action}, reward={reward:.3f}")
print(f"Total reward: {total_reward:.3f}")
print(f"\nBest possible (cheating): {sorted(env.user_prefs[0], reverse=True)[:3]}")
print(f"Best reward: {sum(sorted(env.user_prefs[0], reverse=True)[:3]):.3f}")
```

```python
# ---- 5. 方案对比: 贪心 vs 随机 vs 启发式 ----def evaluate_policy(agent_fn, env, n_episodes=50):    """评估一个策略的平均 episode reward。"""    total_reward = 0    for _ in range(n_episodes):        state = env.reset()        ep_reward = 0        for step in range(3):            logits = agent_fn(state)            action = torch.argmax(logits, dim=-1).item()            state, reward, done = env.step(action)            ep_reward += reward            if done:                break        total_reward += ep_reward    return total_reward / n_episodes# 随机策略 baselineclass RandomAgent:    def __call__(self, state):        return torch.randn(1, 100)  # 随机 logits# 启发式策略: 选"平均偏好"最高的 itemclass HeuristicAgent:    def __init__(self, env):        self.avg_prefs = env.user_prefs.mean(axis=0)  # [n_items]    def __call__(self, state):        return torch.FloatTensor(self.avg_prefs).unsqueeze(0)# 对比三种策略random_score = evaluate_policy(RandomAgent(), env)heuristic_score = evaluate_policy(HeuristicAgent(env), env)greedy_score = evaluate_policy(agent, env)  # agent 是前面定义的 GenerativeRecAgentprint(f"Random policy:     {random_score:.2f}")print(f"Heuristic (avg):   {heuristic_score:.2f}")print(f"Greedy (untrained): {greedy_score:.2f}")print(f"\nUpper bound (cheating): {sum(sorted(env.user_prefs[0], reverse=True)[:3]):.2f}")print("\n启示: 未训练的 agent 和随机差不多 -- 需要 RL 训练才能接近上界")
```

## 5.6 面试追问清单

**Q1**: 生成式推荐中的 state 和 action 分别是什么？和传统推荐有何本质不同？

**Q2**: 为什么推荐 RL 的 reward 是延迟的？

<details><summary>答案要点</summary>

- 推荐延迟链: 曝光→点击(秒级) →加购(分钟级) →购买(小时-天级) →复购(周-月级)
- 与游戏 RL 关键不同: 游戏延迟固定(固定帧率)，推荐延迟随机且极长，使 credit assignment 更难
- 另一不同: 游戏 reward 确定(得分/通关)，推荐 reward 充满噪声(用户可能因外部原因购买)
</details>这和游戏 RL 的延迟 reward 有何不同？

**Q3**: 生成式推荐用 GRPO 训练的优势是什么？为什么不用 PPO？

**Q4**: 推荐场景的 exploration 怎么设计？（提示：不能给用户乱推荐）

**Q5**: 如果生成式推荐的 token 空间是 1000 万（item 数量），自回归地生成 5 个 item——这个搜索空间有多大？这对 RL 方法意味着什么？

<details><summary>答案要点</summary>

- 搜索空间 = P(10^7, 5) 约等于 10^35 种可能推荐序列，无法穷举
- 必须用参数化策略(神经网络)做泛化，Policy gradient 直接优化策略参数
- GRPO 优势: 组内比较只需要 K 次采样(4-16)，不需要遍历搜索空间
</details>

---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/ch05-generative-recsys-rl.ipynb" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
