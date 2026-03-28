---
title: "动态规划：完全背包理论与五道应用"
date: 2026-03-09T10:00:00+08:00
draft: false
slug: "dp-knapsack-complete"
tags:
  - "动态规划"
categories:
  - "LeetCode"
description: "涵盖 LeetCode 518/377/322/279/139。完全背包与01背包的唯一区别是内层遍历改为正序，物品可重复选取；求组合数外层物品内层容量，求排列数外层容量内层物品——两句话区分五道题。"
---

> **本文涵盖**：LeetCode 518 零钱兑换 II / 377 组合总和 IV / 322 零钱兑换 / 279 完全平方数 / 139 单词拆分
>
> 难度：中等 | 关键词：完全背包、正序遍历、组合数 vs 排列数、最值初始化

---

## 识别信号

遇到以下特征，优先考虑完全背包模板：

- 题目明确说明物品（硬币、数字、单词）**可以无限次重复使用**
- 问恰好凑成某个目标值的**方案数**（组合数或排列数）
- 问凑成目标的**最少物品个数**，凑不到则返回 -1
- 问能否将字符串/数字**拼接/分解**为给定集合中的元素（可行性判断）

---

## 核心模板（速查）

```python
# 完全背包模板 A：外层物品，内层容量（用于求组合数 / 最值）
dp = [init_val] * (target + 1)
dp[0] = base_val

for item in items:
    for j in range(item, target + 1):   # 正序！允许重复选同一物品
        dp[j] = update(dp[j], dp[j - item])

# 完全背包模板 B：外层容量，内层物品（用于求排列数）
dp = [init_val] * (target + 1)
dp[0] = base_val

for j in range(1, target + 1):
    for item in items:
        if j >= item:
            dp[j] = update(dp[j], dp[j - item])
```

**与 0/1 背包的唯一代码差异：内层循环从 `item` 正序到 `target`（0/1 背包是从 `target` 倒序到 `item`）。**

| 题号 | 求什么 | 外层 | 内层方向 | dp[0] | 转移函数 |
|------|--------|------|---------|-------|---------|
| 518  | 组合数 | 物品 coins | 正序容量 j | 1 | `dp[j] += dp[j-coin]` |
| 377  | 排列数 | 容量 j | 正序物品 nums | 1 | `dp[j] += dp[j-num]` |
| 322  | 最少硬币 | 物品 coins | 正序容量 j | 0（其余 inf）| `dp[j] = min(dp[j], dp[j-coin]+1)` |
| 279  | 最少平方数 | 物品 squares | 正序容量 j | 0（其余 inf）| `dp[j] = min(dp[j], dp[j-sq]+1)` |
| 139  | 能否拼成 | 容量 j | 正序单词 words | True | `if dp[j-l]: dp[j]=True` |

> **正序 vs 倒序**：完全背包内层正序 = 本轮更新时可以再次使用当前物品；0/1 背包内层倒序 = 保证用的是上一轮未更新的值，物品只取一次。

---

## ⚠️ 高频错误（先看这里）

### 错误 1：内层循环写成倒序，退化为 0/1 背包

完全背包允许重复选取，内层**必须正序**。一旦改为倒序，当前物品在本轮最多只被选一次，语义完全改变。

```python
# ❌ 错误：倒序 → 变成 0/1 背包，每种硬币最多用一次
for coin in coins:
    for j in range(amount, coin - 1, -1):
        dp[j] += dp[j - coin]

# ✅ 正确：正序 → 完全背包，同一硬币可多次使用
for coin in coins:
    for j in range(coin, amount + 1):
        dp[j] += dp[j - coin]
```

### 错误 2：518 将外层与内层对调，求出排列数而非组合数

518 要求组合数（{1,2} 和 {2,1} 算同一种），必须把**物品放外层**。若把容量放外层，每个容量都遍历所有物品，{1,2} 和 {2,1} 会被分别计入，结果偏大。

