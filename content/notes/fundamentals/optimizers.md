---
title: "优化器全景：从 SGD 到 Sophia 的演进与实战"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "optimizers"
tags:
  - "优化器"
categories:
  - "Deep Learning"
math: true
description: "深度梳理 SGD、Momentum、NAG、AdaGrad、RMSprop、Adam、FTRL、AdamW、Lion、Sophia 的定义、直觉、公式与适用场景，聚焦推荐系统（稀疏 Embedding、混合策略）与大语言模型（解耦 Weight Decay、低精度、二阶优化）的实战选型。"
---

> **关键词**：优化器、SGD、Adam、AdamW、FTRL、Lion、Sophia、AdaGrad、Weight Decay、稀疏特征
>
> **涵盖**：SGD / Momentum / NAG / AdaGrad / RMSprop / Adam / FTRL / AdamW / Lion / Sophia
>
> **聚焦场景**：推荐系统（核心） / 大语言模型

---

## 一、问题的本质

给定损失函数 $L(\theta)$，优化器回答一个问题：

$$
\theta_{t+1} = \theta_t - \Delta\theta_t
$$

$\Delta\theta_t$ 怎么算，决定了训练的效率、稳定性和最终效果。

**推荐系统和大语言模型面对的根本矛盾完全不同：**

| 维度 | 推荐系统 | 大语言模型 |
|------|---------|-----------|
| 核心痛点 | 稀疏特征学习不充分 | 训练不稳定、显存不够 |
| 参数分布 | 99% Embedding + 1% Dense | 99%+ Dense |
| 特征频率 | 长尾分布，冷门 ID 几乎无梯度 | 均匀分布，每个 token 频率接近 |
| 单次训练成本 | 中等（可接受调参试错） | 极高（试错代价大） |
| 线上部署 | 需要模型稀疏化（压缩 Embedding 表） | 不关心稀疏 |

这两个场景对优化器的需求差异巨大，后文会沿着这两条线展开。

---

## 二、基础方法：从 SGD 到 NAG

### 2.1 SGD：所有优化器的起点

$$
\theta_{t+1} = \theta_t - \eta \cdot g_t
$$

其中 $g_t = \nabla_\theta L(\theta_t)$。

**优点**：简单，泛化性好（噪声本身是一种隐式正则化）。

**致命缺陷**：所有参数共享同一个学习率 $\eta$。

在推荐系统里这意味着：user_id=12345（冷门用户，出现 5 次）和 item_id=888（热门物品，出现 10 万次）的 Embedding 被同一个步长更新。热门物品梯度密集，Embedding 迅速收敛；冷门用户梯度稀疏，Embedding 几乎原地踏步。

这就是优化器要解决的第一个问题：**不同参数需要不同的学习率**。

### 2.2 Momentum：用历史方向纠正当下

SGD 在峡谷地形（一个方向陡峭、另一个方向平缓）中会剧烈震荡：

```
Loss 等高线狭长 → 梯度方向反复横跳 → 收敛极慢
```

Momentum 用一个"速度"变量积累历史梯度方向，抑制震荡：

$$
\begin{aligned}
v_t &= \beta \cdot v_{t-1} + g_t \\
\theta_{t+1} &= \theta_t - \eta \cdot v_t
\end{aligned}
$$

**直觉**：把参数想象成从山上滚下的球。梯度是瞬时的力，动量是累积的速度。山谷中的震荡梯度会相互抵消，而沿山谷方向的梯度持续叠加。

$\beta = 0.9$ 是经验甜点：相当于当前梯度权重 $1/(1-0.9) = 10$ 步的指数移动平均。太小（0.5）震荡抑制不足，太大（0.99）反应迟钝。

### 2.3 NAG：看一步再走

Nesterov Accelerated Gradient 把"前瞻"引入动量：

$$
\begin{aligned}
v_t &= \beta \cdot v_{t-1} - \eta \cdot \nabla_\theta L(\theta_t + \beta \cdot v_{t-1}) \\
\theta_{t+1} &= \theta_t + v_t
\end{aligned}
$$

**直觉**：先在动量方向上走一步，再在那个位置算梯度。相当于"我按当前速度继续走会到哪？到那之后再算我应该往哪拐"。

理论上有更好的收敛保证（凸优化中 $O(1/t^2)$ vs Momentum 的 $O(1/t)$），但在深度学习的非凸场景中，相比 Momentum 的收益有限。推荐系统和大模型里几乎不直接用 NAG，但它的"前瞻"思想被后续方法继承。

---

## 三、自适应学习率：为什么 AdaGrad 是推荐系统的天然盟友

### 3.1 AdaGrad：稀疏特征的守护者

**核心公式**：

$$
\begin{aligned}
G_t &= G_{t-1} + g_t^2 \quad \text{（逐元素累加梯度平方）} \\
\theta_{t+1} &= \theta_t - \frac{\eta}{\sqrt{G_t + \varepsilon}} \cdot g_t
\end{aligned}
$$

