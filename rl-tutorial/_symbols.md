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
| $\epsilon$ | PPO clip 范围（ch02/ch03）；ε-greedy 探索率（ch01 $\\varepsilon$, ch06） | `clip_epsilon` / `eps` |
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
