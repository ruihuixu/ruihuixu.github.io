---
title: "TokenMixer-Large: 字节 15B 参数大规模推荐架构"
date: 2026-03-24
published: 2025-01-01
tags:
  - "Discriminative Recommendation"
  - "Token Mixer"
  - "MoE"
description: "字节跳动 15B 参数大规模推荐架构，RankMixer 的系统性演进版本"
---

## 📌 一句话总结

**TokenMixer-Large 是 RankMixer 的大规模演进版本**，通过 Mixing & Reverting 残差对齐、Inter-Residual + Aux Loss 深层稳定性设计、Sparse-PerToken MoE 稀疏训练，将最大参数规模从 1B 扩展至 15B，MFU 从 45% 提升至 60%，在电商场景带来订单量 +1.66%、人均预览支付 GMV +2.98% 的显著收益。

## ❓ 问题背景

### 2.1 RankMixer 的成功与局限

**成功：**
- 替换自注意力为轻量 Token 混合，平衡效果与效率
- MFU 从 4.5% 提升至 45%，实现 70 倍参数扩展

**局限（深层配置时的五大瓶颈）：**
1. **次优残差设计** - 混合前后 Token 直接相加，语义不对齐
2. **模型架构不纯** - 保留大量碎片化算子（LHUC、DCNv2 等）
3. **深层模型梯度更新不足** - 通常仅 2 层，加深后训练不稳定
4. **MoE 稀疏化不充分** - "稠密训练，稀疏推理"，训练成本未降低
5. **规模探索有限** - 仅扩展到约 1B 参数

### 2.2 TokenMixer-Large 目标

1. 扩展到 7B（在线）/ 15B（离线）参数规模
2. 解决深层训练稳定性问题
3. 实现"稀疏训练，稀疏推理"

## 💡 方法框架

### 3.1 核心贡献

1. **Mixing & Reverting 操作** - 双层对称设计，确保输入输出维度一致，实现跨层残差连接的语义对齐
2. **深层训练稳定性设计** - Inter-Residual 跨层残差、Auxiliary Loss 辅助损失、Down-Matrix Small Init 小初始化
3. **Sparse-PerToken MoE 升级** - 从"稠密训练，稀疏推理"升级为"稀疏训练，稀疏推理"
4. **纯模型设计** - 移除碎片化算子，MFU 从 45% 提升至 60%

### 3.2 总体架构

```
输入 X ∈ R^(T×D) → Mixing → H ∈ R^(H×T·D/H) → Reverting → X_revert ∈ R^(T×D) → 残差连接 → 输出
```

### 3.3 Mixing & Reverting 操作

**核心思想：** 双层对称设计，第一层混合，第二层恢复维度

```
输入 X ∈ R^(T×D)
  ↓
Mixing → H ∈ R^(H×T·D/H)  ← 混合信息
  ↓
Reverting → X_revert ∈ R^(T×D)  ← 恢复原始维度
  ↓
残差连接：X_revert + X  ✅ 语义对齐
```

**优势：**
- 输入输出维度严格一致
- 残差连接语义对齐
- 支持深层网络稳定训练

### 3.4 深层训练稳定性设计

**1. Inter-Residual（跨层残差）：**
```
Layer 1 → Layer 2 → Layer 3 → Layer 4
   │                        ↑
   └────────────────────────┘
每 2-3 层添加跨层残差，增强低层到高层的信息流
```

**2. Auxiliary Loss（辅助损失）：**
- 低层输出 logits + 高层输出 logits → 联合损失
- 让低层学习"估计高层特征偏差"
- 防止低层参数训练不充分

**3. Down-Matrix Small Init：**
- SwiGLU 的 FCdown 初始化标准差从 1 降至 0.01
- 早期训练接近恒等映射 F(x)+x ≈ x
- 缓解 SwiGLU 中 up×gate 的数值爆炸问题

**4. Pre-Norm 替代 Post-Norm：**
- Post-Norm 易梯度爆炸 → Pre-Norm 稳定训练

**消融实验结果：**

| 配置 | AUC 变化 |
|------|----------|
| w/o Inter-Residual & AuxLoss | -0.04% |
| w/o Down-Matrix Small Init | -0.03% |

### 3.5 Sparse-PerToken MoE

**RankMixer (ReLU-MoE) 的问题：**
- 训练模式：Dense Train, Sparse Infer
- 训练成本未降低（所有参数都更新）
- 推理时激活专家数不确定（需截断策略）
- 需要 DTSI 策略（训练时降低阈值，推理时提高）
- 训练 - 推理不一致

**TokenMixer-Large (Sparse-PerToken MoE) 的解决方案：**
- 训练模式：Sparse Train, Sparse Infer ✅
- 路由：Softmax + Top-K（统一范式）

