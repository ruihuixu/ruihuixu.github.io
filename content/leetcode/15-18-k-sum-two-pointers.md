---
title: "LeetCode 15 / 18：K-Sum 的去重工程——排序 + 对撞指针模板"
date: 2026-01-24T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Array"
  - "Two Pointers"
  - "Collision Pointers"
  - "Java"
categories:
  - "LeetCode"
description: "K-Sum 的难点不是求和而是去重。本文建立统一模型：排序把重复变成连续块，外层去重锁定开头，内层对撞指针跳过重复，并用最小和/最大和剪枝加速，覆盖 3Sum/4Sum。"
---

> 题目链接：
>
> - [15. 三数之和](https://leetcode.cn/problems/3sum/)
> - [18. 四数之和](https://leetcode.cn/problems/4sum/)
>
> 难度：中等 / 中等 ｜ 标签：数组、排序、双指针、去重

## 核心心智：K-Sum 的本质是“去重工程”，排序让一切可控

很多人第一次写 3Sum 会下意识套 Two Sum：固定一个数 `a`，再用 `HashSet` 去找 `-(a+b)`。

这条路的致命问题不是“能不能找到”，而是**结果必须去重**：

- 同一组数会以不同顺序出现（例如 `[-1, 0, 1]` 与 `[0, -1, 1]`）。
- 同一个值可能需要用多次（例如 `[-1, -1, 2]`），而 `Set` 天然“只记一次”，会把你逼进复杂的计数/多集合判断。

**排序是把“去重难题”变成“跳过连续重复块”**：重复值会挤成一段，你只需要在关键位置（外层 `i/j`，内层 `left/right`）跳过重复即可。

从 3Sum 到 4Sum，再到一般 K-Sum，统一抽象是：

- 排序
- 前 `K-2` 层枚举（循环或递归）+ 去重
- 最后一层用对撞指针做 2Sum

---

## 一、三数之和（LeetCode 15）

### 题目描述

给你一个整数数组 `nums`，返回所有满足 `nums[i] + nums[j] + nums[k] == 0` 的不重复三元组。

注意：答案中不可以包含重复的三元组。

### 核心思路：排序 + 固定一个数 + 对撞指针

1. 排序：`Arrays.sort(nums)`
2. 枚举 `i`（三元组最小值的位置），并做 `i` 去重
3. 在区间 `[i+1, n-1]` 上做对撞：
   - `sum < 0` → `left++`（让和变大）
   - `sum > 0` → `right--`（让和变小）
   - `sum == 0` → 记录答案，然后同时跳过 `left/right` 的重复值

**为什么 `left` 从 `i+1` 开始，而不是从 `0` 开始？**

因为我们把“三元组的顺序”固定为 `i < left < right`。

- 当外层走到某个 `i`，意味着“以更小下标开头”的组合都已处理过。
- 如果 `left` 回到 `0`，会制造大量重复（本质是同一组三元组换了个排列）。

### 图解：对撞指针如何“只向中间走”

以排序后数组 `[-4, -1, -1, 0, 1, 2]` 为例：

```text
i=1, nums[i]=-1

[-4, -1, -1, 0, 1, 2]
      i   L           R

sum = -1 + (-1) + 2 = 0  -> 记录 [-1, -1, 2]
跳过重复：L 从第二个 -1 移到 0，R 从 2 移到 1

[-4, -1, -1, 0, 1, 2]
      i      L     R

sum = -1 + 0 + 1 = 0 -> 记录 [-1, 0, 1]
L++, R-- -> L >= R 结束
```

### 代码实现（Java）

```java
import java.util.*;

class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> res = new ArrayList<>();
        if (nums == null || nums.length < 3) return res;

        Arrays.sort(nums);
        int n = nums.length;

        for (int i = 0; i < n - 2; i++) {
            // 1) i 去重：同一个值只当一次开头
            if (i > 0 && nums[i] == nums[i - 1]) continue;

            // 2) 基础剪枝：最小值都 > 0，就不可能再凑出 0
            if (nums[i] > 0) break;

            // 3) 进阶剪枝：最小和 / 最大和
            int minSum = nums[i] + nums[i + 1] + nums[i + 2];
            if (minSum > 0) break;

            int maxSum = nums[i] + nums[n - 2] + nums[n - 1];
            if (maxSum < 0) continue;

            int left = i + 1;
            int right = n - 1;
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                if (sum == 0) {
                    res.add(Arrays.asList(nums[i], nums[left], nums[right]));

                    // left 去重：跳过所有相同的 nums[left]
                    int leftVal = nums[left];
                    while (left < right && nums[left] == leftVal) left++;

                    // right 去重：跳过所有相同的 nums[right]
                    int rightVal = nums[right];
                    while (left < right && nums[right] == rightVal) right--;
                } else if (sum < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return res;
    }
}
```

---

## 二、四数之和（LeetCode 18）

### 题目描述

给你一个由 `n` 个整数组成的数组 `nums`，以及一个目标值 `target`。请你找出并返回满足 `nums[a] + nums[b] + nums[c] + nums[d] == target` 的不重复四元组。

### 核心思路：多一层枚举 + 同样的对撞指针 + long 防溢出

与 3Sum 唯一结构变化：

- 外层两层枚举 `i/j`（并分别去重）
- 内层仍然是对撞指针

额外必须注意：

- 四个 `int` 相加可能溢出，所以比较时要用 `long`。
- 剪枝同样适用，而且收益更高（因为 4Sum 是 $O(n^3)$）。

### 代码实现（Java）

```java
import java.util.*;

class Solution {
    public List<List<Integer>> fourSum(int[] nums, int target) {
        List<List<Integer>> res = new ArrayList<>();
        if (nums == null || nums.length < 4) return res;

        Arrays.sort(nums);
        int n = nums.length;

        for (int i = 0; i < n - 3; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;

            long minI = (long) nums[i] + nums[i + 1] + nums[i + 2] + nums[i + 3];
            if (minI > target) break;
            long maxI = (long) nums[i] + nums[n - 1] + nums[n - 2] + nums[n - 3];
            if (maxI < target) continue;

            for (int j = i + 1; j < n - 2; j++) {
                if (j > i + 1 && nums[j] == nums[j - 1]) continue;

                long minJ = (long) nums[i] + nums[j] + nums[j + 1] + nums[j + 2];
                if (minJ > target) break;
                long maxJ = (long) nums[i] + nums[j] + nums[n - 1] + nums[n - 2];
                if (maxJ < target) continue;

                int left = j + 1;
                int right = n - 1;
                while (left < right) {
                    long sum = (long) nums[i] + nums[j] + nums[left] + nums[right];
                    if (sum == target) {
                        res.add(Arrays.asList(nums[i], nums[j], nums[left], nums[right]));

                        int leftVal = nums[left];
                        while (left < right && nums[left] == leftVal) left++;

                        int rightVal = nums[right];
                        while (left < right && nums[right] == rightVal) right--;
                    } else if (sum < target) {
                        left++;
                    } else {
                        right--;
                    }
                }
            }
        }

        return res;
    }
}
```

---

## 三、复杂度分析

- **3Sum**
  - 时间复杂度：$O(n^2)$（外层枚举 $n$ 次，内层对撞 $O(n)$）
  - 空间复杂度：$O(\log n)$（排序栈空间；不计输出）
- **4Sum**
  - 时间复杂度：$O(n^3)$
  - 空间复杂度：$O(\log n)$（同上）

---

## 四、易错点清单（Bug-Free Guide）

### 1）用 HashSet 套 3Sum：最难的是“去重正确性”

```text
❌ 误区：固定 a，用 Set 找 -(a+b)
问题：同值多次使用、结果排列去重、重复三元组判等，都会把你拖入复杂度泥潭。

✅ 正解：先排序，把重复值变成连续块，然后在 i/left/right 三个关键点跳过重复。
```

### 2）去重写成 left++/right--：可能漏跳多个重复值

```java
// ❌ 可能重复输出（或死循环风险）：只移动一步
left++;
right--;

// ✅ 应该跳过“连续重复块”
int leftVal = nums[left];
while (left < right && nums[left] == leftVal) left++;
```

### 3）剪枝条件写错方向：minSum 用 break，maxSum 用 continue

```text
minSum（当前最小可能和） > target -> 后面只会更大 -> break
maxSum（当前最大可能和） < target -> 当前太小 -> continue
```

### 4）4Sum int 溢出：比较一定要用 long

```java
// ❌ 溢出风险
int sum = nums[i] + nums[j] + nums[left] + nums[right];

// ✅ 用 long 承接
long sum = (long) nums[i] + nums[j] + nums[left] + nums[right];
```

---

## 五、口诀式总结：K-Sum 排序 + 去重 + 对撞

```text
【K-Sum 通用套路（去重工程版）】

1) 先排序：重复值挤成连续块，后续才能“跳过重复”。

2) 前 K-2 层枚举：
   - 当前层先做“同值只用一次”的去重（i>start && nums[i]==nums[i-1] -> continue）
   - 做最小和/最大和剪枝（minSum -> break，maxSum -> continue）

3) 最后一层做 2Sum：
   - left/right 对撞
   - 命中后，left/right 分别跳过连续重复块

【核心不变量】
- 排序后，重复值是连续的
- 组合下标严格递增（避免排列重复）
- 去重发生在“选择点”（外层开头 + 内层命中后）
```

---

## 总结

3Sum/4Sum 看起来是“求和题”，真正的门槛是“去重正确、剪枝有效”。排序把重复变成连续块后，去重就退化成“跳过一段相同值”，这也是对撞指针在 K-Sum 里最有价值的地方。

### 扩展应用

- [1. 两数之和](https://leetcode.cn/problems/two-sum/)：返回下标 → 更偏 HashMap
- [454. 四数相加 II](https://leetcode.cn/problems/4sum-ii/)：四个独立数组、只问次数 → HashMap 分治 $O(n^2)$
- [16. 最接近的三数之和](https://leetcode.cn/problems/3sum-closest/)：排序 + 对撞指针
