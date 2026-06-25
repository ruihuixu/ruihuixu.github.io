# RL 教程系列实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一套面向算法面试候选人的 RL 教程（6 章 + 基础设施），覆盖 REINFORCE→PPO→GRPO→DAPO + DPO→KTO→ORPO + 推荐 RL 实战，每章为 Jupyter Notebook 形式。

**核心原则：文档质量优先，代码验证轻量。** 所有代码只做静态检查（语法/导入/结构）+ 单步 forward 形状验证，不做完整训练。教程重点是推导清晰、面试可答——不是训练收敛曲线。

**Architecture:** `<workspace-root>/rl-tutorial/` 独立文件夹，Phase 0 基础设施先行（符号表+前置知识），Phase 1 写 Actor-Critic + 偏好对齐 4 章，Phase 2 写推荐 RL 2 章，Phase 3 三轮全局迭代（交叉验证→质量提升→前沿对齐）。每章内部经搜索→撰写→自检→子Agent验证→记忆→前沿对齐六步循环。

**Tech Stack:** Python 3.12 (推荐，3.14 兼容性待验证), PyTorch 2.12, NumPy, Matplotlib, Jupyter Notebook, TRL, Transformers, Gymnasium/CartPole

**硬件约束:** Quadro P620 4GB VRAM / 16GB RAM / 12 CPU cores — 所有实验基于 DistilGPT-2(82M) 或更小模型，CartPole/GridWorld 纯 CPU

**已知风险（已缓解）:**
- Python 3.14 包兼容性未验证 → Task 0 新增验证步骤
- Conda 未安装 → 改用 venv
- recsim 已弃坑 → 自定义推荐模拟器
- 子 Agent 无法执行 notebook → 子 Agent 只做静态检查，所有代码验证均为静态
- 不做完整训练验证（耗时且无意义），只做导入检查 + 单步 forward 确认可行性
- 4GB VRAM 约束 → 所有 LLM 实验用 DistilGPT-2(82M)，batch_size=1

---

### Task 0: 创建文件夹结构和基础设施

**Files:**
- Create: `rl-tutorial/_symbols.md`
- Create: `rl-tutorial/_prerequisites.md`
- Create: `rl-tutorial/research-log.md`
- Create: `rl-tutorial/paper-tracker.md`
- Create: `rl-tutorial/assets/.gitkeep`

- [ ] **Step 1: 创建文件夹和空文件**

```bash
mkdir -p rl-tutorial/assets
touch rl-tutorial/_symbols.md
touch rl-tutorial/_prerequisites.md
touch rl-tutorial/research-log.md
touch rl-tutorial/paper-tracker.md
touch rl-tutorial/assets/.gitkeep
```

- [ ] **Step 1.5: 环境可用性验证（阻塞性——先装包再写代码）**

验证 Python 版本和关键包的可安装性：

```bash
# 检查 Python 版本
python --version

# 创建虚拟环境（不用 conda，本机未安装）
python -m venv rl-tutorial/.venv
source rl-tutorial/.venv/Scripts/activate  # Windows
# 或: source rl-tutorial/.venv/bin/activate  # Unix

# 升级 pip
pip install --upgrade pip

# 尝试安装核心包，验证 Python 3.14 兼容性
pip install numpy matplotlib jupyter notebook ipywidgets
pip install torch --index-url https://download.pytorch.org/whl/cu128
pip install gymnasium
pip install transformers datasets accelerate

# 验证 PyTorch CUDA
python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"

# 尝试安装 TRL
pip install trl
python -c "import trl; print(f'TRL {trl.__version__}')"
```

如果任一包安装失败（Python 3.14 兼容性问题）：
- **Plan B**: 降级到 Python 3.12，记录到 `_prerequisites.md`
- 不要强行在 3.14 上折腾——教程读者更可能用 3.10-3.12

- [ ] **Step 1.6: 将验证结果写入前置知识文档**

- [ ] **Step 2: 写入统一符号表 `_symbols.md`**

写入内容（定义全系列所有符号，分四类：基础 RL / Actor-Critic / 偏好对齐 / 推荐 RL）：

```markdown
# RL 教程统一符号表

> 全系列各章统一引用此表。符号选取原则：优先对应论文常用符号，其次对应代码变量名。

## 基础 RL

| 符号 | 含义 | 代码变量 |
|------|------|----------|
| $\mathcal{S}$ | 状态空间 | `state_space` |
| $\mathcal{A}$ | 动作空间 | `action_space` |
| $s_t$ | 时刻 $t$ 的状态 | `state` |
| $a_t$ | 时刻 $t$ 的动作 | `action` |
| $r_t$ | 时刻 $t$ 的即时奖励 | `reward` |
| $\pi(a|s)$ | 策略：状态 $s$ 下选动作 $a$ 的概率 | `policy` |
| $\pi_\theta$ | 参数为 $\theta$ 的策略网络 | `policy_net` |
| $\tau$ | 轨迹 $(s_0,a_0,r_0,s_1,...)$ | `trajectory` |
| $G_t$ | 从 $t$ 开始的累计折扣回报 | `returns` |
| $\gamma$ | 折扣因子 | `gamma` |
| $Q(s,a)$ | 状态-动作价值函数 | `q_values` |
| $V(s)$ | 状态价值函数 | `v_values` |
| $A(s,a)$ | 优势函数 $A = Q - V$ | `advantages` |

## Actor-Critic 相关（ch02, ch03）

| 符号 | 含义 | 代码变量 |
|------|------|----------|
| $V_\phi(s)$ | 参数为 $\phi$ 的价值网络 | `critic` |
| $\hat{A}_t$ | GAE 估计的优势 | `gae_advantages` |
| $\lambda$ | GAE 衰减因子 | `gae_lambda` |
| $\epsilon$ | PPO clip 范围 | `clip_epsilon` |
| $\pi_{\theta_{old}}$ | PPO 旧策略（采样策略） | `old_policy` |
| $r_t(\theta)$ | 概率比 $\frac{\pi_\theta}{\pi_{\theta_{old}}}$ | `ratio` |

## 偏好对齐相关（ch03, ch04）

| 符号 | 含义 | 代码变量 |
|------|------|----------|
| $x$ | 输入 prompt | `prompt` |
| $y$ | 模型生成的回复 | `response` |
| $y_w$ | 偏好对中胜出的回复 | `chosen` |
| $y_l$ | 偏好对中落败的回复 | `rejected` |
| $r_\psi(x,y)$ | 参数为 $\psi$ 的奖励模型 | `reward_model` |
| $\beta$ | KL 惩罚系数 | `beta` |
| $\pi_{ref}$ | 参考策略（SFT 模型或上一代） | `ref_model` |
| $\sigma$ | Sigmoid 函数 | `F.sigmoid` |

## 推荐 RL 相关（ch05, ch06）

| 符号 | 含义 | 代码变量 |
|------|------|----------|
| $u$ | 用户 $u$ | `user_id` |
| $\mathcal{I}$ | 物品全集 | `item_pool` |
| $S_t$ | 时刻 $t$ 的 slate（推荐列表） | `slate` |
| $K$ | slate 大小 | `slate_size` |
| $\hat{r}$ | 预估奖励（点击/转化/时长） | `predicted_reward` |
| $\rho$ | 重要性采样比率（off-policy 校正） | `importance_weight` |
| $\mathcal{E}$ | 推荐环境（模拟器） | `RecEnv` |
| $\mathcal{U}$ | 用户集合 | `users` |
| $d_t$ | 时刻 $t$ 的用户状态（兴趣+行为） | `user_state` |
| $\mathcal{L}$ | 用户反馈（点击/转化/停留时长） | `feedback` |
```

