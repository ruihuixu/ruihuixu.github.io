---
title: "k数之和：对撞指针降维套路"
date: 2026-03-09T10:00:00+08:00
draft: false
slug: "k-sum"
tags:
  - "双指针"
categories:
  - "LeetCode"
description: "涵盖 LeetCode 15/18。排序+对撞指针是三/四数之和的核心：两数之和用哈希，三数之和排序+双指针，四数之和再套一层枚举，去重逻辑是变体题的关键难点。"
---

> **本文涵盖**：LeetCode 1（两数之和）/ 15（三数之和）/ 18（四数之和）
>
> **难度**：简单 / 中等 / 中等 ｜ **关键词**：排序、对撞指针、去重、剪枝

---

## 识别信号
> 看到什么特征，想到这篇笔记？

- 数组中找若干个数之和等于目标值，且结果不能包含重复组合
- k ≥ 3 时暴力 O(n^k) 超时，题目允许排序（返回值而非下标）
- 出现"不重复三元组 / 四元组"或要求返回所有满足条件的组合
- k = 2 且必须返回**下标**（不能排序）→ 改用哈希表，不走本篇套路

---

## 核心模板（速查）

三数之和 / 四数之和的通用结构：**排序 → 外层每层枚举并去重 → 最内两层用对撞指针**。

```python
# 三数之和通用模板（target 可替换为任意目标值）
def threeSum_template(nums: list[int], target: int = 0) -> list[list[int]]:
    nums.sort()
    n, res = len(nums), []

    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:       # 外层去重：同值只当一次最小数
            continue
        if nums[i] + nums[i+1] + nums[i+2] > target:  # 最小和剪枝 → break
            break
        if nums[i] + nums[n-2] + nums[n-1] < target:  # 最大和剪枝 → continue
            continue

        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == target:
                res.append([nums[i], nums[left], nums[right]])
                lv, rv = nums[left], nums[right]
                while left < right and nums[left] == lv:   # 跳左侧重复块
                    left += 1
                while left < right and nums[right] == rv:  # 跳右侧重复块
                    right -= 1
            elif s < target:
                left += 1
            else:
                right -= 1

    return res
```

各题在模板里的区别：

| 题号 | 固定层数 | 目标值 | 特殊处理 | 时间复杂度 |
|------|---------|--------|---------|-----------|
| 1    | 0 层    | target | 不排序，哈希表返回下标 | O(n) |
| 15   | 1 层 `i` | 0 | 无（标准模板） | O(n²) |
| 18   | 2 层 `i/j` | target | `j` 去重条件是 `j > i+1` | O(n³) |

---

## ⚠️ 高频错误

**1. 三数之和用哈希法，结果去重逻辑极难写对**

```python
# ❌ 错误思路：固定两个数，用 set 找第三个
seen = set()
for i in range(n):
    for j in range(i + 1, n):
        c = -(nums[i] + nums[j])
        if c in seen:
            res.add(tuple(sorted([nums[i], nums[j], c])))
# 问题：[-1,-1,2] 需要用两次 -1，但 seen 只记一次；tuple 去重也很脆弱

# ✅ 正确：先排序，对撞指针天然保证下标有序，去重只需比较相邻值
nums.sort()
```

**2. 内层命中后只移动一步，未跳过连续重复块**

```python
# ❌ 错误：移动一步后，下一轮可能再次命中相同值 → 重复答案
if s == 0:
    res.append([nums[i], nums[left], nums[right]])
    left += 1    # nums[left] 可能与移动前相同
    right -= 1

# ✅ 正确：while 循环跳过整个重复块，指针落在新值上
if s == 0:
    res.append([nums[i], nums[left], nums[right]])
    lv, rv = nums[left], nums[right]
    while left < right and nums[left] == lv:
        left += 1
    while left < right and nums[right] == rv:
        right -= 1
```

**3. 外层去重少写了 `i > 0`，导致访问 `nums[-1]` 误判**

```python
# ❌ 错误：i=0 时 nums[i-1] = nums[-1]（最后一个元素），可能误跳合法答案
if nums[i] == nums[i - 1]: continue

# ✅ 正确：i > 0 作前置保护，防止越界比较
if i > 0 and nums[i] == nums[i - 1]: continue
```

**4. 四数之和第二层去重条件写成 `j > 0`**

```python
# ❌ 错误：j > 0 会误判，j=i+1 首次出现时不该跳过
if j > 0 and nums[j] == nums[j - 1]: continue

# ✅ 正确：j 从 i+1 开始，首次（j == i+1）不去重，之后同值才跳
if j > i + 1 and nums[j] == nums[j - 1]: continue
```

**5. 剪枝方向混淆：minSum 应 `break`，maxSum 应 `continue`**