**魔法在哪里？** 分母 $\sqrt{G_t}$ 是每个参数历史上所有梯度平方和的平方根。一个参数被更新得越多，$G_t$ 越大，有效学习率 $\eta / \sqrt{G_t}$ 越小。反之亦然。

**用具体数字感受一下：**

假设 Embedding 维度 128，学习率 $\eta = 0.01$：

| 特征 | 出现次数 | 累积梯度平方 $G_t$ | 有效 LR |
|------|---------|-------------------|---------|
| user_id=12345（冷门用户） | 5 次 | ~5 | $0.01/\sqrt{5} \approx 0.0045$ |
| item_id=888（热门物品） | 100,000 次 | ~100,000 | $0.01/\sqrt{100000} \approx 0.000032$ |

**冷门用户的有效学习率是热门物品的 ~140 倍**。这正是我们想要的：冷门特征数据少，需要大步快学；热门特征数据多，需要小步精调。

不需要任何人工干预，AdaGrad 自动做到了这一点。这就是为什么它至今仍是许多推荐模型 Embedding 层的标配。

**致命缺陷**：$G_t$ 只会增长，永不衰减。训练足够久后，所有参数的有效学习率都趋近于零，训练停滞。这对 Embedding 层尤其致命——热门物品在训练后期完全学不动了。

### 3.2 RMSprop：用遗忘解决单调衰减

RMSprop 用指数移动平均替换累加和：

$$
v_t = \beta_2 \cdot v_{t-1} + (1 - \beta_2) \cdot g_t^2
$$

$\beta_2 = 0.999$ 的含义：有效窗口约为 $1/(1-0.999) = 1000$ 步。超过 1000 步的历史梯度信息会被"遗忘"。

**为什么不是 0.99 或 0.9999？** 0.99 窗口太短（~100 步），噪声大；0.9999 窗口太长（~10000 步），接近 AdaGrad 的单调问题。0.999 是平衡点。

RMSprop 解决了 AdaGrad 的致命问题，但它没有动量机制——它在处理峡谷地形时仍然会震荡。

### 3.3 Adam：动量 + 自适应的联姻

Adam 把 Momentum 的一阶矩和 RMSprop 的二阶矩结合在一起：

$$
\begin{aligned}
m_t &= \beta_1 \cdot m_{t-1} + (1 - \beta_1) \cdot g_t \quad &\text{（一阶矩，动量）} \\
v_t &= \beta_2 \cdot v_{t-1} + (1 - \beta_2) \cdot g_t^2 \quad &\text{（二阶矩，自适应 LR）} \\
\hat{m}_t &= \frac{m_t}{1 - \beta_1^t} \quad &\text{（偏差修正）} \\
\hat{v}_t &= \frac{v_t}{1 - \beta_2^t} \quad &\text{（偏差修正）} \\
\theta_{t+1} &= \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon}
\end{aligned}
$$

**偏差修正为什么必要？** $m_0 = 0$，$v_0 = 0$，所以第一步 $m_1 = (1-\beta_1)g_1$，被缩小了 $1-\beta_1 = 0.1$ 倍。如果不修正，前几步的更新量被严重低估。$m_t / (1-\beta_1^t)$ 让前几步的矩估计"回到正常尺度"。

**默认超参的由来：**

| 超参 | 默认值 | 含义 |
|------|-------|------|
| $\beta_1$ | 0.9 | 动量窗口 ~10 步 |
| $\beta_2$ | 0.999 | 自适应窗口 ~1000 步 |
| $\varepsilon$ | 1e-8 | 防止除零，通常不需要改 |
| $\eta$ | 0.001 | 需要场景调整的最大因素 |

$\beta_1$ 和 $\beta_2$ 的默认值非常稳健，几乎不需要改。真正需要调的只有学习率 $\eta$。

**在推荐系统中的位置**：Adam 是推荐模型稠密层（MLP、Attention）的默认选择。但它有一个盲区——稀疏 Embedding 上，Adam 的二阶矩估计对低频特征会剧烈波动（样本太少，$v_t$ 不稳定），效果常不如朴素的 AdaGrad。

---

## 四、推荐系统的优化器实战 ★

### 4.1 参数二元性：一个推荐模型，两种参数

一个典型的推荐模型（如 DLRM、DeepFM）由两类参数组成：

| 特征 | Embedding 层 | Dense 层 |
|------|------------|---------|
| 参数量 | 十亿级（用户/物品/类目 ID） | 百万级 |
| 参数占比 | > 99% | < 1% |
| 梯度来源 | 仅当该 ID 出现在 batch 中 | 每个 batch 都有 |
| 更新频率 | 极度不均（长尾分布） | 均匀 |
| 对 LR 的需求 | 冷门 ID 要大，热门 ID 要小 | 中等、稳定 |

