---
title: "动态规划：打家劫舍三题"
date: 2026-03-09T10:00:00+08:00
draft: false
slug: "dp-house-robber"
tags:
  - "Algorithm"
  - "Dynamic Programming"
  - "Array"
  - "Tree"
  - "Python"
categories:
  - "LeetCode"
description: "涵盖 LeetCode 198/213/337。打家劫舍核心是「不能连续偷相邻房间」的状态转移：线性版直接DP，环形版拆分两次线性，树形版后序DFS返回偷/不偷两种状态——三题共享同一转移公式。"
---

> **本文涵盖**：LeetCode 198 / 213 / 337
>
> **难度**：中等 | **关键词**：线性DP、化环为线、树形后序DP、状态对、滚动变量

| 题号 | 题目 | 数据结构 | 核心技巧 |
|:----:|:-----|:-------:|:-------:|
| 198  | 打家劫舍 | 线性数组 | 经典线性 DP，O(1) 空间压缩 |
| 213  | 打家劫舍 II | 环形数组 | 拆两段，各跑一次 198 |
| 337  | 打家劫舍 III | 二叉树 | 后序 DFS，每节点返回 (偷, 不偷) 元组 |

---

## 识别信号

> 看到什么特征，想到这篇笔记？

- 一排（或一圈）数字，**不能选相邻的两个**，求可选数字的最大总和
- 数组首尾额外相邻（围成环），需要同时处理"头节点"与"尾节点"互斥
- 问题搬上**二叉树**，父子节点不能同时被选，要求全树最优解
- 每个状态只依赖**前两步**的结果，用两个变量滚动即可替代完整 dp 数组

---

## 核心模板（速查）

### 通用线性打劫辅助函数

```python
def rob_linear(nums: list[int]) -> int:
    """对线性数组做打家劫舍，O(n) 时间 O(1) 空间。"""
    prev2, prev1 = 0, 0
    for num in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + num)
        #              ↑ 先把 prev1 存到 prev2，再更新 prev1
        #              ↑ 必须同时赋值，否则 prev2 被覆盖后 prev1 算错
    return prev1
```

### 三题速查对比

| 题号 | 调用方式 | 关键边界 | 返回值 |
|:----:|:--------|:--------|:------|
| 198  | `rob_linear(nums)` | `len==1` 直接返回 `nums[0]` | 最大金额 |
| 213  | `max(rob_linear(nums[:-1]), rob_linear(nums[1:]))` | `len==1` 直接返回 `nums[0]` | 最大金额 |
| 337  | 后序 DFS，返回 `(rob_this, skip_this)` | 空节点返回 `(0, 0)` | `max(dfs(root))` |

---

## ⚠️ 高频错误（先看这里）

**1. 198 长度为 1 时 dp 数组下标越界**

```python
# ❌ 错误：n=1 时 dp[1] = nums[0] 执行后，range(2, 2) 空循环没问题，
#         但若写成 dp = [0] * n（长度 n 而不是 n+1），dp[1] 就越界了
n = len(nums)
dp = [0] * n          # 长度仅为 n，访问 dp[n] 时越界
dp[1] = nums[0]       # n=1 时 dp[1] 等于 dp[n]，已越界

# ✅ 正确：开 n+1 长度，或者在滚动变量版本里提前特判
if len(nums) == 1:
    return nums[0]
```

**2. 213 在同一次 DP 中同时考虑首尾（环形约束被忽略）**

```python
# ❌ 错误：直接对整个数组跑线性 DP，首尾可以同时被选，违反环形约束
def rob(nums):
    return rob_linear(nums)   # 没有处理首尾互斥！

# ✅ 正确：拆成两段分别跑，首尾永远不会同时出现在同一段里
def rob(nums):
    if len(nums) == 1:
        return nums[0]
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```

**3. 337 用全局变量记录最优解（漏掉"偷"与"不偷"的区分）**

