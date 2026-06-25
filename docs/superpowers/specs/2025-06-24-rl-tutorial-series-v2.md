# RL 教程系列 v2 — 正式设计

> 状态：已确认 | 创建：2025-06-24 | 替代 v1 草稿

## 设计决策汇总

| 决策 | 选择 |
|------|------|
| 符号表 | Phase 0 最先完成 |
| 章节顺序 | **教学顺序**，拆 Actor-Critic / 偏好对齐两条平行线 |
| 推荐 RL | 独立 2 章（ch05 生成式 + ch06 工业实践） |
| 目标读者 | 算法面试候选人（熟悉 DL，有概率论/优化基础） |
| 数学深度 | 核心公式 + 直觉 + 关键证明，跳过冗长推导 |
| 代码形式 | Jupyter Notebook（`.ipynb`），推导代码交织 |
| 环境策略 | 双线：CartPole 展示算法原理 + GPT-2 展示对齐/推荐实战 |
| 新文件夹 | `<workspace-root>/rl-tutorial/` |
| 迭代模式 | 长期运行：每章搜索→写作→自检→子Agent验证→记忆 |

## 文件夹结构

```
rl-tutorial/
├── _symbols.md              # Phase 0: 统一符号表
├── _prerequisites.md        # Phase 0: 前置知识 + 环境搭建
├── research-log.md          # 业界调研日志（持续更新）
├── paper-tracker.md         # 论文追踪清单（每章搜索后更新）
├── ch01-thinking-framework.ipynb
├── ch02-policy-gradient-ppo.ipynb
├── ch03-actor-critic-evolution.ipynb   # RLOO → GRPO → DAPO
├── ch04-preference-alignment.ipynb     # DPO → KTO → ORPO
├── ch05-generative-recsys-rl.ipynb     # 生成式推荐中的 RL
├── ch06-industrial-recsys-rl.ipynb     # 传统推荐 RL + 工业实践
└── assets/                  # 图片/数据文件
```

## 两条教学线

```
Actor-Critic 线（CartPole 为主）         偏好对齐线（GPT-2 为主）
  ch02: REINFORCE → PPO                   ch04: DPO → KTO → ORPO
  ch03: RLOO → GRPO → DAPO
          ↘                                ↙
           ch05: 生成式推荐 RL（两线交汇）
           ch06: 工业推荐 RL
```

## 各章内容规格

### Phase 0: 基础设施

**_symbols.md** — 全系列统一符号：
- 状态/动作/奖励/策略/价值函数符号
- Actor-Critic 相关：π, V, Q, A, GAE
- 偏好对齐相关：x, y_w, y_l, r_θ, β
- 推荐相关：user, item, slate, reward

**_prerequisites.md** — 前置知识清单 + 环境搭建：
- 概率论：期望/方差/KL 散度/重要性采样
- 优化：梯度下降/Adam/学习率调度
- DL：PyTorch/Transformer/GPT-2 加载
- 环境搭建：conda/pip 依赖、GPU 配置要求

### ch01: RL 思想框架
- 驱动问题：为什么监督学习不够？
- 统一视角："用偏好信号替代显式标签进行优化"
- MDP 五元组、Policy 定义、Bellman 方程（压缩推导）
- 代码：Tabular Q-learning on GridWorld（~50行 numpy）
- 面试追问：推荐为什么不能用点击率作为唯一信号？
- 环境：GridWorld

### ch02: Policy Gradient → PPO（核心章节，篇幅最大）
- 完整推导链：REINFORCE → Actor-Critic → GAE → PPO
- 组织方式：问题驱动（每个算法解决什么问题、代价是什么）
- PPO on-policy 困境专节讨论
- 代码：PPO on CartPole（~200行，对标 CleanRL）
- 面试追问：PPO clip 为什么对称？GAE λ=0/1 退化为什么？
- 环境：CartPole

### ch03: Actor-Critic 演进线
- 驱动问题：Critic 能更简单吗？能去掉吗？
- RLOO：去掉 Value Function，用 leave-one-out baseline
- GRPO：组内相对排序，完全无 Critic
- DAPO：解决 GRPO 的 reward hacking 和训练崩溃
- 代码：RLOO/GRPO 对比实验（CartPole + GPT-2）
- 面试追问：GRPO 何时失效？DAPO 为什么需要动态采样？
- 环境：CartPole → GPT-2

