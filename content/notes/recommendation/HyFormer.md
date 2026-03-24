---
title: "HyFormer: 字节统一混合 Transformer 架构"
date: 2026-03-24
tags:
  - "Discriminative Recommendation"
  - "Transformer"
  - "Long Sequence"
description: "字节跳动统一混合 Transformer 架构，Query Decoding+Boosting 交替优化"
---

## 📌 一句话总结

**HyFormer 是字节跳动提出的统一混合 Transformer 架构**，通过 Query Decoding + Query Boosting 交替优化机制，将长序列建模与异构特征交互统一至单一骨干网络，实现双向信息流，在相同参数量和 FLOPs 下 AUC 提升 +0.17%，在线 A/B 测试带来人均观看时长 +0.293%、视频完播数 +1.111% 的显著收益。

## ❓ 问题背景

### 2.1 工业大推荐模型扩展的两大挑战

1. **严格的效率约束** - 必须满足 <50ms 端到端延迟，支持百万级 QPS，长序列建模和特征交互需在有限计算预算下完成
2. **现有架构的解耦设计局限** - "先长序列建模，后异构特征交互"的两阶段流水线（如 LONGER+RankMixer）在序列长度和模型容量持续增加时暴露出根本性限制

### 2.2 传统两阶段范式的三大问题

1. **Query 表示过于简化** - Query Token 仅来自有限的候选相关特征或全局特征子集，限制长期用户兴趣建模
2. **交互发生阶段过晚** - 序列压缩 Token 与异构非序列 Token 的交互仅在模型后期发生，跨特征推理被推迟
3. **扩展效率低下** - 增加模型容量或序列长度主要改进孤立组件而非联合表示，性能提升增速放缓

## 💡 方法框架

### 3.1 核心贡献

1. **Query Decoding 机制** - 将非序列特征扩展为全局 Token，在长行为序列的层间 Key-Value 表示上进行长序列解码
2. **Query Boosting 机制** - 通过高效 Token Mixing 增强跨 Query 和跨序列的异构交互，逐层丰富语义表示
3. **交替优化框架** - Query Decoding 和 Query Boosting 两层机制迭代执行，实现序列建模与特征交互的协同进化
4. **多序列独立建模** - 为每个行为序列构建独立的 Query Token 集，避免序列合并导致的语义损失

### 3.2 总体架构

HyFormer 的整体流程为：输入特征经过 Tokenization 转换为 Token 序列，然后通过 L 层 HyFormer Block 进行联合建模，最后通过 MLP 输出预测结果。

```
输入 Tokenization → Query Generation → [Query Decoding + Query Boosting] × L → MLP → 预测
```

### 3.3 输入 Tokenization

**策略：** 基于语义的特征分组

- 遵循 RankMixer 的 Tokenization 策略，输入 Token 可按语义分组或自动切分组织
- HyFormer 采用语义分组以保持结构化归纳偏置并提高可解释性
- Token 数量配置：输入 Token 数对齐为 16，包括 13 个非序列 Token 和 3 个全局 Token（每个序列 1 个）

### 3.4 Query Generation

**核心思想：** 将异构非序列特征转换为用于解码长行为序列的语义 Query Token

**机制：**
```
Q = [FFN₁(Global Info), ..., FFNₙ(Global Info)] ∈ R^(N×D)
Global Info = Concat(F₁, ..., Fₘ, MeanPool(Seq))
```

**深层 Query 复用：** 在更深的 HyFormer 层中，Query 不再通过 MLP 重新生成，而是复用前一层的 Query，以 progressively richer semantics  interrogate 长序列

### 3.5 Query Decoding

**核心思想：** 将非序列特征转换为语义 Query，通过 Cross-Attention 从长行为序列中提取目标感知信息

**序列表示编码（三种策略）：**

| 编码策略 | 公式 | 复杂度 | 适用场景 |
|----------|------|--------|----------|
| Full Transformer | Hₗ = TransformerEncₗ(S) | O(L_S²) | 最高建模容量 |
| LONGER-style | Hₗ = CrossAttn(S_short, S, S) | O(L_H·L_S) | 长序列效率优先 |
| Decoder-style | Hₗ = SwiGLUₗ(S) | O(L_S) | 延迟敏感场景 |

