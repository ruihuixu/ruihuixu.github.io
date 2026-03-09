---
title: "KMP 字符串匹配：前缀表的两种应用"
date: 2026-03-09T10:00:00+08:00
draft: false
slug: "kmp-string"
tags:
  - "Algorithm"
  - "String"
  - "KMP"
  - "Python"
categories:
  - "LeetCode"
description: "涵盖 LeetCode 28/459。KMP 核心是主串指针永不回退，靠前缀表（next 数组）实现：28 建立标准匹配模板，459 利用 next[len-1] 推导字符串周期，同一套前缀表解决两类问题。"
---

> **本文涵盖**：LeetCode 28 / 459
>
> **难度**：中等 / 简单 ｜ **关键词**：前缀表、next 数组、字符串周期、主串不回退

---

## 识别信号

> 看到什么特征，想到这篇笔记？

- 在主串中查找子串**第一次出现的位置**，需要优于 O(M×N) 的解法
- 判断字符串是否由某个**子串重复多次**构成（周期性问题）
- 题目涉及字符串的"前缀""后缀"相等关系，或要求"最长公共前后缀长度"
- 暴力匹配每次失败都让主串指针回退，直觉上觉得"已扫描的信息没被利用"
- 题目出现"最长快乐前缀""failure function""prefix function"等关键词，均指同一套前缀表

---

## 核心模板（速查）

### 第一段：构建 next 数组

```python
def build_next(pattern: str) -> list[int]:
    n = len(pattern)
    next_arr = [0] * n
    j = 0                           # j：前缀末尾指针，也代表当前最长前后缀长度
    for i in range(1, n):           # i：后缀末尾指针，从 1 开始向右扫
        while j > 0 and pattern[i] != pattern[j]:
            j = next_arr[j - 1]     # 失配：退到前一位的 next 值（不是 next[j]！）
        if pattern[i] == pattern[j]:
            j += 1                  # 前后缀相等：延伸一位
        next_arr[i] = j             # 记录 s[0..i] 的最长相等前后缀长度
    return next_arr
```

### 第二段：匹配（28）与周期判断（459）

```python
# 28：在主串中找子串首次出现下标
def strStr(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    m = len(needle)
    next_arr = build_next(needle)
    j = 0                               # j：模式串指针
    for i in range(len(haystack)):      # i：主串指针，永不回退
        while j > 0 and haystack[i] != needle[j]:
            j = next_arr[j - 1]         # 失配：模式串回退，主串 i 不动
        if haystack[i] == needle[j]:
            j += 1                      # 匹配：模式串前进
        if j == m:                      # 模式串走完：找到一次完整匹配
            return i - m + 1            # 匹配起点 = 当前末尾下标 - 长度 + 1
    return -1


# 459：判断是否由重复子串构成
def repeatedSubstringPattern(s: str) -> bool:
    n = len(s)
    next_arr = build_next(s)            # 对字符串自身建前缀表
    last = next_arr[n - 1]             # 整串的最长相等前后缀长度
    unit = n - last                    # 最小重复单元候选长度
    # last > 0：存在非平凡前后缀；n % unit == 0：单元能整除总长
    return last > 0 and n % unit == 0
```

### 两题速查对比

| 题号 | `build_next` 的对象 | 核心逻辑 | 返回值 |
|------|-------------------|---------|-------|
| 28   | `needle`（模式串） | 循环匹配，`j == len(needle)` 时报起点 | 首次下标或 -1 |
| 459  | `s`（字符串自身）  | 只看 `next_arr[-1]`，检查整除条件 | True / False |

> 前缀：包含首字符、不包含尾字符的所有子串；后缀：包含尾字符、不包含首字符的所有子串。`next_arr[i]` 存储的是 `s[0..i]` 中长度相等的最长前后缀对的长度，不计入整个字符串自身。

---

## ⚠️ 高频错误（先看这里）

**1. 回退时写成 `j = next_arr[j]` 而非 `j = next_arr[j - 1]`**

```python
# ❌ 错误：j 处失配，用 next_arr[j] 会多跳一位，逻辑完全错误
while j > 0 and s[i] != s[j]:
    j = next_arr[j]

# ✅ 正确：j 处失配说明"长度 j 撑不住了"，要退回 j-1 位的最长前后缀值
while j > 0 and s[i] != s[j]:
    j = next_arr[j - 1]
```

