---
title: "二叉树 BFS 应用：层序遍历八题变体"
date: 2026-03-09T10:00:00+08:00
draft: false
slug: "binary-tree-bfs"
tags:
  - "Algorithm"
  - "BFS"
  - "Tree"
  - "Python"
categories:
  - "LeetCode"
description: "涵盖 LeetCode 107/637/429/515/116/117/104/111。层序遍历统一框架：deque+按层处理适配八道题，区别只在每层处理逻辑（逆序/均值/N叉/最大/填充指针/最小深度等）。"
---

> **本文涵盖**：LeetCode 107 / 637 / 429 / 515 / 116 / 117 / 104 / 111（共 8 题）
>
> **难度**：简单 / 中等 ｜ **关键词**：层序遍历、BFS、deque、按层处理

---

## 识别信号

> 看到什么特征，想到这篇笔记？

- 题目要求"按层"处理或输出：每层的均值、最大值、从底部倒序输出各层
- 题目涉及同层节点之间的关系：填充同层相邻节点的 `next` 指针
- 求从根到叶节点的最大或最小深度，且希望利用"层"的结构提前终止
- 二叉树推广至 N 叉树，"按层遍历"的逻辑与二叉树完全一致

---

## 核心模板（速查）

```python
from collections import deque

def levelOrder(root):
    if not root:
        return []
    queue = deque([root])
    res = []
    while queue:
        level_size = len(queue)           # 锁层：固定当前层节点数（关键！）
        current_level = []
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)   # ← 【改动点 A】每层收集逻辑
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)     # ← 【改动点 B】子节点入队方式
        res.append(current_level)            # ← 【改动点 C】层结果写入方式
    return res
```

八道题的所有改动均限定在 A / B / C 三处，框架本身一字不动。

### 八题变化点对比

| 题号 | 改哪里 | 具体改动 |
|------|--------|---------|
| **107** 层序遍历 II | C | `res.appendleft(current_level)`（头插实现逆序） |
| **637** 层平均值 | A、C | 维护 `level_sum`，输出 `level_sum / level_size` |
| **429** N 叉树 | B | `for child in node.children` 替换左右子节点 |
| **515** 层最大值 | A、C | 维护 `level_max`，输出 `level_max` |
| **116/117** 填充指针 | A | 层内 `node.next = queue[0]`（同层相邻连接） |
| **104** 最大深度 | C | 不收集值，层结束时 `depth += 1` |
| **111** 最小深度 | A | 检测叶节点，遇叶立即 `return depth` |

---

## ⚠️ 高频错误

**1. 没有"锁层"——在循环内动态取 `len(queue)`**

```python
# ❌ 错误：每轮循环时 queue 的大小随子节点入队而增大，下一层也被当前层处理
while queue:
    for _ in range(len(queue)):    # 子节点入队后 len 变大，越界到下一层！
        node = queue.popleft()
        ...

# ✅ 正确：循环前一次性固定当前层大小
while queue:
    level_size = len(queue)        # 先锁层
    for _ in range(level_size):
        node = queue.popleft()
        ...
```

**2. 111 最小深度——把空子树当叶节点（DFS 版高频错）**

```python
# ❌ 错误：直接 min，左子树为空时 minDepth(None)=0，min(0,x)=0，返回 1
def minDepth(root):
    if not root:
        return 0
    return 1 + min(minDepth(root.left), minDepth(root.right))
# 对只有左子树的节点（右为 None）：min(left_depth, 0)=0，输出 1，错误！

# ✅ 正确：只有一侧子树时，必须走有节点的那一侧，不能"走空路"
def minDepth(root):
    if not root:
        return 0
    if not root.left:
        return 1 + minDepth(root.right)
    if not root.right:
        return 1 + minDepth(root.left)
    return 1 + min(minDepth(root.left), minDepth(root.right))
```

**3. 用 `list` 代替 `deque`——`pop(0)` 性能陷阱**

```python
# ❌ 错误：list.pop(0) 是 O(n)，节点多时会超时
queue = [root]
node = queue.pop(0)   # 每次移动整个列表

# ✅ 正确：deque.popleft() 是 O(1)
from collections import deque
queue = deque([root])
node = queue.popleft()
```

**4. 116/117 填充指针——层末节点被错误连接到下一层**

```python
# ❌ 错误：未判断层末，queue[0] 此时已是下一层头节点
for i in range(level_size):
    node = queue.popleft()
    node.next = queue[0]   # 层末节点出队后 queue[0] 是下一层节点，错误！

# ✅ 正确：i < level_size - 1 时才连接，层末节点 next 保持 None
for i in range(level_size):
    node = queue.popleft()
    if i < level_size - 1:
        node.next = queue[0]
```