**Cross-Attention 解码：**
```
Q̃⁽ˡ⁾ = CrossAttn(Q⁽ˡ⁾, K⁽ˡ⁾, V⁽ˡ⁾)
```

### 3.6 Query Boosting

**核心思想：** 在解码后增强 Query 表示，显式混合 Query Token 之间的信息并注入额外非序列特征信号

**机制：**

1. **统一 Query 表示** - Q = [Q̃⁽ˡ⁾, F₁, ..., Fₘ] ∈ R^(T×D)，T = N + M
2. **MLP-Mixer Token Mixing** - 对每个 Query Token 划分为 T 个通道子空间，聚合所有 Token 位置的信息
3. **Per-Token FFN refinement** - 对每个 Query Token 应用独立的前馈变换
4. **残差连接** - Q_boost = Q + Q̃

### 3.7 多序列建模

**策略：独立建模** - 每个 HyFormer Block 中独立处理每个行为序列

- 为每个序列构建专用的 Query Token 集，对相应序列表示执行 Query Decoding
- 跨序列交互通过 Query-level Token Mixing 在后期处理，无需显式序列拼接

**为什么优于序列合并：**
- 保持序列特异性语义
- 避免强制对齐不同序列的侧信息或稀疏维度
- 可为更重要序列自适应分配更多全局 Token
- 实验显示序列合并导致 AUC 下降 0.06%

## 📊 实验验证

### 离线实验 (AUC 对比)

| 架构 | 序列建模 | 特征交互 | AUC | ΔAUC | Params(M) | FLOPs(T) |
|------|----------|----------|-----|------|-----------|----------|
| BaseArch | LONGER | RankMixer | 0.6478 | - | 386 | 3.5 |
| HyFormer | - | - | **0.6489** | **+0.17%** | 418 | 3.9 |

### 消融实验

| 配置 | AUC | ΔAUC | 说明 |
|------|-----|------|------|
| HyFormer | 0.6489 | - | 完整模型 |
| Query w/o Seq Pooling Tokens | 0.6486 | -0.05% | 移除跨序列 Pooling Token |
| Query w/o Nonseq and Seq Pooling | 0.6484 | -0.08% | 仅保留 Target 特征 |
| HyFormer + Merge Seq | 0.6485 | -0.06% | 序列合并策略 |

### 在线 A/B 测试 (抖音搜索)

| 指标 | 变化 |
|------|------|
| 人均观看时长 | +0.293% ↑ |
| 人均视频完播数 | +1.111% ↑ |
| Query 改写率 | -0.236% ↓ |

## 🔍 对比与思考

### 与两阶段范式对比

| 维度 | LONGER+RankMixer | HyFormer |
|------|------------------|----------|
| 信息流 | 单向（序列→交互） | 双向（交替优化） |
| 融合时机 | 晚期融合 | 逐层融合 |
| Query 表示 | 有限特征子集 | 全局特征 + 序列 Pooling |
| 交互深度 | 仅在后期 | 每层都交互 |
| 扩展效率 | 较低 | 更陡峭的 Scaling 曲线 |

### 核心创新点

1. **重新定义 Query Token 角色** - 从单一候选特征扩展为全局特征 + 序列 Pooling，增强 Query 表示容量
2. **交替优化范式** - Query Decoding（序列建模）与 Query Boosting（特征交互）交替执行，实现双向信息流
3. **多序列独立建模** - 避免序列合并导致的语义损失，为不同序列分配独立 Query Token
4. **高效 Token Mixing** - 采用 MLP-Mixer 替代 Self-Attention 进行特征交互，保持线性复杂度

### 本质

HyFormer 不是简单统一序列建模和特征交互，而是通过 Query Decoding + Query Boosting 的交替优化机制，实现两者的协同进化和双向信息流，在保持服务效率的同时突破了两阶段范式的扩展天花板。
