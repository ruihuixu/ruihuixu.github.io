---
title: "激活函数全景：从 Sigmoid 到 GELU 的演进与对比"
date: 2026-06-17T10:00:00+08:00
draft: false
slug: "activation-functions"
tags:
  - "激活函数"
categories:
  - "Deep Learning"
math: true
description: "全面对比 Sigmoid、Tanh、ReLU、Leaky ReLU、PReLU、ELU、SELU、GELU、SiLU、Mish、Softplus 的定义、公式、导数、优缺点及适用场景，覆盖梯度消失、Dead Neuron、自归一化等核心问题。"
---

> **关键词**：激活函数、梯度消失、Dead Neuron、自归一化、GELU、SiLU/Swish
>
> **涵盖**：Sigmoid / Tanh / ReLU / Leaky ReLU / PReLU / ELU / SELU / GELU / SiLU / Mish / Softplus

---

## 一、为什么需要激活函数

没有激活函数，多层网络等价于单层线性变换。激活函数引入**非线性**，使网络具备通用逼近能力。

核心诉求：

- **非线性**：万能逼近定理的必要条件
- **可微**：支持反向传播
- **计算高效**：前向 + 反向都要快
- **缓解梯度消失**：导数不能持续趋近于 0
- **输出有界/零中心**：利于训练稳定

---

## 二、逐一定义与公式

### 2.1 Sigmoid

$$
\sigma(x) = \frac{1}{1 + e^{-x}}
$$

**导数**：$\sigma'(x) = \sigma(x)(1 - \sigma(x))$

| 优点 | 缺点 |
|------|------|
| 输出 (0, 1)，可解释为概率 | 饱和区梯度 ≈ 0，导致**梯度消失** |
| 平滑可微 | 输出非零中心（全正），导致 zig-zag 更新 |
| 有界输出，防止数值爆炸 | `exp()` 运算开销大 |

**适用场景**：二分类输出层、门控机制（LSTM/GRU 的门）

---

### 2.2 Tanh

$$
\tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}} = 2\sigma(2x) - 1
$$

**导数**：$\tanh'(x) = 1 - \tanh^2(x)$

| 优点 | 缺点 |
|------|------|
| 输出 (-1, 1)，**零中心** | 同样存在饱和区梯度消失 |
| 梯度比 Sigmoid 更大（导数最大为 1 vs 0.25） | 仍含 `exp()`，计算开销大 |

**适用场景**：RNN/LSTM 的隐藏状态激活（配合 Sigmoid 门控）

---

### 2.3 ReLU

$$
\text{ReLU}(x) = \max(0, x)
$$

**导数**：

$$
\text{ReLU}'(x) = \begin{cases} 1 & x > 0 \\ 0 & x \leq 0 \end{cases}
$$

| 优点 | 缺点 |
|------|------|
| **计算极简**：仅需 `max(0,x)` | **Dead Neuron**：负半区梯度恒为 0，神经元永久失效 |
| 正半区导数恒为 1，**缓解梯度消失** | 输出非零中心 |
| 稀疏激活（约 50% 神经元激活），利于表示学习 | 无界输出，可能数值爆炸 |

> **Dead Neuron 成因**：学习率过大导致权重更新后神经元对所有输入均输出负值，或偏置初始化为较大负值。

**适用场景**：CNN、MLP 的默认首选（ResNet、VGG 等经典架构均用 ReLU）

---

### 2.4 Leaky ReLU

$$
\text{LeakyReLU}(x) = \max(\alpha x, x) = \begin{cases} x & x > 0 \\ \alpha x & x \leq 0 \end{cases}
$$

其中 $\alpha$ 为小的正常数（默认 $\alpha = 0.01$）。

**导数**：

$$
\text{LeakyReLU}'(x) = \begin{cases} 1 & x > 0 \\ \alpha & x \leq 0 \end{cases}
$$

| 优点 | 缺点 |
|------|------|
| 负半区保留小梯度，**缓解 Dead Neuron** | $\alpha$ 需手动设定 |
| 保持 ReLU 的正半区优势 | 实际效果并不总是优于 ReLU |

---

### 2.5 PReLU (Parametric ReLU)

$$
\text{PReLU}(x) = \begin{cases} x & x > 0 \\ \alpha x & x \leq 0 \end{cases}
$$

形式同 Leaky ReLU，但 $\alpha$ **是可学习参数**，通过反向传播更新。

| 优点 | 缺点 |
|------|------|
| $\alpha$ 由数据自动学习 | 参数量增加（每个通道一个 $\alpha$） |
| 在 ImageNet 上首次超越人类水平（何恺明 ResNet 使用） | 在大规模模型中使用较少 |