> 记忆锚点：匹配失败发生在第 `j` 位，所以看"第 `j-1` 位有多长的前后缀可以继承"。

---

**2. 忘记 `j > 0` 的守卫条件，导致负索引或死循环**

```python
# ❌ 错误：j == 0 时，Python 的 next_arr[-1] 不报错但取到了末尾元素，逻辑崩溃
while s[i] != s[j]:
    j = next_arr[j - 1]

# ✅ 正确：j == 0 时已无路可退，while 直接不进入，保持 j = 0
while j > 0 and s[i] != s[j]:
    j = next_arr[j - 1]
```

---

**3. 459 题漏掉 `last > 0`，单字符串误判为 True**

```python
# ❌ 错误：s = "a" 时 next_arr[-1]=0，unit=1，1%1==0 -> 错误返回 True
def repeatedSubstringPattern(s: str) -> bool:
    n = len(s)
    next_arr = build_next(s)
    return n % (n - next_arr[n - 1]) == 0

# ✅ 正确：必须同时要求存在相等前后缀（即真正有"重叠"才算重复）
def repeatedSubstringPattern(s: str) -> bool:
    n = len(s)
    next_arr = build_next(s)
    last = next_arr[n - 1]
    return last > 0 and n % (n - last) == 0
```

---

**4. 匹配成功后返回下标差一**

```python
# ❌ 错误：i 是最后匹配字符的下标，直接 i - m 会少 1
if j == m:
    return i - len(needle)      # 差一

# ✅ 正确：起点 = 末尾下标 - 长度 + 1
if j == m:
    return i - len(needle) + 1
```

**5. next 数组三种写法混用，导致跳转逻辑不一致**

网上常见三种 next 数组实现，回退公式各不相同，混用必然出错：

```python
# 方案 A：原值法（本文采用）
# next_arr[i] = s[0..i] 的最长相等前后缀长度
# 失配跳转：j = next_arr[j - 1]

# 方案 B：减一法
# next_arr[i] = 最长相等前后缀长度 - 1（首位初始化为 -1）
# 失配跳转：j = next_arr[j]（因为已经减一，不用再 -1）

# 方案 C：右移法
# next_arr 整体右移一位，next_arr[0] = -1，next_arr[i] = s[0..i-1] 的最长长度
# 失配跳转：j = next_arr[j]（同减一法）
```

```python
# ❌ 错误：用了原值法的 build_next，却用减一法的跳转公式
# next_arr[j] 在 j>0 时取到的是"当前位的值"，而非"应跳转目标"
while j > 0 and s[i] != s[j]:
    j = next_arr[j]   # 应为 next_arr[j - 1]

# ✅ 正确：原值法构建，原值法跳转，配套使用
while j > 0 and s[i] != s[j]:
    j = next_arr[j - 1]
```

> 口诀：**前缀表不减一，回退找前一位**。选定一种写法，从 `build_next` 到匹配/周期判断全部保持一致。

---

## 详解

### 28. 找出字符串中第一个匹配项的下标

#### 核心思路

暴力匹配每次失败都让主串指针 `i` 回退，浪费了"已匹配的前缀信息"。

KMP 的洞察：当 `haystack[i]` 与 `needle[j]` 失配时，`needle[0..j-1]` 已经与 `haystack[i-j..i-1]` 完全对齐。如果 `needle[0..j-1]` 存在长度为 `k` 的相等前后缀，那么直接把模式串向右滑动到"前缀对上后缀"的位置，下一步从 `needle[k]` 开始比较即可——主串指针 `i` 纹丝不动。

`next_arr[j-1]` 存储的正是这个 `k`，这就是前缀表的物理意义。

**一个值得注意的对称性**：`build_next` 本身的逻辑结构与匹配过程完全相同——它本质上是模式串与自身的 KMP 匹配（`i` 扫后缀末尾，`j` 追前缀末尾）。看懂了 `build_next`，`strStr` 的匹配循环无需另行理解。

#### Python 代码

