---
title: "LeetCode 704. 二分查找：从模板到变体通杀"
date: 2026-01-05T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Array"
  - "Binary Search"
  - "Interval Definition"
  - "Java"
categories:
  - "LeetCode"
description: "二分查找的本质是区间定义的一致性。本文建立统一模板：左闭右闭与左闭右开的对比，找边界、找插入点以及值域二分的通用解法。"
---

> 题目链接：[704. Binary Search](https://leetcode.cn/problems/binary-search/description/)
>
> 难度：简单 ｜ 标签：数组、二分查找

## 题目描述

给定一个有序整型数组 `nums` 和目标值 `target`，返回 `target` 的下标，不存在则返回 `-1`。假设数组元素互不重复。

## 核心心智：先锁定“区间定义”，其他一切随之而来

写二分时，脑子里只需要挂住两件事：

1. 我维护的搜索区间是闭的 `[left, right]`，还是左闭右开的 `[left, right)`？
2. 我在循环里是否一直坚持这个定义，不做“半开半闭”的摇摆？

当你想清楚这两件事，`while` 条件和边界收缩就会自然长出来。

## 模板一：左闭右闭 `[left, right]`（更直觉，推荐）

- 定义：`target` 一直被限制在 `[left, right]`。
- 初始化：`left = 0`，`right = nums.length - 1`（因为右边是闭的，必须是有效下标）。
- 循环条件：`while (left <= right)`，当 `left == right` 时仍有一个候选元素。
- 边界收缩：
  - `nums[mid] > target` → 右边界收缩到 `mid - 1`。
  - `nums[mid] < target` → 左边界收缩到 `mid + 1`。

```java
public int search(int[] nums, int target) {
    int left = 0;
    int right = nums.length - 1; // 闭区间

    while (left <= right) { // left == right 依然有效
        int mid = left + (right - left) / 2; // 防溢出写法
        if (nums[mid] == target) return mid;
        if (nums[mid] > target) {
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }
    return -1;
}
```

## 模板二：左闭右开 `[left, right)`

- 定义：`target` 落在 `[left, right)`，右端不取。
- 初始化：`left = 0`，`right = nums.length`（右端可以等于长度）。
- 循环条件：`while (left < right)`，当 `left == right` 时区间为空。
- 边界收缩：
  - `nums[mid] > target` → 右边界收缩到 `mid`（无需 `-1`，因为右端开）。
  - `nums[mid] < target` → 左边界收缩到 `mid + 1`。

```java
public int search(int[] nums, int target) {
    int left = 0, right = nums.length; // 左闭右开
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] > target) {
            right = mid; // 右端开，直接收缩到 mid
        } else {
            left = mid + 1;
        }
    }
    return -1;
}
```

## 实战变体：把模板“拧成”面试常考题

### 1) 寻找插入位置（LeetCode 35）

思路：标准二分即可。若找到直接返回 `mid`；若找不到，循环结束时 `left` 正好指向“第一个大于 target 的位置”，也就是插入点。

```java
public int searchInsert(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] > target) right = mid - 1; else left = mid + 1;
    }
    return left; // 未命中时，left 即插入位置
}
```

### 2) 查找左右边界（LeetCode 34）

常见坑（写代码时脑子里过一遍）：

- **短路顺序**：先判空再访问 `nums[right]`，否则空数组会越界。
- **指针重置**：双循环方案，第二段查右边界前记得把 `left/right` 复位。
- **结果校验**：找到的 `first`、`last` 必须满足 `first <= last`，否则返回 `[-1, -1]`。

直观写法（两个循环分头找左右端点）：

```java
public int[] searchRange(int[] nums, int target) {
    int n = nums.length;
    if (n == 0 || target < nums[0] || target > nums[n - 1]) return new int[]{-1, -1};

    // 找左边界：最左的 >= target
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] < target) left = mid + 1; else right = mid - 1;
    }
    int first = left;
    if (first >= n || nums[first] != target) return new int[]{-1, -1};

    // 找右边界：最右的 <= target
    left = 0; right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] > target) right = mid - 1; else left = mid + 1;
    }
    int last = right;
    return new int[]{first, last};
}
```

模板化写法（`lowerBound` 复用）：

```java
class Solution {
    public int[] searchRange(int[] nums, int target) {
        int start = lowerBound(nums, target);
        if (start == nums.length || nums[start] != target) return new int[]{-1, -1};
        int end = lowerBound(nums, target + 1) - 1;
        return new int[]{start, end};
    }

    // 返回最小的 i，使得 nums[i] >= target；若不存在，返回 nums.length
    private int lowerBound(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] >= target) right = mid - 1; else left = mid + 1;
        }
        return left;
    }
}
```

### 3) 在值域上二分（LeetCode 69）

没有数组也能二分——值域天然有序。目标是找到最大的 `k`，使得 `k * k <= x < (k + 1) * (k + 1)`。

```java
public int mySqrt(int x) {
    if (x == 0) return 0;
    int left = 1, right = x, ans = 0;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if ((long) mid * mid <= x) { // 注意溢出
            ans = mid; // 先收下这个可行解，再看能否更大
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return ans;
}
```

## 总结：写二分时的“口头禅”

- 先问自己：我维护的是闭区间还是左闭右开？然后死磕一致性。
- 写 `mid` 时用 `left + (right - left) / 2`，不用担心溢出。
- 没找到时，闭区间模板的 `left` 会落到“第一个大于 target”的位置，常用于插入点。
- 找边界时，命中后不要急着返回，让条件继续收缩直到不满足为止。
- 面对非数组场景（如开平方、分配问题），把“搜索范围”换成“答案的数值区间”，一样能二分。