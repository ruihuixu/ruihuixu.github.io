---
title: "LeetCode 704. 二分查找：深入理解循环不变量"
date: 2026-01-05T00:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Binary Search"
  - "Java"
categories:
  - "LeetCode"
description: "二分查找代码虽短，细节却是魔鬼。本文对比左闭右闭与左闭右开两种写法，彻底搞懂边界条件。"
---

> 题目链接： [704. Binary Search](https://leetcode.cn/problems/binary-search/description/)
>
> 难度：简单 ｜ 标签：数组、二分查找

## 题目描述

给定一个 n 个元素有序的（升序）整型数组 `nums` 和一个目标值 `target`，写一个函数搜索 `nums` 中的 `target`，如果 `target` 存在返回下标，否则返回 `-1`。

前提：数组中所有元素是不重复的。

## 核心思考：循环不变量

二分查找代码虽短，但每次写的时候，总是在纠结两个细节：

- `while` 里面到底是 `<` 还是 `<=`？
- `right` 更新的时候到底是 `mid` 还是 `mid - 1`？

其实如果不从原理上想清楚，光靠背是很容易混淆的。这里的核心概念叫 **循环不变量**（Loop Invariant）。说人话就是：你一开始定义的区间是什么样的，整个循环里就要一直遵守这个定义。

通常就两种写法：左闭右闭 与 左闭右开。

## 写法一：左闭右闭区间 `[left, right]`（推荐）

这是最符合直觉的写法。我们定义 `target` 是在 `[left, right]` 这个闭区间里寻找。

- **初始化**：`right = nums.length - 1`。因为是闭区间，`right` 指向的那个位置（最后一个元素）必须是有效的，可能会被取到。
- **循环条件**：`while (left <= right)`。当 `left == right` 时（比如数组只有一个元素），`[0, 0]` 依然包含一个元素，是有效区间，所以必须还能进入循环再查一次。
- **边界更新**：
  - `nums[mid] > target`：`mid` 肯定不是目标值了，而且我们要在左半边找。因为区间是闭的，排除 `mid` 后右边界应为 `mid - 1`。
  - `nums[mid] < target`：同理，左边界变成 `mid + 1`。

```java
public int search(int[] nums, int target) {
    // 避免整型溢出，等同于 (left + right) / 2
    int left = 0;
    int right = nums.length - 1; // 闭区间，right 指向最后一个元素

    while (left <= right) { // 包含 left == right 的情况
        int mid = left + (right - left) / 2;
        int num = nums[mid];

        if (num == target) {
            return mid;
        } else if (num > target) {
            // target 在左区间，mid 既然不是，right 就要移一位
            right = mid - 1;
        } else {
            // target 在右区间，mid 既然不是，left 就要移一位
            left = mid + 1;
        }
    }
    return -1;
}
```

## 写法二：左闭右开区间 `[left, right)`

这种写法在 C++ STL 的迭代器里很常见。我们定义 `target` 是在 `[left, right)` 这个左闭右开区间里。

- **初始化**：`right = nums.length`。因为右边是开区间，`right` 取不到，所以可以指向数组长度（越界位置）。
- **循环条件**：`while (left < right)`。当 `left == right` 时，`[1, 1)` 是空集，区间无效，循环结束。
- **边界更新**：
  - `nums[mid] > target`：右边界本来就是“开”的（不包含），所以直接 `right = mid`，新的区间 `[left, mid)` 就把 `mid` 排除在外了。
  - `nums[mid] < target`：左边还是闭的，所以 `left = mid + 1`。

```java
public int search(int[] nums, int target) {
    int left = 0;
    int right = nums.length; // 开区间，right 取不到

    while (left < right) { // left == right 时区间无效
        int mid = left + (right - left) / 2;
        int num = nums[mid];

        if (num == target) {
            return mid;
        } else if (num > target) {
            // 右边是开的，right = mid 会把 mid 排除在下一次搜索之外
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return -1;
}
```

## 总结

两种写法本质上没有高下之分，关键是逻辑自洽。

- 如果习惯 `right = nums.length - 1`，那就锁死 `while (left <= right)` 和 `right = mid - 1`。
- 如果习惯 `right = nums.length`，那就锁死 `while (left < right)` 和 `right = mid`。

我自己更倾向于第一种（左闭右闭），逻辑上更顺畅，不用去想开闭区间的转换。

## 复杂度

- 时间复杂度：$O(log n)$
- 空间复杂度：$O(1)$