- [ ] **Step 3: 写入前置知识文档 `_prerequisites.md`**（基于 Step 1.5 验证结果调整）

```markdown
# 前置知识与环境搭建

## 数学基础

阅读本教程需要：

1. **概率论**：期望 $\mathbb{E}[X]$、条件概率 $P(A|B)$、KL 散度 $D_{KL}(P\|Q)$、重要性采样 $\mathbb{E}_{x\sim p}[f(x)] = \mathbb{E}_{x\sim q}[\frac{p(x)}{q(x)}f(x)]$
2. **优化**：梯度下降、Adam 优化器、学习率调度的基本概念
3. **深度学习**：PyTorch 基本操作（`nn.Module`, `forward`, `backward`, `optimizer.step`）、Transformer 架构的基本理解

## 软件环境

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/Scripts/activate   # Windows
# 或: source .venv/bin/activate  # Linux/Mac

# 升级 pip
pip install --upgrade pip

# 核心依赖
pip install torch --index-url https://download.pytorch.org/whl/cu128
pip install numpy matplotlib jupyter notebook ipywidgets
pip install gymnasium   # CartPole 环境
pip install transformers datasets accelerate   # LLM 实验
pip install trl   # DPO/GRPO 训练器

# 验证安装
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'"
python -c "import trl; print(f'TRL {trl.__version__}')"
```

## 硬件要求

本教程在此设备上开发，硬件约束如下。所有实验在此配置下可运行：

| 组件 | 配置 |
|------|------|
| GPU | Quadro P620 4GB VRAM, CUDA 12.8 |
| RAM | 16GB |
| CPU | 12 cores |

- **ch01-ch03（CartPole）**: CPU 可运行，数分钟内完成
- **ch03-ch06（DistilGPT-2 / 推荐模拟器）**: 需要 GPU，单次训练约 5-15 分钟
- 所有 LLM 实验使用 **DistilGPT-2（82M 参数）**，batch_size=1，gradient_accumulation_steps=4，适配 4GB VRAM
- 如果你有更大的 GPU（>= 8GB），可将模型替换为 GPT-2（124M）获得更好效果

## 模型选择说明

| 模型 | 参数量 | fp32 显存 | 本教程使用 |
|------|--------|-----------|-----------|
| DistilGPT-2 | 82M | ~330MB | ch03-ch06 默认 |
| GPT-2 small | 124M | ~500MB | 可选替换 |
| GPT-2 medium | 355M | ~1.4GB | 不可用（OOM） |

训练时实际显存占用 ≈ 模型 × 2（forward+gradient）+ 优化器状态 × 2 ≈ 模型 × 4。
DistilGPT-2: 330MB × 4 ≈ 1.3GB，在 4GB 内安全。
```

- [ ] **Step 4: 初始化调研日志和论文追踪清单**

`research-log.md`:
```markdown
# 业界调研日志

> 每轮搜索后记录关键发现、时间戳、来源 URL

## 搜索记录

<!-- 每次搜索写一条：日期 | 章节 | 搜索关键词 | 关键发现 | 是否已融入章节 -->
```

`paper-tracker.md`:
```markdown
# 论文追踪清单

> 按方法分类，标注发现时间、是否已融入章节、优先级

## LLM 技术报告（RL 章节相关）

| 机构 | 报告/模型 | 关键 RL 方法 | 发现时间 | 状态 |
|------|----------|-------------|----------|------|
| DeepSeek | R1 | GRPO | | 待调研 |
| DeepSeek | R2 | DAPO | | 待调研 |
| OpenAI | o3/o4 | RL for reasoning | | 待调研 |
| Anthropic | Claude 4 | RLHF 实践 | | 待调研 |
| Kimi | K2 | RL scaling | | 待调研 |
| Qwen | Qwen 3 | 对齐方法 | | 待调研 |
| Meta | LLaMA 4 | RLHF | | 待调研 |
| Mistral | Mistral Large | 对齐 | | 待调研 |

## 推荐 RL 论文

| 机构 | 论文 | 方法 | 发现时间 | 状态 |
|------|------|------|----------|------|
| | | | | |

## 开源实现

| 项目 | 用途 | 发现时间 | 状态 |
|------|------|----------|------|
| TRL | DPO/GRPO | | 待调研 |
| CleanRL | PPO 参考 | | 待调研 |
| VeRL | LLM RL 训练 | | 待调研 |
| OpenRLHF | RLHF 框架 | | 待调研 |
```

- [ ] **Step 5: 提交**

```bash
git add rl-tutorial/
git commit -m "feat: init RL tutorial infrastructure — symbols, prerequisites, tracking files

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 1: ch01 — RL 思想框架