```python
# ❌ 错误：全局变量只记录一个值，子节点无法告知父节点「是否已被偷」
self.res = 0
def dfs(node):
    if not node:
        return
    dfs(node.left)
    dfs(node.right)
    self.res = max(self.res, node.val + ...)   # 无法知道左右孩子的状态

# ✅ 正确：每个节点返回 (rob_this, skip_this) 元组，父节点按需取值
def dfs(node):
    if not node:
        return (0, 0)
    left_rob, left_skip = dfs(node.left)
    right_rob, right_skip = dfs(node.right)
    rob_this  = node.val + left_skip + right_skip
    skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)
    return (rob_this, skip_this)
```

**4. 滚动变量更新顺序错误（prev2 被提前覆盖）**

```python
# ❌ 错误：先更新 prev2，再用已被修改的 prev2 计算 prev1
for num in nums:
    prev2 = prev1                      # prev2 已变成旧 prev1
    prev1 = max(prev1, prev2 + num)    # prev2 + num = 旧prev1 + num，逻辑错误！

# ✅ 正确：Python 多重赋值一次性完成，右侧全部先求值再赋值
for num in nums:
    prev2, prev1 = prev1, max(prev1, prev2 + num)   # prev2 在 prev1 更新前已保存
```

**5. 213 长度为 2 时返回错误值**

```python
# ❌ 错误：nums[:-1]=[nums[0]], nums[1:]=[nums[1]]，两段各只含 1 个元素，
#         结果是 max(nums[0], nums[1])，看起来对，但若写成 rob_linear 里
#         没有处理空数组，当 n=1 传入 nums[:-1] 后 nums[1:] 为空，空数组
#         的 rob_linear 返回 0，答案就错了
def rob(nums):
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
    # 若 rob_linear([]) 没有处理空输入，nums 长度为 1 时 nums[1:]=[] 出错

# ✅ 正确：在入口处特判 len==1，让 rob_linear 永远收到非空输入
def rob(nums):
    if len(nums) == 1:
        return nums[0]
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```

---

## 详解

### 198. 打家劫舍

#### 核心思路

一排 n 间房，相邻两间不能同晚被偷，求最大金额。

定义 `dp[i]` 为考虑前 `i` 间房（下标 `0..i-1`）能偷到的最高金额（不强制要偷第 i 间）。

对第 `i` 间房只有两种决策：

- **偷第 i 间**：第 i-1 间不能偷，最优来自 `dp[i-2] + nums[i-1]`
- **不偷第 i 间**：沿用 `dp[i-1]`

递推公式：

```text
dp[i] = max(dp[i-1], dp[i-2] + nums[i-1])
```

初始化：`dp[0] = 0`（0 间房偷 0 元），`dp[1] = nums[0]`（只有 1 间就偷它）。

#### Python 代码

```python
class Solution:
    def rob(self, nums: list[int]) -> int:
        n = len(nums)
        if n == 1:
            return nums[0]

        # 空间 O(1)：用两个滚动变量代替完整 dp 数组
        # prev2 对应 dp[i-2]，prev1 对应 dp[i-1]
        prev2, prev1 = 0, nums[0]

        for i in range(1, n):
            # 同时赋值：右侧先全部求值，再写入左侧，防止 prev2 被提前覆盖
            prev2, prev1 = prev1, max(prev1, prev2 + nums[i])

        return prev1
```

#### 图解

以 `nums = [2, 7, 9, 3, 1]` 为例，追踪 prev2 / prev1 的变化：

```text
初始:           prev2=0,  prev1=2   (只考虑 nums[0]=2)

i=1, num=7:     prev2=2,  prev1=max(2, 0+7)=7
i=2, num=9:     prev2=7,  prev1=max(7, 2+9)=11
i=3, num=3:     prev2=11, prev1=max(11, 7+3)=11
i=4, num=1:     prev2=11, prev1=max(11, 11+1)=12

返回 prev1=12  （偷 nums[0]+nums[2]+nums[4] = 2+9+1 = 12）
```

