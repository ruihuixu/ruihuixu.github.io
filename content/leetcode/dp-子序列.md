---
title: "动态规划：子序列九题统一框架"
date: 2026-03-09T10:00:00+08:00
draft: false
slug: "dp-subsequences"
tags:
  - "Algorithm"
  - "Dynamic Programming"
  - "Array"
  - "String"
  - "Python"
categories:
  - "LeetCode"
description: "涵盖 LeetCode 300/674/718/1143/1035/392/115/583/72。子序列DP分三型：单序列（300/674/718）、双序列公共（1143/1035）、双序列编辑（392/115/583/72）——状态定义决定转移方向，末尾字符相等时的处理是核心。"
---

> **本文涵盖**：LeetCode 300/674/718/1143/1035/392/115/583/72

---

## 识别信号

拿到一道子序列题，先对照关键词确定分型，再套对应模板。

| 关键词 / 特征 | 分型 | 代表题 |
|:---|:---|:---|
| 单个数组/字符串，选出递增子序列 | 单序列 LIS 型 | 300 |
| 单个数组，要求**连续**递增 | 单序列连续型 | 674 |
| 两个数组，要求**连续**公共子数组 | 双序列连续（子数组）| 718 |
| 两个字符串，最长公共子序列（不连续）| 双序列公共 LCS | 1143 |
| 连线不交叉，两数组对齐 | 双序列公共 LCS（换皮）| 1035 |
| 判断 s 是否为 t 的子序列 | 双序列编辑-判断 | 392 |
| s 中有多少子序列等于 t，求**计数** | 双序列编辑-计数 | 115 |
| 删除最少字符使两串相等 | 双序列编辑-最优（删）| 583 |
| 三种操作（增/删/改）最小次数 | 双序列编辑-最优（全）| 72 |

---

## 核心模板（速查）

### 模板一：单序列 LIS（300）

```python
def lis_template(nums: list[int]) -> int:
    n = len(nums)
    dp = [1] * n                        # 每个元素自身构成长度 1 的子序列
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:       # 可以把 nums[i] 接在 nums[j] 后面
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)                      # 答案是整个 dp 的最大值，不是 dp[-1]
```

### 模板二：双序列 LCS（1143/1035）

```python
def lcs_template(s: str, t: str) -> int:
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]   # 多一行一列表示空串
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1  # 相等：斜上角 +1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # 不等：保留最大
    return dp[m][n]                               # 答案在右下角
```

### 模板三：编辑距离（72）

```python
def edit_dist_template(w1: str, w2: str) -> int:
    m, n = len(w1), len(w2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i   # 删光 w1 前 i 个字符
    for j in range(n + 1): dp[0][j] = j   # 插入 j 个字符变成 w2
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if w1[i - 1] == w2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]           # 相等：无需操作
            else:
                dp[i][j] = min(
                    dp[i - 1][j],       # 删 w1[i-1]（看上）
                    dp[i][j - 1],       # 插入字符（看左）
                    dp[i - 1][j - 1]    # 替换（看斜上）
                ) + 1
    return dp[m][n]
```

### 三大模板对比

| 特征 | 单序列 LIS | 双序列 LCS | 编辑距离 |
|:---|:---|:---|:---|
| dp 维度 | 一维 `dp[i]` | 二维 `dp[i][j]` | 二维 `dp[i][j]` |
| 相等时 | `dp[j]+1`（需枚举 j） | `dp[i-1][j-1]+1` | `dp[i-1][j-1]`（不加 1）|
| 不等时 | 跳过 | `max(上, 左)` | `min(上, 左, 斜上)+1` |
| 答案位置 | `max(dp)` | `dp[m][n]` | `dp[m][n]` |

---

## ⚠️ 高频错误（先看这里）

### 错误一：单序列题返回 `dp[-1]` 而非 `max(dp)`

❌ `return dp[-1]`
✅ `return max(dp)`

dp[i] 定义为"以 nums[i] **结尾**的最优解"，最优解不一定以最后一个元素结尾。
例如 `nums = [5, 4, 3, 2, 1]`，每个 dp[i] 都是 1，dp[-1] = 1 正确；
但 `nums = [1, 3, 2]`，LIS 是 `[1, 3]`，dp = [1, 2, 2]，`dp[-1] = 2` 恰好对；
换成 `[3, 1, 2]`，dp = [1, 1, 2]，`dp[-1] = 2` 正确，但如果数组是 `[1, 2, 3, 0]`，
dp = [1, 2, 3, 1]，`dp[-1] = 1` 就**完全错误**了，必须取 `max(dp) = 3`。