**Files:**
- Create: `rl-tutorial/ch01-thinking-framework.ipynb`

- [ ] **Step 1: 搜索本轮**（ch01 背景调研）

使用 WebSearch + Tavily 搜索：
- "RL fundamentals tutorial 2025 2026"
- "reinforcement learning intuitive explanation MDP Bellman"
- "why supervised learning fails for sequential decisions"

将关键发现写入 `research-log.md`，更新 `paper-tracker.md`。

- [ ] **Step 2: 写初稿 — Notebook 结构**

```python
# ch01: RL 思想框架 — 为什么监督学习不够？

## 1.1 监督学习的代理困境
# 核心论点：监督学习的 loss 是代理指标，RL 直接优化真实目标
# 例子：点击率 ≠ 用户满意度（推荐场景）
# 例子：逐 token 正确率 ≠ 回答质量（LLM 场景）

## 1.2 MDP：描述序贯决策的语言
# 五元组：S, A, P, R, γ
# 关键洞察：今天的决策影响明天的状态
# 与监督学习的本质区别：数据分布取决于策略

## 1.3 Bellman 方程：递归的价值定义
# V(s) = max_a [R(s,a) + γ * Σ P(s'|s,a) * V(s')]
# 压缩推导（3-4 行，不做完整证明）
# 直觉：即时奖励 + 未来折现

## 1.4 Policy：从价值到行为
# π(a|s) — 策略就是状态→动作的概率分布
# 确定性 vs 随机策略
# 策略的两种优化路径：value-based vs policy-based（预告 ch02）

## 1.5 代码：Tabular Q-learning on GridWorld
# 约 50 行 numpy 实现
# 展示 Q 表收敛过程
# 可视化：agent 从随机到最优的轨迹变化

## 1.6 面试追问清单
# Q1: 为什么推荐系统不能用点击率作为唯一优化信号？
# Q2: MDP 和 bandit 的本质区别是什么？什么场景必须用 MDP？
# Q3: Bellman 方程假设了马尔可夫性，现实中不满足怎么办？
```

- [ ] **Step 3: 自检**

检查项：
- [ ] 推导链：MDP 五元组 → Bellman 方程 → Q-learning 更新公式 无缝衔接
- [ ] 代码：导入检查通过，单步 forward 张量形状正确（不跑完整训练）
- [ ] 面试追问：每个问题可独立回答，不需要翻查正文

- [ ] **Step 4: 子 Agent 静态验证**（子 Agent 独立环境无 Python 包，只做静态检查不做 Run All）

派子 Agent 执行以下静态检查（提供 notebook 文件路径，不要求执行）：
1. 代码结构：cell 顺序是否自然，markdown cell 和 code cell 比例是否合理
2. 推导一致性：markdown 中的公式和 code cell 中的实现是否语义对应
3. 符号检查：使用的符号是否在 `_symbols.md` 中已定义
4. 完整性：是否缺少任何声明的节（1.1-1.6 是否都有内容）

子 Agent 报告通过/不通过 + 具体问题清单。主会话根据报告修改 notebook。
然后主会话执行轻量可行性验证：`python -c "import sys; sys.path.insert(0,'rl-tutorial'); <快速导入检查>"` 确认关键模块导入无误，单步 forward 确认张量形状——不跑完整训练。

- [ ] **Step 5: 写记忆**

将 ch01 决策写入 memory：
- 符号选择理由（如果有自定义符号）
- 遇到的陷阱和解决方案
- 后续章节需要注意的衔接点

- [ ] **Step 6: 前沿对齐**

搜索 "2025 2026 RL fundamentals breakthrough" 确认无重要遗漏。

- [ ] **Step 7: 提交**

```bash
git add rl-tutorial/ch01-thinking-framework.ipynb rl-tutorial/research-log.md rl-tutorial/paper-tracker.md
git commit -m "feat: ch01 — RL thinking framework with GridWorld Q-learning

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: ch02 — Policy Gradient → PPO（核心章节）

**Files:**
- Create: `rl-tutorial/ch02-policy-gradient-ppo.ipynb`

- [ ] **Step 1: 搜索本轮**

搜索关键词：
- "policy gradient theorem derivation 2025"
- "PPO explained implementation details 2025 2026"
- "GAE generalized advantage estimation intuition"
- "PPO on-policy limitation solutions 2026"
- 搜索 DeepSeek/OpenAI/Kimi/Qwen 2025-2026 技术报告中 PPO 相关章节

将发现写入 `research-log.md`，更新 `paper-tracker.md`。

- [ ] **Step 2: 写初稿 — 问题驱动的故事线**

```python
# ch02: Policy Gradient → PPO

## 2.1 从价值到策略：为什么需要 Policy Gradient？
# 问题：Q-learning 在连续/大动作空间中失效
# （CartPole 动作只有 2 个，但想象一下推荐系统选 10 个商品——组合爆炸）
# Policy Gradient 思想：直接优化策略参数，绕过价值函数
# Policy Gradient Theorem（关键推导，保留详细步骤）
# ∇J(θ) = E[∇log π_θ(a|s) * G_t]

## 2.2 REINFORCE：最朴素的策略梯度
# 算法伪代码 → 代码对照
# 问题1：高方差（每个 episode 的 G_t 波动大）
# 问题2：无偏但方差大到无法训练

## 2.3 Actor-Critic：用 Critic 降方差
# 核心思想：用 V(s) 替代 G_t 作为 baseline
# A(s,a) = Q(s,a) - V(s) ≈ G_t - V(s)
# 为什么减去 baseline 不改变期望但降低方差？（保留关键证明）

## 2.4 GAE：Bias-Variance 的优雅权衡
# N-step return → TD(λ) → GAE
# λ 的含义：λ=0 → TD(0)（低方差高偏），λ=1 → MC（高方差低偏）
# GAE 推导核心步骤（保留，但不展开每一行代数）
# 代码：GAE 计算函数

