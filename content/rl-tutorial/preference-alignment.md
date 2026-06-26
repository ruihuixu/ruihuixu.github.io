---
title: "第 4 章：偏好对齐线 —— 直接从偏好数据学习"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "preference-alignment"
tags:
  - "RL"
  - "RLHF"
  - "DPO"
  - "PPO"
categories:
  - "RL Tutorial"
description: "驱动问题：RLHF 需要训练 Reward Model + PPO Fine-tuning，三阶段级联复杂且不稳定。能不能直接从偏好数据学习，跳过 Reward Model？"
chapter: 4
difficulty: "核心"
section: "偏好对齐线"
---

# 第 4 章：偏好对齐线 —— 直接从偏好数据学习

> **驱动问题**：RLHF 需要训练 Reward Model + PPO Fine-tuning，三阶段级联复杂且不稳定。能不能直接从偏好数据学习，跳过 Reward Model？
> **本章目标**：理解 DPO → KTO → ORPO 的推导链和适用场景。
> **代码**：TRL DPOTrainer 实验 + KTO/ORPO 对比（DistilGPT-2 + 合成偏好数据）。
> **前置**：ch02（PPO、KL 约束）、ch03（GRPO 组内比较）。

## 4.1 RLHF 回顾：三阶段的必要性

标准 RLHF（InstructGPT / ChatGPT 的训练方式）：

```
Phase 1: SFT           → 模型学会"说人话"
Phase 2: Reward Model   → 学习人类偏好（需要大量偏好标注）
Phase 3: PPO Fine-tuning → 用 RM 信号优化策略
```

### 三阶段的代价

1. **RM 训练成本高**：需要数十万条偏好标注，且 RM 本身的泛化能力有限
2. **RM 过时问题**：随着 PPO 训练推进，策略生成的 response 分布偏移，RM 的评分不再准确
3. **PPO 不稳定**：4 个模型（Actor + Critic + Old Actor + RM）级联，任何一环出问题都可能导致训练崩溃
4. **超参耦合**：PPO 的 clip $\epsilon$、KL 系数 $\beta$、RM 的更新频率——三个超参相互影响，调参地狱

### 本章的核心问题

能不能绕过 Phase 2（Reward Model）和 Phase 3（PPO），直接从偏好数据中学习？
答案是——**可以**，而且方法出奇地简洁。

## 4.2 DPO：直接优化偏好

DPO（Direct Preference Optimization, NeurIPS 2023）的核心洞察：

> RLHF 的 PPO 目标 + Bradley-Terry 偏好模型，联合求解后，可以**消去 Reward Model**，
> 得到一个只依赖策略 $\pi_\theta$ 和参考策略 $\pi_{\text{ref}}$ 的 loss。

### 推导过程（关键步骤保留）

**Step 1: Bradley-Terry 偏好模型**

人类偏好概率：$P(y_w \succ y_l | x) = \sigma(r(x, y_w) - r(x, y_l))$

其中 $r(x,y)$ 是隐式的"真实奖励"，$\sigma$ 是 sigmoid。

**Step 2: PPO 的优化目标**

$$\max_\pi \mathbb{E}_{x \sim D, y \sim \pi}[r(x,y)] - \beta \cdot D_{KL}(\pi \| \pi_{\text{ref}})$$

最大化期望奖励，同时用 KL 散度约束不偏离参考策略太远。

**Step 3: 求解最优策略（关键一步）**

这个约束优化问题有闭式解：

$$\pi^*(y|x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y|x) \exp\left(\frac{1}{\beta} r(x,y)\right)$$

重新排列：$r(x,y) = \beta \log\frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \log Z(x)$

**Step 4: 代入 Bradley-Terry，消去 Reward**

将 $r(x,y)$ 的表达式代入 BT 偏好概率：

