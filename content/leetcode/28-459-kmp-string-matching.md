---
title: "LeetCode 28 / 459：KMP 算法详解——从暴力匹配到前缀表的时空跳跃"
date: 2026-01-28T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Two Pointers"
  - "String"
  - "Java"
categories:
  - "LeetCode"
description: "KMP 的核心不是匹配，而是'不回退'。本文通过前缀表建立有限状态机模型：28 题建立 KMP 标准模板，459 题利用 Next 数组的循环节性质，彻底解决字符串匹配与周期性问题。"
---

> 题目链接：
>
> - [28. 找出字符串中第一个匹配项的下标](https://leetcode.cn/problems/find-the-index-of-the-first-occurrence-in-a-string/)
> - [459. 重复的子字符串](https://leetcode.cn/problems/repeated-substring-pattern/)
>
> 难度：中等/简单 ｜ 标签：字符串、KMP、前缀表

## 核心心智：前缀表——时空跳跃的指南针

字符串匹配的暴力解法是 $O(M \times N)$，因为每次匹配失败，主串指针 `i` 都要回退（傻傻地重来）。
**KMP (Knuth-Morris-Pratt)** 的伟大之处在于：**主串指针 `i` 永远不回退**，只回退模式串指针 `j`。

如何做到？依靠 **前缀表（Prefix Table / Next Array）**。

1.  **物理意义**：`next[j]` 告诉我们，“如果在位置 `j` 匹配失败了，我不必回到起点 `0`，而是可以直接跳到位置 `next[j-1]` 继续比”。
2.  **数学定义**：`next[i]` 表示子串 `s[0...i]` 的 **最长相等前后缀的长度**。
    - **前缀**：包含首字符，不包含尾字符的所有子串。
    - **后缀**：包含尾字符，不包含首字符的所有子串。
    - **相等**：前缀和后缀内容完全一样。

掌握了 KMP，你不仅能解决匹配问题（28），还能利用前缀表的数学性质解决周期性问题（459）。

---

## 一、标准模板：实现 strStr()（LeetCode 28）

### 题目描述

给你两个字符串 `haystack` 和 `needle` ，请你在 `haystack` 字符串中找出 `needle` 字符串的第一个匹配项的下标（下标从 0 开始）。如果不存在，则返回 -1 。

### 核心思路：构建 Next 数组 + 状态机匹配

KMP 的实现分为两步：
1.  **自查（构建 Next）**：模式串 `needle` 自己跟自己比，计算出每一位匹配失败后应该回退到哪里。
2.  **匹配（Matching）**：主串 `haystack` 跟模式串 `needle` 比，利用 Next 数组加速。

**关于 Next 数组的减一问题**：
KMP 有多种实现方式（右移一位、减一、原值）。
为了逻辑统一且便于理解，本文采用 **“原值法”**：`next[i]` 直接存储最长相等前后缀的长度。
- 跳转逻辑：如果 `j` 处不匹配，则找前一位 `j-1` 的最长前后缀长度，即 `j = next[j-1]`。

### 代码实现

```java
public int strStr(String haystack, String needle) {
    if (needle.length() == 0) return 0;
    
    int[] next = new int[needle.length()];
    getNext(next, needle);
    
    int j = 0; // j 指向模式串 needle
    for (int i = 0; i < haystack.length(); i++) { // i 指向主串，永不回退
        // 1. 不匹配时的处理（while 循环回退）
        // 如果当前字符不同，且 j > 0（还可以回退），则 j 回退到 next[j-1]
        while (j > 0 && haystack.charAt(i) != needle.charAt(j)) {
            j = next[j - 1];
        }
        
        // 2. 匹配时的处理
        if (haystack.charAt(i) == needle.charAt(j)) {
            j++;
        }
        
        // 3. 匹配完成
        if (j == needle.length()) {
            return i - needle.length() + 1;
        }
    }
    
    return -1;
}

/**
 * 构建 Next 数组的核心逻辑
 * next[i] 表示前缀 s[0...i] 的最长相等前后缀长度
 */
private void getNext(int[] next, String s) {
    // 初始化：j 指向前缀末尾位置（也代表当前最长相等前后缀长度）
    // i 指向后缀末尾位置
    int j = 0;
    next[0] = 0; // 第一个字符没有前后缀，长度为 0
    
    for (int i = 1; i < s.length(); i++) {
        // 1. 前后缀不相同：j 回退
        // 这里的逻辑和匹配过程惊人地一致！因为找前后缀本质上就是自己匹配自己
        while (j > 0 && s.charAt(i) != s.charAt(j)) {
            j = next[j - 1];
        }
        
        // 2. 前后缀相同：j 前移
        if (s.charAt(i) == s.charAt(j)) {
            j++;
        }
        
        // 3. 更新 next 值
        next[i] = j;
    }
}
```

### 图解：Next 数组构建过程

以 `s = "aabaaf"` 为例：

```text
i=1, s[1]='a', s[j=0]='a': 相同 -> j++, next[1]=1 (前缀"a", 后缀"a")
i=2, s[2]='b', s[j=1]='a': 不同 -> j=next[0]=0
     s[2]='b', s[j=0]='a': 不同 -> j=0 -> next[2]=0
i=3, s[3]='a', s[j=0]='a': 相同 -> j++, next[3]=1
i=4, s[4]='a', s[j=1]='a': 相同 -> j++, next[4]=2 ("aa" == "aa")
i=5, s[5]='f', s[j=2]='b': 不同 -> j=next[1]=1
     s[5]='f', s[j=1]='a': 不同 -> j=next[0]=0
     s[5]='f', s[j=0]='a': 不同 -> j=0 -> next[5]=0

最终 next 数组: [0, 1, 0, 1, 2, 0]
```

---

## 二、抽象推论：重复的子字符串（LeetCode 459）

### 题目描述

给定一个非空的字符串 `s`，检查是否可以通过由它的一个子串重复多次构成。

**示例**：`"abab"` -> True；`"aba"` -> False；`"abcabcabc"` -> True。

### 核心思路：Next 数组的数学性质

这道题如果是暴力解法，需要枚举所有可能的子串长度 `len`，时间复杂度 $O(N^2)$。但利用 KMP 的 next 数组，可以 $O(N)$ 解决。

**数学推论**：

假设字符串 `s` 的长度为 `len`，最长相等前后缀长度为 `next[len-1]`。如果 `s` 是由重复子串构成的，那么：

- 最小重复单元长度 `unit_len = len - next[len-1]`。
- **充要条件**：`next[len-1] > 0` 且 `len % unit_len == 0`。

**直观理解**：

- `s = "abcabcabc"` (len=9)
- 最长相等前后缀是 `"abcabc"` (next[8]=6)。
- `unit_len = 9 - 6 = 3` (`"abc"`)。
- 因为 next 数组把最长的前后缀对齐了，剩下的错位部分就是最小重复单元！

### 代码实现

```java
public boolean repeatedSubstringPattern(String s) {
    if (s.length() == 0) return false;
    
    int len = s.length();
    int[] next = new int[len];
    getNext(next, s); // 直接复用上面的 getNext 函数
    
    // 核心判断逻辑
    // 1. next[len-1] > 0：说明有相等的前后缀（至少有重复部分）
    // 2. len % (len - next[len-1]) == 0：说明重复单元能整除总长度
    if (next[len - 1] > 0 && len % (len - next[len - 1]) == 0) {
        return true;
    }
    return false;
}

// getNext 函数同上，不再重复粘贴
```

### 图解：循环节推导

```text
字符串: "a b a b a b a b"
下标:   0 1 2 3 4 5 6 7
Next:   0 0 1 2 3 4 5 6

len = 8
next[7] = 6 (最长相等前后缀 "ababab")
unit_len = 8 - 6 = 2 ("ab")

8 % 2 == 0 -> True!

如果不满足：
字符串: "a b a c"
Next:   0 0 1 0
len=4, next[3]=0 -> False
```

---

## 三、统一对比与抽象升级

| 特性 | 匹配问题 (28) | 周期问题 (459) |
|------|---------------|----------------|
| Next 数组作用 | 指导回退位置，避免重复匹配 | 计算最长重叠，推导最小循环节 |
| 关注点 | 过程：j 怎么跳 | 结果：next[len-1] 的值 |
| 核心公式 | `j = next[j-1]` | `len % (len - next[len-1]) == 0` |

**抽象总结**：KMP 不仅仅是一个匹配算法，它通过 next 数组对字符串的**自相似性（Self-Similarity）**进行了极度压缩。任何关于"前缀"、"后缀"、"重复"、"周期"的问题，都可以往 next 数组上想。

---

## 四、易错点清单（Bug-Free Guide）

### 1. Next 数组的越界与回退

```java
// ❌ 错误：死循环或越界
while (s.charAt(i) != s.charAt(j)) {
    j = next[j]; // 如果 j 已经是 0，这里会死循环或越界
}

// ✅ 正确：必须判断 j > 0
while (j > 0 && s.charAt(i) != s.charAt(j)) {
    j = next[j - 1]; // 回退到前一位的 next 值
}
```

### 2. Next 数组的含义混淆

网上有三种 Next 数组写法，面试时必须选定一种并坚持到底，千万别混用：

- **原值法（推荐）**：next[i] 就是最长长度。回退找 next[j-1]。
- **右移法**：next[i] 是 s[0...i-1] 的最长长度。
- **减一法**：next[i] 是最长长度减一。

**口诀**：前缀表不减一，回退看前一位。

### 3. 空串处理

```java
// 28 题要求 needle 为空返回 0
if (needle.length() == 0) return 0;
// 如果不加这句，new int[0] 虽然没问题，但逻辑上可能有坑
```

---

## 五、口诀式总结

```text
【KMP 算法通关诀】

求 Next，双指针：i 往前走，j 往回退。
不匹配，看前位：j 变成 next[j-1]。
匹配了，齐步走：i 和 j 同时加一。
循环节，有公式：len 减 next 便是基。
```

---

## 总结

KMP 是字符串算法的分水岭。跨过这道坎，你对"状态机"、"空间换时间"的理解将上升一个台阶。

在实际工程中（如 `String.indexOf`），虽然未必直接用 KMP（可能用 Boyer-Moore 等更优算法），但 KMP 所代表的**利用已知信息减少无效计算**的思想，是算法设计的灵魂。

至此，我们的字符串三部曲（基础操作 -> 高阶反转 -> 模式匹配）已全部完成。建议将这三篇笔记结合起来复习，建立完整的字符串知识图谱。

### 扩展应用

- **LeetCode 1392. 最长快乐前缀**：本质就是求 `next[len-1]`
- **LeetCode 214. 最短回文串**：KMP + 回文串的结合