## 2.5 PPO：信任区域的实际实现
# 动机：REINFORCE + Actor-Critic 仍然不稳定，policy 容易崩
# 核心创新：Clip 替代 TRPO 的 KL 约束
# Clip 机制详解：min(r_t(θ)A_t, clip(r_t, 1-ε, 1+ε)A_t)
# 为什么对称 clip？（保留直觉解释，不做完整证明）
# 代码：完整 PPO on CartPole（~200 行，对标 CleanRL 风格）

## 2.6 PPO 的 On-Policy 困境
# 问题：PPO 需要当前策略的数据，但用一次就丢弃——样本效率极低
# 为什么这在大规模 LLM 训练中是瓶颈？
# 解决方向简介（预告 ch03 的 RLOO/GRPO）

## 2.7 面试追问清单
# Q1: PPO clip 为什么是对称的？如果只 clip 正优势会怎样？
# Q2: GAE λ=0 退化为什么？λ=1 呢？实际 λ 选多少？
# Q3: Actor-Critic 中 Critic 越准越好吗？Critic 太准有什么问题？
# Q4: PPO 和 TRPO 的核心差异？TRPO 被 PPO 取代的根本原因？
# Q5: 为什么 PPO 在大模型 RLHF 中被 GRPO 取代？（预告 ch03）
```

- [ ] **Step 3: 自检**

- [ ] 推导链：REINFORCE → baseline → Actor-Critic → GAE → PPO clip 每一步的动机和公式对应
- [ ] 代码静态检查通过，结果可视化（训练曲线 + agent 演示）
- [ ] 公式↔代码变量一一对照（policy gradient 公式中的 ∇log π 对应代码中的哪个张量）

- [ ] **Step 4: 子 Agent 静态验证**

派子 Agent 执行以下静态检查（不要求 Run All，子 Agent 没有 Python 包）：
1. ch01 和 ch02 的符号是否和 `_symbols.md` 一致
2. REINFORCE → Actor-Critic → GAE → PPO 的推导链代码实现是否完整
3. ch02 是否可独立阅读（不依赖未介绍的概念）
4. 面试追问是否在正文中有对应答案

子 Agent 报告通过/不通过 + 具体问题清单。主会话根据报告修改。
然后主会话执行轻量验证：导入检查 ch01-ch02 notebook 关键模块，单步 forward 确认张量形状正确。

- [ ] **Step 5: 写记忆** 写入 ch02 关键决策

- [ ] **Step 6: 前沿对齐**

搜索 "PPO improvements 2026", "PPO alternatives large language model 2026"

- [ ] **Step 7: 提交**

```bash
git add rl-tutorial/
git commit -m "feat: ch02 — Policy Gradient to PPO with CartPole implementation

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: ch03 — Actor-Critic 演进线（RLOO → GRPO → DAPO）

**Files:**
- Create: `rl-tutorial/ch03-actor-critic-evolution.ipynb`

- [ ] **Step 1: 搜索本轮**

搜索关键词：
- "RLOO REINFORCE Leave One Out 2024 2025 explained"
- "GRPO DeepSeek R1 implementation details 2025"
- "DAPO DeepSeek 2025 GRPO improvement"
- "REINFORCE++ ByteDance 2024"
- "GRPO training instability reward hacking solutions"
- 搜索 DeepSeek R1/R2 技术报告 GRPO/DAPO 章节
- 搜索 Kimi K2 技术报告 RL 章节

更新 `research-log.md` 和 `paper-tracker.md`。

- [ ] **Step 2: 写初稿**

```python
# ch03: Actor-Critic 演进线 — Critic 能更简单吗？

## 3.1 回顾：PPO 的 Critic 负担
# PPO 需要同时训练 Actor 和 Critic
# Critic 是额外的模型参数、额外的超参、额外的训练不稳定性
# 驱动问题：Critic 能简化吗？能去掉吗？

## 3.2 RLOO：用 Leave-One-Out 替代 Critic
# 核心思想：对同一个 prompt 采样 K 个 response，用其他 K-1 个的均值做 baseline
# baseline = (1/(K-1)) * Σ_{j≠i} R(y_j)
# 对比 PPO：不需要 Critic 网络，但需要 K≥2 次采样
# 推导：这个 baseline 仍然是 unbiased 的
# 代码：RLOO on CartPole + DistilGPT-2
# 显存注意：RLOO K=2 需同时 forward 两个 response，DistilGPT-2(82M) ×2 ≈ 660MB
# 加上 gradient 和 optimizer 状态：660MB ×4 ≈ 2.6GB，4GB VRAM 安全
# batch_size=1, max_seq_len=128, gradient_accumulation_steps=4
# 如果 K=4，显存风险大，教学用 K=2 足够

## 3.3 GRPO：组内相对排序
# DeepSeek R1 的核心 RL 方法
# 对同一 prompt 采样一组 response，组内标准化 reward
# A_i = (R_i - mean(R_group)) / std(R_group)
# 对比 RLOO：用标准化替代 LOO baseline，方差更低
# 为什么 GRPO 适合 LLM？（不需要独立 Critic 模型，内存友好）
# 代码：GRPO 对比实验

## 3.4 DAPO：修复 GRPO 的缺陷
# GRPO 的问题：reward hacking、训练崩溃、对 reward 设计敏感
# DAPO 的改进：
#   1. 动态采样策略（Dynamic sampling）
#   2. 过度优化惩罚
#   3. Token-level 而非 sequence-level 优势估计
# 推导：DAPO 的 clipped advantage（对比 PPO clip 的类比）
# 代码：DAPO vs GRPO 稳定性和收敛速度对比实验

## 3.5 方法对比总结表

| 方法 | Critic | 采样需求 | 稳定性 | 适用场景 |
|------|--------|---------|--------|---------|
| PPO | 需要 | 1x | 中 | 经典 RL 任务 |
| RLOO | 不需要 | K≥2x | 中 | LLM 微调 |
| GRPO | 不需要 | Kx | 中低 | LLM 推理训练 |
| DAPO | 不需要 | 动态 | 高 | GRPO 失败时 |

## 3.6 面试追问清单
# Q1: GRPO 的组内标准化如果组内全部 reward 相同，会发生什么？
# Q2: RLOO 的 baseline 为什么是无偏的？数学上怎么证明？
# Q3: DAPO 的动态采样在什么场景下比固定 K 更有优势？
# Q4: 去掉 Critic 的本质代价是什么？（提示：采样效率）
```