```python
# ❌ 错误：外层容量 → 算出的是排列数（377 的写法）
for j in range(1, amount + 1):
    for coin in coins:
        if j >= coin:
            dp[j] += dp[j - coin]

# ✅ 正确：外层物品 → 算出的是组合数（518 的写法）
for coin in coins:
    for j in range(coin, amount + 1):
        dp[j] += dp[j - coin]
```

### 错误 3：322/279 初始化用 0 而非 inf

求最少个数时，`min` 操作需要一个"无穷大"的初始值作为比较基准。若初始化为 0，`min(0, dp[j-coin]+1)` 永远返回 0，所有答案都会错误地变成 0。

```python
# ❌ 错误：全部初始化为 0
dp = [0] * (amount + 1)
# 导致 dp[j] = min(0, anything) = 0，答案全错

# ✅ 正确：全部初始化为 inf，仅 dp[0] = 0
dp = [float('inf')] * (amount + 1)
dp[0] = 0
```

### 错误 4：139 只判断子串匹配，忽略 dp[j-len(w)] 是否可达

139 的转移需要两个条件同时成立：前缀 `s[0:j-l]` 可拼成（`dp[j-l]` 为 True）**且** `s[j-l:j]` 在字典里。缺少前者，即使子串匹配也无法保证整体可达。

```python
# ❌ 错误：只检查子串是否在字典，未检查前缀可达性
for j in range(1, n + 1):
    for w in word_set:
        l = len(w)
        if j >= l and s[j - l:j] == w:
            dp[j] = True

# ✅ 正确：同时检查 dp[j-l] 和子串匹配
for j in range(1, n + 1):
    for w in word_set:
        l = len(w)
        if j >= l and dp[j - l] and s[j - l:j] == w:
            dp[j] = True
```

### 错误 5：279 平方数上界漏掉 +1，丢失最大平方数

`range(1, int(n**0.5) + 1)` 中的 `+1` 不可省略。当 `n` 本身是完全平方数（如 n=4），`int(4**0.5)=2`，若写成 `range(1, 2)` 只有 `[1]`，完全丢失物品 `4`，导致 `dp[4]=4`（用四个 1）而非正确答案 1。

```python
# ❌ 错误：漏掉 +1，n=4 时只生成 [1]，丢失物品 4
squares = [i * i for i in range(1, int(n ** 0.5))]

# ✅ 正确：+1 保证 i=int(√n) 被包含，生成所有 ≤n 的完全平方数
squares = [i * i for i in range(1, int(n ** 0.5) + 1)]
```

---

## 详解

### 518. 零钱兑换 II

#### 核心思路

给定不同面额的硬币 `coins`（每种无限），求凑成总金额 `amount` 的**硬币组合数**，{1,2} 与 {2,1} 视为同一种。

- `dp[j]`：凑成金额 `j` 的组合数
- `dp[0] = 1`：空方案，是所有递推的起点
- 求**组合数** → 物品在外层，容量在内层，内层正序

#### Python 代码

```python
def change(amount: int, coins: list[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1                              # 空方案凑成 0，有 1 种

    for coin in coins:                     # 外层：物品（保证组合不重复）
        for j in range(coin, amount + 1):  # 内层：正序（允许重复使用）
            dp[j] += dp[j - coin]

    return dp[amount]
```

#### 图解

`coins=[1,2], amount=3`，逐轮更新：

```
初始:      dp = [1, 0, 0, 0]

coin=1 后: dp[1]+=dp[0]=1  dp[2]+=dp[1]=1  dp[3]+=dp[2]=1
           dp = [1, 1, 1, 1]   ← 只用 1 凑

coin=2 后: dp[2]+=dp[0]=2  dp[3]+=dp[1]=2
           dp = [1, 1, 2, 2]

答案 dp[3] = 2，对应 {1,1,1} 和 {1,2} ✓
```

---

### 377. 组合总和 IV

