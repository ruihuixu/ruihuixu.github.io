# 论文追踪清单

> 按方法分类，标注发现时间、是否已融入章节、优先级（P0=必须融入 / P1=建议融入 / P2=可省略）

## LLM 技术报告（RL 章节相关）

| 机构 | 报告/模型 | 关键 RL 方法 | 发现时间 | 状态 |
|------|----------|-------------|----------|------|
| DeepSeek | R1 Technical Report | GRPO | 2026-06-24 | 已融入 ch03 |
| DeepSeek | DAPO (arXiv 2503.14476) | DAPO | 2026-06-24 | 已融入 ch03 |
| ByteDance | VAPO (arXiv 2506.15050) | Value-Augmented PPO | 2026-06-24 | 已提及 ch03 |
| ByteDance | REINFORCE++ (veRL) | Batch-normalized PG | 2026-06-24 | 已提及 ch03 |
| - | R2VPO (arXiv 2601.03320) | Variance-regularized PPO | 2026-06-24 | P1 |
| - | KLip-PPO (arXiv 2606.23932) | PPO-Clip = per-sample KL | 2026-06-24 | P1 |
| - | SFPO (ICLR 2026) | Slow-Fast Policy Optimization | 2026-06-24 | P1 |
| Anthropic | Claude 4 MSM | Mid-training alignment | 2026-06-24 | 已融入 ch04 |
| Meta | LLaMA 4 | RLHF + Constitutional AI | 2026-06-24 | 已提及 ch04 |
| Alibaba | Qwen 3 | DPO/LoRA + MSM testbed | 2026-06-24 | 已提及 ch04 |

## 推荐 RL 论文

| 机构 | 论文 | 方法 | 发现时间 | 状态 |
|------|------|------|----------|------|
| JD | GenRec (SIGIR 2026) | GRPO-SR 生成式推荐 | 2026-06-24 | 已融入 ch05 |
| ByteDance | OneTrans (WWW 2026) | 统一 Transformer 推荐 | 2026-06-24 | 已融入 ch05 |
| Kuaishou | OneRec→OneReason→GR4AD | 生成式推荐系列 | 2026-06-24 | 已融入 ch05 |
| - | SAPO (arXiv 2605.17648) | Step-level credit assignment | 2026-06-24 | 已提及 ch05 |
| - | DIG (arXiv 2605.14853) | 判别→生成统一 | 2026-06-24 | P1 |
| - | DiffGRM (WWW 2026) | Masked diffusion for GR | 2026-06-24 | P1 |
| Meituan | MBGR (arXiv 2604.02684) | 多业务生成式推荐 | 2026-06-24 | 已融入 ch05 |
| Kuaishou | Taiji POPO (arXiv 2606.03866) | LLM-as-Enhancer 广告 | 2026-06-24 | 已融入 ch06 |
| WashPost | CQL+OPE (UMAP 2026) | Offline RL paywall | 2026-06-24 | 已融入 ch06 |
| - | DRPO (arXiv 2602.10430) | Hard filtering for offline data | 2026-06-24 | 已提及 ch06 |
| Google | SlateQ (IJCAI 2019) | Slate decomposition | 2026-06-24 | 已融入 ch06 |
| - | GeMS (WSDM 2023) | VAE latent slate | 2026-06-24 | 已融入 ch06 |

## Round 2 LLM RL 新发现（2026-06-24）

| 机构 | 方法 | 关键点 | 优先级 |
|------|------|--------|--------|
| OpenAI | beneficial-trait RL | 5% 数据→83% win, alignment 低维流形 | P0 (ch04) |
| Anthropic | Teaching Claude Why | SFT>RL, 28x 效率, MSM | P0 (ch04) |
| Kimi K2 | RLVR + MuonClip + Seer | 完整技术报告 arXiv, 74-97% throughput | P1 (ch03) |
| Qwen 3 | Hidden-Align | 零开销对齐, +3.8~6.2 over DAPO | P1 (ch03) |
| Meta | RLUF | 隐式反馈信号, +28% 正向反应 | P1 (ch06) |
| Google | deliberative alignment | Gram 安全评估框架 | P2 |
| Mistral | AlphaPO | 7-10% over SimPO | P2 |

## Round 2 Recsys RL 新发现（2026-06-24）

| 机构 | 方法 | 关键点 | 优先级 |
|------|------|--------|--------|
| ByteDance | GRPO(推荐)/VAPO(推理) | 明确分工, +46.49% 活跃天数 | P0 (ch05/06) |
| Kuaishou | Taiji POPO + OneReason | 首个 CoT 推荐, +10.33%, 400M 用户 | P0 (ch06) |
| Meta | GEARS + Memento | agentic ranking, 365天记忆, +1% CTR | P0 (ch06) |
| Google | Self-Evolving Rec | LLM agent 自主优化推荐 | P0 (ch06) |
| Alibaba | 6 种 GRPO 变体 | GRC/EG-GRPO/TaoSR/AIGQ | P1 (ch05/06) |
| Meituan | MTGenRec + 物流 RL | 6 篇 ACL 2026, 物流-12% | P1 (ch06) |
| Amazon | HarmoRec + UGR + Shop-R1 | Offline RL + user simulation | P1 (ch06) |
| JD | GenRec GRPO-SR | +9.5% clicks, +8.7% transactions | P1 (ch05) |

## June 2026 新发现（R3 前沿对齐，P1/P2 供后续迭代融入）

| 方法 | 论文 | 关键点 | 优先级 |
|------|------|--------|--------|
| DPOP | arXiv Jun 10 | DPO + gated penalty on ref greedy, 超 SimPO | P1 (ch04) |
| S-SPPO | arXiv Jun | Semantic self-play, Llama-3-8B 52.19% win rate | P1 (ch04) |
| FlowTracer | ICML 2026 | DAG token credit assignment | P1 (ch03) |
| AdaGRPO | arXiv Jun 7 | Noise-robust GRPO for recsys | P1 (ch05) |
| ExpRL | arXiv Jun 15 | Dense reward scaffolds with reference solutions | P2 |
| HDS | arXiv Jun 23 | SAC for LLM pre-training data mixing | P2 |
| RACO | ICML 2026 Spotlight | Multi-objective Pareto alignment | P2 |
| Semantic Pareto-DQN | IEEE Trans Jun | Multi-objective recsys DQN | P2 |

## 开源实现

| 项目 | 用途 | 发现时间 | 状态 |
|------|------|----------|------|
| TRL | DPO/GRPO 训练器 | | 待调研 |
| CleanRL | PPO 参考实现 | | 待调研 |
| VeRL | LLM RL 训练框架 | | 待调研 |
| OpenRLHF | RLHF 框架 | | 待调研 |