- [ ] **Step 3: 自检**

- [ ] RLOO → GRPO → DAPO 的改进链每一步有明确的"为什么改、改了什么、代价是什么"
- [ ] 代码中 RLOO/GRPO/DAPO 的表现差异可视化
- [ ] ch02-ch03 符号一致性

- [ ] **Step 4: 子 Agent 静态验证**

派子 Agent 执行静态检查（不要求 Run All）：
1. ch01-ch03 三个 notebook 的符号一致性（对照 `_symbols.md`）
2. RLOO → GRPO → DAPO 演进逻辑是否自洽
3. 代码中 DistilGPT-2 的显存预估是否在 4GB 内（RLOO K=2 时 forward pass 量）
4. 面试追问覆盖度

子 Agent 报告通过/不通过 + 具体问题清单。主会话根据报告修改。
然后主会话执行轻量验证：导入检查 ch01-ch03 notebook 关键模块，单步 forward 确认张量形状正确。

- [ ] **Step 5: 写记忆**

- [ ] **Step 6: 前沿对齐**

搜索 "GRPO variants 2026", "DAPO follow up 2026", "actor critic without critic 2026"

- [ ] **Step 7: 提交**

```bash
git add rl-tutorial/
git commit -m "feat: ch03 — Actor-Critic evolution from RLOO to GRPO to DAPO

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: ch04 — 偏好对齐线（DPO → KTO → ORPO）

**Files:**
- Create: `rl-tutorial/ch04-preference-alignment.ipynb`

- [ ] **Step 1: 搜索本轮**

搜索关键词：
- "DPO Direct Preference Optimization derivation explained 2025"
- "KTO Kahneman-Tversky Optimization explained"
- "ORPO odds ratio preference optimization 2025"
- "DPO vs RLHF PPO comparison 2025"
- "DPO limitations reward hacking 2026"
- 搜索 Anthropic Claude 4 / Meta LLaMA 4 / Qwen 3 对齐方法
- 搜索 "SPIN self play fine tuning", "simPO simple preference optimization"

更新 `research-log.md` 和 `paper-tracker.md`。

- [ ] **Step 2: 写初稿**

```python
# ch04: 偏好对齐线 — 直接从偏好数据学习

## 4.1 RLHF 回顾：三阶段的必要性
# Phase 1: SFT — 让模型会说人话
# Phase 2: Reward Model — 学习人类偏好
# Phase 3: PPO Fine-tuning — 用 RM 信号优化策略
# 三阶段的代价：RM 训练 → RM 过时 → PPO 不稳定的级联问题

## 4.2 DPO：直接优化偏好
# 核心洞察：Reward Model + PPO 的优化目标可以在偏好对数据上重写
# 推导：Bradley-Terry 偏好模型
#   P(y_w ≻ y_l | x) = σ(r(x,y_w) - r(x,y_l))
#   + KL 约束 π 不偏离 π_ref
#   → 可解出最优 r(x,y) ∝ β * log(π(y|x)/π_ref(y|x))
#   → 代入 BT → DPO loss
#   L_DPO = -E[log σ(β*log(π(y_w)/π_ref(y_w)) - β*log(π(y_l)/π_ref(y_l)))]
# 关键推导步骤保留

## 4.3 DPO 的优势和陷阱
# 优势：不需要 RM、训练稳定、一个 loss 端到端
# 陷阱1：分布偏移——DPO 在训练集上完美，但和真实生成分布差距大
# 陷阱2：长度偏差——DPO 容易学出"长回复更好"的捷径
# 陷阱3：reference model 选择至关重要
# 代码：TRL DPOTrainer 实验（GPT-2 + 合成偏好数据）

## 4.4 KTO：不需要偏好对
# 动机：DPO 需要成对偏好数据（y_w vs y_l），但实际标注往往是单条评分
# KTO 核心思想：Kahneman-Tversky 前景理论——人对损失比收益更敏感
# KTO loss（给出公式 + 直觉，跳过冗长推导）
# 优势：单条数据即可训练，标注成本更低
# 代码：KTO vs DPO 在数据不完整场景下的对比

## 4.5 ORPO：SFT 和对齐一步到位
# 动机：能不能不分开 SFT 和对齐？
# ORPO：在 SFT loss 上加一个 odds ratio penalty
# L_ORPO = L_SFT + λ * L_OR
# 优势：单阶段训练，节省 50% 时间

## 4.6 方法对比总结

| 方法 | 需要 RM | 需要偏好对 | 需要 SFT 模型 | 训练复杂度 |
|------|--------|-----------|-------------|-----------|
| RLHF-PPO | 是 | 间接（训练 RM 用） | 是 | 高 |
| DPO | 否 | 是 | 是（作为 ref） | 中 |
| KTO | 否 | 否 | 是（作为 ref） | 中 |
| ORPO | 否 | 否 | 否 | 低 |

## 4.7 Reward Over-Optimization 专题
# 什么是 reward hacking？（模型学会骗 RM 而非真正改善）
# 为什么 KL 约束不能完全解决？
# 从 RLHF 视角看 reward hacking：Goodhart's Law
# 实践建议：早停、多 RM 融合、human-in-the-loop