---

### 213. 打家劫舍 II

#### 核心思路

房屋围成一圈，首尾相邻，其余约束同 198。

核心观察：**首尾不能同时被偷**，因此枚举两种互斥情况：

- 情况 A：不考虑最后一间 → 对 `nums[0..n-2]` 跑线性 DP
- 情况 B：不考虑第一间 → 对 `nums[1..n-1]` 跑线性 DP

两种情况共同覆盖所有合法方案（包含"首尾都不偷"的方案），取较大值即为答案。

```text
原环形: [h0, h1, h2, h3, h4]
                            ↑ 首尾相邻

情况 A (去尾): [h0, h1, h2, h3] → rob_linear → result_A
情况 B (去首): [h1, h2, h3, h4] → rob_linear → result_B

答案 = max(result_A, result_B)
```

#### Python 代码

```python
class Solution:
    def rob(self, nums: list[int]) -> int:
        if len(nums) == 1:
            return nums[0]          # 只有 1 间，直接偷

        def rob_linear(arr: list[int]) -> int:
            prev2, prev1 = 0, 0
            for num in arr:
                prev2, prev1 = prev1, max(prev1, prev2 + num)
            return prev1

        # 情况 A：不含最后一间；情况 B：不含第一间
        return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```

#### 图解

以 `nums = [2, 3, 2]` 为例：

```text
情况 A：nums[:-1] = [2, 3]
  prev2=0, prev1=0
  num=2 → prev2=0,  prev1=2
  num=3 → prev2=2,  prev1=max(2, 0+3)=3
  result_A = 3

情况 B：nums[1:] = [3, 2]
  num=3 → prev2=0,  prev1=3
  num=2 → prev2=3,  prev1=max(3, 0+2)=3
  result_B = 3

答案 = max(3, 3) = 3  （只偷 nums[1]=3，首尾都不动）
```

---

### 337. 打家劫舍 III

#### 核心思路

房屋排成二叉树，父子节点不能同时被偷。

关键：每个节点需要同时记录"偷自己"和"不偷自己"两种情况下的最优值，这个信息必须从**子节点向上传递**——因此使用**后序 DFS**（先处理子节点，再处理当前节点）。

每次递归返回一个元组 `(rob_this, skip_this)`：

```text
rob_this  = node.val + left_skip + right_skip
            ↑ 偷当前节点，左右孩子都不能偷，取各自的 skip 值

skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)
            ↑ 不偷当前节点，左右孩子各自独立决定偷不偷，各取较大值
```

终止条件：空节点返回 `(0, 0)`。

#### Python 代码

```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def rob(self, root: Optional[TreeNode]) -> int:
        rob_this, skip_this = self._dfs(root)
        return max(rob_this, skip_this)

    def _dfs(self, node: Optional[TreeNode]) -> tuple[int, int]:
        """
        后序 DFS，返回 (rob_this, skip_this)：
          rob_this  = 偷当前节点能获得的最大金额
          skip_this = 不偷当前节点能获得的最大金额
        """
        if node is None:
            return (0, 0)                               # 空节点，两种状态均为 0

        left_rob,  left_skip  = self._dfs(node.left)   # 先处理左子树
        right_rob, right_skip = self._dfs(node.right)  # 再处理右子树

        # 偷当前节点：左右孩子强制不偷
        rob_this  = node.val + left_skip + right_skip

        # 不偷当前节点：左右孩子各自独立取最优
        skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)

        return (rob_this, skip_this)
```

#### 图解

以下列二叉树为例（答案为 9）：

```text
        3
       / \
      4   5
     / \   \
    1   3   1
```

后序遍历，各节点返回 (rob_this, skip_this)：

