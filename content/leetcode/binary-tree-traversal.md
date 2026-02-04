---
title: "二叉树遍历笔记：DFS 与 BFS 的递归迭代双解——Python 统一模板"
date: 2026-02-03T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Tree"
  - "Recursion"
  - "Iteration"
  - "Python"
categories:
  - "LeetCode"
description: "二叉树遍历的本质是递归与迭代的统一理解。本文建立 Python 视角的统一模板：DFS 三序遍历（递归一行改、迭代手动栈）、BFS 层序遍历（队列锁层），并给出常见报错的避坑指南。"
---

> 题目链接（本文涉及）：
>
> - [144. 二叉树的前序遍历](https://leetcode.cn/problems/binary-tree-preorder-traversal/)
> - [94. 二叉树的中序遍历](https://leetcode.cn/problems/binary-tree-inorder-traversal/)
> - [145. 二叉树的后序遍历](https://leetcode.cn/problems/binary-tree-postorder-traversal/)
> - [102. 二叉树的层序遍历](https://leetcode.cn/problems/binary-tree-level-order-traversal/)
> - [199. 二叉树的右视图](https://leetcode.cn/problems/binary-tree-right-side-view/)
>
> 难度：简单/中等 ｜ 标签：树、深度优先搜索、广度优先搜索、递归、迭代

## 核心心智：树是递归定义的，遍历也是递归思维的延伸

写二叉树题目时，脑子里只需要挂住一件事：

**"对于当前的 `root`，我需要做什么？怎么处理 `left` 和 `right` 返回的结果？"**

不要试图在脑子里模拟整棵树的递归过程——会晕。只考虑当前节点做什么，递归自然帮你搞定子树。

---

## 一、理论基础：二叉树的定义与 Python 特性

### 1.1 节点定义

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

### 1.2 Python 刷树题的三个特性

| 特性 | 说明 | 注意事项 |
|------|------|----------|
| **对象引用** | Python 没有指针概念，用引用操作节点 | 直接赋值即可，无需 `*` 或 `&` |
| **列表可变** | `list` 是可变对象，递归中可直接 `append` | 数字不可变，递归传参需注意作用域 |
| **deque 队列** | `collections.deque` 实现高效双端队列 | BFS 必备，`popleft()` 是 $O(1)$ |

---

## 二、深度优先遍历（DFS）：递归与迭代双解

### 2.1 递归模板（The Easy Way）

逻辑最清晰，**三种遍历的区别仅在于 `res.append(node.val)` 的位置**。

```python
class Solution:
    def traversal(self, root: Optional[TreeNode]) -> List[int]:
        res = []
        
        def dfs(node):
            if not node:
                return
            
            # res.append(node.val)  # 前序 (Preorder): 中 → 左 → 右
            dfs(node.left)
            # res.append(node.val)  # 中序 (Inorder): 左 → 中 → 右
            dfs(node.right)
            # res.append(node.val)  # 后序 (Postorder): 左 → 右 → 中
            
        dfs(root)
        return res
```

### 2.2 迭代模板（The Hard Way）

迭代法需要手动维护一个**栈（Stack）** 来模拟递归调用栈。

#### A. 前序遍历迭代

> **口诀**：先压右，再压左（因为栈是后进先出）。

```python
def preorderTraversal(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    
    stack, res = [root], []
    while stack:
        node = stack.pop()
        res.append(node.val)          # 中
        if node.right:                # 右（先入栈，后出）
            stack.append(node.right)
        if node.left:                 # 左（后入栈，先出）
            stack.append(node.left)
    return res
```

#### B. 中序遍历迭代

> **口诀**：一路向左撞南墙，撞完回头看右旁。

```python
def inorderTraversal(root: Optional[TreeNode]) -> List[int]:
    stack, res = [], []
    curr = root
    
    while curr or stack:
        if curr:
            stack.append(curr)        # 一路向左，保存沿途节点
            curr = curr.left
        else:
            curr = stack.pop()        # 左边没路了，弹出节点
            res.append(curr.val)      # 中
            curr = curr.right         # 转向右子树
    return res
```

#### C. 后序遍历迭代（巧妙翻转法）

> **思路**：后序是"左右中"。按"中右左"遍历（前序变种），最后 `reverse()` 就是后序。

```python
def postorderTraversal(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    
    stack, res = [root], []
    while stack:
        node = stack.pop()
        res.append(node.val)          # 中
        if node.left:                 # 左（先入栈，后出 → 右子树先处理）
            stack.append(node.left)
        if node.right:                # 右
            stack.append(node.right)
    return res[::-1]                  # 翻转：中右左 → 左右中
```

### 2.3 DFS 对比速查表

| 遍历顺序 | 递归位置 | 迭代技巧 | 口诀 |
|----------|----------|----------|------|
| **前序** | 递归前 `append` | 栈：先压右再压左 | "中左右" |
| **中序** | 左递归后 `append` | 指针一路向左 + 栈回溯 | "撞南墙" |
| **后序** | 右递归后 `append` | 前序变种 + 结果翻转 | "翻转法" |

---

## 三、广度优先遍历（BFS/层序）

### 3.1 迭代模板（Queue — 标准解法）

> **关键点**：使用 `collections.deque`；利用 `range(len(queue))` **一次性处理一整层**。

```python
from collections import deque

def levelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    
    queue = deque([root])
    res = []
    
    while queue:
        level_size = len(queue)       # 锁定当前层的节点数量
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()    # 先进先出
            current_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        res.append(current_level)
    return res
```

### 3.2 递归模板（DFS 模拟 BFS）

> **关键点**：携带 `level` 参数，利用索引直接填入结果集。

```python
def levelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    res = []
    
    def dfs(node, level):
        if not node:
            return
        if len(res) == level:         # 新的一层，开辟新空间
            res.append([])
        res[level].append(node.val)
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)
    
    dfs(root, 0)
    return res
```

---

## 四、方法选择决策树

```text
【什么时候用什么？】

                    ┌─ 最短路径 / 层级统计（最大宽度、最小深度）
                    │   → 首选 BFS (Iterative)
你要解决什么？ ─────┤
                    │
                    └─ 回溯 / 路径搜索 / 子树逻辑（翻转二叉树、判断对称）
                        → 首选 DFS (Recursive)

【右视图 / 左视图问题】

- BFS：取每层最后一个 / 第一个
- DFS：优先遍历右子树（根→右→左），记录 depth，每层第一次遇到的即右视图节点
```

---

## 五、易错点清单（Bug-Free Guide）

### 1. `AttributeError: 'NoneType' has no attribute 'val'`

```python
# ❌ 错误：没有检查空节点
def traverse(node):
    print(node.val)        # node 为 None 时报错
    traverse(node.left)

# ✅ 正确：入口处检查
def traverse(node):
    if not node:
        return
    print(node.val)
    traverse(node.left)
```

**记住**：永远在访问 `node.val` 或 `node.left` 前检查 `if node:` 或入口处 `if not root: return`。

### 2. `UnboundLocalError`（嵌套函数作用域问题）

```python
# ❌ 错误：在嵌套函数中修改外部不可变变量
def countNodes(root):
    count = 0
    def dfs(node):
        if not node:
            return
        count += 1         # 报错！Python 认为 count 是局部变量
        dfs(node.left)
    dfs(root)
    return count

# ✅ 正确方案 1：使用 nonlocal
def countNodes(root):
    count = 0
    def dfs(node):
        nonlocal count
        if not node:
            return
        count += 1
        dfs(node.left)
    dfs(root)
    return count

# ✅ 正确方案 2：包装成列表
def countNodes(root):
    count = [0]
    def dfs(node):
        if not node:
            return
        count[0] += 1
        dfs(node.left)
    dfs(root)
    return count[0]
```

### 3. BFS 忘记锁定当前层

```python
# ❌ 错误：没有锁定层大小，会把下一层也处理了
while queue:
    node = queue.popleft()
    # ... 直接处理，导致层级混乱

# ✅ 正确：用 for 循环锁定当前层
while queue:
    level_size = len(queue)           # 先锁定！
    for _ in range(level_size):
        node = queue.popleft()
        # ...
```

---

## 六、口诀式总结

```text
【DFS 递归三行诀】

前序：先记值，再递归左右
中序：先递归左，记值，再递归右
后序：先递归左右，再记值

【DFS 迭代三招】

前序栈法：先压右再压左
中序指针：一路向左撞南墙
后序翻转：中右左 → 反转

【BFS 层序】

队列 + 锁层 = 标准答案
level 参数 + DFS = 递归模拟
```

---

## 总结

二叉树遍历是所有树形题目的基础。核心要点：

1. **递归思维**：只考虑当前节点做什么，子树交给递归
2. **迭代本质**：用栈模拟递归（DFS），用队列按层处理（BFS）
3. **Python 特性**：注意 `nonlocal` 作用域、善用 `deque`

### 扩展题目清单

| 类别 | 题目 |
|------|------|
| **基础遍历** | 144/94/145（DFS）、102（BFS） |
| **构造** | 105（前序+中序构造）、106（中序+后序构造） |
| **属性** | 101（对称二叉树）、104（最大深度）、110（平衡二叉树） |
| **公共祖先** | 236（最近公共祖先 — 递归经典） |