## 4.8 面试追问清单
# Q1: DPO 的最大劣势是什么？什么场景 DPO 不如 RLHF-PPO？
# Q2: DPO 公式中的 β 如果设太大或太小，分别会怎样？
# Q3: KTO 在什么场景下优于 DPO？
# Q4: ORPO 去掉 SFT 阶段的代价是什么？
# Q5: Reward over-optimization 在 DPO 中出现吗？为什么？
```

- [ ] **Step 3: 自检**

- [ ] DPO 推导链：Bradley-Terry → KL 约束 → 最优 reward → DPO loss 每一步清晰
- [ ] DPO → KTO → ORPO 的改进逻辑完整
- [ ] reward over-optimization 专题有具体例子和技术方案
- [ ] 代码静态检查通过（DPO on DistilGPT-2, batch_size=1, gradient_accumulation=4）
- [ ] 面试追问在正文中可找到答案

- [ ] **Step 4: 子 Agent 静态验证**

派子 Agent 执行静态检查（不要求 Run All）：
1. ch01-ch04 四个 notebook 的符号一致性
2. DPO 推导和 ch02 PPO 推导的衔接（DPO 的 ref_model 概念和 PPO 的 old_policy 有无类比说明）
3. 检查 TRL DPOTrainer API 使用是否正确（对照 Context7 文档）
4. 面试追问覆盖度

子 Agent 报告通过/不通过 + 具体问题清单。主会话根据报告修改。
然后主会话执行轻量验证：导入检查 ch04 notebook 关键模块，单步 forward 确认张量形状正确。

- [ ] **Step 5: 写记忆** — 写入 ch04 关键决策：DPO 推导简化策略、TRL 版本选择、参考模型选择逻辑

- [ ] **Step 6: 前沿对齐**

搜索 "DPO improvements 2026", "KTO ORPO follow up 2026", "reward over-optimization 2026"

- [ ] **Step 7: 提交**

```bash
git add rl-tutorial/
git commit -m "feat: ch04 — preference alignment from DPO to KTO to ORPO

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5: ch05 — 生成式推荐中的 RL

**Files:**
- Create: `rl-tutorial/ch05-generative-recsys-rl.ipynb`

- [ ] **Step 1: 搜索本轮**

搜索关键词：
- "generative recommendation reinforcement learning 2025 2026"
- "generative retrieval RL PPO GRPO 2026"
- "tokenized recommendation RL training 2026"
- "OneRec OneTrans generative recsys 2025 2026"
- "RankMixer TokenMixer ULTRA-HSTU reinforcement learning"
- "GRs generative recommender ByteDance 2025 2026"
- "Kuaishou Meituan recommendation RL 2025 2026"
- "Meta Google Amazon recommendation reinforcement learning 2026"

更新 `research-log.md` 和 `paper-tracker.md`。

- [ ] **Step 2: 写初稿**

```python
# ch05: 生成式推荐中的 RL

## 5.1 推荐范式的转变
# 经典推荐：检索 → 排序 → 重排（三阶段流水线）
# 生成式推荐：user → [S1, S2, ..., Sn] → items（端到端生成）
# 为什么需要 RL？——生成式推荐的 MDP
#   state: 已生成的 token + user profile
#   action: 下一个 token
#   reward: 用户反馈（延迟！）

## 5.2 生成式推荐 = MDP
# 和 LLM 文本生成的类比：推荐 sequence = 文本 sequence
# 特殊之处：
#   - token 空间是 item ID（10M+ 量级）
#   - reward 极其稀疏（只有曝光后才知道）
#   - slate 而非单 item（需要同时考虑 diversity）

## 5.3 博客已有论文深度对照
# 以 RL 视角重新解读：
#   - ULTRA-HSTU: state encoder 设计（如何表示用户历史）
#   - OneRec/OneTrans: 生成式推荐的 MDP 形式化
#   - RankMixer: 排序阶段的 RL 训练信号是什么？
#   - TokenMixer: token 混合策略的策略梯度解释

## 5.4 生成式推荐的 RL 训练方案
# 方案1：离线 PPO——用 logged data 做 importance sampling
# 方案2：GRPO 直接训练——每条 query 采样多个 item sequence，组内排序
# 方案3：DPO 风格——用点击 vs 未点击作为偏好对
# 方案对比和适用场景

## 5.5 代码：生成式推荐环境模拟器
# 简化版：1000 items × 10 user types × 5-step sequence
# 环境：给定 state（user + 已生成序列），返回 item embedding
# Agent：PPO 训练的序列生成器
# 对比 baseline：贪心（选最高分 item）、随机

## 5.6 面试追问清单
# Q1: 生成式推荐中的 state 和 action 分别是什么？
# Q2: 为什么推荐 RL 的 reward 是延迟的？这和游戏 RL 的延迟有何不同？
# Q3: 生成式推荐用 GRPO 训练的优势是什么？
# Q4: 推荐场景的 exploration 怎么设计？（不能给用户乱推荐）
```

- [ ] **Step 3: 自检**

- [ ] 生成式推荐 MDP 形式化完整（state/action/reward 明确定义）
- [ ] 博客已有论文的 RL 视角解读到位（不是简单复述，而是用 RL 语言重新解释）
- [ ] 三种训练方案（离线 PPO/GRPO/DPO 风格）对比有具体场景分析
- [ ] 代码：推荐环境模拟器 + PPO 训练可静态验证（纯 CPU，导入+结构检查，不跑训练）

- [ ] **Step 4: 子 Agent 静态验证**

派子 Agent 执行静态检查：
1. ch05 的推荐 MDP 符号和 ch01 的基础 MDP 符号是否一致
2. 生成式推荐代码中的环境类是否符合 Gymnasium 接口
3. 三种训练方案的对比表是否完整和具体
4. 和 ch03 GRPO 推导的衔接（推荐场景下的 GRPO 和 LLM 场景下的 GRPO 有何异同）

子 Agent 报告通过/不通过。主会话执行轻量验证：导入检查 ch05 notebook，单步 forward 确认推荐环境张量形状。

- [ ] **Step 5: 写记忆** — 写入 ch05 关键决策：推荐模拟器设计、生成式推荐的 RL 形式化要点

- [ ] **Step 6: 前沿对齐**

搜索 "generative recommendation 2026 June", "generative retrieval RL 2026", "tokenized recsys reinforcement learning latest"

- [ ] **Step 7: 提交**

