---
title: "844. 比较含退格的字符串"
draft: false
tags:
    - "Algorithm"
    - "Two Pointers"
    - "String"
    - "Java"
categories:
  - "LeetCode"
description: "从后往前双指针 + skip 计数，O(1) 空间比较退格后的最终字符串。"
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

## 复杂度分析

- **时间复杂度**：$O(N + M)$，其中 $N,M$ 分别为 `s`、`t` 的长度，每个指针只会单调左移。
- **空间复杂度**：$O(1)$，只使用常数额外变量。