### ch04: 偏好对齐线
- 驱动问题：能否直接从偏好数据学习，不需要 reward model？
- DPO：Bradley-Terry + KL 约束 → DPO loss 完整推导
- KTO/ORPO 及其与 DPO 的差异和适用场景
- reward over-optimization 讨论
- 代码：TRL DPO 实验（GPT-2 级别）
- 面试追问：DPO 最大劣势？KTO 的优势场景？
- 环境：GPT-2

### ch05: 生成式推荐中的 RL
- 驱动问题：推荐怎么从"预测 item"变成"生成 item"？
- 生成式推荐范式：GRs / Token 化 / 序列生成
- 博客已有论文深度对照：RankMixer, TokenMixer, ULTRA-HSTU
- 新论文补充：OneRec v2, OneTrans 等
- 代码：生成式推荐环境模拟器 + PPO/GRPO 训练
- 环境：推荐模拟器

### ch06: 工业推荐 RL
- 推荐 RL 特殊性：slate action、高维稀疏 state、延迟噪声 reward
- exploration/exploitation 平衡（主线索）
- 离线到在线 gap 的工程方案
- 工业案例：字节/快手/美团/Meta 的推荐 RL 实践
- 代码：推荐环境模拟器 + PPO vs 贪心对比
- 环境：推荐模拟器

## 迭代架构

### 单章流程（每章循环）

```
1. 搜索轮: WebSearch + Tavily 定向搜索本章相关的最新论文/报告
   → 更新 paper-tracker.md
2. 写初稿: 按章节规格撰写 .ipynb
3. 自检: RL 原理一致性、证据链完整、公式↔代码对应
4. 子Agent验证: 独立验证旧章代码可运行、推导链一致
5. 记忆: 关键决策写入 memory，关键发现写入 research-log.md
6. 前沿对齐: 新发现方法和刚写完的内容交叉比对，
   需要调整则回第2步
```

### 全局流程

```
Phase 0: 符号表 + 前置知识
    ↓
Phase 1: ch01 → ch02 → ch03 → ch04（Actor-Critic + 对齐线）
    ↓     每章完成后搜索本轮，更新日志
Phase 2: ch05 → ch06（推荐 RL 两章）
    ↓     每章完成后搜索本轮，更新日志
Phase 3: 全局迭代
    ├─ R1 交叉验证轮: 章节间术语/符号/推导一致性
    ├─ R2 质量提升轮: 知识阶梯自然度、代码可运行性终检
    ├─ R3 前沿对齐轮: 最终搜索确认无重大遗漏
    └─ 定稿
```

### 搜索迭代规则

- **范围**: LLM 技术报告（DeepSeek/OpenAI/Anthropic/Meta/Kimi/Qwen 等）+ 推荐 RL 论文（字节/快手/美团/Meta/Google/Amazon）
- **频率**: 每写完一章立即执行一轮搜索
- **输出**: 更新 `paper-tracker.md`（按方法分类，标注发现时间和是否已融入章节）
- **回溯**: 如果新发现的方法显著影响已写完的章节，立即回溯修改

### 质量门禁

每章必须通过以下检查才进入下一章：
- [ ] 代码 `Run All` 可执行，无 error
- [ ] 推导链完整（公式 → 代码变量 → 实验结果 一一对应）
- [ ] 面试追问清单每个问题可答
- [ ] 最新一轮搜索无重大遗漏
- [ ] 子 Agent 已验证旧章无衰退

## 执行顺序

| 阶段 | 任务 | 预估工作量 |
|------|------|-----------|
| Phase 0 | 符号表 + 前置知识 | 1 轮 |
| Phase 1 | ch01 → ch04（4 章 × 单章流程） | 4 轮 |
| Phase 2 | ch05 → ch06（2 章 × 单章流程） | 2 轮 |
| Phase 3 | R1 交叉验证 → R2 质量提升 → R3 前沿对齐 | 3 轮 |
| **合计** | **10 轮核心 + 搜索迭代** | |