**单一优化器 + 单一 LR 是行不通的**。同一个 LR 下，要么冷门特征学不动，要么热门特征过拟合。

工业界的答案很简单：**Embedding 层和 Dense 层用不同的优化器**。

### 4.2 FTRL：CTR 预估的工业标准

在推荐模型上线时，还有一个额外需求：**模型稀疏化**。十亿级的 Embedding 表全存下来成本太高，我们希望大量无用特征（低频、低信息量）的 Embedding 权重精确为零。

理想情况下，L1 正则化应该能做到这一点。但 L1 + SGD 在实际中产不出真正的稀疏。

**为什么 L1 + SGD 无效？**

L1 正则化的梯度是常数 $\pm \lambda$，SGD 的更新是 $\theta \leftarrow \theta - \eta(g + \lambda \cdot \text{sign}(\theta))$。理论上这应该把权重推向零，但实际上：

- 数据梯度 $g$ 也在同时更新。一个参数可能被 L1 推向 0，但紧接着被数据梯度拉回来。
- 所有参数共享同一个 $\lambda$ 和 $\eta$，冷门参数的 L1 力度和热门一样——但冷门参数本身就更新少，L1 推动不足以消除权重。

**FTRL（Follow The Regularized Leader）的解法**：为每个参数维护独立的累积梯度历史，让 L1 正则化真正"有机会"把不重要参数的权重精确置零。

FTRL 的更新公式（per-coordinate 形式）：

$$
\begin{aligned}
\theta_{t+1,i} &=
\begin{cases}
0 & \text{if } |z_{t,i}| \leq \lambda_1 \\
-\left(\frac{\beta+\sqrt{n_{t,i}}}{\alpha} + \lambda_2\right)^{-1} \cdot (z_{t,i} - \text{sign}(z_{t,i}) \cdot \lambda_1) & \text{otherwise}
\end{cases} \\[1em]
\text{其中：}& \\
z_{t,i} &= g_{1:t,i} - \sum_{s=1}^{t} \sigma_{s,i} \cdot \theta_{s,i} \quad \text{（累积梯度，含校正项）} \\
n_{t,i} &= \sum_{s=1}^{t} g_{s,i}^2 \quad \text{（累积梯度平方，同 AdaGrad）}
\end{aligned}
$$

**四个超参的含义与调参经验：**

| 超参 | 作用 | 经验范围 | 调参顺序 |
|------|------|---------|---------|
| $\alpha$ | 控制整体学习率规模 | 0.001 ~ 0.1 | 先定 |
| $\beta$ | 稳定性系数，越大越像 AdaGrad | 0 ~ 1（通常 1） | 次调 |
| $\lambda_1$ | L1 正则化力度，越大越稀疏 | 0 ~ 0.1 | 后调 |
| $\lambda_2$ | L2 正则化力度，标准 Weight Decay | 0 ~ 0.01 | 最后 |

调参策略：先设 $\lambda_1 = 0$，$\lambda_2 = 0$，调好 $\alpha$ 和 $\beta$（看 AUC 收敛）。然后逐步增大 $\lambda_1$ 直到稀疏度达标同时 AUC 不降超 0.1%。

**适用场景**：CTR 预估模型（Wide&Deep、DeepFM、DCN 等）的 Embedding 层。Google 2013 年提出，至今仍是广告/推荐系统中 Embedding 层的工业标准。

### 4.3 混合策略：工业界的事实标准

推荐模型的最终答案：**Embedding 层和 Dense 层分开伺候**。

```
推荐模型训练配置（经典组合）
├── Embedding 层
│   ├── 优化器：FTRL（需要稀疏化）或 AdaGrad（追求效果）
│   ├── LR：0.01 ~ 0.1
│   ├── λ₁：0.005 ~ 0.02（仅 FTRL）
│   └── 初始化：均匀分布 [-0.01, 0.01]
│
├── Dense 层（MLP / Attention）
│   ├── 优化器：Adam
│   ├── LR：0.0001 ~ 0.001
│   ├── β₁=0.9, β₂=0.999
│   └── 初始化：He 初始化（配合 ReLU 系）
│
└── 其他
    ├── BatchNorm 层通常不设 Weight Decay
    └── LR Scheduler：Constant 或 Step Decay（每 5 epoch ×0.5）
```

**关键数字**：Embedding LR 通常是 Dense LR 的 **10~100 倍**。这不是偶然，而是由参数更新频率的差异决定的——Embedding 参数更新稀疏，每次更新的"信息量"也大，需要更大的步长来利用有限的梯度信号。

**主流模型的真实配置参考：**

| 模型 | Embedding 优化器 | Dense 优化器 | 备注 |
|------|----------------|------------|------|
| DLRM (Meta) | SGD + per-param LR | Adam | Embedding 用 BN 后分桶设置 LR |
| Wide&Deep (Google) | FTRL (wide) | AdaGrad (deep) | Wide 部分 L1 稀疏，Deep 部分自适应 |
| DeepFM | FTRL / AdaGrad | Adam | 与 W&D 类似思路 |
| DIN (Alibaba) | AdaGrad | Adam | 兴趣提取网络 + Embedding 分离 |