#### 核心思路

给定正整数数组 `nums`（无重复，每个可无限选），求和为 `target` 的**排列数**，{1,2} 与 {2,1} 算两种。

- `dp[j]`：凑成目标值 `j` 的排列数
- `dp[0] = 1`：递推基础
- 求**排列数** → 容量在外层，物品在内层

#### Python 代码

```python
def combinationSum4(nums: list[int], target: int) -> int:
    dp = [0] * (target + 1)
    dp[0] = 1                              # 递推基础

    for j in range(1, target + 1):         # 外层：容量（枚举每个位置）
        for num in nums:                   # 内层：物品（每个位置尝试所有数字）
            if j >= num:
                dp[j] += dp[j - num]

    return dp[target]
```

#### 图解

`nums=[1,2], target=3`：

```
dp[1] = dp[0]         = 1   对应序列：(1)
dp[2] = dp[1]+dp[0]   = 2   对应序列：(1,1)  (2)
dp[3] = dp[2]+dp[1]   = 3   对应序列：(1,1,1)  (1,2)  (2,1)
```

与 518 相比多出了 (2,1)，正好体现排列比组合多的部分。

---

### 322. 零钱兑换

#### 核心思路

硬币 `coins` 每种无限，求凑成 `amount` 的**最少硬币数**；无法凑成返回 -1。

- `dp[j]`：凑成金额 `j` 所需的最少硬币数
- 初始化全为 `float('inf')`，`dp[0]=0`
- 最终若 `dp[amount]` 仍为 `inf`，说明无法凑成，返回 -1

#### Python 代码

```python
def coinChange(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0                              # 凑成 0 需要 0 枚

    for coin in coins:
        for j in range(coin, amount + 1):
            dp[j] = min(dp[j], dp[j - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
```

#### 图解

`coins=[1,2,5], amount=6`：

```
初始:      [0, inf, inf, inf, inf, inf, inf]
coin=1 后: [0,  1,   2,   3,   4,   5,   6]
coin=2 后: [0,  1,   1,   2,   2,   3,   3]
coin=5 后: [0,  1,   1,   2,   2,   1,   2]
                                         ↑
答案 dp[6] = 2，对应 1+5 ✓
```

---

### 279. 完全平方数

#### 核心思路

完全平方数（1, 4, 9, 16, ...）每个可无限使用，求和为 `n` 的**最少数量**。

与 322 结构完全相同，区别只在于"物品"是由 `n` 动态生成的完全平方数列表，不需要考虑无解的情况（数学上任何正整数都可由四个以内的完全平方数组成）。

#### Python 代码

```python
def numSquares(n: int) -> int:
    squares = [i * i for i in range(1, int(n ** 0.5) + 1)]

    dp = [float('inf')] * (n + 1)
    dp[0] = 0

    for sq in squares:
        for j in range(sq, n + 1):
            dp[j] = min(dp[j], dp[j - sq] + 1)

    return dp[n]   # 数学定理保证 dp[n] 必然有限，无需判断 inf
```

#### 图解

`n=12`，squares=[1, 4, 9]：

```
初始:      [0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf]
sq=1 后:   [0,  1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12]
sq=4 后:   [0,  1,   2,   3,   1,   2,   3,   4,   2,   3,   4,   5,   3]
sq=9 后:   [0,  1,   2,   3,   1,   2,   3,   4,   2,   1,   2,   3,   3]
                                                          ↑
答案 dp[12] = 3，对应 4+4+4 ✓
```

---

### 139. 单词拆分

#### 核心思路

字符串 `s`，字典 `wordDict`（单词可重复使用），判断 `s` 能否由字典单词拼接而成。

- 背包容量 = 字符串位置下标（0 到 n）
- 物品 = 字典中每个单词，长度 `l = len(w)`
- `dp[j]`：`s[0:j]` 能否由字典单词拼成（布尔值）
- 转移：`dp[j-l]` 为 True 且 `s[j-l:j] == w` → `dp[j] = True`
- 单词拼接**顺序有意义** → 外层容量（位置），内层物品（单词）