```python
# ❌ 错误：两个方向都用 continue，minSum 超标后仍在无意义枚举
if min_sum > target: continue   # 应该是 break！
if max_sum < target: continue

# ✅ 正确：min_sum 超标后续只会更大，break 退出整层；max_sum 不足则跳下一个 i
if min_sum > target: break      # 排序后 i 越大，min_sum 只增不减
if max_sum < target: continue   # 当前 i 太小，换更大的 i 试试
```

---

## 详解

### 两数之和（LeetCode 1）

#### 核心思路

本题返回**下标**，排序会破坏原始位置 → 不能用对撞指针，改用哈希表。
遍历时维护「已见值 → 下标」映射，当前数 `x` 的配对目标是 `target - x`，若命中则直接返回。

#### Python 代码

```python
def twoSum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}        # 值 → 下标
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i
    return []
```

- 时间复杂度：O(n)；空间复杂度：O(n)
- 与三/四数之和的根本区别：**返回下标 → 哈希；返回值组合 → 排序 + 对撞**

---

### 三数之和（LeetCode 15）

#### 核心思路

固定最左数 `nums[i]`，在右侧区间 `[i+1, n-1]` 做对撞 2-Sum，目标是 `-nums[i]`：

1. 排序，使重复值连续排列
2. 枚举 `i`，同值只当一次最小数（外层去重）
3. 对撞过程：命中则跳过左右重复块，否则按大小方向移动指针

#### 图解：以 `[-4, -1, -1, 0, 1, 2]`，`i=1`（`nums[i]=-1`，2-Sum 目标 = 1）为例

```text
初始状态
[-4, -1, -1,  0,  1,  2]
      ↑    ↑            ↑
      i    L            R    s = (-1)+2 = 1 ✓ → 记录 [-1,-1,2]

跳重复：lv=-1 → L 移至下标3(0)；rv=2 → R 移至下标4(1)
[-4, -1, -1,  0,  1,  2]
      ↑         ↑   ↑
      i         L   R       s = 0+1 = 1 ✓ → 记录 [-1,0,1]

L++, R-- → L(4) >= R(3)，内层结束

外层 i=0（nums[0]=-4）：最大和 = -4+1+2 = -1 < 0 → continue（已被剪枝跳过）
```

#### Python 代码

```python
def threeSum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    n = len(nums)
    res: list[list[int]] = []

    for i in range(n - 2):
        # 外层去重：跳过重复的 nums[i]，只用第一次出现的值作为三元组最小数
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # 剪枝：三个最小数之和仍 > 0，之后只会更大
        if nums[i] + nums[i + 1] + nums[i + 2] > 0:
            break
        # 剪枝：三个最大数之和仍 < 0，当前 i 太小，换下一个
        if nums[i] + nums[n - 2] + nums[n - 1] < 0:
            continue

        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                res.append([nums[i], nums[left], nums[right]])
                lv, rv = nums[left], nums[right]
                while left < right and nums[left] == lv:   # 左侧跳重复
                    left += 1
                while left < right and nums[right] == rv:  # 右侧跳重复
                    right -= 1
            elif s < 0:
                left += 1    # 和太小，左指针右移（取更大的数）
            else:
                right -= 1   # 和太大，右指针左移（取更小的数）

    return res
```

- 时间复杂度：O(n²)；空间复杂度：O(1)（不含输出）

---

### 四数之和（LeetCode 18）

#### 核心思路

在三数之和外层再加一层枚举 `j`，形成**两层固定 + 一层对撞**：

- `i` 层：与三数之和完全一致的去重 + 剪枝
- `j` 层（从 `i+1` 起）：去重条件改为 `j > i+1`；剪枝用 `i+j` 两个固定值计算
- 最内层：对撞 2-Sum，目标变为 `target - nums[i] - nums[j]`

**两层剪枝必须各自独立计算**，不能复用 `i` 层的 `min/max`。

#### 图解：双层枚举结构

```text
for i in range(n - 3):            # 固定第一个数
    for j in range(i+1, n - 2):   # 固定第二个数
        left, right = j+1, n-1
        while left < right:       # 对撞找后两个数
            ...
```

#### Python 代码