### 4.4 监控什么

训练推荐模型时，以下指标能帮你判断优化器是否合适：

- **稀疏度**（FTRL）：Embedding 中绝对值 $< 10^{-6}$ 的参数比例。上线前通常要求 > 60%。
- **有效学习率**：per-layer 的 $\eta / \sqrt{v_t}$ 分位数（P10/P50/P90）。如果热门特征的 P50 有效 LR 降到初始 LR 的 1% 以下，可能需要重置或切换优化器。
- **梯度范数**：Embedding 层和 Dense 层的梯度范数比例。如果 Embedding 梯度范数远小于 Dense（< 0.01x），说明 Embedding 学不动，考虑提升 Embedding LR 或换 AdaGrad/FTRL。
- **AUC / Loss curve**：验证集 AUC 在训练后期（最后 20% steps）仍持续上升 0.0005 以上，说明 LR 衰减不充分或被 AdaGrad 单调收缩拖累。

---

## 五、大语言模型的优化器实战 ★

### 5.1 AdamW：一个参数的觉醒

**核心问题：Adam 中 L2 正则化不等于 Weight Decay。**

标准的 L2 正则化在损失函数上加 $\frac{\lambda}{2}\|\theta\|^2$，梯度变为 $g_t + \lambda\theta_t$。在 SGD 中，这等价于 Weight Decay：$\theta_{t+1} = (1-\eta\lambda)\theta_t - \eta g_t$。

但在 Adam 中，梯度 $g_t + \lambda\theta_t$ 会经过**自适应缩放** $\frac{1}{\sqrt{\hat{v}_t}}$。这意味着：一个参数的二阶矩估计 $\hat{v}_t$ 越大，它的 L2 正则化力度就越弱。正则化变得不均匀——频繁更新的参数（$\hat{v}_t$ 大）被正则化得更少，这恰恰和我们的意图背道而驰。

**AdamW 的解法——解耦**：把 Weight Decay 从梯度计算中彻底分离，直接加到参数更新步骤：

$$
\theta_{t+1} = \theta_t - \eta \cdot \left(\frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon} + \lambda \cdot \theta_t\right)
$$

Loshchilov & Hutter (2019) 的实验令人震惊：仅仅把 Weight Decay 从 Adam 更新式的分子搬到外面，就在 ImageNet 上带来了显著提升。这一改动现在已成为所有大模型训练的标准。

**GPT / LLaMA / Qwen 的标准配置：**

```python
# 大模型训练的经典优化器配置
optimizer = AdamW(
    params,
    lr=3e-4,           # 初始学习率
    betas=(0.9, 0.95), # β₂=0.95 而非默认 0.999（更短的二阶窗口）
    eps=1e-5,          # 不是默认 1e-8！
    weight_decay=0.1   # 看起来很大，实际上是合理的
)
```

**$\beta_2 = 0.95$ 而非 0.999 的原因**：大模型训练 step 数通常 100K~500K，$\beta_2=0.999$ 的窗口（~1000 步）太短，对 loss spike 过于敏感。0.95 的窗口（~20 步）让二阶估计更快响应梯度变化，训练更稳定。

**$\varepsilon = 10^{-5}$ 而非 $10^{-8}$ 的原因**：bfloat16 精度下，$\hat{v}_t$ 的小值噪声更大，$10^{-8}$ 太小起不到稳定作用。增大到 $10^{-5}$ 到 $10^{-3}$ 在很多大模型训练中能明显降低 loss spike 频率。

**weight_decay = 0.1 看起来很大**：解耦后的 Weight Decay 效果和 L2 正则的 $\lambda$ 完全不同。0.1 经 $\eta$ 缩放后，每次更新约衰减参数 0.003%（$3\times10^{-4} \times 0.1 = 3\times10^{-5}$），这是合理的。

### 5.2 梯度裁剪：大模型的安全阀

大模型训练中会突然出现 loss spike——某一步梯度范数爆炸（>100），更新后参数被打到极差的位置。原因可能是：长文本中的重复模式导致梯度累积、某层的数值不稳定、batch 内数据分布异常。

梯度裁剪是最简单有效的防御：

