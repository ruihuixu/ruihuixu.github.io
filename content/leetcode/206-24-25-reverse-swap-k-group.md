---
title: "LeetCode 206 / 24 / 25：链表反转的统一心智模型——从单次反转到 K 组翻转"
date: 2026-01-22T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Linked List"
  - "Java"
categories:
  - "LeetCode"
description: "链表反转的本质是指针重连的原子操作。本文建立统一模板：206 全反转是基础，24 两两交换是 k=2 特例，25 K 组翻转是通用抽象。"
---

> 题目链接：
>
> - [206. 反转链表](https://leetcode.cn/problems/reverse-linked-list/)
> - [24. 两两交换链表中的节点](https://leetcode.cn/problems/swap-nodes-in-pairs/)
> - [25. K 个一组翻转链表](https://leetcode.cn/problems/reverse-nodes-in-k-group/)
>
> 难度：简单 / 中等 / 困难 ｜ 标签：链表、递归、迭代

## 核心心智：链表反转 = 指针重连的原子步骤

链表题的难点不在算法复杂度，而在**指针管理**：稍有不慎就会断链（丢失节点）或成环（死循环）。

这三道题构成完整的抽象升级路径：

- **206**：全链表反转，建立"三指针迭代"的基础模板
- **24**：两两交换，本质是 **K=2 的分组反转**
- **25**：K 个一组翻转，通用抽象，前两题都是它的特例

掌握这套统一模板后，你会发现所有链表反转题都是同一个"指针重连舞蹈"的不同编排。

---

## 一、基础：206. 反转链表

### 题目描述

给你单链表的头节点 `head`，请你反转链表，并返回反转后的链表。

### 核心思路：三指针迭代

要在遍历过程中改变指针方向，需要维护三个视角：

1. **prev（前驱）**：反转后，当前节点要指向它
2. **curr（当前）**：正在处理的节点
3. **next（后继）**：**最容易丢的**！在改变 `curr.next` 之前，必须先保存它，否则链表就断了

### 原子操作三步走（每轮循环）

```text
1. 保存后继：next = curr.next  （防止断链）
2. 反转指针：curr.next = prev  （核心操作）
3. 整体前进：prev = curr; curr = next
```

### 代码实现

```java
public ListNode reverseList(ListNode head) {
    ListNode prev = null; // 反转后的尾节点指向 null
    ListNode curr = head;

    while (curr != null) {
        // 1. 暂存后继节点（防止断链）
        ListNode next = curr.next;

        // 2. 反转指针（核心步骤）
        curr.next = prev;

        // 3. 整体前进
        prev = curr;
        curr = next;
    }

    // 循环结束时，curr 为 null，prev 指向新头节点
    return prev;
}
```

### 关键点

- **为什么 prev 初始为 null？** 因为原头节点反转后变成尾节点，尾节点的 `next` 应该是 `null`。
- **为什么返回 prev？** 循环结束时 `curr` 已经走到 `null`，`prev` 才是最后一个有效节点（新头）。
---

## 二、进阶：24. 两两交换链表中的节点

### 题目描述

给你一个链表，两两交换其中相邻的节点，并返回交换后链表的头节点。

### 核心思路：Dummy + 分组反转（k=2）

这道题本质是 **每 2 个节点为一组进行局部反转**，与 206 的区别在于：

- 不是全局反转，而是**分组操作**
- 需要处理**组与组之间的连接**
- 头节点会变，必须用 **Dummy Node** 统一处理

### 为什么需要 Dummy？

因为头节点会变（原来的第 2 个变成第 1 个），使用 `dummy` 指向 `head` 可以避免单独处理头节点的特殊情况。

### 操作步骤（以 cur -> 1 -> 2 -> 3 为例）

假设 `cur` 指向待交换一对节点的前驱：

```text
原始：cur -> 1 -> 2 -> 3
目标：cur -> 2 -> 1 -> 3

步骤：
1. 保存 node1 = cur.next, node2 = cur.next.next, next = node2.next
2. 重连：cur.next = node2
3. 反转：node2.next = node1
4. 接续：node1.next = next
5. 前进：cur = node1（为下一组做准备）
```

### 代码实现

```java
public ListNode swapPairs(ListNode head) {
    ListNode dummy = new ListNode(-1);
    dummy.next = head;

    ListNode cur = dummy;

    // 必须保证后面有两个节点才能交换
    while (cur.next != null && cur.next.next != null) {
        ListNode node1 = cur.next;
        ListNode node2 = cur.next.next;
        ListNode next = node2.next; // 暂存下一组的开头

        // 核心三步走
        cur.next = node2;   // 前驱指向第 2 个
        node2.next = node1; // 第 2 个指向第 1 个（反转）
        node1.next = next;  // 第 1 个接续后面

        // 准备下一轮
        cur = node1; // node1 现在是这一对的第二个节点，也是下一对的前驱
    }

    return dummy.next;
}
```

### 关键点

- **循环条件**：`cur.next != null && cur.next.next != null`，顺序不能反（先判 `next` 再判 `next.next`，否则 NPE）
- **指针保存顺序**：必须先 `next = node2.next`，再修改 `node2.next`，否则后续节点丢失
- **cur 的前进**：`cur = node1`，因为 `node1` 交换后变成了这一对的第二个节点
---

## 三、通用抽象：25. K 个一组翻转链表

### 题目描述

给你链表的头节点 `head`，每 `k` 个节点一组进行翻转，返回修改后的链表。

- `k` 是一个正整数，它的值小于或等于链表的长度
- 如果节点总数不是 `k` 的整数倍，那么请将最后剩余的节点保持原有顺序

### 核心思路：分组 + 组内反转 + 组间重连

这是链表反转的**最通用模板**，206 和 24 都是它的特例：

- **206**：`k = n`（全链表长度）
- **24**：`k = 2`

### 算法步骤

1. **计数**：先遍历一遍得到链表总长度 `n`
2. **分组循环**：外层循环控制分组（`n >= k` 时继续，每组处理后 `n -= k`）
3. **组内反转**：内层循环用 206 的三指针迭代法反转 `k` 个节点
4. **组间重连**：利用 `p0.next` 巧妙完成组头、组尾的重连
5. **尾段处理**：不足 `k` 个的尾段自动保持原顺序

### 关键变量

- `dummy`：虚拟头节点，统一处理头节点变化
- `p0`：**当前组的前驱节点**（组外连接点，核心指针）
- `pre / cur`：组内反转时的前驱和当前节点
- `nxt`：临时保存 `cur.next`，防止断链

### 代码实现（迭代版）

```java
public ListNode reverseKGroup(ListNode head, int k) {
    // 1. 统计节点个数
    int n = 0;
    for (ListNode cur = head; cur != null; cur = cur.next) {
        n++;
    }

    // 2. 初始化 dummy 和 p0（组前驱）
    ListNode dummy = new ListNode(0, head);
    ListNode p0 = dummy;
    ListNode pre = null;
    ListNode cur = head;

    // 3. k 个一组处理
    for (; n >= k; n -= k) { // 外层：只要剩余节点 >= k 就继续
        // 3.1 组内反转（标准三指针迭代，反转 k 次）
        for (int i = 0; i < k; i++) {
            ListNode nxt = cur.next;
            cur.next = pre; // 每次循环只修改一个 next
            pre = cur;
            cur = nxt;
        }
        // 循环结束时：pre 指向新组头，cur 指向下一组开头

        // 3.2 组间重连（精髓：利用 p0.next 完成两步连接）
        ListNode nxt = p0.next;      // 暂存原组头（反转后变成组尾）
        p0.next.next = cur;          // 新组尾连接下一组
        p0.next = pre;               // 前驱连接新组头
        p0 = nxt;                    // 下一组的前驱是当前组的尾
    }

    return dummy.next;
}
```

### 图解（以 1->2->3->4->5, k=2 为例）

```text
初始：dummy -> 1 -> 2 -> 3 -> 4 -> 5
      p0      cur

第 1 组（反转 1, 2）：
  组内反转后：pre=2, cur=3
  p0.next = 1（原组头，即将变成组尾）

  重连步骤：
    nxt = p0.next = 1
    p0.next.next = cur  →  1.next = 3（组尾接下一组）
    p0.next = pre       →  dummy.next = 2（前驱接新组头）
    p0 = nxt            →  p0 = 1（准备下一组）

  结果：dummy -> 2 -> 1 -> 3 -> 4 -> 5
                     p0   cur

第 2 组（反转 3, 4）：
  组内反转后：pre=4, cur=5
  p0.next = 3

  重连步骤：
    nxt = p0.next = 3
    p0.next.next = cur  →  3.next = 5
    p0.next = pre       →  1.next = 4
    p0 = nxt            →  p0 = 3

  结果：dummy -> 2 -> 1 -> 4 -> 3 -> 5
                          p0   cur

剩余（5）：n=1 < k=2，循环结束，保持原顺序

最终：dummy -> 2 -> 1 -> 4 -> 3 -> 5
```

### 关键点

- **组内反转**：标准三指针迭代，循环 `k` 次后 `pre` 指向新组头，`cur` 指向下一组
- **组间重连的精髓**：
  - `p0.next` 始终指向**原组头**（反转后变成组尾）
  - 先用 `nxt` 暂存 `p0.next`（原组头）
  - `p0.next.next = cur`：让组尾接下一组
  - `p0.next = pre`：让前驱接新组头
  - `p0 = nxt`：移动到下一组的前驱位置
- **循环条件**：`n >= k` 自动处理尾段，`n -= k` 每组递减
- **为什么不需要提前找 kth？** 因为组内反转循环固定 `k` 次，反转完 `cur` 自然指向下一组

---

## 四、统一对比与抽象升级

| 特性 | 206. 反转链表 | 24. 两两交换 | 25. K 组翻转 |
|------|--------------|-------------|-------------|
| **操作范围** | 全局反转 | 每 2 个一组 | 每 k 个一组 |
| **Dummy 节点** | 非必须 | 必须 | 必须 |
| **核心操作** | 三指针迭代 | 分组 + 组内反转 | 分组 + 组内反转 + 组间重连 |
| **指针步长** | 每次 1 个节点 | 每次 2 个节点 | 每次 k 个节点 |
| **尾段处理** | 无需处理 | 自动保留 | 不足 k 个保持原顺序 |
| **抽象关系** | 基础模板 | k=2 特例 | 通用抽象 |

### 统一模板的本质

无论是 206、24 还是 25，核心都是：

1. **保存后继**：在断链前先保存 `next`
2. **反转指针**：改变 `curr.next` 的指向
3. **整体前进**：移动 `prev` 和 `curr`
4. **组间重连**（分组题）：处理组头、组尾与外部的连接

---

## 五、复杂度分析

### 时间复杂度

- **206**：$O(n)$，每个节点访问一次
- **24**：$O(n)$，每个节点访问一次
- **25**：$O(n)$，计数 $O(n)$ + 分组反转 $O(n)$

### 空间复杂度

- **迭代版**：$O(1)$，只用常数个指针
- **递归版**（未展示）：$O(n/k)$，递归栈深度

---

## 六、易错点清单（Bug-Free Guide）

### 1. 空指针判断顺序

```java
// ❌ 错误：可能在 cur.next 为 null 时访问 cur.next.next
while (cur.next.next != null && cur.next != null)

// ✅ 正确：先判断 next，再判断 next.next
while (cur.next != null && cur.next.next != null)
```

### 2. 后继节点丢失

```java
// ❌ 错误：先改 node2.next，再访问 node2.next 会得到错误值
node2.next = node1;
node1.next = node2.next; // 此时 node2.next 已经是 node1 了！

// ✅ 正确：先保存，再修改
ListNode next = node2.next;
node2.next = node1;
node1.next = next;
```

### 3. 组间重连顺序（25 题的精髓）

```java
// ❌ 错误：先移动 p0，再连接会导致前驱丢失
p0 = p0.next;
p0.next = pre; // 此时 p0 已经变了！

// ✅ 正确：先暂存，再连接，最后移动
ListNode nxt = p0.next;  // 暂存原组头
p0.next.next = cur;      // 组尾接下一组
p0.next = pre;           // 前驱接新组头
p0 = nxt;                // 移动到下一组前驱
```

**为什么要用 `p0.next` 而不是单独变量？**

- `p0.next` 在反转前指向**原组头**，反转后这个节点变成**新组尾**
- 通过 `p0.next.next = cur` 直接让组尾接下一组，无需额外变量追踪组尾
- 这是利用"反转前后同一节点身份变化"的巧妙设计

### 4. 成环风险

反转时如果忘记断开原有连接，可能形成环：

```java
// ❌ 错误：忘记让组尾指向下一组
p0.next = prev; // 只连了组头，组尾还指向组内节点

// ✅ 正确：组尾必须指向下一组
newTail.next = next;
```

### 5. Dummy 的意义

- **何时必须用 Dummy？** 头节点可能变化时（24、25）
- **Dummy 的值重要吗？** 不重要，只是占位符
- **返回什么？** 返回 `dummy.next`，不是 `dummy`

---

## 七、口诀式总结：一套模板通吃三题

```text
【链表反转万能模板】

1. 头变必加 Dummy，统一处理不特判
2. 先保后继 nxt，再断再连不成环
3. 三指针舞蹈：pre ← cur → nxt，循环前进
4. 分组反转（25 题精髓）：
   - 外层循环：n >= k 继续，n -= k 递减
   - 内层循环：标准三指针，反转 k 次
   - 组间重连：利用 p0.next（原组头 = 新组尾）
     ① nxt = p0.next（暂存原组头）
     ② p0.next.next = cur（组尾接下一组）
     ③ p0.next = pre（前驱接新组头）
     ④ p0 = nxt（移动到下一组前驱）
5. 空指针判断：先 next 再 next.next，顺序不能反
6. 返回新头：dummy.next，不是 dummy

【抽象升级路径】
206（全反转）→ 基础模板：三指针迭代
24（k=2）    → 分组 + Dummy + 组间重连
25（k 组）   → 通用抽象：计数 + 双层循环 + p0.next 技巧

【核心不变量】
- 每轮循环后，已处理部分的指针方向正确，未处理部分保持原样
- p0 始终指向"已完成组"的最后一个节点（下一组的前驱）
- p0.next 在反转前是原组头，反转后变成新组尾（利用这个身份变化完成重连）
```

---

## 总结

链表反转题的本质是**指针重连的原子操作**，掌握这套统一模板后：

- **206** 是基础，建立三指针迭代的肌肉记忆
- **24** 是特例，理解分组与 Dummy 的必要性
- **25** 是通用，融会贯通后可以秒杀所有链表反转变体

记住：**先保存，再断链，再重连，最后前进**。画图推演一遍，代码自然长出来。
