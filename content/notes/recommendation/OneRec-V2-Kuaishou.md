---
title: "OneRec-V2: 快手 Lazy Decoder-Only 生成式推荐架构"
date: 2026-03-24
published: 2025-01-01
tags:
  - "Generative Recommendation"
  - "Decoder-Only"
  - "Preference Alignment"
description: "快手 Lazy Decoder-Only 架构，计算量减少 94%，基于真实用户反馈的偏好对齐"
---

## 📌 一句话总结

**OneRec-V2 是快手提出的 Lazy Decoder-Only 生成式推荐架构**，针对 OneRec-V1 的 Encoder-Decoder 架构计算效率低、RL 依赖 Reward 模型受限于采样与 reward hacking 问题，通过消除 Encoder 瓶颈和简化交叉注意力机制，将计算量减少 94%、训练资源降低 90%，支持 0.5B→8B 参数扩展，在快手主站带来 APP 使用时长 +0.54%、极速版 +1.24% 的显著收益。

## ❓ 问题背景

### 2.1 OneRec-V1 的两大瓶颈

1. **计算资源分配失衡** - Encoder 处理超长用户行为序列，97.66% 的计算消耗在 Context Encoding 而非 Target Item 生成，极大限制了模型的扩展能力
2. **RL 依赖 Reward 模型的两类问题**：
   - **采样效率低** - Reward 模型引入额外计算开销，只能采样部分用户近似计算
   - **Reward Hacking** - 模型可能利用奖励函数缺陷获取高奖励，而未学到预期行为

### 2.2 核心挑战

1. **如何消除 Encoder 瓶颈** - 将 97.66% 的计算资源重新分配到产生梯度信号的部分
2. **如何直接使用真实用户反馈** - 避免 Reward Hacking，使策略更好地对齐用户偏好

## 💡 方法框架

### 3.1 核心贡献

1. **Lazy Decoder-Only 架构** - 消除 Encoder 瓶颈，简化 Cross Attention，计算量减少 94%，训练资源降低 90%，支持 0.5B→8B 扩展
2. **基于真实用户反馈的偏好对齐** - 时长感知 Reward 缓解视频时长偏差；提出 GBPO 算法，通过自适应梯度约束稳定策略优化

### 3.2 总体架构

```
New Impression Only 样本组织 → Context Processor → Lazy Decoder Block → 偏好对齐
```

### 3.3 样本组织形式

| 方式 | 特点 | 问题 |
|------|------|------|
| User-Centric | 每用户一条样本 | 时序泄漏、流行度偏差，难适配增量更新 |
| Naive Impression | 按时序曝光预测 | 存在重复计算 |
| New Impression Only（本文采用） | 按曝光组织，仅在 Target Item 上做 NTP | 无信息泄漏，支持增量/流式更新 |

### 3.4 Lazy Decoder-Only 架构

**训练开销分析：**

| 组件 | 占比 | 问题 |
|------|------|------|
| Context Encoding | 97.66% | Encoder 转换 + Cross Attention 的 KV 投影，不直接参与 Loss 计算 |
| Target Decoding | 极低 | Self Attention + FFN + Cross Attention 的 QO 变换，直接参与 Loss 计算 |

**核心矛盾：** 绝大部分算力消耗在不产生梯度信号的编码阶段

### 3.5 Context Processor

将异构用户特征（静态特征、短期行为、长期行为）经小 FC 对齐后，输出统一表示供 Decoder 使用。

**输出维度：**
```
d_context = S_kv · L_kv · G_kv · d_head
```

| 参数 | 含义 |
|------|------|
| S_kv | K/V 共享策略（1=共享，2=分离） |
| L_kv | Decoder 层间 KV 分组共享数 |
| G_kv | Multi-head 注意力分组数 |
| d_head | 每个注意力头的维度 |

**实验结论：** 三者影响极小，均可设为 1，即 `d_context = d_head`，最大程度共享以减少 FLOPs。

### 3.6 Lazy Decoder Block

Decoder 输入为 `h^(0) = Embed([BOS, s^1, s^2])`，经 N_layer 层处理，每层包含：

