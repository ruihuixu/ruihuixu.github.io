---
title: "27. 移除元素"
draft: false
tags:
  - "Algorithm"
  - "Two Pointers"
  - "Array"
  - "Java"
categories:
  - "LeetCode"
description: "双指针基础题，掌握方法、拓展思路"
---

> 题目链接：[27. Remove Element](https://leetcode.cn/problems/remove-element/description/)
>
> 难度：简单 ｜ 标签：数组、双指针

## 题目描述
给你一个数组 `nums` 和一个值 `val`，你需要**原地**移除所有数值等于 `val` 的元素，并返回移除后数组的剩余元素的长度。 不要使用额外的数组空间，你必须仅使用 O(1) 额外空间并**原地**修改输入数组。 元素的顺序可以改变。你不需要考虑数组中超出新长度后面的元素。

## 解题思路：快慢指针
本题是双指针中**快慢指针**的经典应用。`fast` 指针负责遍历数组，`slow` 指针负责维护“新数组”的边界。 
- 当 `nums[fast] == val` 时，`fast` 继续前进，跳过该元素。
- 当 `nums[fast] != val` 时，将 `nums[fast]` 赋值给 `nums[slow]`，然后 `slow` 前进一位。
最终 `slow` 的值即为新数组的长度。

```java
public int removeElement(int[] nums, int val) {
    int slow = 0;
    for (int fast = 0; fast < nums.length; fast++) {
        if (nums[fast] != val) {
            nums[slow] = nums[fast];
            slow++;
        }
    }
    return slow;
}
```

另一种简化的思路，基于栈的思想维护一个栈指针stack, 遇到不等于val的元素就入栈，操作上还是基于数组原地操作，实际上也是快慢指针的变种，下面代码里的stack指针相当于上面代码里的slow指针，i相当于fast指针。

```java
public int removeElement(int[] nums, int val) {
    int stack = 0;
    for (int i = 0; i < nums.length; i++) {
        if (nums[i] != val) {
            nums[stack++] = nums[i];
        }
    }
    return stack;
}
```

## 复杂度分析
- **时间复杂度**：$O(N)$，其中 $N$ 是数组的长度。我们只遍历了一次数组。
- **空间复杂度**：$O(1)$，我们只使用了常数级别的额外空间。