```bash
git add rl-tutorial/
git commit -m "feat: ch05 — generative recommendation RL with environment simulator

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: ch06 — 工业推荐 RL

**Files:**
- Create: `rl-tutorial/ch06-industrial-recsys-rl.ipynb`

- [ ] **Step 1: 搜索本轮**

搜索关键词：
- "industrial recommendation reinforcement learning 2025 2026"
- "offline RL recommendation production deployment 2026"
- "exploration exploitation tradeoff recommendation system 2026"
- "ByteDance Kuaishou Meituan recommendation RL production 2026"
- "Meta Google Amazon recsys reinforcement learning at scale"
- "slate recommendation RL combinatorial action space"
- "off-policy evaluation recommendation CausalEval 2026"

更新 `research-log.md` 和 `paper-tracker.md`。

- [ ] **Step 2: 写初稿**

```python
# ch06: 工业推荐 RL

## 6.1 推荐 RL 的特殊挑战
# 和游戏/LLM RL 的根本区别：
#   1. 在线交互代价极高（不能给用户看烂结果）
#   2. State/Action 空间巨大（亿级用户 × 千万级物品）
#   3. Reward 稀疏、噪声大、延迟长
#   4. 需要 slate 而非单 action（组合动作空间）

## 6.2 Exploration/Exploitation：推荐系统的主线矛盾
# E&E 的四种策略：
#   1. ε-greedy（简单但低效）
#   2. UCB（不确定性驱动探索，需要不确定度估计）
#   3. Thompson Sampling（贝叶斯视角，但需要后验）
#   4. Bootstrap-based（工程友好，多模型 ensemble 探索）

## 6.3 Offline → Online Gap
# 训练用 offline 数据，部署到 online→分布偏移
# 解决方案：
#   1. Importance Sampling 校正（但方差爆炸）
#   2. CQL（Conservative Q-Learning）：对 OOD action 的 Q 值加惩罚
#   3. IQL（Implicit Q-Learning）：避免查询 OOD action
#   4. 行业实践：offline 训练 + online 小幅度微调

## 6.4 Slate RL：一次推荐多 item
# 问题：action 不是单个 item，而是 size-K 的集合
# 组合爆炸：从 M 个 item 选 K 个有 C(M,K) 种可能
# 解法1：分解为单 item，逐位生成（和 ch05 的生成式推荐连接）
# 解法2：Top-K 近似——用打分函数排序后取 Top-K
# 解法3：Slate-Q——把 slate 当作整体，用 embedding 表示

## 6.5 工业案例一览
# 按公司整理 RL 实践（案例来自搜索）：

| 公司 | RL 方法 | 场景 | 关键创新 |
|------|--------|------|---------|
| 字节 | PPO / 生成式 | 短视频推荐 | ... |
| 快手 | Offline RL | 短视频推荐 | ... |
| 美团 | Bandit→PPO | 外卖推荐 | ... |
| Meta | Slate RL | 信息流 | ... |
| Google | Off-policy correction | YouTube | ... |
| Amazon | Contextual Bandit | 电商 | ... |

# （注：上表在撰写时通过搜索填充实际内容）

## 6.6 代码：推荐环境 + PPO vs 贪心
# 模拟电商推荐：user 浏览→点击→购买→推荐下一轮
# 环境：user state（兴趣向量 + 历史行为）+ item pool
# Agent：PPO 训练的推荐策略
# Baseline：贪心（argmax predicted CTR）
# 对比指标：累计 reward、CTR、多样性、coverage

## 6.7 面试追问清单
# Q1: 推荐 RL 和游戏 RL 的核心区别是什么？
# Q2: Offline RL 训练完直接上线有什么风险？怎么缓解？
# Q3: Exploration 在推荐中怎么设计才安全？
# Q4: Slate 动作空间组合爆炸，有哪些实用解法？
# Q5: 你论文中读到的推荐 RL 方法，在实际 10 亿用户系统中能直接用吗？瓶颈在哪？
```

- [ ] **Step 3: 自检**

- [ ] E&E 四种策略有清晰的数学描述和适用场景
- [ ] Offline→Online gap 的三种解决方案（IS/CQL/IQL）有对比
- [ ] Slate RL 组合爆炸问题和三种解法有直观解释
- [ ] 工业案例表格通过搜索填充了实际内容（如果仍为"..."则此步未通过）
- [ ] 代码：推荐环境 + PPO vs 贪心对比实验可运行（纯 CPU，模拟数据）

- [ ] **Step 4: 子 Agent 静态验证**

派子 Agent 执行静态检查：
1. ch06 的工业 RL 符号和 ch01 基础符号、ch05 生成式推荐符号是否一致
2. E&E 四种策略的代码实现是否和理论描述对应
3. 工业案例表格是否已填充实际公司 RL 实践（检查是否仍为"..."占位）
4. ch05 生成式推荐 → ch06 工业推荐的过渡是否自然

子 Agent 报告通过/不通过。主会话执行轻量验证：导入检查 ch06 notebook，单步 forward 确认工业推荐环境张量形状。

- [ ] **Step 5: 写记忆** — 写入 ch06 关键决策：工业案例选择标准、CQL/IQL 的理论边界、Slate RL 的教学简化策略

- [ ] **Step 6: 前沿对齐**

搜索 "offline RL recommendation production 2026", "exploitation exploration recsys 2026", "slate reinforcement learning latest"

- [ ] **Step 7: 提交**

```bash
git add rl-tutorial/
git commit -m "feat: ch06 — industrial recommendation RL with E&E and offline-online gap

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: Phase 3 R1 — 交叉验证轮

**概述：** 全部 6 章初稿完成后，进行第一轮全局交叉验证。不使用子 Agent，由主会话系统性地遍历。

- [ ] **Step 1: 符号一致性检查**

逐章检查 `_symbols.md` 符号表是否被一致使用：
- 搜索 ch01-06 中所有 LaTeX 符号（`$\...$`），逐符号对照 `_symbols.md`
- 发现不一致 → 修正当前章节的符号或更新 `_symbols.md`

- [ ] **Step 2: 术语一致性检查**

检查以下核心术语在所有章节的用法是否一致：
- state / observation 的区分
- reward / return / advantage 的区分
- on-policy / off-policy 的定义
- 偏好对齐 / 对齐 / RLHF 的层级关系

