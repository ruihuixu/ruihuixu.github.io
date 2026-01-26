---
title: "LeetCode 344 / 541 / LCR 122：字符串基础操作——双指针与模拟的物理意义"
date: 2026-01-26T10:00:00+08:00
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
description: "字符串题目的两大陷阱是库函数滥用与边界控制。本文建立字符串处理的基础模型：首尾双指针（反转）、倒序双指针（填充），并解析 Java 字符串不可变性带来的工程与算法权衡。"
---

> 题目链接：
>
> - [344. 反转字符串](https://leetcode.cn/problems/reverse-string/)
> - [541. 反转字符串 II](https://leetcode.cn/problems/reverse-string-ii/)
> - [LCR 122. 路径加密 (替换空格)](https://leetcode.cn/problems/ti-huan-kong-ge-lcof/)
>
> 难度：简单 ｜ 标签：双指针、字符串、模拟

## 核心心智：打破“库函数”的幻觉

在处理字符串问题时，初学者很容易陷入两个极端：要么疯狂使用 `StringBuilder.reverse()` 等 API 导致面试挂科，要么用 `String +=` 进行拼接导致超时。

建立正确的 Java 字符串算法心智：

1.  **物理基础：不可变性（Immutability）**
    - Java 的 `String` 是不可变的。任何修改操作（如 `str += "a"`）都会创建新对象。
    - **算法推论**：若需频繁修改，必须转化为 **`char[]`**（原地修改）或使用 **`StringBuilder`**（动态拼接）。对于算法题，**操作 `char[]` 才是考察的本质**。

2.  **双指针的物理模型**
    - **对撞指针**（反转）：像两扇门从两边向中间关闭，交换通过的元素。
    - **倒序双指针**（填充）：像倒车入库。为了避免 $O(N^2)$ 的数组元素搬移，必须先扩容，再从后向前填充。

3.  **库函数使用守则**
    - **核心逻辑**：如果题目叫“反转字符串”，你用 `reverse()`，那是作弊。
    - **辅助逻辑**：如果题目是“复杂的字符串模拟”，反转只是其中一小步，那么用 API 是为了代码整洁。

---

## 一、基础模型：对撞指针（LeetCode 344）

### 题目描述

编写一个函数，其作用是将输入的字符串反转过来。输入字符串以字符数组 `s` 的形式给出。必须**原地修改**输入数组、使用 $O(1)$ 的额外空间解决这一问题。

### 核心思路：门的关闭

这是双指针最基础的模型。定义两个指针 `left` 和 `right`，分别指向数组的头部和尾部。

- **过程**：`left` 向右走，`right` 向左走。
- **操作**：每次移动前，交换两个指针指向的元素。
- **终止**：当 `left >= right` 时，两扇门碰头或交错，关闭完成。

### 代码实现

```java
public void reverseString(char[] s) {
    int left = 0;
    int right = s.length - 1;
    
    // 核心不变量：区间 [left, right] 是尚未反转的区域
    while (left < right) {
        // 交换元素
        char temp = s[left];
        s[left] = s[right];
        s[right] = temp;
        
        // 缩小区间
        left++;
        right--;
    }
}
```

### 图解

```text
初始：['h', 'e', 'l', 'l', 'o']
       L                   R

第一次交换后：
      ['o', 'e', 'l', 'l', 'h']
            L         R

第二次交换后：
      ['o', 'l', 'l', 'e', 'h']
                 L
                 R
      (L=R，相遇，循环结束)
```

---

## 二、进阶技巧：扩容与倒序填充（LCR 122）题目描述把字符串 s 中的每个空格替换成 "%20"。核心思路：为什么要倒序？这道题在 Java 中通常直接用 StringBuilder 解决，但为了学习算法思想，我们需要理解 C++ 视角下的“数组填充”痛点，这对理解底层内存操作非常有帮助。如果从前向后填充：每遇到一个空格，需要把后面的所有元素向后移动 2 位，时间复杂度是 $O(N^2)$。优化方案：预先扩容 + 倒序填充。扩容：先统计空格数量，计算出新字符串的长度。双指针：left 指向原字符串末尾。right 指向新字符串末尾。倒车：如果 left 指向非空格，填入 right，两指针前移。如果 left 指向空格，right 依次填入 '0', '2', '%', right 前移 3 步，left 前移 1 步。物理类比：就像整理书架，如果想在中间塞书，后面的书都要往后推（累）。但如果先把书架加长，从最后面开始把书一本本搬到新位置，就不会发生拥挤。代码实现（模拟数组操作版）Javapublic String replaceSpace(String s) {
    if (s == null) return null;
    
    // 1. 扩容：将 String 转为可变容器，并预留足够空间
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < s.length(); i++) {
        if (s.charAt(i) == ' ') {
            sb.append("  "); // 每个空格多补两个位置（原1个变3个）
        }
    }
    
    // 如果没有空格，直接返回
    if (sb.length() == 0) return s;
    
    // 2. 只有当确实需要扩容时，才进行倒序操作
    // 此时 left 指向原字符串末尾
    int left = s.length() - 1;
    // 将 s 追加到 sb 后面，让 sb 变成包含原字符串+扩容空间的样子
    // 注意：这里为了演示"原地"双指针逻辑，我们模拟从数组末尾操作
    // 实际 Java 简单写法是直接 new StringBuilder 遍历 append
    
    // 为了严格模拟"数组扩容后倒序填充"的算法思想，我们使用 char[]
    char[] oldChars = s.toCharArray();
    int count = 0;
    for(char c : oldChars) {
        if (c == ' ') count++;
    }
    
    // 新数组长度
    char[] newChars = new char[oldChars.length + count * 2];
    int right = newChars.length - 1;
    left = oldChars.length - 1;
    
    // 3. 倒序填充
    while (left >= 0) {
        if (oldChars[left] == ' ') {
            newChars[right--] = '0';
            newChars[right--] = '2';
            newChars[right--] = '%';
        } else {
            newChars[right--] = oldChars[left];
        }
        left--;
    }
    
    return new String(newChars);
}
```

---

## 三、逻辑控制：步长跳跃（LeetCode 541）

### 题目描述

给定一个字符串 `s` 和一个整数 `k`，从字符串开头算起，每计数至 `2k` 个字符，就反转这 `2k` 字符中的前 `k` 个字符。

### 核心思路：For 循环的艺术

很多同学会写复杂的计数器逻辑，甚至用 flag 变量来标记。其实，这道题考察的是对 **For 循环表达式** 的掌控力。

- **传统思维**：`i++`，每步走 1 格，走到 2k 触发一次。
- **算法思维**：`i += 2 * k`，每步直接跳 2k 格。

**操作逻辑**：

对于每个 `i`（区间起点），我们需要反转的区间是 `[i, i + k - 1]`。唯一需要注意的是边界处理：如果剩下的字符不足 `k` 个，则反转剩余所有字符。

### 代码实现

```java
public String reverseStr(String s, int k) {
    char[] ch = s.toCharArray();
    int n = ch.length;
    
    // 核心：步长直接设为 2k，省去计数器逻辑
    for (int i = 0; i < n; i += 2 * k) {
        // 1. 确定反转区间的右边界
        // 如果 i + k <= n，说明剩余字符够 k 个，右边界为 i + k - 1
        // 如果 i + k > n，说明剩余不够 k 个，右边界为 n - 1 (末尾)
        // 使用 Math.min 统一逻辑
        int right = Math.min(i + k - 1, n - 1);
        
        // 2. 调用基础反转函数（复用 344 的逻辑）
        reverse(ch, i, right);
    }
    
    return new String(ch);
}

// 封装基础反转逻辑，便于复用
private void reverse(char[] ch, int start, int end) {
    while (start < end) {
        char temp = ch[start];
        ch[start] = ch[end];
        ch[end] = temp;
        start++;
        end--;
    }
}
```

---

## 四、统一对比与抽象升级

| 题目 | 核心模型 | 指针运动方式 | 关键难点 | Java 特性点 |
|------|----------|--------------|----------|-------------|
| 344. 反转字符串 | 对撞指针 | L -> ... <- R | 终止条件 `L < R` | 必须转 `char[]` 操作 |
| LCR 122. 替换空格 | 倒序指针 | L <- ... R <- | 预先计算扩容大小 | 避免 $O(N^2)$ 的数据搬移 |
| 541. 反转 II | 区间指针 | i += 2k (跳跃) | 边界 `Math.min` | 复用 `reverse` 函数 |

**抽象总结**：字符串处理的本质是对**字符数组下标（Index）**的精细控制。

- 344 是控制 **Value**（交换）。
- LCR 122 是控制 **Capacity**（扩容+倒序）。
- 541 是控制 **Step**（步长）。

---

## 五、易错点清单（Bug-Free Guide）

### 1. 库函数依赖症

```java
// ❌ 错误：面试中直接调用
public void reverseString(char[] s) {
    // 题目要求原地修改 char[]，你却转成 StringBuilder 又转回来
    // 这不仅使用了 O(N) 空间，还完全没展示算法能力
    s = new StringBuilder(new String(s)).reverse().toString().toCharArray(); 
}

// ✅ 正确：老老实实写 while 循环交换
```

### 2. 反转区间的闭合性

```java
// ❌ 错误：右边界越界
// 很多同学习惯写 i + k，忘记下标是从 0 开始的，或者是忘记检查是否超标
reverse(ch, i, i + k); 

// ✅ 正确：
// 1. 下标要 -1：i + k - 1
// 2. 必须取 min 防止越界：Math.min(i + k - 1, n - 1)
```

### 3. Java 字符串的比较

```java
// ❌ 错误：用 == 比较字符串内容
if (s1 == s2) { ... }

// ✅ 正确：用 equals
if (s1.equals(s2)) { ... }
// 算法题中通常操作 char，直接 == 比较字符即可：ch[i] == ' '
```

---

## 六、口诀式总结

```text
【字符串双指针模板】

要反转，看首尾：对撞指针中间凑。
要填充，往后退：预先扩容倒着写。
有规律，跳着走：循环步长设 2k。

【核心不变量】
char[] 是 Java 字符串算法的 "物理实体"。
一切操作都是基于 index 的映射变换。
```

---

## 总结

字符串基础操作看似简单，实则考察了对**内存模型（原地修改）**和**控制流（循环步长）**的理解。

- 344 让你理解了"原地"的含义。
- LCR 122 让你明白了"扩容"的代价和"倒序"的智慧。
- 541 让你学会了如何优雅地控制循环逻辑。

掌握了这三板斧，你对字符串的掌控力就超过了只会调 API 的水平。接下来，我们将挑战更高阶的字符串反转问题——如何把这些基础动作组合起来，实现更复杂的逻辑。

### 扩展应用

- **LeetCode 151. 翻转字符串里的单词**（下一篇详解）
- **LeetCode 917. 仅仅反转字母**（344 的变体，增加判断条件）