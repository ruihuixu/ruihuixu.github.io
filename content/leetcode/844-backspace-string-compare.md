---
title: "LeetCode 844. 比较含退格的字符串：逆向双指针的 O(1) 空间解法"
date: 2026-01-24T11:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "String"
  - "Two Pointers"
  - "Reverse Traversal"
  - "Java"
categories:
  - "LeetCode"
description: "从后往前双指针 + skip 计数器，O(1) 空间比较退格后的最终字符串。核心心智：逆向扫描避免栈，用计数器模拟退格消除。"
---

> 题目链接：[844. Backspace String Compare](https://leetcode.cn/problems/backspace-string-compare/description/)
>
> 难度：简单 ｜ 标签：字符串、双指针

## 题目描述

给定字符串 `s` 和 `t`，它们被输入到空白文本编辑器中：

- 普通字符会被直接输入
- `#` 表示退格（删除前一个字符）
- 对空文本输入退格，文本仍为空

若两者最终文本相同，返回 `true`。

## 解题思路：从后往前双指针（O(1) 空间）

如果从左往右模拟，最直观是用栈，但会用到 $O(N)$ 空间。

更优写法：从右往左扫描，用 `skip` 计数“还需要跳过多少个有效字符”。

对每个字符串维护：

- 指针 `i/j`：当前扫描位置（从末尾开始）
- `skipS/skipT`：待退格计数

规则：

- 遇到 `#`：`skip += 1`，指针左移
- 遇到普通字符：
  - 若 `skip > 0`，说明该字符会被退格掉：`skip -= 1`，指针左移
  - 若 `skip == 0`，这是当前“可见字符”，可以拿来比较

每轮取出 `s` 与 `t` 的下一个可见字符，比对是否相同；直到两边都耗尽。

```java
public boolean backspaceCompare(String s, String t) {
    int i = s.length() - 1;
    int j = t.length() - 1;
    int skipS = 0;
    int skipT = 0;

    while (i >= 0 || j >= 0) {
        // 找到 s 的下一个有效字符
        while (i >= 0) {
            char c = s.charAt(i);
            if (c == '#') {
                skipS++;
                i--;
            } else if (skipS > 0) {
                skipS--;
                i--;
            } else {
                break;
            }
        }

        // 找到 t 的下一个有效字符
        while (j >= 0) {
            char c = t.charAt(j);
            if (c == '#') {
                skipT++;
                j--;
            } else if (skipT > 0) {
                skipT--;
                j--;
            } else {
                break;
            }
        }

        // 比较当前有效字符
        char cs = (i >= 0) ? s.charAt(i) : 0;
        char ct = (j >= 0) ? t.charAt(j) : 0;
        if (cs != ct) return false;

        i--;
        j--;
    }

    return true;
}
```

### 图解（以 s = "ab##", t = "c#d#" 为例）

```text
s = "ab##"  →  最终结果：""（两个字符都被退格）
t = "c#d#"  →  最终结果：""（两个字符都被退格）

逆向扫描过程：

s: a  b  #  #
   ↑  ↑  ↑  ↑
   0  1  2  3

从右往左扫描 s：
i=3: s[3]='#' → skipS=1, i=2
i=2: s[2]='#' → skipS=2, i=1
i=1: s[1]='b', skipS=2 → 被退格，skipS=1, i=0
i=0: s[0]='a', skipS=1 → 被退格，skipS=0, i=-1
结果：s 无有效字符

从右往左扫描 t：
j=3: t[3]='#' → skipT=1, j=2
j=2: t[2]='d', skipT=1 → 被退格，skipT=0, j=1
j=1: t[1]='#' → skipT=1, j=0
j=0: t[0]='c', skipT=1 → 被退格，skipT=0, j=-1
结果：t 无有效字符

两者都为空，返回 true
```

### 关键点

- **为什么从右往左？** 因为退格是"向前删除"，从右往左扫描时，`#` 的影响范围是它左边的字符
- **为什么用 skip 计数器？** 避免使用栈，用计数器记录"还需要跳过多少个字符"
- **循环条件**：`while (i >= 0 || j >= 0)`，确保两个字符串都扫描完
- **边界处理**：当 `i < 0` 或 `j < 0` 时，用字符 `0`（或任意相同值）表示"已无字符"

---

## 易错点清单（Bug-Free Guide）

### 1. 循环条件错误

```java
// ❌ 错误：只有两者都有效时才比较，会漏掉一个字符串先结束的情况
while (i >= 0 && j >= 0) {
    // ...
}

// ✅ 正确：只要有一个字符串还有字符，就继续
while (i >= 0 || j >= 0) {
    // ...
}
```

### 2. 边界字符处理错误

```java
// ❌ 错误：当 i < 0 时访问 s.charAt(i) 会越界
char cs = s.charAt(i);
char ct = t.charAt(j);

// ✅ 正确：用三元运算符处理边界
char cs = (i >= 0) ? s.charAt(i) : 0;
char ct = (j >= 0) ? t.charAt(j) : 0;
```

### 3. 内层循环条件遗漏

```java
// ❌ 错误：没有判断 i >= 0，可能越界
while (true) {
    char c = s.charAt(i);
    if (c == '#') {
        skipS++;
        i--;
    } else if (skipS > 0) {
        skipS--;
        i--;
    } else {
        break;
    }
}

// ✅ 正确：每次循环都判断 i >= 0
while (i >= 0) {
    char c = s.charAt(i);
    if (c == '#') {
        skipS++;
        i--;
    } else if (skipS > 0) {
        skipS--;
        i--;
    } else {
        break;
    }
}
```

### 4. 忘记移动指针

```java
// ❌ 错误：比较完后忘记移动指针，导致死循环
if (cs != ct) return false;
// 忘记 i-- 和 j--

// ✅ 正确：比较完后必须移动指针
if (cs != ct) return false;
i--;
j--;
```

### 5. skip 计数器未重置

```java
// ❌ 错误：两个字符串共用一个 skip 变量
int skip = 0;
// 处理 s 时用 skip
// 处理 t 时也用 skip（错误！）

// ✅ 正确：每个字符串独立的 skip 计数器
int skipS = 0;
int skipT = 0;
```

---

## 口诀式总结：逆向双指针的万能模板

```text
【逆向双指针 + 计数器模板】

1. 为什么逆向？
   - 正向需要栈（O(n) 空间）
   - 逆向用计数器（O(1) 空间）
   - 退格影响的是"前面"的字符，从后往前扫描更自然

2. 核心不变量
   - skip：还需要跳过多少个有效字符
   - 遇到 '#'：skip++（获得消除令牌）
   - 遇到字符且 skip > 0：skip--（使用令牌）
   - 遇到字符且 skip == 0：这是有效字符

3. 双指针同步
   while (i >= 0 || j >= 0) {
       // 找 s 的下一个有效字符
       while (i >= 0 && (s[i] == '#' || skipS > 0)) { ... }

       // 找 t 的下一个有效字符
       while (j >= 0 && (t[j] == '#' || skipT > 0)) { ... }

       // 比较有效字符
       if (s[i] != t[j]) return false;

       // 移动指针
       i--; j--;
   }

4. 边界处理
   - 用三元运算符：(i >= 0) ? s.charAt(i) : 0
   - 或者在内层循环判断：while (i >= 0 && ...)

【决策树】
- 看到"退格/删除" + "O(1) 空间" → 逆向扫描 + 计数器
- 看到"比较两个字符串" → 双指针同步扫描
- 看到"栈模拟" → 考虑能否用计数器替代
```

---

## 复杂度分析

- **时间复杂度**：$O(N + M)$，其中 $N,M$ 分别为 `s`、`t` 的长度，每个指针只会单调左移。
- **空间复杂度**：$O(1)$，只使用常数额外变量。

---

## 总结

这道题的核心是**用逆向扫描 + 计数器替代栈**，实现 O(1) 空间复杂度。

**关键洞察**：
- 退格影响的是"前面"的字符，从后往前扫描时，`#` 的作用范围是它左边
- 用 `skip` 计数器记录"还需要跳过多少个字符"，避免使用栈
- 双指针同步扫描，每次取出两个字符串的下一个有效字符进行比较

**扩展应用**：
- **1047. 删除字符串中的所有相邻重复项**：可以用栈，也可以用双指针原地修改
- **20. 有效的括号**：经典栈问题，但如果要求 O(1) 空间，可以考虑类似的计数器思路（仅限特定情况）

掌握逆向扫描思维，字符串处理问题更上一层楼！