```python
# 按范数裁剪（标准做法）
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

`max_norm=1.0` 是经验默认值。太大会丧失保护效果，太小会减慢收敛。如果训练全程 loss spike 频率 > 1/1000 step，降到 0.5 试试。

### 5.3 Lion：进化的馈赠

Lion (EvoLved Sign Momentum) 是 Google 通过**进化搜索**发现的优化器，不是人为设计的：

$$
\begin{aligned}
u_t &= \beta_1 \cdot m_{t-1} + (1 - \beta_1) \cdot g_t \quad \text{（插值动量，不是 EMA！）} \\
\theta_{t+1} &= \theta_t - \eta \cdot \left(\text{sign}(u_t) + \lambda \cdot \theta_t\right)
\end{aligned}
$$

**极简**：
- 只需要符号，不需要梯度大小——省掉了整个二阶矩 $v_t$ 的存储
- 动量更新是插值（$\beta_1=0.9$），不是 EMA
- 推荐 $\beta_1=0.9$，$\beta_2=0.99$——注意和 Adam 完全不同

**内存节省**：AdamW 需要存 $m_t$ 和 $v_t$ 两份，Lion 只需要 $m_t$ 一份。对于一个 7B 模型，AdamW 的优化器状态占用 ~56GB（fp32），Lion 只需要 ~28GB——省了 50%。

**为什么符号梯度能行？** 对千亿参数模型而言，每个参数梯度的具体大小可能不如方向重要。Sign 相当于一个"极端归一化"，所有参数用同样的步长，让梯度的相对大小信息让位于梯度方向。在大模型的海量参数中，这种"民主化"可能反而减少了某些层主导训练的问题。

**局限性**：小模型（<1B）上 Lion 通常不如 AdamW。因为有足够的数据和参数时 AdamW 的二阶信息才有价值，小模型更需要精细的自适应。所以你的推荐模型的 Dense 层还是用 Adam，别换 Lion。

### 5.4 Sophia：二阶的诱惑

Adam 的一阶矩 $m_t$ 只是梯度的移动平均。Sophia 的核心想法：**如果能知道 Hessian 对角，就能做更好的预处理**。

Hessian 对角 $h_t = \text{diag}(H_t)$ 衡量每个参数上损失函数的**曲率**。曲率大的参数需要小步（容易 overshoot），曲率小的可以大步。

**问题**：Hessian 对角在千亿参数模型上没法精确算。Sophia 用 Hutchinson 方法做**无偏估计**：

$$
\hat{h}_t = g_t \odot \frac{H_t z}{\|z\|}
$$

其中 $z \sim \mathcal{N}(0, 1)$ 是随机向量。关键洞察：不需要 $H$ 本身，只需要 $H$ 作用在随机向量上的结果，而 $Hz = \nabla_\theta(g_t^\top z)$ 可以通过一次额外的反向传播得到。

更新规则：

$$
\theta_{t+1} = \theta_t - \eta \cdot \text{clip}\left(\frac{m_t}{\max(\hat{h}_t, \varepsilon)},\ \rho\right)
$$

$\rho$ 是 clip 阈值，防止单个 Hessian 估计的噪声破坏更新。没有 $\rho$ 的话，某个参数上 Hessian 估计过小会导致一次灾难性的大更新。

**效果**：LLM 预训练中，达到同等 loss 只需要 AdamW **一半的训练步数**。代价是每步多一次反向传播（用于计算 $Hz$），算力开销约 +30~50%。但总体 wall-clock 时间仍比 AdamW 快，且最终 loss 更优。

**局限**：额外的前向/反向开销在小模型上不值得；Hutchinson 估计有方差，小 batch 下不稳定。

---

## 六、两域对比总览

| 维度 | 推荐系统 | 大语言模型 |
|------|---------|-----------|
| **核心痛点** | 长尾稀疏特征学习不充分 | 训练不稳定 + 显存瓶颈 |
| **参数分布** | 99% Embedding（十亿级） | 99%+ Dense（百亿~万亿级） |
| **Embedding 优化器** | FTRL / AdaGrad | N/A |
| **Dense 优化器** | Adam | AdamW |
| **β₂ 典型值** | 0.999（默认） | 0.95（更短窗口防 spike） |
| **ε 典型值** | 1e-8 | 1e-5（bf16 稳定） |
| **Weight Decay** | 仅 Dense 层（可选） | 全局解耦，~0.1 |
| **学习率调度** | Constant 或 Step Decay | Warmup + Cosine Decay |
| **梯度裁剪** | 极少使用 | 必需，max_norm=1.0 |
| **混合策略** | 普遍（Embedding + Dense 分开） | 单一优化器 |
| **内存关注** | 不敏感（Embedding 参数在 CPU/PS 上） | 极度敏感（优化器状态占显存大头） |
| **稀疏化需求** | 极高（上线前压缩 Embedding 表） | 无 |

---

## 七、前沿探索

### 7.1 Schedule-Free：告别学习率调度

传统训练依赖手动设置的学习率衰减计划（Warmup + Cosine / Step / Linear）。Defazio et al. (2024) 提出的 Schedule-Free 方法**完全不需要学习率调度**。

核心思想：维护两组参数——在线参数（用于推理）和评估参数（用于梯度计算）。每次更新用两者的插值作为实际优化目标，等效于自动退火学习率。

实际效果：在多个 benchmark 上逼近甚至超过精心调度的 AdamW。如果未来成熟，将大幅简化训练流程。

### 7.2 二阶方法复兴

**Shampoo**：用层权重的 Kronecker 分解做预条件。对每个权重矩阵 $W \in \mathbb{R}^{m \times n}$，分别维护左预条件子 $L_t \in \mathbb{R}^{m \times m}$ 和右预条件子 $R_t \in \mathbb{R}^{n \times n}$，更新为 $W_{t+1} = W_t - \eta \cdot L_t^{-1/4} G_t R_t^{-1/4}$。

实际效果比 AdamW 好，但 $m, n$ 较大时 $L_t$ 和 $R_t$ 的计算和求逆开销不可忽略。Google 内部在一些大规模生产模型中使用。

**K-FAC (Kronecker-Factored Approximate Curvature)**：自然梯度下降的近似，用 Fisher 信息矩阵的 Kronecker 分解替代 Hessian。计算开销大，但在某些小到中等规模的模型上展现出极快收敛。

**为什么现在二阶方法复兴？** 大模型训练极其昂贵，如果额外的二阶计算能让训练步数减半，算力开销的 +30% 完全值得。Sophia 就是这一思路的最新代表。

### 7.3 低精度优化器

优化器状态（$m_t$ 和 $v_t$）通常以 fp32 存储，对于大模型是显存的大头：

| 场景 | 参数 (fp16) | 梯度 (fp16) | 优化器状态 (fp32) | 优化器占比 |
|------|-----------|-----------|-----------------|----------|
| 7B 模型 | 14 GB | 14 GB | 56 GB | 67% |
| 70B 模型 | 140 GB | 140 GB | 560 GB | 67% |

**8-bit Adam**：将 $m_t$ 和 $v_t$ 量化到 8-bit，显存从 56GB → 14GB，节省 75%。通过分块量化（block-wise quantization）保持动态范围，精度损失通常 < 0.1% 在最终 loss 上。

**4-bit 优化器 (QLoRA 场景)**：QLoRA 把预训练权重量化到 4-bit，LoRA 参数用 8-bit 优化器状态。这使得 65B 模型可以在单张 48GB GPU 上微调。

### 7.4 分布式优化器

当单卡装不下优化器状态时：

**ZeRO-1**：优化器状态分片到所有 GPU，每张卡只存 $1/N$ 的状态。通信开销小（all-reduce 梯度即可）。

**ZeRO-Offload**：优化器状态 offload 到 CPU 内存。CPU 做优化器更新，GPU 做前向/反向。PCIe 带宽是瓶颈，但比 OOM 强。

**ZeRO-Infinity**：进一步 offload 到 NVMe SSD。对于无法负担足够 GPU 的研究团队，这是训练大模型的唯一方式。

### 7.5 学习率调度新范式

**WSD (Warmup-Stable-Decay)**：在 Warmup 之后保持一段恒定的高 LR（Stable 阶段），然后快速衰减。Stable 阶段允许模型在高 LR 下探索更多模式，最后快速压缩到局部极小值。在部分 LLM 训练中表现优于 Cosine。

**Cyclic LR**：学习率周期性升降。在推荐模型训练中有时有用——Embedding 层在低 LR 阶段精调，高 LR 阶段探索新模式。

**Learned Optimizers (L2O)**：用一个小的神经网络来预测每个参数的更新量。VeLO (Google, 2023) 是第一个在多种任务上普遍有效的 L2O。但目前训练开销和泛化性仍不如 AdamW，离工业应用还有距离。

### 7.6 其他值得关注的方向

**SAM (Sharpness-Aware Minimization)**：不直接改优化器更新规则，而是修改优化的"目标"——刻意寻找损失平面上的**平坦极小值**。两次前向 + 一次反向（min-max 结构），泛化性更好。可以和 AdamW 组合使用（额外 ~2x 算力）。

**AdaFactor**：专门为超大模型设计的 Adam 变体，将二阶矩 $v_t$ 从 $m \times n$ 矩阵分解为 $m \times 1$ 和 $1 \times n$ 两个向量（秩一分解），显存从 $O(mn)$ 降到 $O(m+n)$。T5 和 PaLM 曾使用。

---

## 八、实战调参手册

### 8.1 推荐模型

**调参顺序（按优先级）：**

1. **先定架构**：混合策略还是单一？Embedding 是否需要上线稀疏？（需要 → FTRL，不需要 → AdaGrad）
2. **Embedding LR**：从 0.01 起，看前 1000 步的 loss 下降斜率。如果 < 0.1%/step，翻倍 LR。如果 loss 震荡 > 5% batch-to-batch，减半。
3. **Dense LR**：从 Embedding LR / 50 起。比如 Embedding LR=0.05，Dense LR 从 0.001 起。
4. **FTRL 超参**：先设 $\lambda_1=0, \lambda_2=0$，调 $\alpha$（控制整体 LR 规模）。然后加 $\beta$（通常设为 1 即可）。最后逐步加 $\lambda_1$ 到稀疏度目标和 AUC 的平衡点。
5. **验证**：看验证集 AUC 在最后 20% steps 是否还在涨。如果早停（提前 30% steps 就 plateau），说明 LR 衰减太快（AdaGrad 的 G_t 过大），换 RMSprop/Adam 或降低初始 LR。

**高频错误 5 条：**

1. **❌ Embedding 和 Dense 用同一个 LR，还纳闷冷门特征为啥学不动**
   → ✅ Embedding LR = Dense LR × 10~100

2. **❌ FTRL 的 $\lambda_1$ 一上来就设 0.01，结果模型稀疏度 99% 但 AUC 掉了 2%**
   → ✅ 从 0 开始，0.001 步进，观察稀疏度和 AUC 的 Pareto 曲线

3. **❌ 推荐模型的 Dense 层用 FTRL**
   → ✅ FTRL 为稀疏特征设计，Dense 层用 Adam。FTRL 在密集参数上的 L1 会乱杀有用权重

4. **❌ AdaGrad 训练很久后发现 Embedding 层参数几乎不再变化，以为收敛了**
   → ✅ 可能是 $G_t$ 太大导致 LR 趋零。检查有效 LR，如果 < 初始 1%，需要重置或换 RMSprop

5. **❌ 给 Embedding 层加 Weight Decay，效果下降**
   → ✅ Embedding 层的语义是"查表"，不应正则化。Weight Decay 只加在 Dense 层

### 8.2 大语言模型

**标准配方速查：**

```
优化器：AdamW
lr: 3e-4（从头训练）或 2e-5（微调）
betas: (0.9, 0.95)
eps: 1e-5（bf16）或 1e-8（fp32）
weight_decay: 0.1
gradient_clipping: 1.0（by norm）

