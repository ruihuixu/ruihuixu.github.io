---
title: "26. 删除有序数组中的重复项"
draft: false
tags:
  - "Algorithm"
  - "Two Pointers"
  - "Array"
  - "Java"
categories:
  - "LeetCode"
description: "快慢指针原地去重：保持相对顺序，返回唯一元素个数。"
---

> 题目链接：[26. Remove Duplicates from Sorted Array](https://leetcode.cn/problems/remove-duplicates-from-sorted-array/description/)
>
> 难度：简单 ｜ 标签：数组、双指针

## 题目描述

给你一个**非严格递增**排列的数组 `nums`，请你**原地**删除重复出现的元素，使每个元素只出现一次，并返回删除后数组的新长度 `k`。

要求：

- `nums` 的前 `k` 个元素应包含去重后的唯一元素（相对顺序保持一致）
- `k` 之后的元素可以忽略

## 解题思路：快慢指针（原地去重）

这是快慢指针最经典的“原地压缩”模型：

- `slow`：指向“已放好唯一元素”的最后一个位置
- `fast`：向前扫描新元素

由于数组有序，重复元素一定相邻：

- 若 `nums[fast] != nums[slow]`，说明找到一个新值：`slow += 1` 并写入 `nums[slow] = nums[fast]`
- 否则跳过重复值，`fast` 继续前进

遍历结束后，唯一元素个数为 `slow + 1`。

```java
public int removeDuplicates(int[] nums) {
    if (nums == null || nums.length == 0) return 0;

    int slow = 0;
    for (int fast = 1; fast < nums.length; fast++) {
        if (nums[fast] != nums[slow]) {
            slow++;
            nums[slow] = nums[fast];
        }
    }
    return slow + 1;
}
```

## 复杂度分析

- **时间复杂度**：$O(N)$，其中 $N$ 是数组长度，`fast` 只遍历一遍。
- **空间复杂度**：$O(1)$，原地修改，仅用常数额外空间。