---

### 错误二：718 不等时漏写 `dp[i][j] = 0`

❌ 只写 `if` 分支，`else` 留空
✅ `else: dp[i][j] = 0`（或依赖初始化全零的 dp 表，但需确认每次循环 dp 没被污染）

718 要求连续子数组，不匹配时必须断链归零。用 Python 列表推导初始化全零的 dp
时默认已经是 0，省略 `else` 能过题；但滚动数组优化时若复用旧行，**漏写会导致错误**。

---

### 错误三：115 相等时只写 `dp[i-1][j-1]`，漏掉 `dp[i-1][j]`

❌ `dp[i][j] = dp[i-1][j-1]`
✅ `dp[i][j] = dp[i-1][j-1] + dp[i-1][j]`

s 中可能有多个字符和 t 中某字符相同，"用 s[i-1] 匹配"和"不用 s[i-1] 匹配"是**两个独立方案**，
都要累加。只写前者会漏掉大量方案，结果严重偏小。

---

### 错误四：583/72 忘记初始化第一行/列

❌ `dp = [[0]*(n+1) for _ in range(m+1)]`，不再做其他初始化
✅ `for i in range(m+1): dp[i][0] = i`；`for j in range(n+1): dp[0][j] = j`

583 的 `dp[i][0] = i` 表示 word1 前 i 个字符全删才能变成空串，
72 同理。忘记初始化边界，整个表的第一行/列全为 0，推出的结果会整体偏小。

---

### 错误五：1143 和 718 的"不等时"混淆

❌ 1143 写成 `dp[i][j] = 0`（误用 718 的逻辑）
❌ 718 写成 `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`（误用 1143 的逻辑）

记忆口诀：**连续的归零，不连续的保留**。
718 是连续子数组，断链必须归零；1143 是不连续子序列，不等时保留两方向最大值。

---

## 详解

### 单序列组

#### 300. 最长递增子序列（LIS）

**题意**：从 nums 中选出严格递增的子序列（不要求连续），求最大长度。

**dp 定义**：`dp[i]` = 以 `nums[i]` 结尾的最长递增子序列长度，初始化全为 1。

**递推**：枚举所有 j < i，若 `nums[j] < nums[i]`，则 `nums[i]` 可接在以 `nums[j]` 结尾的序列后：

```python
def lengthOfLIS(nums: list[int]) -> int:
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

时间 O(n²)，空间 O(n)。答案取 `max(dp)` 而非 `dp[-1]`。

---

#### 674. 最长连续递增序列

**题意**：与 300 相同，但子序列必须**连续**。

**关键区别**：只需和前一个元素比较，不等时直接重置为 1，无需双层循环。

```python
def findLengthOfLCIS(nums: list[int]) -> int:
    n = len(nums)
    if n == 0:
        return 0
    dp = [1] * n
    for i in range(1, n):
        if nums[i] > nums[i - 1]:
            dp[i] = dp[i - 1] + 1
        # else: dp[i] 保持初始值 1，连续中断
    return max(dp)