```python
def fourSum(nums: list[int], target: int) -> list[list[int]]:
    nums.sort()
    n = len(nums)
    res: list[list[int]] = []

    for i in range(n - 3):
        # i 层去重
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # i 层剪枝
        if nums[i] + nums[i+1] + nums[i+2] + nums[i+3] > target:
            break
        if nums[i] + nums[n-1] + nums[n-2] + nums[n-3] < target:
            continue

        for j in range(i + 1, n - 2):
            # j 层去重：j=i+1 是第一次出现，不跳；之后遇到同值才跳
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            # j 层剪枝（固定 i 和 j 后重新计算 min/max）
            if nums[i] + nums[j] + nums[j+1] + nums[j+2] > target:
                break
            if nums[i] + nums[j] + nums[n-1] + nums[n-2] < target:
                continue

            left, right = j + 1, n - 1
            while left < right:
                s = nums[i] + nums[j] + nums[left] + nums[right]
                if s == target:
                    res.append([nums[i], nums[j], nums[left], nums[right]])
                    lv, rv = nums[left], nums[right]
                    while left < right and nums[left] == lv:
                        left += 1
                    while left < right and nums[right] == rv:
                        right -= 1
                elif s < target:
                    left += 1
                else:
                    right -= 1

    return res
```

- 时间复杂度：O(n³)；空间复杂度：O(1)（不含输出）

---

### 通用 k 数之和（递归骨架）

理解三数和四数之和的模板后，一般 k 数之和可以递归通用化：k 减到 2 时调对撞 2-Sum，外层每一层做相同的去重和剪枝。

```python
def kSum(nums: list[int], target: int, k: int, start: int) -> list[list[int]]:
    if k == 2:                                  # 递归基：用对撞指针
        res, left, right = [], start, len(nums) - 1
        while left < right:
            s = nums[left] + nums[right]
            if s == target:
                res.append([nums[left], nums[right]])
                lv, rv = nums[left], nums[right]
                while left < right and nums[left] == lv: left += 1
                while left < right and nums[right] == rv: right -= 1
            elif s < target: left += 1
            else: right -= 1
        return res
    res = []
    for i in range(start, len(nums) - k + 1):
        if i > start and nums[i] == nums[i - 1]:    # 去重
            continue
        for sub in kSum(nums, target - nums[i], k - 1, i + 1):
            res.append([nums[i]] + sub)
    return res
```

---

## 统一对比

| 维度 | LeetCode 1 | LeetCode 15 | LeetCode 18 |
|------|-----------|-------------|-------------|
| 题意 | 找一对数，返回下标 | 找三元组，返回值 | 找四元组，返回值 |
| 能否排序 | 否（下标失效） | 是 | 是 |
| 核心方法 | 哈希表 | 1 层枚举 + 对撞 | 2 层枚举 + 对撞 |
| 外层去重 | 无 | `i > 0 and nums[i] == nums[i-1]` | 同上；`j` 层用 `j > i+1` |
| 内层去重 | 无 | 命中后 while 跳重复块 | 同 15 |
| 剪枝层数 | 无 | `i` 层 min/max 各一次 | `i` 和 `j` 层各独立一次 |
| 时间复杂度 | O(n) | O(n²) | O(n³) |
| 整数溢出 | 无风险 | 无风险 | Python 无风险；Java 需转 `long` |

---

## 口诀

```text
【k 数之和三步口诀】

第一步：先排序
  重复值挤成连续块，"跳过重复"才能用相邻比较实现

第二步：外层枚举 + 去重 + 剪枝
  去重：i > 0 且 nums[i] == nums[i-1] → continue（不是 break！）
  去重：j > i+1 且 nums[j] == nums[j-1] → continue
  剪枝：最小和 > target → break（只会更大，无需继续）
  剪枝：最大和 < target → continue（当前太小，换更大的）

第三步：最内层对撞去重
  命中后，左右各用 while 跳过整个重复块
  不是 +=1，是 while nums[p] == val: p 移动

【降维公式】
k 数之和 = (k-2) 层枚举去重 + 1 层对撞 2-Sum
两数之和（返回下标）是例外：哈希 O(n)，不走排序路线

【剪枝方向助记】
最小可能和 > target → break   （排序后只会更大，直接退出）
最大可能和 < target → continue（当前层太小，试下一个值）
```

---

## 总结与扩展

k 数之和的真正难点不在求和，而在**去重的正确性**。排序把"判断重复"从 O(n) 哈希问题压缩成 O(1) 的相邻比较；对撞指针把最内层 2-Sum 从 O(n²) 暴力降到 O(n)，整体比暴力少一个量级。

三数之和到四数之和是机械地多套一层枚举，模板复用率极高。理解去重逻辑后，任意 k 数之和都可以递归通用化：前 k-2 层递归枚举，最后一层调对撞 2-Sum。

### 相关题目

- [16. 最接近的三数之和](https://leetcode.cn/problems/3sum-closest/)：排序 + 对撞，改为追踪最小差值，去重逻辑完全相同
- [454. 四数相加 II](https://leetcode.cn/problems/4sum-ii/)：四个独立数组只问次数不去重 → 哈希分治 O(n²)
- [611. 有效三角形的个数](https://leetcode.cn/problems/valid-triangle-number/)：排序 + 对撞，条件改为 `a+b > c`，套路完全一致