LR Schedule:
  Warmup: 2000 steps（从头训练）或 100 steps（微调）
  Decay: Cosine to 10% of max LR
  Min LR: 3e-5（即为 1e-4 × 10%）

Batch size: 4M tokens（全局）
Precision: bf16 参数 + fp32 优化器状态
```

**高频错误 3 条：**

1. **❌ 微调时 weight_decay 还设 0.1 → 过拟合被过度抑制**
   → ✅ 微调 weight_decay: 0.01~0.05

2. **❌ $\beta_2$ 用默认 0.999 → bf16 下 loss spike 频率高**
   → ✅ bf16 训练用 $\beta_2 = 0.95$

3. **❌ 梯度裁剪设 max_norm=10.0 → 形同虚设，spike 来了照样炸**
   → ✅ max_norm=1.0，如果收敛没问题就不要放松

---

## 九、核心问题速答

**Q1: 推荐系统为什么不用 Adam 训练 Embedding？**

Adam 的二阶矩 $v_t$ 在稀疏梯度下估计极不稳定——一个 ID 每 10000 步才被采样一次，两次梯度之间的 9999 步 $v_t$ 都在衰减。当它终于被采样时，$\sqrt{\hat{v}_t}$ 可能已经衰减到一个很小的值，导致一次过大的更新，然后又被"遗忘"9999 步。AdaGrad 的累加式 $G_t$ 反而在这种场景下更稳定。

**Q2: AdamW 和带 L2 正则的 Adam 区别到底有多大？**

L2 在 Adam 里经过 $1/\sqrt{\hat{v}_t}$ 缩放，大 $\hat{v}_t$ 的参数（频繁更新）被正则化得更少，小 $\hat{v}_t$ 的参数（低频更新）被正则化得更多——恰好反了。AdamW 确保每个参数的 Weight Decay 力度均匀，对于 Transformer 这种所有参数更新频率相近的架构，这个修正不是微调，是根本性的修正。

**Q3: FTRL 为什么能产出稀疏模型而 Adam 不能？**

FTRL 的 per-coordinate 更新中有一个"零化区间"：当 $|z_{t,i}| \leq \lambda_1$ 时，$\theta_{t+1,i}$ 被**精确置零**（不是趋近于零）。Adam 的更新没有这个机制——L1 正则化的常数梯度被除以 $\sqrt{\hat{v}_t}$ 后力度不确定，加上动量积累，参数只会在零附近震荡而不会精确归零。

**Q4: 大模型训练为什么必须 Warmup？**

训练初期，$m_t$ 和 $v_t$ 从零初始化，偏差修正虽然让它们回到"正常尺度"但方向完全随机。前几十步的梯度方向极其不可靠。如果一开始就用全量 LR，一次方向错误的更新就能把参数打到极差的位置（尤其是深层 Transformer 对初始化极为敏感）。Warmup 用逐渐增大的 LR 给优化器一个"冷启动"窗口。

**Q5: Lion 比 AdamW 好在哪里？局限是什么？**

好处：内存省 50%（没有 $v_t$），训练速度略快（少一次逐元素运算）。局限：小模型（<1B 参数）上不如 AdamW；超参需要重新摸索（$\beta_1=0.9, \beta_2=0.99$，和 Adam 完全不同）；符号梯度的"极端归一化"在 batch size 较小（<256）时不稳定。

**Q6: Sophia 的二阶信息为什么能快两倍？**

Hessian 对角衡量曲率。在高曲率方向（损失面陡峭），Adam 可能会 overshoot 而被迫用小 LR；Sophia 用 $1/\hat{h}_t$ 自动在这一方向缩步长，允许整体 LR 更大而不震荡。等价于做了一个"曲率感知的归一化"，比 Adam 的纯一阶归一化 $\sqrt{\hat{v}_t}$ 更精确。

**Q7: 推荐模型的 Embedding LR 为什么比 Dense LR 大那么多？**

Embedding 参数每个 step 只有 batch 中出现的 ID 被更新。一个 1000 万用户的模型，batch size 4096，每个用户 step 平均只被采样 4096/1000 万 ≈ 0.04% 次。Dense 参数每个 step 都被更新。为了公平，Embedding LR 需要比 Dense LR 大约 $1/0.0004 ≈ 2500$ 倍。实际 10~100 倍已经是经验折中。

**Q8: 什么时候用 SGD 而不是 Adam？**

CV 任务（CNN 分类、检测、分割）中，SGD + Momentum 的泛化性常优于 Adam。但推荐系统和 NLP/LLM 几乎不需要考虑这个问题——前者需要自适应处理稀疏特征，后者需要 Adam 的稳定性和收敛速度。SGD 在这两个场景中都已被历史淘汰。

**Q9: Adam 的 $\varepsilon = 10^{-8}$ 从来不用改？**

float32 下确实几乎不需要改。但 bfloat16（大模型训练的默认精度）只有 7 位有效尾数，$\varepsilon = 10^{-8}$ 对 16 位表示来说太小，起不到防止除零的作用——在数值上已经被截断为零了。$10^{-5}$ 到 $10^{-3}$ 才是 bfloat16 下的合理范围。

**Q10: 混合精度训练下，优化器状态应该用什么精度？**

**永远用 fp32**。这是硬规则。参数和梯度可以用 fp16/bf16，但 $m_t$ 和 $v_t$ 必须 fp32，因为它们的更新涉及多次累加的小量（$(1-\beta)g_t$ 当 $\beta$ 接近 1 时非常小），fp16 会直接截断。8-bit Adam 等低精度优化器是这条规则的例外——它们有专门的量化策略来补偿精度损失。

---

## 十、选型速查

```
┌─ 你在训练什么？
│
├── 推荐模型
│   ├── Embedding 层（十亿级稀疏 ID）
│   │   ├── 需要上线稀疏化 ──→ FTRL（α=0.005, β=1, λ₁ 从 0 逐步加）
│   │   └── 不稀疏也能接受 ──→ AdaGrad（η=0.01）
│   │
│   ├── Dense 层（MLP / Attention）
│   │   └── Adam（η=0.0001~0.001, β₁=0.9, β₂=0.999）
│   │
│   └── Embedding LR 设为 Dense LR 的 10~100 倍
│
├── 大语言模型（预训练）
│   └── AdamW（η=3e-4, β₁=0.9, β₂=0.95, ε=1e-5, wd=0.1）
│       + Warmup 2000 steps + Cosine to 10%
│       + Gradient Clip 1.0
│       + bf16 参数 + fp32 优化器状态
│
├── 大语言模型（微调 / SFT）
│   └── AdamW（η=2e-5, β₁=0.9, β₂=0.95, ε=1e-5, wd=0.01）
│       + Warmup 100 steps + Cosine to 10%
│
├── 大语言模型（显存极度紧张）
│   └── Lion（省 50% 优化器显存）或 8-bit Adam（省 75%）
│
└── CV 分类/检测
    └── SGD + Momentum（η=0.1, β=0.9）+ Step Decay
```

---

> **参考论文**：
> - Sutskever et al., 2013 — "On the importance of initialization and momentum in deep learning"（Momentum 经典）
> - Duchi et al., 2011 — "Adaptive Subgradient Methods"（AdaGrad）
> - Kingma & Ba, 2015 — "Adam: A Method for Stochastic Optimization"
> - McMahan et al., 2013 — "Ad Click Prediction: a View from the Trenches"（FTRL, Google）
> - Loshchilov & Hutter, 2019 — "Decoupled Weight Decay Regularization"（AdamW）
> - Chen et al., 2023 — "Symbolic Discovery of Optimization Algorithms"（Lion）
> - Liu et al., 2023 — "Sophia: A Scalable Stochastic Second-order Optimizer for Language Model Pre-training"
> - Defazio et al., 2024 — "Schedule-Free Learning"
