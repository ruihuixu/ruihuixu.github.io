---
title: "推荐算法 (Recommendation)"
description: "推荐系统算法与工程实践"
---

## 笔记格式规范

本目录笔记遵循统一结构：

1. **📌 一句话总结** - 核心贡献与效果
2. **❓ 问题背景** - 分点简明阐释 (2-4 点)
3. **💡 方法框架** - 总体流程 + 逐个点详细讲解
4. **📊 实验验证** - 简洁呈现关键结果
5. **🔍 对比批判优化** - 可选：与其他方法对比/批判性思考/优化方向

## 论文笔记列表

### 生成式推荐 (Generative Recommendation)

| 论文 | 机构 | 核心贡献 |
|------|------|----------|
| [GRs](GRs-Meta.md) | Meta | 万亿参数序列转导模型，HSTU 架构，首次验证推荐 Scaling Law |
| [MTGR](MTGR-Meituan.md) | 美团 | 保留交叉特征的生成式推荐，65 倍 FLOPs 提升 |
| [OneREC v1](OneREC-v1-Kuaishou.md) | 快手 | 端到端统一召回 + 精排，DPO 偏好对齐 |
| [OneRec-V2](oneranker_V2.md) | 快手 | Lazy Decoder-Only 架构，计算量减少 94% |

### 判别式推荐 (Discriminative Recommendation)

| 论文 | 机构 | 核心贡献 |
|------|------|----------|
| [HyFormer](HyFormer.md) | 字节 | 统一混合 Transformer，Query Decoding+Boosting 交替优化 |
| [RankMixer](rankmixer.md) | 字节 | 硬件感知精排架构，MFU 从 4.5%→45% |
| [TokenMixer-Large](Tokenmixer-Large.md) | 字节 | RankMixer 大规模演进，15B 参数，MFU 60% |