**创新设计：**

1. **Gate Value Scaling：** α = 1/稀疏比
   - 1:2 稀疏 → α=2
   - 1:4 稀疏 → α=4
   - 补偿稀疏导致的梯度更新不足

2. **Shared Expert：** 每 Token 的共享专家（非全局）
   - 始终激活，保证稳定性
   - 无需额外负载均衡损失

3. **First Enlarge, Then Sparse 策略：**
   - 先设计最优稠密模型
   - 再稀疏化获取效率收益

**效果：** 1:2 稀疏下性能与稠密模型相当（AUC -0.00%），训练成本降低 50%，推理成本降低 50%

### 3.6 纯模型设计

**RankMixer (混合架构) 的问题：**
- 保留历史迭代的碎片化算子：DCNv2、LHUC 等
- 内存访问密集（Memory-Bound）
- 计算强度低，降低整体 MFU

**TokenMixer-Large (纯模型) 的解决方案：**
- 移除所有碎片化算子
- 仅保留 Parameterless Mixing & Reverting
- 仅保留 GroupedGemm（高计算强度）

**DCN 收益随规模递减：**

| 参数规模 | DCN 收益 |
|----------|----------|
| 150M | +0.09% |
| 500M | +0.04% |
| 700M | +0.00% |

### 3.7 工程优化

**1. 高性能算子：**
- MoEPermute：Batch-first → Expert-first
- MoEGroupedFFN：单 Kernel 计算所有专家 FFN
- MoEUnpermute：加权汇总专家输出

**2. FP8 量化：**
- 推理时 FP8 E4M3 量化，训练保持 BF16
- 1.7x 推理加速，精度无损失

**3. Token Parallel：**
- 专为 PerToken 操作设计的模型并行策略
- 通信步骤从 4L 降至 2L+1（L 为层数）
- 4 路并行 + 计算通信重叠 → 96.6% 吞吐提升

## 📊 实验验证

### 离线实验 (AUC 提升)

| 场景 | 规模 | ΔAUC | 参数量 |
|------|------|------|--------|
| Feed Ads | 15B | +1.20% | 7.6B 稠密 |
| E-Commerce | 7B | +1.14% | 4.6B 稠密 |
| Live Stream | 4B | +1.14% | 2.3B 激活/4.6B 总 |

### 在线实验 (业务指标)

| 场景 | 指标 | 提升 |
|------|------|------|
| 电商 | 订单量 | +1.66% |
| 电商 | 人均预览支付 GMV | +2.98% |
| 广告 | ADSS | +2.0% |
| 直播 | 收入 | +1.4% |

### 相同参数量下对比 (~500M)

| 模型 | ΔAUC | Params | FLOPs/Batch |
|------|------|--------|-------------|
| RankMixer | +0.84% | 567M | 4.6T |
| TokenMixer-Large | +0.94% | 501M | 4.2T |
| 提升 | +0.10% | -12% | -9% |

### 规模扩展能力

| 模型 | 最大参数 | 最大层数 | MFU |
|------|----------|----------|-----|
| RankMixer | 1B | 2-4 层 | ~45-50% |
| TokenMixer-Large | 15B | 24+ 层 | ~60% |

## 🔍 对比与思考

### TokenMixer-Large vs RankMixer 详细对比

| 维度 | RankMixer | TokenMixer-Large | 改进幅度 |
|------|-----------|------------------|----------|
| 最大参数规模 | 1B | 15B | 15x |
| 层数 | 2-4 层 | 24+ 层 | 6x+ |
| MFU | ~45-50% | ~60% | +10-15% |
| 残差对齐 | ❌ 语义不对齐 | ✅ Mixing&Reverting | 关键改进 |
| 深层稳定 | ❌ 无专门设计 | ✅ Inter-Residual+AuxLoss | 关键改进 |
| MoE 训练 | 稠密训练 | 稀疏训练 | 成本 -50% |
| 模型纯度 | 混合架构 | 纯模型 | MFU +15% |
| 归一化 | LayerNorm+Post | RMSNorm+Pre | 吞吐 +8.4% |
| 初始化 | 标准 Xavier | Down-Matrix Small | AUC +0.03% |

### 核心洞察

1. **系统性解决瓶颈** - TokenMixer-Large 不是推翻 RankMixer，而是系统性地解决了 RankMixer 在大规模扩展时的关键瓶颈
2. **继承的设计** - Token Mixer 核心机制、Per-Token 架构思想、MoE 扩展方向
3. **改进的设计** - 残差连接、深层稳定性、MoE 训练模式、模型纯度、归一化与初始化

### 本质

TokenMixer-Large 是 RankMixer 的**工业级大规模演进版本**，专为 10B+ 参数场景设计！