---

## 详解

### 107. 二叉树的层序遍历 II

#### 核心思路

与标准层序遍历（102）逻辑完全相同，区别仅在于结果要从底向上输出。将结果容器改为 `deque`，每层用 `appendleft` 头插，遍历结束后转为 `list` 返回。

#### Python 代码

```python
from collections import deque
from typing import Optional, List

class Solution:
    def levelOrderBottom(self, root: Optional[TreeNode]) -> List[List[int]]:
        if not root:
            return []
        queue = deque([root])
        res = deque()                       # 用 deque 支持 appendleft

        while queue:
            level_size = len(queue)
            current_level = []
            for _ in range(level_size):
                node = queue.popleft()
                current_level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            res.appendleft(current_level)   # 头插：最底层最先进，最终在列表头部

        return list(res)
```

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 637. 二叉树的层平均值

#### 核心思路

每层遍历时维护 `level_sum` 累加节点值，层结束后除以 `level_size` 得均值追加到结果。

#### Python 代码

```python
class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> List[float]:
        if not root:
            return []
        queue = deque([root])
        res = []

        while queue:
            level_size = len(queue)
            level_sum = 0
            for _ in range(level_size):
                node = queue.popleft()
                level_sum += node.val          # 累加当层所有节点值
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            res.append(level_sum / level_size) # 当层均值

        return res
```

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 429. N 叉树的层序遍历

#### 核心思路

N 叉树每节点有 `children` 列表。将二叉树的 `if node.left / if node.right` 替换为遍历 `node.children`，注意 `children` 中元素可能为 `None`，入队前需判断。

#### Python 代码

```python
class Solution:
    def levelOrder(self, root: 'Node') -> List[List[int]]:
        if not root:
            return []
        queue = deque([root])
        res = []

        while queue:
            level_size = len(queue)
            current_level = []
            for _ in range(level_size):
                node = queue.popleft()
                current_level.append(node.val)
                for child in node.children:    # 遍历所有子节点
                    if child:                  # children 可能含 None，需判断
                        queue.append(child)
            res.append(current_level)

        return res
```

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 515. 在每个树行中找最大值

#### 核心思路

每层维护 `level_max = float('-inf')`，遍历当层节点时持续更新，层结束后追加到结果。

#### Python 代码

```python
class Solution:
    def largestValues(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []
        queue = deque([root])
        res = []

        while queue:
            level_size = len(queue)
            level_max = float('-inf')           # 每层重置最大值
            for _ in range(level_size):
                node = queue.popleft()
                level_max = max(level_max, node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            res.append(level_max)

        return res
```

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 116. 填充每个节点的下一个右侧节点指针

#### 核心思路

利用层序遍历，对同层内相邻节点进行"拉链"操作：处理第 `i` 个出队节点时，若 `i < level_size - 1`，此时 `queue[0]` 恰好是右侧紧邻的节点。

```text
层内节点出队顺序：  A → B → C → D
next 连接过程：
  A 出队时 queue[0]=B  →  A.next = B
  B 出队时 queue[0]=C  →  B.next = C
  C 出队时 queue[0]=D  →  C.next = D
  D 是层末节点（i == level_size-1），跳过  →  D.next = None
```

#### Python 代码

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        if not root:
            return root
        queue = deque([root])

        while queue:
            level_size = len(queue)
            for i in range(level_size):
                node = queue.popleft()
                if i < level_size - 1:
                    node.next = queue[0]   # queue[0] 是同层右侧相邻节点
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return root
```

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 117. 填充每个节点的下一个右侧节点指针 II

#### 核心思路

与 116 代码完全一致。BFS 层序方案天然处理普通二叉树，"完美二叉树"条件只使 116 存在 $O(1)$ 空间的进阶解法（沿已建立的 `next` 链遍历下一层，省去 queue），但本题无需该进阶。

#### Python 代码

```python
class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        if not root:
            return root
        queue = deque([root])

        while queue:
            level_size = len(queue)
            for i in range(level_size):
                node = queue.popleft()
                if i < level_size - 1:
                    node.next = queue[0]   # 与 116 完全相同
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return root
```

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 104. 二叉树的最大深度

#### 核心思路

BFS 每处理完一层，`depth += 1`。所有层处理完毕后，`depth` 即为最大深度。

#### Python 代码

```python
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        queue = deque([root])
        depth = 0

        while queue:
            level_size = len(queue)
            depth += 1                         # 处理完一层，深度 +1
            for _ in range(level_size):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return depth