---

### 2.6 ELU (Exponential Linear Unit)

$$
\text{ELU}(x) = \begin{cases} x & x > 0 \\ \alpha(e^x - 1) & x \leq 0 \end{cases}
$$

其中 $\alpha > 0$（默认 $\alpha = 1$）。

**导数**：

$$
\text{ELU}'(x) = \begin{cases} 1 & x > 0 \\ \alpha e^x = \text{ELU}(x) + \alpha & x \leq 0 \end{cases}
$$

| 优点 | 缺点 |
|------|------|
| 负半区输出**趋近于零中心**，加速收敛 | `exp()` 计算开销较大 |
| 连续可微，负半区平滑过渡 | 对输入尺度敏感 |
| 输出均值更接近 0，缓解 bias shift | 无 Dead Neuron 但可能 "saturated neuron" |

---

### 2.7 SELU (Scaled ELU)

$$
\text{SELU}(x) = \lambda \begin{cases} x & x > 0 \\ \alpha e^x - \alpha & x \leq 0 \end{cases}
$$

其中 $\alpha \approx 1.6733$，$\lambda \approx 1.0507$（由数学推导确定）。

**核心特性**：**自归一化**（Self-Normalizing）—— 在特定条件下（LeCun 初始化、全连接网络），输出自动趋近均值 0、方差 1，无需 BatchNorm。

| 优点 | 缺点 |
|------|------|
| 训练极深网络时无需 BatchNorm | 对初始化和网络结构有严格约束 |
| 理论保证的方差稳定 | CNN/RNN 中效果不如 MLP |

**适用场景**：深度全连接网络（尤其表格数据）

---

### 2.8 GELU (Gaussian Error Linear Unit)

$$
\text{GELU}(x) = x \cdot \Phi(x) = x \cdot \frac{1}{2}\left[1 + \text{erf}\left(\frac{x}{\sqrt{2}}\right)\right]
$$

其中 $\Phi(x)$ 是标准正态分布的累积分布函数 (CDF)。

**常用近似**：

$$
\text{GELU}(x) \approx 0.5x\left(1 + \tanh\left[\sqrt{\frac{2}{\pi}}\left(x + 0.044715x^3\right)\right]\right)
$$

**导数**（精确形式）：

$$
\text{GELU}'(x) = \Phi(x) + x \cdot \phi(x)
$$