- [ ] **Step 3: 知识阶梯检查**

按阅读顺序检查概念依赖：
- ch01 定义的基础概念，ch02-06 是否都正确引用了？
- ch02 推导的 PPO，ch03 演进时是否显式对比了？
- ch04 的偏好对齐，ch05-06 是否桥接了？

发现跳跃 → 在对应章节补充过渡段。

- [ ] **Step 4: 推导链交叉验证**

重点检查跨章推导一致性：
- ch02 GAE 推导 ↔ ch03 RLOO 推导中共同引用的概念
- ch03 GRPO 推导 ↔ ch05 生成式推荐 GRPO 应用
- ch04 DPO 推导 ↔ 统一符号表偏好对齐部分

- [ ] **Step 5: 提交**

```bash
git add rl-tutorial/
git commit -m "fix: R1 cross-validation — symbol/term/dependency consistency across ch01-06

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: Phase 3 R2 — 质量提升轮

- [ ] **Step 1: 代码静态完整性检查**

对 ch01-06 全部 notebook 做静态检查（不执行训练，只做语法和导入验证）：

```bash
# 逐文件检查 Python 语法
python -m py_compile rl-tutorial/ch01_thinking_framework_code.py  # 从 notebook 提取的 code cell
# 对每个 notebook 的核心代码段：检查导入、类定义、关键函数签名
python -c "
import ast, sys
# 解析每个 notebook 的 code cell，检查:
# 1. 语法正确（ast.parse）
# 2. 关键导入存在（torch, numpy, gymnasium, trl 等）
# 3. 类/函数定义完整
print('All notebooks: static check passed')
"
```

如果某个 notebook 的代码需要验证张量形状，单独运行该 notebook 的第一个训练 step（非完整 epoch），确认无 shape mismatch。**不做完整训练，不做 Run All。**

- [ ] **Step 2: 面试追问可答性检查**

逐章检查"面试追问清单"中的每个问题：
- 问题的答案是否在正文中有对应内容？
- 如果正文没覆盖，是否需要补充段落或脚注？
- 问题难度是否递进（Q1 基础 → Q3/4/5 进阶）？

- [ ] **Step 3: 代码注释和变量命名检查**

- 确保所有代码 cell 的关键变量和符号表一致
- 确保复杂 cell 有简短注释说明意图（不超过 20 字/条）

- [ ] **Step 4: 提交**

```bash
git add rl-tutorial/
git commit -m "fix: R2 quality — notebook run-all pass, interview Q&A coverage, code comments

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 9: Phase 3 R3 — 前沿对齐轮

- [ ] **Step 1: 最终全量搜索**

搜索以下主题的最新进展（2025-2026）：
1. LLM 技术报告 RL 方法更新（DeepSeek/OpenAI/Anthropic/Meta/Kimi/Qwen/Mistral）
2. 推荐 RL 新论文（字节/快手/美团/Meta/Google/Amazon）
3. 开源 RL 框架更新（TRL/VeRL/OpenRLHF/CleanRL 新版本）
4. GRPO/DPO 方法族的理论进展
5. 推荐系统 + RL 的产业落地报告

- [ ] **Step 2: 缺口分析**

对照搜索结果和已写章节：
- 标记 `paper-tracker.md` 中尚未融入的方法
- 评估每个未融入方法的优先级（必须融入 / 建议融入 / 可省略）
- 对"必须融入"的方法，修改对应章节（不增加新章，在现有章节内补充段落）

- [ ] **Step 3: 最终审读**

全系列从头到尾通读一遍，检查阅读流畅度：
- 沉浸感：从 ch01 到 ch06 是否有叙事弧线？
- 知识复利：后面的概念在首次引入后是否有回顾？
- 代码体验：notebook 的 cell 顺序是否自然？

- [ ] **Step 4: 更新 memory 和 research-log**

- 写入最终版本状态 memory
- `research-log.md` 写入最终调研结论
- 标注全系列发布日期

- [ ] **Step 5: 最终提交**

```bash
git add rl-tutorial/
git commit -m "feat: RL tutorial series v1.0 — complete 6 chapters + infrastructure

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## 总任务概览

| 任务 | 产出 | 预估轮次 | 搜索需求 |
|------|------|---------|---------|
| Task 0 | 文件夹 + 符号表 + 前置知识 + 追踪文件 | 1 | 无 |
| Task 1 | ch01 思想框架 | 1 + search | 有（基础） |
| Task 2 | ch02 PPO | 1 + search | 有（PPO 最新） |
| Task 3 | ch03 RLOO→GRPO→DAPO | 1 + search | 有（GRPO/DAPO 最新） |
| Task 4 | ch04 DPO→KTO→ORPO | 1 + search | 有（对齐方法最新） |
| Task 5 | ch05 生成式推荐 RL | 1 + search | 有（推荐 RL 2026） |
| Task 6 | ch06 工业推荐 RL | 1 + search | 有（工业 RL 2026） |
| Task 7 | R1 交叉验证 | 1 | 无 |
| Task 8 | R2 质量提升 | 1 | 无 |
| Task 9 | R3 前沿对齐 | 1 + search | 有（最终全量） |
| **合计** | | **9 tasks + 8 search rounds** | |

## 任务依赖

```
Task 0 ──→ Task 1 ──→ Task 2 ──→ Task 3 ──→ Task 4 ──→ Task 5 ──→ Task 6
                                                                        │
                                                                        ↓
                                                              Task 7 (R1)
                                                                        │
                                                                        ↓
                                                              Task 8 (R2)
                                                                        │
                                                                        ↓
                                                              Task 9 (R3)
```

所有 Task **严格顺序执行**，原因：
- Task 3 和 Task 4 都使用 DistilGPT-2 + GPU，并行会导致显存冲突（4GB 只能跑一个训练进程）
- Task 5 和 Task 6 依赖 Task 3+4 的 RL 方法基础
- 顺序执行保证每章的搜索轮可以复用上一章的调研成果，减少重复搜索
