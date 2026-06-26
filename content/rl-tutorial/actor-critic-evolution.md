---
title: "第 3 章：Actor-Critic 演进线 —— Critic 能更简单吗？能去掉吗？"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "actor-critic-evolution"
tags:
  - "RL"
  - "GRPO"
  - "RLOO"
  - "TRPO"
categories:
  - "RL Tutorial"
description: "驱动问题：PPO 需要同时训练 Actor 和 Critic。Critic 是额外的模型参数、额外的超参、额外的训练不稳定性。在大模型训练中，多一个 Critic 意味着多几十 GB 显存。能否简化甚至去掉 Critic？"
chapter: 3
difficulty: "进阶"
section: "Actor-Critic 线"
---

# 第 3 章：Actor-Critic 演进线 —— Critic 能更简单吗？能去掉吗？

> **驱动问题**：PPO 需要同时训练 Actor 和 Critic。Critic 是额外的模型参数、额外的超参、额外的训练不稳定性。在大模型训练中，多一个 Critic 意味着多几十 GB 显存。能否简化甚至去掉 Critic？
> **本章目标**：理解 RLOO → GRPO → DAPO 的演变逻辑和适用场景。
> **代码**：GRPO 对比实验（CartPole + DistilGPT-2）。
> **前置**：ch02（PPO、GAE、Actor-Critic 架构）。

## 3.1 回顾：PPO 的 Critic 负担

PPO 的组件清单：

| 组件 | 参数量 | 作用 |
|------|--------|------|
| Actor $\pi_\theta$ | 等价于模型大小 | 输出策略 |
| Critic $V_\phi$ | 接近模型大小 | 估计状态价值 |
| Old Actor $\pi_{\theta_{old}}$ | 等价于模型大小 | 计算 ratio |
| Reward Model $r_\psi$（RLHF 场景） | 等价于模型大小 | 提供 reward |

在 LLM RL 场景中，4 个模型同时在显存里——这就是为什么 PPO 在 LLM 训练中不实用。

**本章的主题**：沿着"去掉 Critic"这条线，从 RLOO 到 GRPO 再到 DAPO，看每一步解决了什么问题，代价是什么。

## 3.2 RLOO：用 Leave-One-Out 替代 Critic

### 核心思想

对同一个 prompt $x$，采样 $K$ 个 response $y_1, ..., y_K$。
对每个 $y_i$，用其他 $K-1$ 个 response 的平均 reward 作为 baseline：

$$\text{baseline}_i = \frac{1}{K-1} \sum_{j \neq i} R(y_j)$$

$$A_i = R(y_i) - \text{baseline}_i$$

### 为什么这个 baseline 是无偏的？

$\mathbb{E}[\text{baseline}_i] = \mathbb{E}[R(y_j)]_{j \neq i} = \mathbb{E}[R(y)]$

而 $\mathbb{E}[R(y_i) - \mathbb{E}[R(y)]] = \mathbb{E}[R] - \mathbb{E}[R] = 0$，
所以减去 baseline 不引入偏差。

### 对比 PPO

| | PPO | RLOO |
|---|-----|------|
| Critic 网络 | 需要 | 不需要 |
| 采样次数 | 1x | K≥2x |
| 显存 | Actor + Critic + Old Actor | Actor + Old Actor |
| 方差 | 取决于 Critic 质量 | 取决于 K |

### 代价

$K$ 次采样意味着 $K$ 倍的推理成本。RLOO 用额外的计算换取了更简单的架构。
对于 LLM 来说，推理比训练便宜得多（forward 不需要存梯度），所以这个 trade-off 是划算的。

```python
import torch# ---- RLOO baseline 演示 ----rewards = torch.tensor([0.3, 0.7, 0.2, 0.8])K = len(rewards)baselines = [(rewards.sum() - rewards[i]) / (K - 1) for i in range(K)]advantages_loo = rewards - torch.tensor(baselines)advantages_grpo = (rewards - rewards.mean()) / (rewards.std() + 1e-8)print('RLOO advantages:', advantages_loo.tolist())print('GRPO advantages:', advantages_grpo.tolist())print(f'RLOO baseline mean = {torch.tensor(baselines).mean():.3f} == reward mean = {rewards.mean():.3f}')
```

## 3.3 GRPO：组内相对排序

GRPO（Group Relative Policy Optimization）是 DeepSeek R1 的核心 RL 方法，
也是 2025 年最有影响力的 RL 技术创新之一。

### 核心改进

RLOO 用 leave-one-out mean 做 baseline，但组内 response 的 reward 可能有很大的绝对差异。
GRPO 改用**组内标准化**：

