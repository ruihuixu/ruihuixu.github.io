---
title: "283. 移动零"
draft: false
tags:
  - "Algorithm"
  - "Two Pointers"
  - "Array"
  - "Java"
categories:
  - "LeetCode"
description: "快慢指针原地稳定移动：把非零元素前移，0 自然被推到末尾。"
---

> 题目链接：[283. Move Zeroes](https://leetcode.cn/problems/move-zeroes/description/)
>
> 难度：简单 ｜ 标签：数组、双指针

## 题目描述

给定一个数组 `nums`，请你编写一个函数，将所有 `0` 移动到数组末尾，同时保持非零元素的相对顺序。

要求：必须**原地**操作，不能拷贝数组。

## 解题思路：快慢指针（稳定前移）

把它看成“过滤非零元素”的原地压缩：

- `slow`：指向下一个“应该放非零元素”的位置（也可以理解为第一个 0 的位置）
- `fast`：扫描数组

当 `nums[fast] != 0` 时，把该非零元素放到 `slow` 位置：

- 若 `slow == fast`，说明本来就在正确位置，不用动
- 若 `slow < fast`，交换 `nums[slow]` 与 `nums[fast]`

这样能保证**相对顺序不变**：因为 `slow` 总是从左到右依次放入遇到的非零元素。

```java
public void moveZeroes(int[] nums) {
    if (nums == null || nums.length == 0) return;

    int slow = 0;
    for (int fast = 0; fast < nums.length; fast++) {
        if (nums[fast] != 0) {
            if (slow != fast) {
                int tmp = nums[slow];
                nums[slow] = nums[fast];
                nums[fast] = tmp;
            }
            slow++;
        }
    }
}
```

## 复杂度分析

- **时间复杂度**：$O(N)$，每个元素最多被访问/交换一次。
- **空间复杂度**：$O(1)$，只使用常数额外空间。