$$P(y_w \succ y_l) = \sigma\left(\beta\log\frac{\pi^*(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\frac{\pi^*(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

$Z(x)$ 抵消了！因为我们比较的是两个 response 的**差异**。

**Step 5: DPO Loss**

最大化这个似然，取负对数：

$$L_{\text{DPO}} = -\mathbb{E}_{(x,y_w,y_l)}\left[\log \sigma\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]$$

### 直觉

DPO 直接告诉模型："对于同一个 prompt，增大 winner 的相对概率，减小 loser 的相对概率"。
$\beta$ 控制更新幅度——$\beta$ 越大，差异被放大，更新越激进；$\beta$ 越小，越保守。

### 和 RLHF-PPO 的对比

| | RLHF-PPO | DPO |
|---|----------|-----|
| Reward Model | 需要单独训练 | 不需要 |
| PPO 训练循环 | 4 模型级联 | 不需要 |
| 训练稳定性 | 低（PPO 容易崩） | 高（一个 loss，端到端） |
| 数据需求 | 偏好对（训练 RM）+ prompt（PPO） | 偏好对 |
| 核心超参 | $\epsilon$, $\beta$, RM update freq | $\beta$ |

## 4.3 DPO 的优势和陷阱

### 优势

1. **简洁**：一个 loss，端到端训练，不需要 RL 训练循环
2. **稳定**：没有 PPO 的策略崩溃问题
3. **高效**：不需要维护多个模型，训练速度快

### 陷阱 1：分布偏移（Distribution Shift）

DPO 只在**训练集的偏好对**上优化——它只见过人类标注者写的 response。
但在推理时，模型自己生成的 response 分布完全不同。

> DPO 在训练集上完美区分 winner/loser，但面对自己生成的新 response 时，
> 没有见过对应的偏好信号——这就是 DPO 的泛化盲区。

RLHF-PPO 的优势在于：PPO 阶段用当前策略**在线采样**，每一轮都在应对"自己的分布"。

### 陷阱 2：长度偏差（Length Bias）

DPO 容易学出"长回复更好"的捷径——因为人类标注者倾向于选择更详细的回复，
而 $\beta \log(\pi/\pi_{\text{ref}})$ 天然会给长序列更多权重（每个 token 贡献一点 log prob 差异）。

缓解：对 loss 按 response 长度归一化，或使用 SimPO（用平均 log prob 而非总和）。

### 陷阱 3：Reference Model 选择至关重要

$\pi_{\text{ref}}$ 如果太弱（和 $\pi_\theta$ 差距大），DPO 容易过度偏离，失去已有能力。
$\pi_{\text{ref}}$ 如果太强（和 $\pi_\theta$ 几乎一样），梯度信号弱，学不动。

实践建议：$\pi_{\text{ref}}$ = SFT 模型，$\pi_\theta$ 初始化为 $\pi_{\text{ref}}$ 的副本。

## 4.4 KTO：不需要偏好对

### 动机

DPO 需要**成对**偏好数据（$y_w$ vs $y_l$），但实际标注中往往只有单条评分——
"这个回复打 4/5 分"比"比较这 2 个回复哪个好"更自然、成本更低。

### 核心思想：Kahneman-Tversky 前景理论

KTO（Kahneman-Tversky Optimization）借鉴了认知心理学的前景理论：

> 人对**损失**的敏感度远大于对**收益**的敏感度。
> 损失 100 元的痛苦 ≈ 收益 200 元的快乐。

KTO 将这一思想映射到对齐训练：
- 对于"好"回复（评分高）：鼓励模型增大其概率，但允许一定程度的保守
- 对于"差"回复（评分低）：强力惩罚，不让模型生成这类内容

### KTO Loss（简化版）

$$L_{\text{KTO}} = \mathbb{E}_{(x,y,\text{label})}\left[w(y) \cdot \left(1 - \sigma\left(\beta\log\frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)} - z_{\text{ref}}\right)\right)\right]$$

其中 $\text{label} \in \{\text{good}, \text{bad}\}$，$w(y)$ 根据 label 和是否"满足"来调整权重。

### DPO vs KTO

| | DPO | KTO |
|---|-----|-----|
| 数据需求 | 偏好对 ($y_w$, $y_l$) | 单条评分 |
| 标注成本 | 高（成对比较） | 低（单条打分） |
| 数学基础 | Bradley-Terry 偏好模型 | Kahneman-Tversky 前景理论 |
| 最佳场景 | 有高质量偏好对 | 数据稀缺或不完整 |

```python
import torchimport torch.nn.functional as Fdef kto_loss(pi_logps, ref_logps, labels, beta=0.1):    """KTO for unpaired binary feedback.    labels: 1=desirable, 0=undesirable"""    ratio = beta * (pi_logps - ref_logps)    z_ref = ratio.median()  # reference point    losses = torch.where(        labels == 1,        1 - F.sigmoid(ratio - z_ref),    # want sigma(ratio-z_ref)->1        1 - F.sigmoid(z_ref - ratio)      # want sigma(z_ref-ratio)->1    )    return losses.mean()# Demo: 2 desirable + 2 undesirablepi = torch.tensor([-1.5, -0.8, -2.5, -3.0])ref = torch.tensor([-1.4, -0.9, -2.0, -2.2])labels = torch.tensor([1, 1, 0, 0])print(f"KTO Loss: {kto_loss(pi, ref, labels):.4f}")
```

## 4.5 ORPO：SFT 和对齐一步到位

### 动机

标准流程：先 SFT $\to$ 再 DPO——两个阶段。能不能合并？

### ORPO 的做法

在 SFT 的交叉熵 loss 上，直接加一个 **odds ratio penalty**：

$$L_{\text{ORPO}} = L_{\text{SFT}} + \lambda \cdot L_{\text{OR}}$$

其中 $L_{\text{OR}} = -\log \sigma\left(\log\frac{\text{odds}_\theta(y_w|x)}{\text{odds}_\theta(y_l|x)}\right)$，$\text{odds}(y) = \frac{P(y)}{1-P(y)}$。

### ORPO 的直觉

- SFT loss：让模型学会生成合理的内容
- OR loss：**同时**让模型学会区分好坏——winner 的 odds 应该比 loser 高

因为 SFT 和对齐共享同一个模型参数，训练信号互相增强——
模型在学"说什么"的同时也在学"什么是好"。

### 优势

1. **单阶段训练**：不需要分开 SFT 和 DPO 两步
2. **保留 SFT 质量**：$L_{\text{SFT}}$ 保证基础能力不退化
3. **更快的总训练时间**：只有一个训练循环

### 代价

ORPO 的 SFT 阶段同时承担"学习语言模型"和"学习偏好"两个任务，
当偏好数据的分布和 SFT 数据的分布差异很大时，两个目标可能冲突。

实践中，通常先用纯 SFT warm-up 几个 epoch，再开启 OR loss。

```python
def orpo_loss(pi_logps_chosen, pi_logps_rejected, sft_loss, lamb=0.1):    """ORPO = SFT loss + odds ratio penalty"""    odds_c = torch.exp(pi_logps_chosen) / (1 - torch.exp(pi_logps_chosen) + 1e-8)    odds_r = torch.exp(pi_logps_rejected) / (1 - torch.exp(pi_logps_rejected) + 1e-8)    or_penalty = -F.logsigmoid(torch.log(odds_c) - torch.log(odds_r)).mean()    return sft_loss + lamb * or_penaltypi_c = torch.tensor([-1.5, -0.8])pi_r = torch.tensor([-3.0, -2.5])print(f"ORPO Loss: {orpo_loss(pi_c, pi_r, sft_loss=2.3):.4f}")
```

## 4.6 前沿扩展：DPOP — DPO 的简单强化

DPOP（DPO with Penalty on Greedy, June 2026）在 DPO 基础上做了一个极简的改进：
对 reference model 自己的贪心回复加惩罚。

### 动机

DPO 的问题是：$\pi_{	ext{ref}}$ 可能自己也偏好某些"看起来好但实际不好"的 pattern
（例如过长回复、套话）。DPO 用 $\pi_{	ext{ref}}$ 作为 anchor，
如果 $\pi_{	ext{ref}}$ 本身有偏差，DPO 会放大这个偏差。

### DPOP 的核心改进

在 DPO loss 中增加一个 gated penalty 项：

2035L_{	ext{DPOP}} = L_{	ext{DPO}} + lpha \cdot \max(0, \lograc{\pi_	heta(y_{	ext{greedy}}|x)}{\pi_{	ext{ref}}(y_{	ext{greedy}}|x)})2035

其中 {	ext{greedy}}$ 是 $\pi_{	ext{ref}}$ 的贪心解码结果。

**直觉**：如果当前策略 $\pi_	heta$ 比 reference 更偏好 ref 自己的贪心输出——
说明模型在"抄袭"ref 的捷径，应该惩罚。

### 效果

在 AlpacaEval 2.0 上，DPOP 超越了 SimPO 和 AlphaDPO，
且实现极其简单——只在 DPO 代码上加 3 行。

> **面试关键点**：DPOP 不需要额外的 reward model、不需要改 BT 模型、
> 不需要在线采样。它的 insight 是——"reference model 自己的偏好也需要被约束"。

## 4.7 前沿扩展：S-SPPO — 自博弈偏好优化

S-SPPO（Semantic-calibrated Self-Play Preference Optimization, June 2026）
代表了偏好对齐的另一个前沿方向——**自博弈**。

### 核心思想

DPO/KTO/ORPO 都依赖**外部**偏好数据（人类标注）。
S-SPPO 完全不需要外部偏好——它让模型**和自己对弈**来生成偏好信号：

1. 当前策略 $\pi_	heta$ 对同一 prompt 采样两个 response：, y_2$
2. 用外部 reward model（或规则）对两个 response 打分
3. 胜者 → winner，败者 → loser
4. 用 DPO 风格 loss 更新策略
5. 重复——**策略在不断改善自己的"对手"**

### 为什么叫"语义校准"？

S-SPPO 在语义空间和策略空间分别做校准：
- **语义空间**：确保 response 和 prompt 语义一致（不跑题）
- **策略空间**：确保更新后的策略不会"overfit 到自己的弱点"

### 效果

用 Llama-3-8B，无任何人类偏好数据，在 AlpacaEval 2.0 上达到 52.19% win rate。

### 和前几章方法的联系

S-SPPO 本质上是在做 **online RL**——和 ch02 的 PPO、ch03 的 GRPO 一样，
它用当前策略在线采样，避免了 DPO 的分布偏移问题。
但它比 PPO 简单（不需要 Critic），比 GRPO 灵活（不需要组内 K 次采样）。

> **面试关键点**：S-SPPO 代表了"self-play alignment"的方向——
> 让模型通过自我博弈提升，而非依赖外部标注。
> 在标注成本极高或标注不可得的场景中尤其有价值。

## 4.8 方法对比总结

| 方法 | 需要 RM | 需要偏好对 | 需要 SFT 模型 | 阶段数 | 训练复杂度 |
|------|--------|-----------|-------------|--------|-----------|
| RLHF-PPO | 是 | 间接（训练 RM 用） | 是 | 3 | 高 |
| DPO | 否 | 是 | 是（作为 ref） | 1（+SFT前置） | 中 |
| KTO | 否 | 否 | 是（作为 ref） | 1（+SFT前置） | 中 |
| ORPO | 否 | 否 | 否 | 1 | 低 |

### 选择指南

- **有高质量成对偏好数据** → DPO
- **只有单条评分** → KTO
- **预算极度有限 / 快速实验** → ORPO
- **在线数据不可替代的场景** → RLHF-PPO（尽管理论上更复杂，但在线交互的价值在某些场景中不可替代）

## 4.9 2026 前沿：当 SFT 比 RL 更有效时

2026 年的一个反直觉发现：在对齐任务上，**好的 SFT 数据有时比 RL 更有效**。

### Anthropic: Teaching Claude Why

Anthropic 2026 年 5 月的实验表明：用 300 万 token 的伦理推理数据做 SFT，
比复杂的 RL honeypot 训练高效 **28 倍**——agentic misalignment 从 22% 降到 3%。

关键 insight：不是 "RL 不好"，而是 "教会模型**为什么**某种行为是对的，
比让它从 reward 信号中摸索更高效"。

> **面试关键点**：RL 不是对齐的银弹。当你能清晰定义"好行为"时，
> 直接用 SFT 教原因（而非用 reward 给反馈）可能更高效。
> 这和 DPO 的思路一脉相承——跳过 reward model，直接学习偏好。

### Model Spec Midtraining (MSM)

Anthropic 的另一个创新：在 pretraining 和 alignment 之间插入一个"中间训练"阶段，
灌输行为准则（constitution）。在 Qwen3-32B 上测试：违规率从 54% 降到 7%，
SFT 数据需求减少 40-60 倍。

### OpenAI: Beneficial-Trait RL

OpenAI 2026 年论文发现了一个关键现象：**alignment 是低维行为流形**。
- 33 个 alignment 评估中，一个主成分解释了 ~28% 的方差
- 混入 5% 的"有益特质"数据（诚实/可纠正性/风险意识等），
  在 53 个 OOD 评估上达到 83% win rate
- **没有能力退化**——这解决了 RLHF 长期被诟病的"alignment tax"

> **面试关键点**：如果 alignment 真的是低维的，那么"少而精"的偏好数据
> 比海量噪声标注更重要。这和 KTO 的"单条评分优于无"是同一个方向的推论。


## 4.10 Reward Over-Optimization 专题

### 什么是 Reward Hacking？

模型学会最大化 reward 信号，但实际质量没有改善——它只是在"骗" reward model。

**经典案例**：
- 输出变长了（标注者倾向于详细的回复）
- 使用了更复杂的词汇（看起来更"高级"，但不一定更准确）
- 重复 safe/neutral 的短语（"这是一个很好的问题..."）

### 为什么 KL 约束不能完全解决？

KL 约束防止的是"策略变化太大"，但不能防止"策略在允许范围内找到 reward 的捷径"。

### Goodhart's Law："当一个指标成为目标时，它就不再是一个好指标"

在 RL 中：当你用 reward model 作为优化目标时，reward model 的评分就不再
代表真实的人类偏好了——因为模型找到了 reward model 的弱点。

### Reward Hacking 在 DPO 中出现吗？

会。DPO 没有显式的 reward model，但仍有隐式的 reward function——
$r(x,y) = \beta\log(\pi/\pi_{\text{ref}})$。当模型学会了最大化这个隐式 reward，
同样的 hacking 模式会出现：偏好 winner 的特征（长度、风格）被过度放大，
即使这些特征和真实质量无关。

### 缓解策略

1. **早停**：监控验证集上的真实质量（而非 reward），出现 reward 上升但质量下降时停止
2. **多 RM 融合**：训练多个不同的 RM，用 ensemble 的分数——更难的 hacking 目标
3. **Human-in-the-loop**：定期人工审核训练中的样本，修正 reward 信号
4. **Process Reward**（ch03 提过 DAPO 的 token-level）：把 reward 从"整段回复好不好"细化到"每个 token 好不好"——更难 hacking

## 4.11 代码：DPO 关键实现片段

以下展示 DPO loss 的计算逻辑。完整 TRL 训练脚本见仓库。

```python
import torch
import torch.nn.functional as F

def dpo_loss(pi_logps_chosen, pi_logps_rejected,
             ref_logps_chosen, ref_logps_rejected,
             beta=0.1):
    """DPO loss for a batch of preference pairs.

    Args:
        pi_logps_chosen:  [B] current policy log-prob for y_w
        pi_logps_rejected: [B] current policy log-prob for y_l
        ref_logps_chosen: [B] reference policy log-prob for y_w
        ref_logps_rejected:[B] reference policy log-prob for y_l
        beta: KL penalty coefficient
    Returns:
        loss: scalar, -log σ(β * (log π(y_w)/π_ref(y_w) - log π(y_l)/π_ref(y_l)))
    """
    # Step 1: 计算隐式 reward ratio = β * log(π/π_ref)
    chosen_ratio = beta * (pi_logps_chosen - ref_logps_chosen)
    rejected_ratio = beta * (pi_logps_rejected - ref_logps_rejected)

    # Step 2: reward difference = ratio_w - ratio_l
    logits = chosen_ratio - rejected_ratio  # [B]

    # Step 3: DPO loss = -log σ(logits)
    loss = -F.logsigmoid(logits).mean()

    # 监控指标
    with torch.no_grad():
        accuracy = (logits > 0).float().mean()  # winner ratio > loser ratio?
        chosen_reward = (beta * (pi_logps_chosen - ref_logps_chosen)).mean()
        rejected_reward = (beta * (pi_logps_rejected - ref_logps_rejected)).mean()

    return loss, {
        'loss/dpo': loss.item(),
        'accuracy/dpo': accuracy.item(),
        'reward/chosen': chosen_reward.item(),
        'reward/rejected': rejected_reward.item(),
        'reward/margin': (chosen_reward - rejected_reward).item()
    }


# ---- 演示：4 个偏好对 ----
pi_chosen = torch.tensor([-2.0, -1.5, -2.5, -1.0])
pi_rejected = torch.tensor([-3.0, -2.0, -2.0, -2.5])
ref_chosen = torch.tensor([-2.1, -1.4, -2.4, -1.1])
ref_rejected = torch.tensor([-2.2, -1.6, -2.3, -1.2])

loss, metrics = dpo_loss(pi_chosen, pi_rejected, ref_chosen, ref_rejected, beta=0.1)
print(f"DPO Loss: {metrics['loss/dpo']:.4f}")
print(f"Accuracy: {metrics['accuracy/dpo']:.2%}")
print(f"Reward margin: {metrics['reward/margin']:.4f}")
print("(margin > 0 means model prefers chosen over rejected — good)")
```

## 4.12 面试追问清单

**Q1**: DPO 的最大劣势是什么？什么场景下 DPO 不如 RLHF-PPO？

**Q2**: DPO 公式中的 $\beta$ 如果设太大或太小，分别会怎样？

**Q3**: DPO 推导中 $Z(x)$（partition function）为什么消掉了？如果 BT 模型不是 sigmoid 形式，$Z(x)$ 还能消掉吗？

**Q4**: KTO 在什么场景下优于 DPO？什么场景下 DPO 更好？

**Q5**: ORPO 把 SFT 和对齐合并——代价是什么？什么情况下不该用 ORPO？

**Q6**: Reward Over-Optimization 在 DPO 中出现吗？和 RLHF-PPO 中的表现有何不同？

**Q7**: 如果你用 DPO 训练后，发现模型在 validation 上的 loss 很低，但实际生成质量下降了，可能是什么原因？

---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/ch04-preference-alignment.ipynb" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