1. **Cross Attention（简化版）** - 去掉 K/V 的 FC 投影，令 `v_l = k_l`（等价于 Target Attention），不同层共享 KV
2. **Self Attention** - 标准自注意力捕捉语义 token 间依赖
3. **FFN** - 深层替换为 DeepSeekMoE，大幅扩展参数量同时维持计算效率

**训练损失：**
```
L_Gen = -1/3 · Σ log p(s^i | BOS, s^<i, Context)
```

### 3.7 架构实验结论

- 同参数规模下，Lazy Decoder-Only 的 FLOPs 不到其他架构的 1/10
- S_kv、L_kv、G_kv 不同取值下 Loss 几乎无差异，验证全共享策略可行
- MoE 架构扩展优势明显，Scaling Law 曲线良好

## 🎯 基于用户反馈的偏好对齐

### 4.1 时长感知 Reward 重构

**问题：** 播放时长与 APP Stay Time 和 LT7 直接相关，但受视频本身时长影响存在偏差

**解决方案：** 按视频时长分桶，仅播放时长处于对应桶 Top25% 分位的才算正样本

**Reward 定义：**
```
A_i = +1,  if q_i > τ_B and neg_i = 0
A_i = -1,  if neg_i = 1
A_i = 0,   otherwise
```

### 4.2 ECPO 的问题

OneRec-V1 的 ECPO 对负优势样本做了梯度截断，但梯度 ∝ 1/π_θ，当 π_θ 很小时：

| 样本类型 | 小概率后果 | 评价 |
|----------|------------|------|
| 正样本 | 小概率→大梯度 | ✅ 有提升空间，合理 |
| 负样本 | 小概率→大梯度 | ❌ 抑制空间小，易过拟合甚至崩溃 |

**结论：** 基于截断的方式无法根本解决梯度不稳定问题

### 4.3 GBPO 算法

**公式：**
```
J_GBPO(θ) = -E[1/G · Σ (π_θ(o_i|u) / π'_θ_old(o_i|u)) · A_i]
```

**核心改进：**

1. **去掉 Clip 操作** - 保留所有样本梯度，促进多样化探索，无 No Gradient 区间
2. **动态梯度约束（Dynamic Bound）** - 用 BCE 损失梯度约束 RL 梯度
   - 对负样本，概率越小梯度越小，天然防止梯度爆炸

**两大优点：** 全样本利用 + 有界梯度稳定

### 4.4 RL 实验结论

- 使用 OneRec 自身样本替代传统精排模型采样，几乎所有指标打正
- 纯用户反馈信号优于纯 Reward 模型，混合信号进一步提升

## 📊 实验验证

### 线上 A/B 实验

| 配置 | 数值 |
|------|------|
| 参数 | 1B |
| 上下文长度 | 3K |
| Beam Size | 512 |
| 时延 | 36ms |
| MFU | 62% |

### 业务指标

| 场景 | 指标 | 提升 |
|------|------|------|
| 快手主站 | APP Stay Time | +0.54% |
| 快手极速版 | APP Stay Time | +1.24% |
| 全场景 | 7 日留存 | 显著提升 |

### 效率对比

| 指标 | 对比 |
|------|------|
| 计算量 | 减少 94% |
| 训练资源 | 减少 90% |
| 参数扩展 | 0.5B → 8B |

### 不足

- 冷启视频曝光下降 36%~44%，对内容生态不太友好

## 🔍 对比与思考

### OneRec-V1 vs OneRec-V2

| 维度 | V1 | V2 |
|------|----|----|
| 架构 | Encoder-Decoder | Lazy Decoder-Only |
| 计算效率 | 97.66% 用于编码 | 计算量减少 94% |
| 训练资源 | - | 减少 90% |
| RL 对齐 | ECPO（梯度截断） | GBPO（动态约束） |

### 核心洞察

1. **Lazy Decoder-Only 架构** - 消除 Encoder 瓶颈是生成式推荐扩展的关键
2. **Context Processor 简化** - 最大程度共享 KV 表示，减少 FLOPs
3. **GBPO 算法** - 全样本利用 + 有界梯度稳定，避免 ECPO 的梯度不稳定问题
4. **冷启动挑战** - 生成式推荐在新内容曝光上仍有改进空间
