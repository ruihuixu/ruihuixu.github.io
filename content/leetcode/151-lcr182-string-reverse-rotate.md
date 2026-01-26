
---
title: "LeetCode 151 / LCR 182：字符串的高阶反转——局部与整体的辩证关系"
date: 2026-01-27T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Two Pointers"
  - "Collision Pointers"
  - "String"
  - "In-Place"
  - "Java"
categories:
  - "LeetCode"
description: "如何用 O(1) 空间实现单词顺序翻转或左旋？核心在于理解'负负得正'的几何意义：局部反转 + 整体反转 = 顺序重排。本文统一'清洗数据 -> 局部操作 -> 整体操作'的解题模板。"
---

> 题目链接：
>
> - [151. 反转字符串中的单词](https://leetcode.cn/problems/reverse-words-in-a-string/)
> - [LCR 182. 动态口令 (左旋转字符串)](https://leetcode.cn/problems/zuo-xuan-zhuan-zi-fu-chuan-lcof/)
>
> 难度：中等 ｜ 标签：双指针、字符串

## 核心心智：线性代数在字符串中的投影

在上一篇中，我们掌握了基础的“整体反转”。但在实际面试中，往往要求我们对字符串的**部分结构**进行重排。

这里有一个通用的数学模型，我称之为**“反转的几何律”**（类似线性代数中的转置性质）：

$$(A^T B^T)^T = BA$$

- **含义**：如果你想把前后两部分内容 $A$ 和 $B$ 交换位置变成 $BA$，你不需要开辟新空间去搬运。
- **操作**：
    1. 把 $A$ 局部反转得到 $A^T$。
    2. 把 $B$ 局部反转得到 $B^T$。
    3. 把整体 $(A^T B^T)$ 再反转一次，神奇的事情发生了，结果变成了 $BA$。

**应用场景**：
- **单词翻转（LeetCode 151）**：单词内部顺序不变，但单词间的顺序反了。可以看作是 $Word_1 Word_2 \dots Word_n$ 变成了 $Word_n \dots Word_2 Word_1$。
- **左旋字符串（LCR 182）**：$ABCDEFG$ 左旋 2 位变成 $CDEFGAB$。

---

## 一、综合演练：反转字符串中的单词（LeetCode 151）

### 题目描述

给你一个字符串 `s` ，请你反转字符串中 **单词** 的顺序。
**示例**：输入 `"  hello world  "`，输出 `"world hello"`。
**要求**：如果字符串在使用 Java，请尝试在**不使用额外空间**（即不使用 `split` 等库函数，操作可变容器）的情况下完成。

### 核心思路：流水线作业

这道题是字符串处理的“集大成者”，它其实是由三个基础问题组合而成的：

1.  **清洗数据（Data Cleaning）**：
    - 移除首尾空格、多余的中间空格。
    - **复用模型**：这不就是 **[LeetCode 27. 移除元素]** 的变体吗？利用**快慢指针**维护有效边界。

2.  **整体反转（Global Reverse）**：
    - 将整个字符串反转，把 `"hello world"` 变成 `"dlrow olleh"`。
    - 此时单词顺序对了（world 在前了），但单词内部倒序了。

3.  **局部反转（Local Reverse）**：
    - 再次遍历，识别每个单词的边界，将其单独反转回正。
    - `"dlrow"` -> `"world"`，`"olleh"` -> `"hello"`。

**物理类比**：
想象一列火车，车厢顺序排错了，而且车厢之间还塞满了垃圾（空格）。
1. **清理**：先把垃圾扔掉，车厢连紧。
2. **掉头**：整列火车掉头，车头变车尾。
3. **调整**：每节车厢内部的乘客再转个身。

### 代码实现（Hardcore 模式）

为了展示算法能力，我们不使用 `s.trim().split("\\s+")` 这种作弊写法，而是老老实实操作 `StringBuilder` 模拟 `char[]` 的原地操作。

```java
public String reverseWords(String s) {
    // 1. 将 String 转换为 StringBuilder，作为我们要操作的"物理内存"
    StringBuilder sb = removeExtraSpaces(s);
    
    // 2. 执行整体反转
    reverseString(sb, 0, sb.length() - 1);
    
    // 3. 执行局部单词反转
    reverseEachWord(sb);
    
    return sb.toString();
}

/**
 * 步骤一：移除多余空格
 * 复用 LeetCode 27 的快慢指针思想
 */
private StringBuilder removeExtraSpaces(String s) {
    int start = 0;
    int end = s.length() - 1;
    
    // 去除首尾空格的逻辑（为了确定快指针范围）
    while (start <= end && s.charAt(start) == ' ') start++;
    while (end >= start && s.charAt(end) == ' ') end--;
    
    StringBuilder sb = new StringBuilder();
    // 这里的 sb 充当了"慢指针"写入的角色
    
    while (start <= end) {
        char c = s.charAt(start);
        // 如果当前字符不是空格，或者（它是空格 但 sb 的最后一个字符不是空格）
        // 这样保证了不会连续写入两个空格
        if (c != ' ' || sb.charAt(sb.length() - 1) != ' ') {
            sb.append(c);
        }
        start++;
    }
    return sb;
}

/**
 * 步骤二：基础反转函数（复用 LeetCode 344）
 */
private void reverseString(StringBuilder sb, int start, int end) {
    while (start < end) {
        char temp = sb.charAt(start);
        sb.setCharAt(start, sb.charAt(end));
        sb.setCharAt(end, temp);
        start++;
        end--;
    }
}

/**
 * 步骤三：反转每个单词
 */
private void reverseEachWord(StringBuilder sb) {
    int start = 0;
    int end = 1;
    int n = sb.length();
    
    while (start < n) {
        // end 指向单词末尾的下一个位置（空格或字符串末尾）
        while (end < n && sb.charAt(end) != ' ') {
            end++;
        }
        
        // 反转当前单词 [start, end - 1]
        reverseString(sb, start, end - 1);
        
        // 更新指针，找下一个单词
        start = end + 1;
        end = start + 1;
    }
}
```

### 图解

```text
输入: "  hello   world  "

1. 清洗数据 (removeExtraSpaces):
   变成: "hello world"

2. 整体反转 (reverseString):
   变成: "dlrow olleh"
          ^^^^^ ^^^^^

3. 局部反转 (reverseEachWord):
   遇到空格前，识别单词 "dlrow" -> 反转 -> "world"
   变成: "world olleh"
   
   继续向后，识别单词 "olleh" -> 反转 -> "hello"
   变成: "world hello"
```

---

## 二、模型应用：左旋转字符串（LCR 182）

### 题目描述

字符串的左旋转操作是把字符串前面的若干个字符转移到字符串的尾部。

**示例**：输入 `s = "abcdefg"`, `k = 2`，输出 `"cdefgab"`。

### 核心思路：三次反转法

这道题如果使用辅助空间，拼接 `s.substring(k) + s.substring(0, k)` 非常简单。但如果要原地操作（模拟），它就是"反转几何律"的标准应用。

我们将字符串分为两部分：

- $A$：前 $k$ 个字符 [0, k-1]。
- $B$：剩余字符 [k, n-1]。

目标是将 $AB$ 变为 $BA$。

**操作步骤**：

1. 反转 $A$：[0, k-1]。
2. 反转 $B$：[k, n-1]。
3. 反转整体：[0, n-1]。

（也可以先整体反转，再反转两部分，效果一样，只是切割点变了）

### 代码实现

```java
public String dynamicPassword(String password, int target) {
    // 转换为 StringBuilder 进行原地操作模拟
    StringBuilder sb = new StringBuilder(password);
    
    // 1. 反转前 target 个字符
    reverseString(sb, 0, target - 1);
    
    // 2. 反转剩余字符
    reverseString(sb, target, sb.length() - 1);
    
    // 3. 整体反转
    reverseString(sb, 0, sb.length() - 1);
    
    return sb.toString();
}

// 依然复用那个万能的 reverseString
private void reverseString(StringBuilder sb, int start, int end) {
    while (start < end) {
        char temp = sb.charAt(start);
        sb.setCharAt(start, sb.charAt(end));
        sb.setCharAt(end, temp);
        start++;
        end--;
    }
}
```

### 图解

```text
输入: s = "abcdefg", k = 2
目标: "cdefgab"

区间划分: A="ab", B="cdefg"

1. 反转 A ("ab" -> "ba"):
   "ba cdefg"

2. 反转 B ("cdefg" -> "gfedc"):
   "ba gfedc"

3. 整体反转 ("bagfedc" -> "cdefgab"):
   "cdefgab"  <-- 成功！
```

---

## 三、统一对比与抽象升级

| 题目 | 核心操作 | 分割逻辑 | 难点 |
|------|----------|----------|------|
| 151. 翻转单词 | 先整体反转，再局部反转 | 按照空格分割 | 数据清洗（快慢指针） |
| LCR 182. 左旋 | 先局部反转，再整体反转 | 按照索引 k 分割 | 确定反转区间边界 |

**抽象模板**：解决"部分重排"问题的通解是**分治 + 组合**。

1. **分**：找到逻辑上的断点（空格或索引）。
2. **治**：对每一部分进行逆序处理（消除内部顺序影响）。
3. **合**：通过整体逆序，调整块与块之间的相对位置。

---

## 四、易错点清单（Bug-Free Guide）

### 1. 151 题的数据清洗逻辑

```java
// ❌ 错误：简单的 if (c == ' ') continue
// 这样会把单词中间的空格也全部删掉，变成 "helloworld"

// ✅ 正确：保留一个空格
if (c != ' ' || sb.charAt(sb.length() - 1) != ' ')
// 只有当当前是空格，且前一个也是空格时，才跳过。
```

### 2. 反转函数的区间定义

```java
// ❌ 错误：左旋时，第二段区间写错
reverse(sb, target + 1, n); 

// ✅ 正确：
// 第一段：0 到 target - 1
// 第二段：target 到 n - 1
// 必须严格画图确认索引
```

### 3. Java API 的性能陷阱

```java
// ❌ 错误：在循环中疯狂使用 String + String
for (int i = 0; i < n; i++) res += words[i] + " ";

// ✅ 正确：
// Java 编译器虽然会优化，但在复杂逻辑下，
// 显式使用 StringBuilder 永远是最佳实践。
```

---

## 五、口诀式总结

```text
【字符串高阶反转】

单词翻转三步走：去空格、翻整体、翻单词。
左旋右旋几何律：翻左边、翻右边、翻全部。
负负得正记心间：两次反转回原序，位置变了序没变。
```

---

## 总结

如果说上一篇（344/541）是在练习挥刀的基本动作，那么这一篇（151/182）就是在练习连招。

151 题强迫你把**快慢指针（去空格）**和**双指针（反转）**结合在一个流程中，这是面试中非常看重的代码掌控力。LCR 182 则展示了算法的数学美感，用简单的操作组合解决移位问题。

掌握了"反转"的全部奥义后，下一篇我们将进入字符串匹配的深水区——KMP 算法。那里的双指针将不再是对撞或倒序，而是并在前行中发生的时空跳跃。

### 扩展应用

- **LeetCode 189. 轮转数组**：这其实就是 LCR 182 的数组版本，完全一样的三次反转法。
- **LeetCode 186. 翻转字符串中的单词 II**：151 的简化版（输入已经是 char[]），更纯粹地考察三次反转。