```

时间 O(n)，空间 O(n)。贪心写法可进一步压到 O(1) 空间。

**300 vs 674**：300 双层循环看全局（不连续），674 只看相邻（连续断链即重置）。

---

#### 718. 最长重复子数组（连续公共子数组）

**题意**：给两个整数数组，求最长的**连续**公共子数组长度。

**dp 定义**：`dp[i][j]` = 以 `nums1[i-1]` 结尾、以 `nums2[j-1]` 结尾的最长公共子数组长度。

```python
def findLength(nums1: list[int], nums2: list[int]) -> int:
    m, n = len(nums1), len(nums2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    result = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if nums1[i - 1] == nums2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                result = max(result, dp[i][j])
            else:
                dp[i][j] = 0   # 连续中断，归零
    return result
```

答案是整张表的最大值（不是 `dp[m][n]`），因为最长匹配可能结束在任意位置。

---

### 双序列公共组

#### 1143. 最长公共子序列（LCS）

**题意**：两个字符串的最长公共子序列（不连续，保持相对顺序），求最大长度。

**dp 定义**：`dp[i][j]` = `text1[0..i-1]` 与 `text2[0..j-1]` 的 LCS 长度。

```python
def longestCommonSubsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

**LCS 表格推导示例**（text1="abcde", text2="ace"）：

```
      ""  a   c   e
""  [  0   0   0   0 ]
a   [  0   1   1   1 ]   'a'=='a' → dp[0][0]+1=1
b   [  0   1   1   1 ]   'b' 不匹配 → max(上,左)
c   [  0   1   2   2 ]   'c'=='c' → dp[2][1]+1=2
d   [  0   1   2   2 ]   'd' 不匹配 → max(上,左)
e   [  0   1   2   3 ]   'e'=='e' → dp[4][2]+1=3
```

答案 `dp[5][3] = 3`，LCS 为 "ace"。

---

#### 1035. 不相交的线（LCS 换皮）

**题意**：两数组各写在一条水平线上，连接相同数字的线段不相交，求最多能画多少条线。

**等价转化**：线段不相交 ⟺ 连接的数字对保持相对顺序 ⟺ **求两数组的 LCS**。

代码与 1143 完全一致，仅变量名从字符串改为整数数组：

```python
def maxUncrossedLines(nums1: list[int], nums2: list[int]) -> int:
    m, n = len(nums1), len(nums2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if nums1[i - 1] == nums2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

---

### 双序列编辑组

#### 392. 判断子序列

**题意**：判断字符串 s 是否为字符串 t 的子序列。

**双指针解法**（O(n) 时间 O(1) 空间，面试首选）：

```python
def isSubsequence(s: str, t: str) -> bool:
    i, j = 0, 0
    while i < len(s) and j < len(t):
        if s[i] == t[j]:
            i += 1
        j += 1
    return i == len(s)
```

**DP 解法**（为后续编辑距离题铺垫）：

`dp[i][j]` = s[0..i-1] 在 t[0..j-1] 中能匹配上的最长长度。
不相等时只允许 t 删字符（`dp[i][j-1]`），s 不能动：

```python
def isSubsequence_dp(s: str, t: str) -> bool:
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = dp[i][j - 1]   # 只能删 t 中字符，s 不动
    return dp[m][n] == m
```

---

#### 115. 不同的子序列

**题意**：计算字符串 s 的子序列中，等于 t 的子序列共有多少种（返回方案数）。

**dp 定义**：`dp[i][j]` = s[0..i-1] 的子序列中 t[0..j-1] 出现的次数。

**初始化**：`dp[i][0] = 1`（任何 s 前缀对空串 t 都有 1 种方案：全删）；`dp[0][j] = 0`（j>0）。

**递推**：

```python
def numDistinct(s: str, t: str) -> int:
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = 1   # s 的任意前缀对空串只有1种方案
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # 统一写法：dp[i-1][j] 始终存在（不用 s[i-1]）
            # 若相等，额外累加 dp[i-1][j-1]（用 s[i-1] 匹配 t[j-1]）
            dp[i][j] = dp[i - 1][j] + (dp[i - 1][j - 1] if s[i - 1] == t[j - 1] else 0)
    return dp[m][n]
```

核心在于：相等时有**两种独立方案**——用或不用 s[i-1] 匹配 t[j-1]，两者方案数相加。

---

#### 583. 两个字符串的删除操作

**题意**：对 word1 和 word2 各自删最少字符，使二者相同，返回总删除步数。

**方法二（转化为 LCS，推荐）**：删除后剩余的公共部分就是 LCS，删去的字符数为：

```
总删除数 = len(word1) + len(word2) - 2 × LCS(word1, word2)
```

```python
def minDistance_583(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    return m + n - 2 * lcs
```

**方法一（直接 DP）**：`dp[i][j]` 定义为使 word1[0..i-1] 与 word2[0..j-1] 相等的最少删除数，
初始化 `dp[i][0]=i`，`dp[0][j]=j`，不相等时 `dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + 1`。

---

#### 72. 编辑距离

**题意**：三种操作（插入/删除/替换）将 word1 转为 word2，求最少操作数。

**dp 定义**：`dp[i][j]` = 将 word1[0..i-1] 转换为 word2[0..j-1] 的最少编辑次数。

**初始化**：`dp[i][0] = i`（全删），`dp[0][j] = j`（全插）。

```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]        # 相等：无需操作，直接继承
            else:
                dp[i][j] = min(
                    dp[i - 1][j],       # 删 word1[i-1]        → 看上方
                    dp[i][j - 1],       # 在 word1 中插入字符  → 看左方
                    dp[i - 1][j - 1]    # 替换 word1[i-1]      → 看左上
                ) + 1
    return dp[m][n]
```

**三方向记忆口诀**：**上删左增斜替换**。

**表格推导示例**（word1="horse", word2="ros"）：

```
        ""  r   o   s
""  [   0   1   2   3  ]
h   [   1   1   2   3  ]
o   [   2   2   1   2  ]
r   [   3   2   2   2  ]
s   [   4   3   3   2  ]
e   [   5   4   4   3  ]

答案：dp[5][3] = 3
路径：horse → rorse（替换 h→r）→ rose（删 r）→ ros（删 e）
```

---

## 统一对比

| 题号 | 题目 | 分型 | dp 定义 | 相等时 | 不等时 | 答案位置 |
|:---:|:---|:---|:---|:---|:---|:---:|
| 300 | 最长递增子序列 | 单序列 | `dp[i]`=以i结尾LIS长 | `max(dp[j]+1)` | 跳过 | `max(dp)` |
| 674 | 最长连续递增 | 单序列 | `dp[i]`=以i结尾连续递增长 | `dp[i-1]+1` | 重置为 1 | `max(dp)` |
| 718 | 最长重复子数组 | 双序列-连续 | `dp[i][j]`=以i-1,j-1结尾公共子数组长 | `dp[i-1][j-1]+1` | `0` | `max(全表)` |
| 1143 | 最长公共子序列 | 双序列-公共 | `dp[i][j]`=前i与前j的LCS长 | `dp[i-1][j-1]+1` | `max(上,左)` | `dp[m][n]` |
| 1035 | 不相交的线 | 双序列-公共 | 同 1143 | 同 1143 | 同 1143 | `dp[m][n]` |
| 392 | 判断子序列 | 双序列-编辑 | `dp[i][j]`=s前i在t前j中匹配长 | `dp[i-1][j-1]+1` | `dp[i][j-1]` | `==m` |
| 115 | 不同的子序列 | 双序列-编辑 | `dp[i][j]`=s前i中t前j出现次数 | `dp[i-1][j-1]+dp[i-1][j]` | `dp[i-1][j]` | `dp[m][n]` |
| 583 | 两字符串删除 | 双序列-编辑 | 转化为 LCS | — | — | `m+n-2×LCS` |
| 72 | 编辑距离 | 双序列-编辑 | `dp[i][j]`=w1前i转w2前j最少操作 | `dp[i-1][j-1]` | `min(上,左,斜上)+1` | `dp[m][n]` |

---

## 口诀

```
子序列 DP 分三型，认清类型定模板：

单序列：结尾定义是根基
  300  双层循环枚举更小 j，答案取 max(dp)，O(n²)
  674  只看相邻，不等就重置，O(n)
  718  两数组版 674，不等归零，答案扫全表

双序列公共：斜上相等加一步
  1143  不等取 max(上, 左)，答案在右下角
  1035  1143 换皮，直接套模板

双序列编辑：从简到繁四阶梯
  392   判断：不等只删 t，最后比 dp==len(s)
  115   计数：相等累加两项，用或不用都算
  583   删除：转化为 m+n-2×LCS，一行搞定
  72    全能：上删左增斜替换，三向取 min 加 1
```

---

## 总结与扩展

**核心规律**：

子序列类 DP 的本质是**状态定义决定转移方向**。

- 单序列 `dp[i]` 定义为"以 i 结尾"，最优解必须用 `max(dp)` 收集；
- 双序列 `dp[i][j]` 采用 i-1、j-1 下标，使空串边界天然为 0，无需特殊处理；
- 末尾字符**相等**时的处理是所有题目的分水岭：公共类取斜上角 +1，编辑类直接继承，计数类累加两来源。

**进阶方向**：

| 方向 | 说明 |
|:---|:---|
| LIS 优化到 O(n log n) | 用二分搜索维护 patience sorting 数组，面试高频 |
| 区间 DP | 回文子序列（516）、戳气球（312），dp 定义变为 `dp[l][r]` |
| 状态机 DP | 买卖股票系列（309/714），在编辑距离基础上增加状态维度 |
| 空间压缩 | 718/1143/72 均可压为滚动数组 O(min(m,n)) 空间 |