$$A_i = \frac{R(y_i) - \text{mean}(R_{\text{group}})}{\text{std}(R_{\text{group}})}$$

### 为什么标准化优于 LOO？

1. **尺度不变性**：无论 reward model 输出 0-1 还是 0-100，标准化后都在同一尺度上
2. **更低方差**：组内排名比绝对值更稳定——即使 reward model 整体偏高了，组内相对顺序不变
3. **自然校准**：标准化自动清除了 reward model 的系统性偏差

### 和 PPO clip 的结合

GRPO 仍然使用 PPO 的 clip 机制来控制更新幅度：

$$L^{\text{GRPO}} = \mathbb{E}\left[\min\left(r_t A_i^{\text{norm}}, \text{clip}(r_t, 1-\epsilon, 1+\epsilon) A_i^{\text{norm}}\right)\right]$$

### 为什么 GRPO 适合 LLM？

- 不需要独立的 Critic 模型 → 显存节约 ~50%
- 不需要 Reward Model 训练（在 RLHF 场景中直接用 rule-based reward 或 existing RM）
- 组内标准化对 reward hacking 有一定免疫（因为是通过相对排名而非绝对值判断）

## 3.4 DAPO：修复 GRPO 的缺陷

GRPO 在 DeepSeek R1 中成功了，但也暴露了几个问题。DAPO（Dynamic sAmpling Policy Optimization）
是 DeepSeek 2025 年 3 月提出的改进版。

### GRPO 的三个问题

**问题 1：组内方差塌陷**
当训练进行到一定阶段，同一个 prompt 的 $K$ 个 response 可能都很相似——组内 reward 几乎相同，
标准化后的 advantage 趋近于 0，梯度消失。

**问题 2：Reward Hacking**
模型学会了增加 reward 信号但实际质量没变好的"捷径"（例如生成长回复、重复模式）。
由于 GRPO 只看相对顺序，无法检测绝对质量下降。

**问题 3：训练崩溃**
KL 散度可能快速发散——policy 偏离 reference model 太远，生成乱码。

### DAPO 的改进

| 改进 | 解决的问题 | 机制 |
|------|-----------|------|
| **动态采样** | 组内方差塌陷 | 监控组内 reward std，小于阈值时增大 $K$ |
| **过度优化惩罚** | Reward Hacking | 当 policy 偏离 ref 超过阈值时加入 KL 惩罚项 |
| **Token-level advantage** | 粗粒度 credit assignment | 不是对整个 response 算一个 advantage，而是每个 token 算 |
| **Upper clip** | 训练崩溃 | 对 advantage 的上界额外 clip，防止大梯度更新 |

### DAPO 的 clipped advantage（和 PPO 的类比）

PPO clip $r_t$（概率比），DAPO 额外 clip $A_i$ 本身。两者的 philosophy 一致：

> 不让任何单次更新走得太远。

PPO 从"不让策略变太多"的角度 clip，DAPO 从"不让单个样本的影响太大"的角度 clip。
| **FlowTracer 借鉴** | Token 级 credit assignment 的验证 | FlowTracer (ICML 2026) 用 DAG 追踪 attention 信息流，实验证明 token-level 优势估计显著优于 sequence-level——支持了 DAPO 的设计选择 |

| **Kimi K2 工程实践** | 大规模 RL 稳定性 | Kimi K2 技术报告 (arXiv 2507.20534) 披露了 MuonClip 优化器和 Seer 快速同步推理系统，在万亿参数 MoE 上实现 74-97% 吞吐提升 |
| **Qwen3 Hidden-Align** | 零成本对齐增强 | Hidden-Align 发现正确 rollout 的最后一层 hidden states 趋于收敛（cosine sim ~0.84），对齐 hidden states 零额外开销，+3.8~6.2 分 over DAPO |


## 3.5 方法对比总结

| 方法 | Critic | 采样 | 稳定性 | 显存 | 适用场景 |
|------|--------|------|--------|------|---------|
| PPO | 需要 | 1x | 中 | 高（4模型） | 经典 RL 任务 |
| RLOO | 不需要 | K≥2x | 中 | 中（2模型） | LLM 微调入门 |
| GRPO | 不需要 | K≥4x | 中低 | 中（2模型） | LLM 推理训练（DeepSeek R1） |
| DAPO | 不需要 | 动态 | 高 | 中（2模型） | GRPO 不稳定时 |

### 去掉 Critic 的本质代价