```text
叶节点 1（4 的左孩子）:
  rob=1, skip=0  → 返回 (1, 0)

叶节点 3（4 的右孩子）:
  rob=3, skip=0  → 返回 (3, 0)

节点 4:
  rob_this  = 4 + left_skip(0) + right_skip(0) = 4
  skip_this = max(1,0) + max(3,0) = 1 + 3 = 4
  → 返回 (4, 4)

叶节点 1（5 的右孩子）:
  rob=1, skip=0  → 返回 (1, 0)

节点 5:
  rob_this  = 5 + 0 + right_skip(0) = 5
  skip_this = max(0,0) + max(1,0) = 0 + 1 = 1
  → 返回 (5, 1)

根节点 3:
  rob_this  = 3 + left_skip(4) + right_skip(1) = 3+4+1 = 8
  skip_this = max(4,4) + max(5,1) = 4 + 5 = 9
  → 返回 (8, 9)

答案 = max(8, 9) = 9  （偷节点4 + 节点5：4+5=9）
```

---

## 统一对比

| 维度 | 198 线性 | 213 环形 | 337 树形 |
|:----:|:--------|:--------|:--------|
| 数据结构 | 一维数组 | 环形数组（首尾相邻）| 二叉树 |
| 约束边界 | 相邻下标不能同选 | 额外：首尾节点互斥 | 父子节点不能同选 |
| 核心公式 | `max(prev1, prev2+num)` | 两次 198，取较大值 | `rob=val+L_skip+R_skip` |
| DP 载体 | 两个滚动变量 | 两个滚动变量（两段）| 递归返回值元组 |
| 时间复杂度 | O(n) | O(n) | O(n) |
| 空间复杂度 | O(1) | O(1) | O(h)（递归栈高度）|
| 边界特判 | `len==1` | `len==1` | 空节点返回 `(0,0)` |

**三题本质**：约束都是"相邻节点不能同时选"，数据结构从数组→环形数组→二叉树，DP 的推进方式随之演变，但核心转移公式始终一致。

---

## 口诀

```text
打家劫舍三连口诀：

198 线性：两变量滚动，同时赋值防覆盖
  prev2, prev1 = prev1, max(prev1, prev2+num)

213 环形：化环为线，掐头或去尾各跑一遍
  max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
  切记 len==1 提前返回，别让切片产生空数组

337 树形：后序 DFS，每节点返回 (偷, 不偷) 对
  偷 = val + 左skip + 右skip
  不偷 = max(左rob,左skip) + max(右rob,右skip)
  根节点取 max(rob, skip)

三题共享一个信念：
  相邻不能同偷，结构变公式不变！
```

---

## 总结与扩展

打家劫舍系列是动态规划的经典递进题组，三题共享"相邻节点不能同时被选"这一核心约束，只是数据结构依次升级。198 建立基础认知——用两个滚动变量替代完整 dp 数组，把 O(n) 空间压缩到 O(1)，并养成"同时赋值防止 prev2 被提前覆盖"的习惯。213 的突破口是将环形约束转化为两个独立的线性子问题：去掉最后一间跑一次，去掉第一间再跑一次，取较大值——"化环为线"的思路在很多环形/循环题里通用。337 将 DP 迁移到二叉树，利用后序遍历"子节点先于父节点处理"的天然顺序，让每个节点通过返回值向上传递"偷/不偷"两种状态，一次遍历以 O(n) 时间解决问题，完全不需要额外的记忆化字典。

三题贯通之后，遇到"相邻约束最优选择"类问题，第一反应是判断数据结构：线性数组用滚动变量直接推，环形数组化成两段线性，树结构用后序 DFS 返回状态对。

**相关扩展题目**：

- [740. 删除并获得点数](https://leetcode.cn/problems/delete-and-earn/)：先将点数频次累加到桶里，再对桶数组跑 198——本质上就是打家劫舍
- [2560. 打家劫舍 IV](https://leetcode.cn/problems/house-robber-iv/)：二分答案 + 贪心验证，打家劫舍的进阶变体
- [124. 二叉树中的最大路径和](https://leetcode.cn/problems/binary-tree-maximum-path-sum/)：树形 DP 后序遍历，返回单侧最优值，结构与 337 相似