```python
def build_next(pattern: str) -> list[int]:
    """构建前缀表：next_arr[i] = s[0..i] 的最长相等前后缀长度"""
    n = len(pattern)
    next_arr = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and pattern[i] != pattern[j]:
            j = next_arr[j - 1]   # 失配：利用已知前后缀信息回退，而非从头重来
        if pattern[i] == pattern[j]:
            j += 1
        next_arr[i] = j
    return next_arr


def strStr(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    m = len(needle)
    next_arr = build_next(needle)
    j = 0                              # 模式串指针
    for i in range(len(haystack)):     # 主串指针，只向前，永不回退
        while j > 0 and haystack[i] != needle[j]:
            j = next_arr[j - 1]        # 模式串回退到前后缀交界处
        if haystack[i] == needle[j]:
            j += 1
        if j == m:                     # 模式串全部匹配完成
            return i - m + 1
    return -1
```

#### 图解：build_next 过程（pattern = "aabaaf"）

```text
j 代表"当前能维持的最长前后缀长度"，i 是后缀末尾

i=1  s[1]='a', s[j=0]='a'  相同 -> j=1, next[1]=1   前缀"a" == 后缀"a"
i=2  s[2]='b', s[j=1]='a'  不同 -> j=next[0]=0
     s[2]='b', s[j=0]='a'  不同，j=0 停止 -> next[2]=0
i=3  s[3]='a', s[j=0]='a'  相同 -> j=1, next[3]=1
i=4  s[4]='a', s[j=1]='a'  相同 -> j=2, next[4]=2   前缀"aa" == 后缀"aa"
i=5  s[5]='f', s[j=2]='b'  不同 -> j=next[1]=1
     s[5]='f', s[j=1]='a'  不同 -> j=next[0]=0
     s[5]='f', s[j=0]='a'  不同，j=0 停止 -> next[5]=0

next 数组: [0, 1, 0, 1, 2, 0]
字符串:     a  a  b  a  a  f
```

#### 图解：匹配过程（haystack = "aabaabaaf"，needle = "aabaaf"）

```text
next = [0, 1, 0, 1, 2, 0]

i=0  h='a', n[j=0]='a'  匹配 -> j=1
i=1  h='a', n[j=1]='a'  匹配 -> j=2
i=2  h='b', n[j=2]='b'  匹配 -> j=3
i=3  h='a', n[j=3]='a'  匹配 -> j=4
i=4  h='a', n[j=4]='a'  匹配 -> j=5
i=5  h='b', n[j=5]='f'  失配 -> j=next[4]=2   ← 主串 i=5 不回退！
     h='b', n[j=2]='b'  匹配 -> j=3
i=6  h='a', n[j=3]='a'  匹配 -> j=4
i=7  h='a', n[j=4]='a'  匹配 -> j=5
i=8  h='f', n[j=5]='f'  匹配 -> j=6 == m=6  -> 返回 8 - 6 + 1 = 3 ✓
```

> 时间复杂度 O(M+N)，空间复杂度 O(M)（M 为模式串长度，N 为主串长度）

---

### 459. 重复的子字符串

#### 核心思路

给定字符串 `s`，判断它能否由某子串重复若干次拼成。

暴力做法枚举所有可能的子串长度，O(N²)。利用 next 数组的数学性质可以 O(N) 完成：

**关键推论**：设字符串长度为 `n`，整串最长相等前后缀长度为 `last = next_arr[n-1]`。

- 候选最小重复单元长度：`unit = n - last`
- 充要条件：`last > 0`（有非平凡前后缀）且 `n % unit == 0`（整除）

**直觉**：前缀和后缀相等意味着字符串头尾"重叠"了一段。如果这段重叠恰好使得剩余部分 `unit` 能整除总长，那么字符串正是由 `unit` 长的基本块拼成的。

#### 图解：充要条件的直觉

```text
s = "abcabcabc"  (n=9)
next_arr[-1] = 6  （前后缀 "abcabc" 相等）

前缀: [a b c a b c] a b c
后缀:  a b c [a b c a b c]
                ↑
        重叠区 = "abc"，unit = 9 - 6 = 3

9 % 3 == 0  ->  True，s 由 "abc" 重复 3 次组成

反例 s = "aba"  (n=3)
next_arr[-1] = 1  （前后缀 "a" 相等）
unit = 3 - 1 = 2
3 % 2 = 1 ≠ 0  ->  False
```

#### Python 代码