```

> DFS 递归一行版：`return 1 + max(maxDepth(root.left), maxDepth(root.right))`。BFS 版在面试中更能体现对层序遍历的掌握。

**复杂度**：时间 $O(n)$，空间 $O(n)$

---

### 111. 二叉树的最小深度

#### 核心思路

BFS 按层推进，**第一次遇到叶节点时当前 `depth` 就是最短路径**，立即返回，无需遍历整棵树。

叶节点定义：**左右子节点均为 `None`**。只有单侧子节点的节点不是叶节点，不能提前返回。

```text
反例：
        1
       /
      2

节点 1 有左子节点，不是叶节点，depth=1 时不能返回。
BFS 第二层遇到节点 2（左右均为 None），才返回 depth=2。
```

#### Python 代码（BFS，推荐）

```python
class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        queue = deque([root])
        depth = 0

        while queue:
            level_size = len(queue)
            depth += 1
            for _ in range(level_size):
                node = queue.popleft()
                if not node.left and not node.right:
                    return depth               # 第一个叶节点即为最短路径终点
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return depth
```

#### Python 代码（DFS，需处理单子节点特殊情况）

```python
class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        if not root.left:                      # 只有右子树，必须走右边，不能取 min(0,x)
            return 1 + self.minDepth(root.right)
        if not root.right:                     # 只有左子树，必须走左边
            return 1 + self.minDepth(root.left)
        return 1 + min(self.minDepth(root.left), self.minDepth(root.right))
```

**复杂度**：BFS 时间 $O(n)$（最坏），空间 $O(n)$；最好情况比 DFS 更早终止

---

## 统一对比

| 题号 | 层内收集逻辑 | 层后输出逻辑 | 提前终止 |
|------|------------|------------|---------|
| **107** 层序 II | `current_level.append(val)` | `res.appendleft(level)` | 否 |
| **637** 层均值 | `level_sum += val` | `res.append(sum/size)` | 否 |
| **429** N 叉树 | `current_level.append(val)` | `res.append(level)` | 否 |
| **515** 层最大值 | `level_max = max(...)` | `res.append(max)` | 否 |
| **116** 填充指针 | `node.next = queue[0]` | 返回 root | 否 |
| **117** 填充指针 II | `node.next = queue[0]` | 返回 root | 否 |
| **104** 最大深度 | —（不收集值） | `depth += 1` | 否 |
| **111** 最小深度 | 检测叶节点 | `return depth` | **是** |

所有题目 BFS 复杂度统一：时间 $O(n)$，空间 $O(n)$（满二叉树最底层约 $n/2$ 个节点）。

---

## 口诀

```text
BFS 层序五步走：
  初始化 deque 放根节点，
  while 非空进外循环，
  level_size 先锁层（不锁就越层！），
  for range 处理当层节点，
  左右子节点入队继续。

八题改哪里？
  改收集逻辑 → 637 均值  515 最大值  107 头插
  改入队方式 → 429 N 叉树用 children
  改层内操作 → 116/117 连接 next 指针
  改返回逻辑 → 104 逐层 +1  111 叶节点即止

最小深度三句话：
  叶 = 左右都空，
  有单子节点 ≠ 叶，必须往下走，
  BFS 遇第一个叶 = 最短路径。
```

---

## 总结与扩展

BFS 层序遍历的核心不变量：**外层 `while` 控制层数，内层 `for range(level_size)` 控制当层节点数**。`level_size = len(queue)` 这一行是层序遍历区别于普通 BFS 的关键——锁住层边界后，变体逻辑只需在循环体内修改。

BFS 与 DFS 的选择准则：
- 涉及"层"的信息（层均值、层最值、填充同层指针）→ 优先 BFS，层结构天然对齐
- 路径问题（根到叶路径、路径总和）→ 优先 DFS，递归更直观
- 最大深度 → 两者均可，DFS 一行代码；最小深度 → BFS 可提前终止，更高效

**扩展题目**

| 题目 | 要点 |
|------|------|
| 102. 二叉树的层序遍历 | 本文所有题的基础模板 |
| 199. 二叉树的右视图 | 每层取最后一个节点（`if i == level_size - 1`） |
| 662. 二叉树最大宽度 | BFS + 节点虚拟编号（左子 `2i`，右子 `2i+1`） |
| 987. 二叉树的垂序遍历 | BFS + `(col, row, val)` 坐标排序 |