Critic 提供的是**逐样本的精确 baseline**。去掉它后，我们用**组统计量**替代——这在小 $K$ 时方差很高。
所以 GRPO/DAPO 需要 $K \geq 4$ 甚至 $K=16$ 来保证有效的梯度信号。
在 LLM 推理场景中，多几次采样的开销远小于维护一个 Critic 模型，所以这个 trade-off 是划算的。

```python
# ---- DAPO vs GRPO: 稳定性对比 ----torch.manual_seed(42)def grad_magnitude(rewards):    std = rewards.std() + 1e-8    advantages = (rewards - rewards.mean()) / std    return advantages.abs().mean()r_high = torch.tensor([0.1, 0.9, 0.2, 0.8])r_low = torch.tensor([0.55, 0.52, 0.58, 0.53])print(f'High var (std={r_high.std():.3f}): grad = {grad_magnitude(r_high):.4f}')print(f'Low var  (std={r_low.std():.3f}): grad = {grad_magnitude(r_low):.4f}')print(f'Ratio: {grad_magnitude(r_high)/grad_magnitude(r_low):.1f}x')
```

## 3.6 代码：GRPO 关键实现片段

以下展示 GRPO 的核心逻辑——组内标准化 + PPO clip。完整训练脚本见仓库。

```python
import torch
import torch.nn.functional as F

def grpo_loss(log_probs, old_log_probs, rewards, clip_epsilon=0.2):
    """GRPO loss for a group of K responses to the same prompt.

    Args:
        log_probs:     [K] current policy log-prob for each response
        old_log_probs: [K] old policy log-prob for each response
        rewards:       [K] reward for each response (from RM or rule)
        clip_epsilon:  PPO clip range
    Returns:
        loss: scalar
    """
    # Step 1: 组内标准化 reward → advantage
    mean_r = rewards.mean()
    std_r = rewards.std() + 1e-8
    advantages = (rewards - mean_r) / std_r

    # Step 2: 计算 probability ratio
    ratio = torch.exp(log_probs - old_log_probs)

    # Step 3: PPO clip（和 ch02 的公式完全一致）
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
    loss = -torch.min(surr1, surr2).mean()

    return loss


def dapo_loss(log_probs, old_log_probs, rewards, clip_epsilon=0.2,
              kl_target=0.01, kl_beta=0.1):
    """DAPO loss: GRPO + KL penalty for over-optimization.

    Additional args:
        kl_target: target KL divergence from ref model
        kl_beta:   weight of KL penalty
    """
    # GRPO base loss
    mean_r, std_r = rewards.mean(), rewards.std() + 1e-8
    advantages = (rewards - mean_r) / std_r

    # Upper clip on advantages (DAPO specific)
    advantages = torch.clamp(advantages, max=5.0)

    ratio = torch.exp(log_probs - old_log_probs)
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
    grpo_term = -torch.min(surr1, surr2).mean()

    # DAPO KL penalty (当 KL > target 时才惩罚)
    # approx_kl = log(π_new / π_old) via log_probs - old_log_probs
    approx_kl = (old_log_probs - log_probs).mean()
    kl_penalty = kl_beta * max(0, approx_kl - kl_target)

    return grpo_term + kl_penalty


# ---- 对比演示 ----
# 模拟 4 个 response 的 reward
rewards = torch.tensor([0.2, 0.5, 0.3, 0.9])
old_log_probs = torch.tensor([-0.5, -0.3, -0.4, -0.2])
log_probs = torch.tensor([-0.4, -0.35, -0.3, -0.15])

print(f"GRPO loss: {grpo_loss(log_probs, old_log_probs, rewards):.4f}")
print(f"DAPO loss: {dapo_loss(log_probs, old_log_probs, rewards):.4f}")
print(f"Reward std = {rewards.std():.3f} — 如果过小，动态采样应增大 K")
```

## 3.7 面试追问清单

**Q1**: GRPO 的组内标准化如果组内全部 reward 相同（$\sigma = 0$），会发生什么？怎么处理？

**Q2**: RLOO 的 baseline 为什么是无偏的？数学上怎么证明？

**Q3**: DAPO 的动态采样在什么场景下比固定 $K$ 更有优势？

**Q4**: 去掉 Critic 的本质代价是什么？什么时候"去掉 Critic"不划算？

**Q5**: 从 PPO → RLOO → GRPO → DAPO，每一步的"驱动问题"是什么？每一步解决了上一个方法的什么缺陷？

**Q6**: 假设你在训练一个 LLM 用 GRPO，发现 reward 持续上升但生成质量下降。可能是什么原因？怎么诊断？

---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/ch03-actor-critic-evolution.ipynb" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