```python
def build_next(pattern: str) -> list[int]:
    n = len(pattern)
    next_arr = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and pattern[i] != pattern[j]:
            j = next_arr[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        next_arr[i] = j
    return next_arr


def repeatedSubstringPattern(s: str) -> bool:
    n = len(s)
    if n == 0:
        return False
    next_arr = build_next(s)           # 对字符串自身建前缀表
    last = next_arr[n - 1]            # 整串的最长相等前后缀长度
    unit = n - last                   # 最小重复单元候选长度
    # 双重条件缺一不可：
    #   last > 0  保证不是"重复 1 次自身"的平凡情况
    #   n % unit == 0  保证单元能恰好拼成整串
    return last > 0 and n % unit == 0
```

> 时间复杂度 O(N)，空间复杂度 O(N)

---

## 统一对比

| 维度 | 28（字符串匹配） | 459（周期判断） |
|------|----------------|----------------|
| `build_next` 作用对象 | `needle`（模式串） | `s`（字符串自身） |
| `next` 的使用方式 | 匹配循环中指导 `j` 实时回退 | 只读 `next_arr[-1]` 一个值 |
| 核心公式 | `j = next_arr[j - 1]`（失配跳转） | `last > 0 and n % (n - last) == 0` |
| 关注过程 / 结果 | 过程：每步 `j` 如何跳，主串不回退 | 结果：最终的前后缀重叠量 |
| 时间复杂度 | O(M+N) | O(N) |

**共同核心**：两题共享同一个 `build_next` 函数，next 数组本质上是对字符串"自相似性"的压缩编码——28 在匹配过程中利用它规避重复扫描，459 用它的终态值量化周期结构。`build_next` 本身也是一次 KMP 过程（模式串和自身匹配），掌握这一个函数即同时覆盖两道题。

**next 数组三种实现汇总**（面试 / 竞赛统一选定一种）：

| 实现方式 | `next_arr[i]` 的含义 | 失配跳转公式 | 推荐场景 |
|---------|-------------------|------------|--------|
| 原值法（本文） | `s[0..i]` 最长相等前后缀长度 | `j = next_arr[j - 1]` | 笔试/面试，逻辑最直观 |
| 减一法 | 最长前后缀长度 - 1 | `j = next_arr[j]` | 部分教材，与原值法等价 |
| 右移法 | `next_arr[0]=-1`，整体右移 | `j = next_arr[j]` | 特定竞赛框架 |

---

## 口诀

```text
【KMP 前缀表通关诀】

建 next：j 盯前缀末，i 扫后缀尾；
不匹配，退前位：j = next[j-1]；
匹配了，双步走：i 前进，j 也升；
j 到末，记长度：next[i] = j 落定。

匹配串：j 跟模式走，i 主串不回头；
失配时，退前位；j 到串长，返起点。

求周期：last = next 末尾值，
        unit = n - last；
last > 0，且整除，重复子串必成立。
```

---

## 总结与扩展

KMP 的伟大不在于代码长度，而在于思想：**把"已扫描的前缀信息"压缩进 next 数组，使主串指针永不回退，将 O(M×N) 的暴力降为 O(M+N)**。

两道题共用一套 `build_next`，区别仅在于"谁来调用、怎么用终态值"。下次遇到前缀/后缀/周期相关的字符串题，先写出前缀表，答案往往就在 `next_arr[-1]` 附近。

**选哪种 next 数组写法**：本文统一使用原值法（`next_arr[i]` 直接存最长前后缀长度），跳转时找 `j-1` 位。这种写法语义最透明，不需要初始化 `-1`，也不需要记忆偏移量，推荐作为默认选择。

**相关题目**：

- LeetCode 1392. 最长快乐前缀：直接返回 `build_next(s)[-1]`，一行解
- LeetCode 214. 最短回文串：对 `s + "#" + s[::-1]` 建 next，末尾值即最长回文前缀长度
- LeetCode 686. 重复叠加字符串匹配：KMP 匹配 + 计算最少拼接次数

**进阶方向**：Boyer-Moore 算法在实践中比 KMP 平均更快（最坏同为 O(N)，平均 O(N/M)）；Z 函数（Z-algorithm）是 KMP 的等价替代，`z[i]` 表示从下标 `i` 开始与整串前缀的最长公共长度，代码结构与 `build_next` 几乎镜像，适合竞赛场景快速切换。

字符串算法中，KMP 是理解"利用已知信息减少无效计算"这一思想的最佳入口，从这里出发能自然延伸到 Aho-Corasick 多模式匹配、后缀数组等更高级的结构。