#### Python 代码

```python
def wordBreak(s: str, wordDict: list[str]) -> bool:
    word_set = set(wordDict)               # 转集合，O(1) 查找
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True                           # 空字符串可拆，递推基础

    for j in range(1, n + 1):             # 外层：容量（字符串位置）
        for w in word_set:                 # 内层：单词（物品）
            l = len(w)
            if j >= l and dp[j - l] and s[j - l:j] == w:
                dp[j] = True
                break                      # 找到一种拆法即可

    return dp[n]
```

#### 图解

`s="applepenapple", wordDict=["apple","pen"]`：

```
dp[0] = True
j=5:  w="apple", l=5, dp[0]=True, s[0:5]="apple" ✓  → dp[5]=True
j=8:  w="pen",   l=3, dp[5]=True, s[5:8]="pen"   ✓  → dp[8]=True
j=13: w="apple", l=5, dp[8]=True, s[8:13]="apple" ✓ → dp[13]=True
返回 True ✓
```

---

## 统一对比

| 题号 | 求什么 | 外层 | dp[0] | 转移函数 | 无解返回 |
|------|--------|------|-------|---------|---------|
| 518  | 组合数 | 物品 coins | 1 | `dp[j] += dp[j-coin]` | 0（必有解） |
| 377  | 排列数 | 容量 j | 1 | `dp[j] += dp[j-num]` | 0（必有解） |
| 322  | 最少硬币 | 物品 coins | 0（其余 inf）| `dp[j] = min(dp[j], dp[j-coin]+1)` | -1 |
| 279  | 最少平方数 | 物品 squares | 0（其余 inf）| `dp[j] = min(dp[j], dp[j-sq]+1)` | 不存在 |
| 139  | 能否拼成 | 容量 j | True（其余 False）| `if dp[j-l] and s[j-l:j]==w: dp[j]=True` | False |

---

## 口诀

```
完全背包，内层正序；0/1 背包，内层倒序。

问方案数，分组合排列：
  顺序无关（组合）→ 物品外层，容量内层  [518]
  顺序有关（排列）→ 容量外层，物品内层  [377 / 139]

问最小数，两层顺序都可以；
  初始化 inf，dp[0]=0；
  最后判 inf，返 -1。        [322 / 279]

问能否到，布尔 dp；
  dp[0]=True，外层容量，内层物品。  [139]

初始化三口诀：
  方案数 → dp[0]=1，其余 0
  最小数 → dp[0]=0，其余 inf
  可行性 → dp[0]=True，其余 False
```

---

## 总结与扩展

完全背包的核心只有两点：

**第一点：内层正序**，这是与 0/1 背包的唯一区别。正序时 `dp[j-item]` 已经是本轮更新过的值（包含了当前物品），相当于可以再次选取，从而实现无限次使用。

**第二点：外层顺序决定组合还是排列**。物品在外层时，同一容量的状态不会包含顺序信息，得到组合数（518）；容量在外层时，每个容量都对所有物品做完整枚举，得到排列数（377、139）。求最值时（322、279）两种顺序结果相同，选更直观的写法即可。

掌握这两点后，遇到完全背包题只需回答三个问题：物品是什么？背包容量是什么？求组合、排列还是最值/可行性？三问答完，模板随手可写。

**拓展练习**（0/1 背包，与完全背包对比加深理解）：

- [416. 分割等和子集](https://leetcode.cn/problems/partition-equal-subset-sum/)：0/1 背包，内层倒序，判断能否恰好装满
- [494. 目标和](https://leetcode.cn/problems/target-sum/)：0/1 背包求方案数，内层倒序，dp[0]=1
- [474. 一和零](https://leetcode.cn/problems/ones-and-zeroes/)：二维 0/1 背包，两个容量维度均倒序