其中 $\phi(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$ 是标准正态 PDF。

| 优点 | 缺点 |
|------|------|
| **随机正则化效果**：概率性地"关掉"神经元 | 计算复杂度高于 ReLU |
| 处处可微，平滑过渡 | 近似版本含 `tanh`，仍有一定开销 |
| 在 NLP 大规模模型中表现优异 | 非零中心 |

> **直观理解**：GELU = 输入 × 输入被"选中"的概率。服从正态分布的输入，正值大概率保留，负值大概率抑制，符合直觉。

**适用场景**：Transformer 系（BERT、GPT、ViT 等均使用 GELU）

---

### 2.9 SiLU / Swish

$$
\text{SiLU}(x) = x \cdot \sigma(x) = \frac{x}{1 + e^{-x}}
$$

Swish 是 Google 提出的同名函数（含可学习 $\beta$：$x \cdot \sigma(\beta x)$），SiLU 是 PyTorch 中的标准命名。

**导数**：

$$
\text{SiLU}'(x) = \sigma(x) + x \cdot \sigma(x)(1 - \sigma(x)) = \sigma(x)(1 + x(1 - \sigma(x)))
$$

| 优点 | 缺点 |
|------|------|
| 处处可微且**非单调**（有极小负值谷底） | 计算含 `exp()` 和乘法 |
| 无界上有界下（下界 ≈ −0.28） | 比 ReLU 慢约 2-3 倍 |
| 自门控特性：$\sigma(x)$ 充当软门 | |

> **非单调性**：SiLU 在 x ≈ −1.28 处有全局最小值 ≈ −0.28。这允许小的负输出，在某些任务中比零输出的 ReLU 更好。

**适用场景**：EfficientNet、MobileNetV3、YOLO 系列、最新的 ViT 变体

---

### 2.10 Mish

$$
\text{Mish}(x) = x \cdot \tanh(\text{softplus}(x)) = x \cdot \tanh(\ln(1 + e^x))
$$

| 优点 | 缺点 |
|------|------|
| 平滑、非单调、无界上有界下 | 计算开销最大（含 `exp`、`ln`、`tanh`） |
| 在多个 benchmark 上略优于 ReLU 和 Swish | 实际收益有限，未广泛采用 |
| 自门控 + 自正则化特性 | 推理速度慢 |

**适用场景**：YOLOv4 中使用，部分视觉任务

---

### 2.11 Softplus

$$
\text{Softplus}(x) = \ln(1 + e^x)
$$

**导数**：$\text{Softplus}'(x) = \sigma(x)$

| 优点 | 缺点 |
|------|------|
| ReLU 的平滑近似 | 饱和区梯度消失 |
| 处处可微 | 几乎总被 ReLU 替代 |

**适用场景**：需要平滑 ReLU 的场景（如变分自编码器的方差参数）

---

## 三、对比总览

| 函数 | 公式 | 值域 | 零点 | 单调 | 平滑 | 计算开销 |
|------|------|------|------|------|------|----------|
| Sigmoid | $\frac{1}{1+e^{-x}}$ | (0, 1) | 0.5 | ✓ | ✓ | 中 |
| Tanh | $\frac{e^x-e^{-x}}{e^x+e^{-x}}$ | (−1, 1) | 0 | ✓ | ✓ | 中 |
| **ReLU** | $\max(0,x)$ | [0, +∞) | 0 | ✓ | ✗ | **极低** |
| Leaky ReLU | $\max(0.01x, x)$ | (−∞, +∞) | 0 | ✓ | ✗ | 极低 |
| PReLU | $\max(\alpha x, x)$ | (−∞, +∞) | 0 | ✓ | ✗ | 极低 |
| ELU | $x>0:\ x,\ x\leq0:\ \alpha(e^x-1)$ | (−α, +∞) | ≈0 | ✓ | ✓ | 高 |
| SELU | $\lambda \cdot \text{ELU}$ | (−λα, +∞) | ≈0 | ✓ | ✓ | 高 |
| **GELU** | $x\cdot\Phi(x)$ | (−∞, +∞) | 0 | ✓ | ✓ | 中 |
| **SiLU** | $x\cdot\sigma(x)$ | [≈−0.28, +∞) | 0 | **✗** | ✓ | 中 |
| Mish | $x\cdot\tanh(\ln(1+e^x))$ | [≈−0.31, +∞) | 0 | **✗** | ✓ | 高 |
| Softplus | $\ln(1+e^x)$ | (0, +∞) | ≈0.69 | ✓ | ✓ | 中 |

---

## 四、选型建议

```
视觉任务 (CNN/MLP)
├── 默认首选：ReLU（简单高效，经大量验证）
├── 需要自归一化：SELU（适合深层全连接，免除 BN）
├── 追求极致性能：SiLU（EfficientNet/YOLO 路线）
└── 轻量 mobile 模型：ReLU6 → Hard-Swish（量化友好）

NLP / Transformer
├── 默认首选：GELU（BERT/GPT/ViT 的事实标准）
├── 新兴替代：SiLU（部分 ViT 变体、LLaMA 使用）
└── 不要用：ReLU（Transformer 中表现显著劣于 GELU）

RNN / LSTM
├── 门控：Sigmoid（有界 (0,1)，天然适合门控机制）
├── 隐状态：Tanh（零中心，配合门控使用）
└── 替代方案：SiLU 搭配 LayerNorm

输出层
├── 二分类：Sigmoid
├── 多分类：Softmax（不是严格意义上的激活函数，但在输出层起类似作用）
├── 回归（正值）：Softplus / ReLU
└── 回归（无界）：Identity / 无激活
```

---

## 五、核心问题速答

**Q1: 为什么 ReLU 在 Transformer 中不如 GELU？**

GELU 的平滑概率性门控与 Transformer 的自注意力机制更适配。ReLU 的硬阈值在注意力权重计算中会丢失细粒度信息，而 GELU 的「软 dropout」效应天然提供正则化。

**Q2: SiLU 和 GELU 怎么选？**

两者形状高度相似（见下图）。GELU 在 NLP 预训练中占主导，SiLU 在视觉和高效架构中更常见。实验差异通常小于 0.5%，两者可互相替代。

**Q3: Dead Neuron 如何检测和缓解？**

- **检测**：统计训练中每层输出为 0 的神经元比例，若持续 > 80% 则存在问题
- **缓解**：降低学习率、使用 Leaky ReLU / ELU、改善权重初始化（He 初始化）

**Q4: 激活函数对梯度消失的影响？**

Sigmoid/Tanh 的饱和区导数为 0，深层网络中梯度连乘趋近于 0。ReLU 族解决了正半区问题，GELU/SiLU 进一步平滑了过渡区。配合 BatchNorm/LayerNorm + 残差连接，基本消除梯度消失。
