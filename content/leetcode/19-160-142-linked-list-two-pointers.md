---
title: "LeetCode 19 / 160 / 142：链表双指针的物理学——距离、路程与速度的统一模型"
date: 2026-01-23T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Linked List"
  - "Two Pointers"
  - "Java"
categories:
  - "LeetCode"
description: "链表无法随机访问，如何精准定位？本文建立统一心智模型：距离差（尺子法）、路程差（拼接法）、速度差（追及法），三种双指针方法通吃链表定位问题。"
---

> 题目链接：
>
> - [19. 删除链表的倒数第 N 个结点](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/)
> - [160. 相交链表](https://leetcode.cn/problems/intersection-of-two-linked-lists/)（面试题 02.07）
> - [142. 环形链表 II](https://leetcode.cn/problems/linked-list-cycle-ii/)
>
> 难度：中等 / 简单 / 中等 ｜ 标签：链表、双指针

## 核心心智：链表双指针 = 相对运动的物理学

在数组中，我们可以通过下标 `index` 瞬间计算距离和位置。但在链表中，我们只能"摸着石头过河"——**无法随机访问**。

为了解决定位问题，我们引入**双指针**技巧。其核心思想是利用两个指针的**相对运动**（距离差、路程差、速度差）来制造我们需要的"尺子"。

这三道题构成完整的物理学模型：

- **19（距离差）**：先后指针，制造固定间距的"尺子"
- **160（路程差）**：拼接指针，消除长度差的"补齐法"
- **142（速度差）**：快慢指针，利用速度倍率的"追及问题"

掌握这套统一模型后，你会发现所有链表定位题都是同一个"相对运动"的不同应用。

---

## 一、距离差：先后指针的"尺子法"（LeetCode 19）

### 题目描述

给你一个链表，删除链表的倒数第 `n` 个结点，并且返回链表的头结点。

### 核心思路：制造固定间距

如果想找到倒数第 `n` 个节点，普通做法是：
1. 先遍历一遍求长度 `L`
2. 再走 `L - n` 步到目标

这需要**扫描两次**。

**双指针只需扫描一次**：

1. 让 `fast` 指针先走 `n` 步
2. 然后 `fast` 和 `slow` 同时走
3. 当 `fast` 走到链表末尾时，`fast` 和 `slow` 之间的距离依然是 `n`
4. 此时 `slow` 刚好在倒数第 `n` 个节点的位置

**物理类比**：我不量全长，我拿一把长为 `n` 的尺子，尺尾顶到末尾时，尺头就在倒数第 `n` 个。

### 关键技巧：找前驱 + Dummy

要删除节点，需要找到目标节点的**前驱**。所以：

- `fast` 先走 `n + 1` 步（多走一步）
- 配合虚拟头节点 `dummy`，统一处理头节点变化

### 代码实现

```java
public ListNode removeNthFromEnd(ListNode head, int n) {
    ListNode dummy = new ListNode(0, head);
    
    ListNode fast = dummy;
    ListNode slow = dummy;
    
    // 1. fast 先走 n + 1 步（制造间距 n+1，slow 会停在前驱）
    for (int i = 0; i <= n; i++) {
        fast = fast.next;
    }
    
    // 2. 同时移动，直到 fast 走到末尾
    while (fast != null) {
        fast = fast.next;
        slow = slow.next;
    }
    
    // 3. 删除操作（slow 现在指向倒数第 n+1 个节点）
    slow.next = slow.next.next;
    
    return dummy.next;
}
```

### 图解（以 1->2->3->4->5, n=2 为例）

```text
初始：dummy -> 1 -> 2 -> 3 -> 4 -> 5
      fast
      slow

fast 先走 3 步（n+1）：
      dummy -> 1 -> 2 -> 3 -> 4 -> 5
      slow              fast

同时移动，直到 fast 为 null：
      dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> null
                        slow         fast

删除 slow.next（节点 4）：
      dummy -> 1 -> 2 -> 3 -> 5

最终返回 dummy.next
```

### 关键点

- **为什么 fast 先走 n+1 步？** 因为要让 `slow` 停在被删除节点的前驱
- **为什么用 dummy？** 统一处理头节点被删除的情况
- **循环条件**：`while (fast != null)`，保证 `slow` 停在正确位置

---

## 二、路程差：拼接指针的"补齐法"（LeetCode 160）

### 题目描述

给你两个单链表的头节点 `headA` 和 `headB`，请你找出并返回两个单链表相交的起始节点。如果两个链表不存在相交节点，返回 `null`。

### 核心思路：消除长度差

两个链表长度不一样（假设 A 长，B 短），如果直接遍历，它们没法同时走到公共节点。

**巧妙解法**：

1. 指针 `pA` 走完链表 A 后，立刻跳到链表 B 头上继续走
2. 指针 `pB` 走完链表 B 后，立刻跳到链表 A 头上继续走

**原理**：`len(A) + len(B) === len(B) + len(A)`

这样它们走过的总路程是一样的：
- 如果有交点，它们一定会在第二次遍历时相遇
- 如果没有交点，它们会同时走到 `null`

**物理类比**：两个人走的路不一样长，那就互相走一遍对方的路，总路程就一样了。

### 代码实现

```java
public ListNode getIntersectionNode(ListNode headA, ListNode headB) {
    if (headA == null || headB == null) return null;

    ListNode pA = headA;
    ListNode pB = headB;

    // 只要没相遇，就一直走
    while (pA != pB) {
        // pA 走完 A 去走 B，pB 走完 B 去走 A
        pA = (pA == null) ? headB : pA.next;
        pB = (pB == null) ? headA : pB.next;
    }

    // 相遇点即为交点（或同时为 null）
    return pA;
}
```

### 图解（A: 1->2->6->7, B: 3->4->5->6->7）

```text
第一轮遍历：
pA: 1 -> 2 -> 6 -> 7 -> null -> 3 -> 4 -> 5 -> 6
pB: 3 -> 4 -> 5 -> 6 -> 7 -> null -> 1 -> 2 -> 6

相遇点：节点 6（交点）

路程分析：
- pA 走了：len(A) + len(B独有) = 4 + 3 = 7 步
- pB 走了：len(B) + len(A独有) = 5 + 2 = 7 步
- 总路程相同，在交点相遇

无交点情况：
pA: 1 -> 2 -> 3 -> null -> 4 -> 5 -> null
pB: 4 -> 5 -> null -> 1 -> 2 -> 3 -> null

相遇点：null（同时到达末尾）
```

### 关键点

- **为什么能保证相遇？** 总路程相同，步速相同，必然同时到达交点或 `null`
- **循环条件**：`while (pA != pB)`，相遇时退出（可能是交点，也可能是 `null`）
- **边界处理**：提前判空，避免无效遍历

---

## 三、速度差：快慢指针的"追及问题"（LeetCode 142）

### 题目描述

给定一个链表，返回链表开始入环的第一个节点。如果链表无环，则返回 `null`。

### 核心思路：追及 + 数学推导

这是一道**物理题**。

#### 第一步：判断有环

- `fast` 每次走 2 步，`slow` 每次走 1 步
- 如果 `fast` 追上了 `slow`，说明有环（龟兔赛跑）

#### 第二步：找入口

假设：
- 头节点到入口距离为 `x`
- 入口到相遇点距离为 `y`
- 从相遇点再走回到入口距离为 `z`（环的剩余部分）

相遇时：
- `slow` 走了：`x + y`
- `fast` 走了：`x + y + n(y + z)`（多走了 `n` 圈）

因为 `fast` 速度是 `slow` 的 2 倍：

```
2(x + y) = x + y + n(y + z)
x + y = n(y + z)
x = n(y + z) - y
x = (n - 1)(y + z) + z
```

**结论**：当 `n = 1` 时，`x = z`

意味着：
- 一个指针从头开始走
- 一个指针从相遇点开始走
- 它们会在入口处相遇

**物理类比**：跑得快的总会套圈跑得慢的；利用相遇点的数学关系反推起点。

### 代码实现

```java
public ListNode detectCycle(ListNode head) {
    ListNode fast = head;
    ListNode slow = head;

    // 第一步：判断有环
    while (fast != null && fast.next != null) {
        fast = fast.next.next;
        slow = slow.next;

        // 相遇，说明有环
        if (fast == slow) {
            // 第二步：找入口
            ListNode ptr = head;
            while (ptr != slow) {
                ptr = ptr.next;
                slow = slow.next;
            }
            return ptr; // 相遇点即为入口
        }
    }

    return null; // 无环
}
```

### 图解（头->1->2->3->4->2，入口为节点 2）

```text
初始：head -> 1 -> 2 -> 3 -> 4
                   ↑_________|

第一步：快慢指针相遇
x = 1（head 到入口）
y = 2（入口到相遇点，假设在节点 4）
z = 1（相遇点回到入口）

slow 走了：x + y = 1 + 2 = 3 步
fast 走了：x + y + (y + z) = 1 + 2 + 3 = 6 步（多走一圈）

验证：2 * 3 = 6 ✓

第二步：找入口
ptr 从 head 出发：head -> 1 -> 2
slow 从相遇点出发：4 -> 2

相遇点：节点 2（入口）

验证：x = z = 1 ✓
```

### 关键点

- **为什么 fast 每次走 2 步？** 保证速度倍率为 2，简化数学推导
- **为什么 x = z？** 数学推导的结论，当 `n = 1` 时成立
- **循环条件**：
  - 第一步：`while (fast != null && fast.next != null)`，判断有环
  - 第二步：`while (ptr != slow)`，找入口

---

## 四、统一对比与抽象升级

这三道题虽然场景不同，但本质都是在克服链表**无法随机访问**的缺陷。

| 特性 | 19. 删除倒数第 N 个 | 160. 链表相交 | 142. 环形链表 II |
|------|-------------------|--------------|----------------|
| **指针模式** | 先后指针 | 拼接指针 | 快慢指针 |
| **核心原理** | 制造固定间距 | 消除长度差 | 利用速度倍率 |
| **物理类比** | 尺子法 | 补齐法 | 追及问题 |
| **相对运动** | 距离差（间距 n） | 路程差（A+B = B+A） | 速度差（2:1） |
| **关键技巧** | fast 先走 n+1 步 + dummy | 走完 A 去走 B | 相遇后从头和相遇点同时走 |
| **循环条件** | `while (fast != null)` | `while (pA != pB)` | `while (fast != null && fast.next != null)` |
| **时间复杂度** | $O(n)$ | $O(m + n)$ | $O(n)$ |
| **空间复杂度** | $O(1)$ | $O(1)$ | $O(1)$ |

### 统一模板的本质

无论是距离差、路程差还是速度差，核心都是：

1. **定义不变量**：两个指针之间的相对关系（间距、路程、速度）
2. **利用相对运动**：通过移动规则制造我们需要的"尺子"
3. **找到目标**：当不变量满足特定条件时，指针指向目标位置

---

## 五、易错点清单（Bug-Free Guide）

### 1. 空指针判断顺序（142 题）

```java
// ❌ 错误：可能在 fast 为 null 时访问 fast.next
while (fast.next != null && fast != null)

// ✅ 正确：先判断 fast，再判断 fast.next
while (fast != null && fast.next != null)
```

### 2. 循环条件选择（19 题）

```java
// ❌ 错误：fast 走到最后一个节点停止，slow 会多走一步
for (int i = 0; i < n; i++) {
    fast = fast.next;
}
while (fast.next != null) { // 错误！
    fast = fast.next;
    slow = slow.next;
}

// ✅ 正确：fast 先走 n+1 步，然后走到 null 停止
for (int i = 0; i <= n; i++) {
    fast = fast.next;
}
while (fast != null) {
    fast = fast.next;
    slow = slow.next;
}
```

### 3. 拼接指针的跳转时机（160 题）

```java
// ❌ 错误：在 pA.next 为 null 时跳转，会漏掉最后一个节点
if (pA.next == null) {
    pA = headB;
} else {
    pA = pA.next;
}

// ✅ 正确：在 pA 为 null 时跳转（已经走完了）
pA = (pA == null) ? headB : pA.next;
```

### 4. 忘记 Dummy 节点（19 题）

```java
// ❌ 错误：直接从 head 开始，删除头节点时需要特殊处理
ListNode fast = head;
ListNode slow = head;
// ... 如果删除的是头节点，无法返回新头

// ✅ 正确：使用 dummy 统一处理
ListNode dummy = new ListNode(0, head);
ListNode fast = dummy;
ListNode slow = dummy;
// ... 最后返回 dummy.next
```

### 5. 数学推导理解错误（142 题）

```java
// ❌ 错误：认为相遇后 slow 继续走一圈就是入口
while (slow != slow) { // 永远不会相等！
    slow = slow.next;
}

// ✅ 正确：从头和相遇点同时走，相遇点是入口
ListNode ptr = head;
while (ptr != slow) {
    ptr = ptr.next;
    slow = slow.next;
}
return ptr;
```

---

## 六、口诀式总结：三种双指针的决策树

```text
【链表双指针万能模板】

1. 看到"倒数第 k 个" → 先后指针（尺子法）
   - fast 先走 k+1 步（找前驱）
   - 同时移动，fast 到末尾时 slow 在目标前驱
   - 必用 dummy（头节点可能变）

2. 看到"两个链表找公共点" → 拼接指针（补齐法）
   - pA 走完 A 去走 B
   - pB 走完 B 去走 A
   - 总路程相同，必在交点或 null 相遇

3. 看到"是否有环/环入口" → 快慢指针（追及法）
   - fast 每次 2 步，slow 每次 1 步
   - 相遇说明有环
   - 从头和相遇点同时走，相遇点是入口（x = z）

【物理学三定律】
- 距离差：制造固定间距的"尺子"
- 路程差：消除长度差的"补齐"
- 速度差：利用倍率的"追及"

【核心不变量】
- 19 题：fast 和 slow 之间始终保持 n+1 的间距
- 160 题：pA 和 pB 走过的总路程始终相同
- 142 题：fast 速度始终是 slow 的 2 倍
```

---

## 总结

链表双指针的本质是**相对运动的物理学**，掌握这套统一模型后：

- **19** 是距离差，用尺子法制造固定间距
- **160** 是路程差，用补齐法消除长度差
- **142** 是速度差，用追及法找环入口

记住：**定义不变量，利用相对运动，找到目标位置**。画图推演一遍，代码自然长出来。

### 扩展应用

这三种方法还可以解决：

- **876. 链表的中间结点**：快慢指针（fast 走 2 步，slow 走 1 步）
- **141. 环形链表**：快慢指针（只判断有环，不找入口）
- **剑指 Offer 22. 链表中倒数第 k 个节点**：先后指针（不删除，只查找）

掌握物理学思维，链表定位问题迎刃而解！


